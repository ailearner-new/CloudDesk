"""Knowledge base repository for CloudDesk Support Platform."""

from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.entities import SupportArticle, TicketCategory
from app.schemas.common import PaginationParams


class KnowledgeRepository:
    """Repository for knowledge base operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, article_id: str) -> Optional[SupportArticle]:
        """Get article by ID."""
        result = await self.session.execute(
            select(SupportArticle).where(SupportArticle.id == article_id)
        )
        return result.scalar_one_or_none()

    async def list_articles(
        self,
        pagination: PaginationParams,
        category: Optional[TicketCategory] = None,
    ) -> tuple[List[SupportArticle], int]:
        """List articles with pagination."""
        query = select(SupportArticle)

        if category:
            query = query.where(SupportArticle.category == category)

        query = query.order_by(SupportArticle.updated_at.desc())

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        # Apply pagination
        offset = (pagination.page - 1) * pagination.page_size
        query = query.offset(offset).limit(pagination.page_size)

        result = await self.session.execute(query)
        articles = result.scalars().all()

        return list(articles), total

    async def create(self, article: SupportArticle) -> SupportArticle:
        """Create a new article."""
        self.session.add(article)
        await self.session.flush()
        await self.session.refresh(article)
        return article

    async def update(self, article: SupportArticle) -> SupportArticle:
        """Update an article."""
        await self.session.flush()
        await self.session.refresh(article)
        return article

    async def delete(self, article_id: str) -> bool:
        """Delete an article."""
        article = await self.get_by_id(article_id)
        if not article:
            return False
        await self.session.delete(article)
        await self.session.flush()
        return True

    async def count_articles(self) -> int:
        """Count total articles."""
        result = await self.session.execute(select(func.count(SupportArticle.id)))
        return result.scalar_one()

    async def get_by_category(self, category: TicketCategory) -> List[SupportArticle]:
        """Get all articles in a category."""
        result = await self.session.execute(
            select(SupportArticle)
            .where(SupportArticle.category == category)
            .order_by(SupportArticle.title)
        )
        return list(result.scalars().all())