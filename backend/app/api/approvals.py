"""Approvals API routes for CloudDesk Support Platform."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.security import get_current_user, require_agent, require_viewer, User
from app.schemas.common import (
    PaginationParams,
    ApprovalRequestResponse,
    ApprovalDecision,
    ApprovalActionResponse,
    ApprovalStatus,
)
from app.core.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.workflow_repository import WorkflowRepository


router = APIRouter(prefix="/approvals", tags=["approvals"])


def get_workflow_repo(session=Depends(get_session)) -> WorkflowRepository:
    return WorkflowRepository(session)


@router.get("", response_model=dict)
async def list_approvals(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    current_user: User = Depends(require_viewer),
    repo: WorkflowRepository = Depends(get_workflow_repo),
):
    """List approval requests."""
    # For simplicity, we'll fetch all and filter in memory
    # In production, add proper query filters
    pagination = PaginationParams(page=1, page_size=1000)
    # Note: Need a method to list all approvals
    # This is a placeholder implementation
    return {
        "items": [],
        "page": page,
        "page_size": page_size,
        "total": 0,
    }


@router.get("/{approval_id}", response_model=ApprovalRequestResponse)
async def get_approval(
    approval_id: str,
    current_user: User = Depends(require_viewer),
    repo: WorkflowRepository = Depends(get_workflow_repo),
):
    """Get approval request by ID."""
    approval = await repo.get_approval_request(approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")

    return ApprovalRequestResponse(
        id=approval.id,
        workflow_id=approval.workflow_id,
        ticket_id=approval.ticket_id,
        tool_name=approval.tool_name,
        tool_args=approval.tool_args,
        status=approval.status.value,
        requested_at=approval.requested_at,
        decided_at=approval.decided_at,
        decided_by=approval.decided_by,
        reason=approval.reason,
    )


@router.post("/{approval_id}/approve", response_model=ApprovalActionResponse)
async def approve_request(
    approval_id: str,
    data: ApprovalDecision,
    current_user: User = Depends(require_agent),
    repo: WorkflowRepository = Depends(get_workflow_repo),
):
    """Approve an approval request."""
    approval = await repo.update_approval_status(
        approval_id=approval_id,
        status=ApprovalStatus.APPROVED,
        decided_by=current_user.id,
        reason=data.reason,
    )
    if not approval:
        raise HTTPException(
            status_code=409,
            detail="Approval request not found or already decided",
        )

    # Resume workflow
    from app.services.workflow_service import WorkflowService
    workflow_service = WorkflowService(repo.session)
    await workflow_service.resume_workflow(approval.workflow_id, approved=True)

    return ApprovalActionResponse(
        id=approval.id,
        status=approval.status.value,
        decided_at=approval.decided_at,
        decided_by=approval.decided_by,
        reason=approval.reason,
    )


@router.post("/{approval_id}/reject", response_model=ApprovalActionResponse)
async def reject_request(
    approval_id: str,
    data: ApprovalDecision,
    current_user: User = Depends(require_agent),
    repo: WorkflowRepository = Depends(get_workflow_repo),
):
    """Reject an approval request."""
    if not data.reason:
        raise HTTPException(
            status_code=400,
            detail="Rejection reason is required",
        )

    approval = await repo.update_approval_status(
        approval_id=approval_id,
        status=ApprovalStatus.REJECTED,
        decided_by=current_user.id,
        reason=data.reason,
    )
    if not approval:
        raise HTTPException(
            status_code=409,
            detail="Approval request not found or already decided",
        )

    # Resume workflow (will route to escalation)
    from app.services.workflow_service import WorkflowService
    workflow_service = WorkflowService(repo.session)
    await workflow_service.resume_workflow(approval.workflow_id, approved=False)

    return ApprovalActionResponse(
        id=approval.id,
        status=approval.status.value,
        decided_at=approval.decided_at,
        decided_by=approval.decided_by,
        reason=approval.reason,
    )