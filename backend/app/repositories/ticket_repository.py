"""Ticket repository for CloudDesk Support Platform."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.entities import Ticket, TicketMessage, TicketStatus, TicketCategory, TicketSeverity, TicketChannel
from app.schemas.common import PaginationParams


class TicketRepository:
    """Repository for ticket operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, ticket: Ticket) -> Ticket:
        """Create a new ticket."""
        self.session.add(ticket)
        await self.session.flush()
        await self.session.refresh(ticket)
        return ticket

    async def get_by_id(self, ticket_id: str) -> Optional[Ticket]:
        """Get ticket by UUID."""
        result = await self.session.execute(
            select(Ticket)
            .options(selectinload(Ticket.customer), selectinload(Ticket.assignee))
            .where(Ticket.id == ticket_id)
        )
        return result.scalar_one_or_none()

    async def get_by_display_id(self, display_id: str) -> Optional[Ticket]:
        """Get ticket by display ID (e.g., CD-1001) or UUID."""
        # Try UUID first
        if len(display_id) == 36 and display_id.count("-") == 4:
            return await self.get_by_id(display_id)

        # Try display ID pattern (CD-XXXX)
        # For now, just try to find by ID prefix match
        result = await self.session.execute(
            select(Ticket)
            .options(selectinload(Ticket.customer), selectinload(Ticket.assignee))
            .where(Ticket.id.like(f"{display_id.lower()}%"))
        )
        return result.scalar_one_or_none()

    async def list_tickets(
        self,
        pagination: PaginationParams,
        status: Optional[TicketStatus] = None,
        severity: Optional[TicketSeverity] = None,
        category: Optional[TicketCategory] = None,
        assignee_id: Optional[str] = None,
        customer_id: Optional[str] = None,
    ) -> tuple[List[Ticket], int]:
        """List tickets with filters and pagination."""
        query = select(Ticket).options(
            selectinload(Ticket.customer),
            selectinload(Ticket.assignee),
        )

        # Apply filters
        if status:
            query = query.where(Ticket.status == status)
        if severity:
            query = query.where(Ticket.severity == severity)
        if category:
            query = query.where(Ticket.category == category)
        if assignee_id:
            query = query.where(Ticket.assignee_id == assignee_id)
        if customer_id:
            query = query.where(Ticket.customer_id == customer_id)

        # Order by created_at desc
        query = query.order_by(Ticket.created_at.desc())

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        # Apply pagination
        offset = (pagination.page - 1) * pagination.page_size
        query = query.offset(offset).limit(pagination.page_size)

        result = await self.session.execute(query)
        tickets = result.scalars().all()

        return list(tickets), total

    async def update(self, ticket: Ticket) -> Ticket:
        """Update a ticket."""
        ticket.updated_at = datetime.now(ticket.created_at.tzinfo) if ticket.created_at.tzinfo else datetime.utcnow()
        await self.session.flush()
        await self.session.refresh(ticket)
        return ticket

    async def add_message(self, message: TicketMessage) -> TicketMessage:
        """Add a message to a ticket."""
        self.session.add(message)
        await self.session.flush()
        await self.session.refresh(message)
        return message

    async def get_messages(self, ticket_id: str) -> List[TicketMessage]:
        """Get all messages for a ticket."""
        result = await self.session.execute(
            select(TicketMessage)
            .options(selectinload(TicketMessage.author))
            .where(TicketMessage.ticket_id == ticket_id)
            .order_by(TicketMessage.created_at.asc())
        )
        return list(result.scalars().all())

    async def search_tickets(
        self,
        query: str,
        pagination: PaginationParams,
    ) -> tuple[List[Ticket], int]:
        """Search tickets by subject or body."""
        search_query = select(Ticket).options(
            selectinload(Ticket.customer),
            selectinload(Ticket.assignee),
        ).where(
            or_(
                Ticket.subject.ilike(f"%{query}%"),
                Ticket.body.ilike(f"%{query}%"),
            )
        ).order_by(Ticket.created_at.desc())

        # Count total
        count_query = select(func.count()).select_from(search_query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        # Apply pagination
        offset = (pagination.page - 1) * pagination.page_size
        search_query = search_query.offset(offset).limit(pagination.page_size)

        result = await self.session.execute(search_query)
        tickets = result.scalars().all()

        return list(tickets), total