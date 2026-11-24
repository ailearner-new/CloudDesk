"""Vector store abstraction for CloudDesk Support Platform."""

import asyncio
import hashlib
import json
import math
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class VectorDocument:
    """Document in vector store."""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


class VectorStoreService(ABC):
    """Abstract vector store service."""

    @abstractmethod
    async def add_documents(self, documents: List[VectorDocument]) -> None:
        """Add documents to the store."""
        pass

    @abstractmethod
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[VectorDocument, float]]:
        """Search for similar documents."""
        pass

    @abstractmethod
    async def delete(self, ids: List[str]) -> None:
        """Delete documents by ID."""
        pass

    @abstractmethod
    async def count(self) -> int:
        """Count total documents."""
        pass

    @abstractmethod
    async def health(self) -> bool:
        """Check store health."""
        pass

    @abstractmethod
    async def list_chunks(self, filter: Optional[Dict[str, Any]] = None) -> List[VectorDocument]:
        """List all chunks (for keyword search)."""
        pass


class InMemoryVectorStore(VectorStoreService):
    """In-memory vector store for demo/testing."""

    def __init__(self):
        self._documents: Dict[str, VectorDocument] = {}
        self._embeddings: Dict[str, List[float]] = {}

    async def add_documents(self, documents: List[VectorDocument]) -> None:
        for doc in documents:
            self._documents[doc.id] = doc
            if doc.embedding:
                self._embeddings[doc.id] = doc.embedding

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[VectorDocument, float]]:
        if not self._embeddings:
            return []

        query_vec = np.array(query_embedding)
        scores = []

        for doc_id, embedding in self._embeddings.items():
            doc = self._documents.get(doc_id)
            if not doc:
                continue

            # Apply filter
            if filter:
                match = True
                for key, value in filter.items():
                    if doc.metadata.get(key) != value:
                        match = False
                        break
                if not match:
                    continue

            # Cosine similarity
            doc_vec = np.array(embedding)
            similarity = np.dot(query_vec, doc_vec) / (
                np.linalg.norm(query_vec) * np.linalg.norm(doc_vec) + 1e-8
            )
            scores.append((doc, float(similarity)))

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    async def delete(self, ids: List[str]) -> None:
        for id in ids:
            self._documents.pop(id, None)
            self._embeddings.pop(id, None)

    async def count(self) -> int:
        return len(self._documents)

    async def health(self) -> bool:
        return True

    async def list_chunks(self, filter: Optional[Dict[str, Any]] = None) -> List[VectorDocument]:
        results = []
        for doc in self._documents.values():
            if filter:
                match = True
                for key, value in filter.items():
                    if doc.metadata.get(key) != value:
                        match = False
                        break
                if not match:
                    continue
            results.append(doc)
        return results


class QdrantVectorStore(VectorStoreService):
    """Qdrant vector store for production."""

    def __init__(self):
        self._client = None
        self._collection_name = get_settings().QDRANT_COLLECTION

    async def _get_client(self):
        if self._client is None:
            from qdrant_client import AsyncQdrantClient
            settings = get_settings()
            self._client = AsyncQdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
            )
            # Ensure collection exists
            await self._ensure_collection()
        return self._client

    async def _ensure_collection(self):
        from qdrant_client.models import Distance, VectorParams
        client = await self._get_client()
        collections = await client.get_collections()
        if self._collection_name not in [c.name for c in collections.collections]:
            await client.create_collection(
                collection_name=self._collection_name,
                vectors_config=VectorParams(
                    size=get_settings().EMBEDDING_DIMENSIONS,
                    distance=Distance.COSINE,
                ),
            )

    async def add_documents(self, documents: List[VectorDocument]) -> None:
        from qdrant_client.models import PointStruct
        client = await self._get_client()

        points = []
        for doc in documents:
            if doc.embedding:
                points.append(PointStruct(
                    id=doc.id,
                    vector=doc.embedding,
                    payload={**doc.metadata, "content": doc.content},
                ))

        if points:
            await client.upsert(collection_name=self._collection_name, points=points)

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[VectorDocument, float]]:
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        client = await self._get_client()

        qdrant_filter = None
        if filter:
            conditions = [
                FieldCondition(key=key, match=MatchValue(value=value))
                for key, value in filter.items()
            ]
            qdrant_filter = Filter(must=conditions)

        results = await client.search(
            collection_name=self._collection_name,
            query_vector=query_embedding,
            limit=top_k,
            query_filter=qdrant_filter,
            with_payload=True,
        )

        documents = []
        for hit in results:
            payload = hit.payload or {}
            content = payload.pop("content", "")
            doc = VectorDocument(
                id=str(hit.id),
                content=content,
                metadata=payload,
            )
            documents.append((doc, hit.score))

        return documents

    async def delete(self, ids: List[str]) -> None:
        from qdrant_client.models import PointIdsList
        client = await self._get_client()
        await client.delete(
            collection_name=self._collection_name,
            points_selector=PointIdsList(points=ids),
        )

    async def count(self) -> int:
        client = await self._get_client()
        info = await client.get_collection(collection_name=self._collection_name)
        return info.points_count

    async def health(self) -> bool:
        try:
            client = await self._get_client()
            await client.get_collections()
            return True
        except Exception:
            return False

    async def list_chunks(self, filter: Optional[Dict[str, Any]] = None) -> List[VectorDocument]:
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        client = await self._get_client()

        qdrant_filter = None
        if filter:
            conditions = [
                FieldCondition(key=key, match=MatchValue(value=value))
                for key, value in filter.items()
            ]
            qdrant_filter = Filter(must=conditions)

        results = []
        offset = None
        while True:
            hits, next_offset = await client.scroll(
                collection_name=self._collection_name,
                limit=100,
                offset=offset,
                scroll_filter=qdrant_filter,
                with_payload=True,
                with_vectors=False,
            )
            for hit in hits:
                payload = hit.payload or {}
                content = payload.pop("content", "")
                doc = VectorDocument(
                    id=str(hit.id),
                    content=content,
                    metadata=payload,
                )
                results.append(doc)

            if next_offset is None:
                break
            offset = next_offset

        return results


# Global instance
_vector_store: Optional[VectorStoreService] = None


def get_vector_store() -> VectorStoreService:
    """Get or create the vector store."""
    global _vector_store
    if _vector_store is None:
        settings = get_settings()
        if settings.VECTOR_STORE == "qdrant":
            _vector_store = QdrantVectorStore()
        else:
            _vector_store = InMemoryVectorStore()
    return _vector_store