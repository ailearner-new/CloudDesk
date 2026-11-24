"""Workflow repository for CloudDesk Support Platform."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.entities import (
    WorkflowRun,
    WorkflowEvent,
    WorkflowStatus,
    WorkflowEventType,
    ResolutionAction,
    ApprovalRequest,
    ApprovalStatus,
    Escalation,
    EscalationStatus,
)
from app.schemas.common import PaginationParams


class WorkflowRepository:
    """Repository for workflow operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_run(self, run: WorkflowRun) -> WorkflowRun:
        """Create a new workflow run."""
        self.session.add(run)
        await self.session.flush()
        await self.session.refresh(run)
        return run

    async def get_run(self, workflow_id: str) -> Optional[WorkflowRun]:
        """Get workflow run by ID."""
        result = await self.session.execute(
            select(WorkflowRun)
            .options(selectinload(WorkflowRun.ticket))
            .where(WorkflowRun.id == workflow_id)
        )
        return result.scalar_one_or_none()

    async def get_run_by_ticket(self, ticket_id: str, status: Optional[WorkflowStatus] = None) -> Optional[WorkflowRun]:
        """Get latest workflow run for a ticket."""
        query = (
            select(WorkflowRun)
            .where(WorkflowRun.ticket_id == ticket_id)
            .order_by(WorkflowRun.started_at.desc())
        )
        if status:
            query = query.where(WorkflowRun.status == status)
        result = await self.session.execute(query.limit(1))
        return result.scalar_one_or_none()

    async def update_run(self, run: WorkflowRun) -> WorkflowRun:
        """Update a workflow run."""
        await self.session.flush()
        await self.session.refresh(run)
        return run

    async def add_event(self, event: WorkflowEvent) -> WorkflowEvent:
        """Add a workflow event."""
        self.session.add(event)
        await self.session.flush()
        await self.session.refresh(event)
        return event

    async def get_events(
        self,
        workflow_id: str,
        event_types: Optional[List[WorkflowEventType]] = None,
    ) -> List[WorkflowEvent]:
        """Get workflow events."""
        query = (
            select(WorkflowEvent)
            .where(WorkflowEvent.workflow_id == workflow_id)
            .order_by(WorkflowEvent.timestamp.asc())
        )
        if event_types:
            query = query.where(WorkflowEvent.event_type.in_(event_types))
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def add_resolution_action(self, action: ResolutionAction) -> ResolutionAction:
        """Add a resolution action."""
        self.session.add(action)
        await self.session.flush()
        await self.session.refresh(action)
        return action

    async def get_resolution_actions(self, workflow_id: str) -> List[ResolutionAction]:
        """Get resolution actions for a workflow."""
        result = await self.session.execute(
            select(ResolutionAction)
            .where(ResolutionAction.workflow_id == workflow_id)
            .order_by(ResolutionAction.created_at.asc())
        )
        return list(result.scalars().all())

    async def create_approval_request(self, approval: ApprovalRequest) -> ApprovalRequest:
        """Create an approval request."""
        self.session.add(approval)
        await self.session.flush()
        await self.session.refresh(approval)
        return approval

    async def get_approval_request(self, approval_id: str) -> Optional[ApprovalRequest]:
        """Get approval request by ID."""
        result = await self.session.execute(
            select(ApprovalRequest).where(ApprovalRequest.id == approval_id)
        )
        return result.scalar_one_or_none()

    async def get_pending_approval(self, workflow_id: str) -> Optional[ApprovalRequest]:
        """Get pending approval for a workflow."""
        result = await self.session.execute(
            select(ApprovalRequest).where(
                ApprovalRequest.workflow_id == workflow_id,
                ApprovalRequest.status == ApprovalStatus.PENDING,
            )
        )
        return result.scalar_one_or_none()

    async def update_approval_status(
        self,
        approval_id: str,
        status: ApprovalStatus,
        decided_by: str,
        reason: Optional[str] = None,
    ) -> Optional[ApprovalRequest]:
        """Update approval status atomically."""
        from sqlalchemy import update
        from datetime import datetime

        result = await self.session.execute(
            update(ApprovalRequest)
            .where(
                ApprovalRequest.id == approval_id,
                ApprovalRequest.status == ApprovalStatus.PENDING,
            )
            .values(
                status=status,
                decided_by=decided_by,
                decided_at=datetime.utcnow(),
                reason=reason,
            )
            .returning(ApprovalRequest)
        )
        await self.session.flush()
        return result.scalar_one_or_none()

    async def create_escalation(self, escalation: Escalation) -> Escalation:
        """Create an escalation."""
        self.session.add(escalation)
        await self.session.flush()
        await self.session.refresh(escalation)
        return escalation

    async def get_escalation(self, escalation_id: str) -> Optional[Escalation]:
        """Get escalation by ID."""
        result = await self.session.execute(
            select(Escalation).where(Escalation.id == escalation_id)
        )
        return result.scalar_one_or_none()

    async def list_escalations(
        self,
        pagination: PaginationParams,
        status: Optional[EscalationStatus] = None,
    ) -> tuple[List[Escalation], int]:
        """List escalations with pagination."""
        query = select(Escalation).order_by(Escalation.created_at.desc())

        if status:
            query = query.where(Escalation.status == status)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        # Apply pagination
        offset = (pagination.page - 1) * pagination.page_size
        query = query.offset(offset).limit(pagination.page_size)

        result = await self.session.execute(query)
        escalations = result.scalars().all()

        return list(escalations), total

    async def update_escalation(self, escalation: Escalation) -> Escalation:
        """Update an escalation."""
        await self.session.flush()
        await self.session.refresh(escalation)
        return escalation