"""Retriever for CloudDesk Support Platform RAG pipeline.

Implements hybrid retrieval: semantic + keyword (BM25) -> RRF -> heuristic rerank -> optional LLM rerank.
"""

import asyncio
import hashlib
import json
import math
import re
import time
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import get_settings
from app.core.logging import get_logger
from rag.vector_store import get_vector_store, VectorDocument

logger = get_logger(__name__)


@dataclass
class SearchResult:
    """Search result with score and metadata."""
    id: str
    title: str
    source: str
    snippet: str
    score: float
    url: str
    article_id: str


class BM25Index:
    """Simple BM25 implementation for keyword search."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.documents: List[VectorDocument] = []
        self.doc_freqs: Dict[str, int] = {}
        self.doc_lengths: List[int] = []
        self.avgdl: float = 0
        self._built = False

    def build(self, documents: List[VectorDocument]) -> None:
        """Build BM25 index from documents."""
        self.documents = documents
        self.doc_freqs = {}
        self.doc_lengths = []

        # Tokenize all documents
        for doc in documents:
            tokens = self._tokenize(doc.content)
            self.doc_lengths.append(len(tokens))
            # Count document frequency
            unique_tokens = set(tokens)
            for token in unique_tokens:
                self.doc_freqs[token] = self.doc_freqs.get(token, 0) + 1

        self.avgdl = sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0
        self._built = True

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization."""
        # Lowercase, split on non-alphanumeric
        tokens = re.findall(r'\b\w+\b', text.lower())
        # Filter stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'it', 'its', 'you', 'your', 'we', 'our', 'they',
            'their', 'he', 'she', 'his', 'her', 'him', 'i', 'me', 'my', 'mine'
        }
        return [t for t in tokens if t not in stop_words and len(t) > 1]

    def search(self, query: str, top_k: int = 10) -> List[Tuple[VectorDocument, float]]:
        """Search using BM25."""
        if not self._built:
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        scores = []
        N = len(self.documents)

        for i, doc in enumerate(self.documents):
            doc_tokens = self._tokenize(doc.content)
            token_counts = Counter(doc_tokens)
            dl = self.doc_lengths[i]

            score = 0.0
            for token in query_tokens:
                if token not in self.doc_freqs:
                    continue
                df = self.doc_freqs[token]
                tf = token_counts.get(token, 0)
                if tf == 0:
                    continue

                # BM25 formula
                idf = math.log((N - df + 0.5) / (df + 0.5) + 1)
                score += idf * (tf * (self.k1 + 1)) / (tf + self.k1 * (1 - self.b + self.b * dl / self.avgdl))

            if score > 0:
                scores.append((doc, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


# Global BM25 index
_bm25_index: Optional[BM25Index] = None


def get_bm25_index() -> BM25Index:
    """Get or create BM25 index."""
    global _bm25_index
    if _bm25_index is None:
        _bm25_index = BM25Index()
    return _bm25_index


def rebuild_bm25_index(documents: List[VectorDocument]) -> None:
    """Rebuild BM25 index with new documents."""
    global _bm25_index
    _bm25_index = BM25Index()
    _bm25_index.build(documents)


# Cache for retrieval results
_retrieval_cache: Dict[str, Tuple[List[SearchResult], float]] = {}
CACHE_TTL = 300  # 5 minutes


def _cache_key(query: str, category: Optional[str], mode: str, top_k: int) -> str:
    """Generate cache key."""
    key_data = f"{query}|{category or ''}|{mode}|{top_k}"
    return hashlib.md5(key_data.encode()).hexdigest()


async def retrieve(
    query: str,
    category: Optional[str] = None,
    mode: str = "hybrid",
    top_k: int = 5,
    category_hint: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Main retrieval function: hybrid search with reranking."""
    settings = get_settings()

    # Check cache
    cache_key = _cache_key(query, category, mode, top_k)
    if cache_key in _retrieval_cache:
        results, timestamp = _retrieval_cache[cache_key]
        if time.time() - timestamp < CACHE_TTL:
            return results[:top_k]

    # Get vector store
    vs = get_vector_store()

    # Get query embedding
    query_embedding = await _get_query_embedding(query)

    # Semantic search
    semantic_results = []
    if mode in ("hybrid", "semantic"):
        filter_dict = {}
        if category:
            filter_dict["category"] = category
        elif category_hint:
            # category_hint only nudges rerank, doesn't filter
            pass

        semantic_raw = await vs.search(query_embedding, top_k=top_k * 3, filter=filter_dict if filter_dict else None)
        semantic_results = [
            SearchResult(
                id=doc.id,
                title=doc.metadata.get("title", ""),
                source=f"kb://{doc.metadata.get('slug', 'unknown')}#{doc.metadata.get('heading', 'content')}",
                snippet=doc.content[:300],
                score=score,
                url=f"/knowledge/articles/{doc.metadata.get('article_id', doc.id)}",
                article_id=doc.metadata.get("article_id", doc.id),
            )
            for doc, score in semantic_raw
        ]

    # Keyword search (BM25)
    keyword_results = []
    if mode in ("hybrid", "keyword"):
        bm25 = get_bm25_index()
        filter_dict = {}
        if category:
            filter_dict["category"] = category

        keyword_raw = bm25.search(query, top_k=top_k * 3)
        # Apply filter if needed
        if filter_dict:
            keyword_raw = [(doc, score) for doc, score in keyword_raw if doc.metadata.get("category") == category]

        keyword_results = [
            SearchResult(
                id=doc.id,
                title=doc.metadata.get("title", ""),
                source=f"kb://{doc.metadata.get('slug', 'unknown')}#{doc.metadata.get('heading', 'content')}",
                snippet=doc.content[:300],
                score=score,
                url=f"/knowledge/articles/{doc.metadata.get('article_id', doc.id)}",
                article_id=doc.metadata.get("article_id", doc.id),
            )
            for doc, score in keyword_raw
        ]

    # Reciprocal Rank Fusion (RRF)
    fused_results = _reciprocal_rank_fusion(
        semantic_results,
        keyword_results,
        k=60,
    )

    # Heuristic rerank
    reranked = _heuristic_rerank(fused_results, query, category, category_hint)

    # Deduplicate: one hit per article
    final_results = _deduplicate_by_article(reranked, top_k)

    # Convert to dict
    result_dicts = [
        {
            "id": r.id,
            "title": r.title,
            "source": r.source,
            "snippet": r.snippet,
            "score": r.score,
            "url": r.url,
            "article_id": r.article_id,
        }
        for r in final_results
    ]

    # Cache results
    _retrieval_cache[cache_key] = (result_dicts, time.time())

    return result_dicts[:top_k]


def _reciprocal_rank_fusion(
    semantic: List[SearchResult],
    keyword: List[SearchResult],
    k: int = 60,
) -> List[SearchResult]:
    """Combine results using Reciprocal Rank Fusion."""
    scores: Dict[str, float] = {}
    items: Dict[str, SearchResult] = {}

    # Process semantic results
    for rank, result in enumerate(semantic):
        rrf_score = 1.0 / (k + rank + 1)
        if result.id in scores:
            scores[result.id] += rrf_score
        else:
            scores[result.id] = rrf_score
            items[result.id] = result

    # Process keyword results
    for rank, result in enumerate(keyword):
        rrf_score = 1.0 / (k + rank + 1)
        if result.id in scores:
            scores[result.id] += rrf_score
        else:
            scores[result.id] = rrf_score
            items[result.id] = result

    # Sort by combined score
    sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

    fused = []
    for id in sorted_ids:
        result = items[id]
        result.score = scores[id]
        fused.append(result)

    return fused


def _heuristic_rerank(
    results: List[SearchResult],
    query: str,
    category: Optional[str],
    category_hint: Optional[str],
) -> List[SearchResult]:
    """Apply heuristic reranking based on category match and title overlap."""
    query_lower = query.lower()
    query_tokens = set(re.findall(r'\b\w+\b', query_lower))

    for result in results:
        # Category match boost
        if category and result.source:
            # Extract category from source or metadata
            pass  # Would need category in metadata

        # Title overlap boost
        title_tokens = set(re.findall(r'\b\w+\b', result.title.lower()))
        title_overlap = len(query_tokens & title_tokens) / max(len(query_tokens), 1)
        result.score += title_overlap * 0.1

        # Category hint boost (soft)
        if category_hint and category_hint in result.source:
            result.score += 0.05

    results.sort(key=lambda x: x.score, reverse=True)
    return results


def _deduplicate_by_article(results: List[SearchResult], top_k: int) -> List[SearchResult]:
    """Keep only one result per article (highest scoring)."""
    seen_articles = set()
    deduplicated = []

    for result in results:
        if result.article_id not in seen_articles:
            seen_articles.add(result.article_id)
            deduplicated.append(result)
            if len(deduplicated) >= top_k:
                break

    return deduplicated


async def _get_query_embedding(query: str) -> List[float]:
    """Get embedding for query."""
    settings = get_settings()

    if settings.EMBEDDING_PROVIDER == "fake":
        return _fake_embedding(query)
    elif settings.EMBEDDING_PROVIDER == "openai":
        return await _openai_embedding(query)
    else:
        return _fake_embedding(query)


def _fake_embedding(text: str) -> List[float]:
    """Generate fake embedding using hashed bag-of-words."""
    dimensions = 384
    tokens = re.findall(r'\b\w+\b', text.lower())
    vec = [0.0] * dimensions

    for token in tokens:
        # Hash token to index
        idx = int(hashlib.md5(token.encode()).hexdigest(), 16) % dimensions
        vec[idx] += 1.0

    # Normalize
    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 0:
        vec = [v / norm for v in vec]

    return vec


async def _openai_embedding(text: str) -> List[float]:
    """Get embedding from OpenAI."""
    try:
        from openai import AsyncOpenAI
        settings = get_settings()
        client = AsyncOpenAI(api_key=settings.LLM_API_KEY)
        response = await client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=text,
            dimensions=settings.EMBEDDING_DIMENSIONS,
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"OpenAI embedding failed: {e}")
        return _fake_embedding(text)


async def ingest_knowledge_base(kb_dir) -> Dict[str, int]:
    """Ingest knowledge base articles into vector store."""
    import os
    from pathlib import Path
    from rag.chunking import load_article_file, chunk_text
    from rag.vector_store import get_vector_store, VectorDocument

    settings = get_settings()
    vs = get_vector_store()

    articles_count = 0
    chunks_count = 0
    all_chunks = []

    for md_file in Path(kb_dir).glob("*.md"):
        metadata, content = load_article_file(str(md_file))

        if not metadata.get("title") or not metadata.get("category"):
            logger.warning(f"Skipping {md_file}: missing title or category")
            continue

        # Generate slug from filename
        slug = md_file.stem
        article_id = f"art-{slug}"

        # Chunk the article
        chunks = chunk_text(
            content,
            title=metadata["title"],
            article_id=article_id,
        )

        # Create vector documents
        for i, chunk in enumerate(chunks):
            chunk_id = f"{article_id}-chunk-{i}"
            vec_doc = VectorDocument(
                id=chunk_id,
                content=chunk.content,
                metadata={
                    "title": metadata["title"],
                    "category": metadata["category"],
                    "tags": metadata.get("tags", []),
                    "summary": metadata.get("summary", ""),
                    "slug": slug,
                    "heading": chunk.heading,
                    "article_id": article_id,
                    "chunk_index": i,
                },
            )
            all_chunks.append(vec_doc)

        articles_count += 1
        chunks_count += len(chunks)

    # Generate embeddings and add to vector store
    for doc in all_chunks:
        doc.embedding = await _get_query_embedding(doc.content)

    await vs.add_documents(all_chunks)

    # Rebuild BM25 index
    rebuild_bm25_index(all_chunks)

    logger.info(f"Ingested {articles_count} articles, {chunks_count} chunks")

    return {"chunks": chunks_count, "articles": articles_count}