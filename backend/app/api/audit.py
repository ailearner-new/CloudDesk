"""Audit API routes for CloudDesk Support Platform."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.security import get_current_user, require_admin, User
from app.schemas.common import PaginationParams, AuditLogResponse
from app.core.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.audit_repository import AuditRepository


router = APIRouter(prefix="/audit", tags=["audit"])


def get_audit_repo(session=Depends(get_session)) -> AuditRepository:
    return AuditRepository(session)


@router.get("", response_model=dict)
async def list_audit_logs(
    page: int = 1,
    page_size: int = 50,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(require_admin),
    repo: AuditRepository = Depends(get_audit_repo),
):
    """List audit logs (admin only)."""
    pagination = PaginationParams(page=page, page_size=page_size)
    logs, total = await repo.list_logs(
        pagination=pagination,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        start_date=start_date,
        end_date=end_date,
    )

    return {
        "items": [
            AuditLogResponse(
                id=log.id,
                user_id=log.user_id,
                user_email=log.user_email,
                action=log.action,
                resource_type=log.resource_type,
                resource_id=log.resource_id,
                request_id=log.request_id,
                method=log.method,
                path=log.path,
                status_code=log.status_code,
                duration_ms=log.duration_ms,
                ip=log.ip,
                user_agent=log.user_agent,
                details=log.details,
                created_at=log.created_at,
            )
            for log in logs
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
    }