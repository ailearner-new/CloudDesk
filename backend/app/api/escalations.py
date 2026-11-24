"""Escalations API routes for CloudDesk Support Platform."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.security import get_current_user, require_agent, require_viewer, User
from app.schemas.common import (
    PaginationParams,
    EscalationResponse,
    EscalationCreate,
    EscalationUpdate,
    EscalationStatus,
)
from app.core.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.workflow_repository import WorkflowRepository


router = APIRouter(prefix="/escalations", tags=["escalations"])


def get_workflow_repo(session=Depends(get_session)) -> WorkflowRepository:
    return WorkflowRepository(session)


@router.get("", response_model=dict)
async def list_escalations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    current_user: User = Depends(require_viewer),
    repo: WorkflowRepository = Depends(get_workflow_repo),
):
    """List escalations."""
    status_enum = None
    if status:
        try:
            status_enum = EscalationStatus(status)
        except ValueError:
            pass

    pagination = PaginationParams(page=page, page_size=page_size)
    escalations, total = await repo.list_escalations(pagination, status_enum)

    return {
        "items": [
            EscalationResponse(
                id=e.id,
                ticket_id=e.ticket_id,
                reason=e.reason,
                team=e.team,
                status=e.status.value,
                created_by=e.created_by,
                assigned_to=e.assigned_to,
                resolution=e.resolution,
                created_at=e.created_at,
                updated_at=e.updated_at,
                resolved_at=e.resolved_at,
            )
            for e in escalations
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
    }


@router.get("/{escalation_id}", response_model=EscalationResponse)
async def get_escalation(
    escalation_id: str,
    current_user: User = Depends(require_viewer),
    repo: WorkflowRepository = Depends(get_workflow_repo),
):
    """Get escalation by ID."""
    escalation = await repo.get_escalation(escalation_id)
    if not escalation:
        raise HTTPException(status_code=404, detail="Escalation not found")

    return EscalationResponse(
        id=escalation.id,
        ticket_id=escalation.ticket_id,
        reason=escalation.reason,
        team=escalation.team,
        status=escalation.status.value,
        created_by=escalation.created_by,
        assigned_to=escalation.assigned_to,
        resolution=escalation.resolution,
        created_at=escalation.created_at,
        updated_at=escalation.updated_at,
        resolved_at=escalation.resolved_at,
    )


@router.patch("/{escalation_id}", response_model=EscalationResponse)
async def update_escalation(
    escalation_id: str,
    data: EscalationUpdate,
    current_user: User = Depends(require_agent),
    repo: WorkflowRepository = Depends(get_workflow_repo),
):
    """Update an escalation."""
    escalation = await repo.get_escalation(escalation_id)
    if not escalation:
        raise HTTPException(status_code=404, detail="Escalation not found")

    if data.status is not None:
        escalation.status = data.status
        if data.status == EscalationStatus.RESOLVED:
            from datetime import datetime
            escalation.resolved_at = datetime.utcnow()
    if data.resolution is not None:
        escalation.resolution = data.resolution

    escalation = await repo.update_escalation(escalation)

    return EscalationResponse(
        id=escalation.id,
        ticket_id=escalation.ticket_id,
        reason=escalation.reason,
        team=escalation.team,
        status=escalation.status.value,
        created_by=escalation.created_by,
        assigned_to=escalation.assigned_to,
        resolution=escalation.resolution,
        created_at=escalation.created_at,
        updated_at=escalation.updated_at,
        resolved_at=escalation.resolved_at,
    )