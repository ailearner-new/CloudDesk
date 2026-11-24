"""Knowledge service for CloudDesk Support Platform."""

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import SupportArticle, TicketCategory
from app.repositories.knowledge_repository import KnowledgeRepository
from app.schemas.common import PaginationParams, KnowledgeSearchRequest, KnowledgeSearchResponse, KnowledgeSearchResult, ReindexResponse


class KnowledgeService:
    """Service for knowledge base operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.knowledge_repo = KnowledgeRepository(session)

    async def get_article(self, article_id: str) -> Optional[SupportArticle]:
        """Get article by ID."""
        return await self.knowledge_repo.get_by_id(article_id)

    async def list_articles(
        self,
        pagination: PaginationParams,
        category: Optional[str] = None,
    ) -> tuple[List[SupportArticle], int]:
        """List articles with pagination."""
        category_enum = None
        if category:
            try:
                category_enum = TicketCategory(category)
            except ValueError:
                pass

        return await self.knowledge_repo.list_articles(pagination, category_enum)

    async def search(self, request: KnowledgeSearchRequest) -> KnowledgeSearchResponse:
        """Search knowledge base using RAG."""
        from rag.retriever import retrieve

        results = await retrieve(
            query=request.q,
            category=request.category.value if request.category else None,
            mode=request.mode,
            top_k=request.top_k,
        )

        search_results = [
            KnowledgeSearchResult(
                id=r["id"],
                title=r["title"],
                source=r["source"],
                snippet=r["snippet"],
                score=r["score"],
                url=r["url"],
                article_id=r["article_id"],
            )
            for r in results
        ]

        return KnowledgeSearchResponse(
            query=request.q,
            mode=request.mode,
            results=search_results,
        )

    async def reindex(self) -> ReindexResponse:
        """Reindex the knowledge base."""
        from rag.ingest import ingest_knowledge_base
        from app.core.config import get_settings

        settings = get_settings()
        kb_dir = settings.knowledge_base_dir

        result = await ingest_knowledge_base(kb_dir)

        return ReindexResponse(indexed=result)