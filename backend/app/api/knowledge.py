"""Knowledge API routes for CloudDesk Support Platform."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.security import get_current_user, require_admin, require_viewer, User
from app.schemas.common import (
    PaginationParams,
    SupportArticleResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    ReindexResponse,
)
from app.services.knowledge_service import KnowledgeService
from app.core.database import get_session

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


def get_knowledge_service(session=Depends(get_session)) -> KnowledgeService:
    return KnowledgeService(session)


@router.get("/articles", response_model=dict)
async def list_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    current_user: User = Depends(require_viewer),
    service: KnowledgeService = Depends(get_knowledge_service),
):
    """List knowledge base articles."""
    pagination = PaginationParams(page=page, page_size=page_size)
    articles, total = await service.list_articles(pagination, category)

    return {
        "items": [
            SupportArticleResponse(
                id=a.id,
                title=a.title,
                category=a.category.value,
                tags=a.tags,
                summary=a.summary,
                content=a.content,
                created_at=a.created_at,
                updated_at=a.updated_at,
            )
            for a in articles
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
    }


@router.get("/articles/{article_id}", response_model=SupportArticleResponse)
async def get_article(
    article_id: str,
    current_user: User = Depends(require_viewer),
    service: KnowledgeService = Depends(get_knowledge_service),
):
    """Get article by ID."""
    article = await service.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    return SupportArticleResponse(
        id=article.id,
        title=article.title,
        category=article.category.value,
        tags=article.tags,
        summary=article.summary,
        content=article.content,
        created_at=article.created_at,
        updated_at=article.updated_at,
    )


@router.get("/search", response_model=KnowledgeSearchResponse)
async def search_knowledge(
    q: str = Query(..., min_length=1),
    category: Optional[str] = None,
    mode: str = Query("hybrid", pattern="^(hybrid|semantic|keyword)$"),
    top_k: int = Query(5, ge=1, le=20),
    current_user: User = Depends(require_viewer),
    service: KnowledgeService = Depends(get_knowledge_service),
):
    """Search knowledge base."""
    category_enum = None
    if category:
        from app.models.entities import TicketCategory
        try:
            category_enum = TicketCategory(category)
        except ValueError:
            pass

    request = KnowledgeSearchRequest(
        q=q,
        category=category_enum,
        mode=mode,
        top_k=top_k,
    )

    return await service.search(request)


@router.post("/reindex", response_model=ReindexResponse)
async def reindex_knowledge(
    current_user: User = Depends(require_admin),
    service: KnowledgeService = Depends(get_knowledge_service),
):
    """Reindex knowledge base (admin only)."""
    return await service.reindex()