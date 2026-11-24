"""Ticket service for CloudDesk Support Platform."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Ticket, TicketMessage, TicketStatus, TicketChannel, Profile
from app.repositories.ticket_repository import TicketRepository
from app.repositories.customer_repository import CustomerRepository
from app.schemas.common import PaginationParams, TicketCreate, TicketUpdate, TicketMessageCreate


class TicketService:
    """Service for ticket operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.ticket_repo = TicketRepository(session)
        self.customer_repo = CustomerRepository(session)

    async def create_ticket(self, data: TicketCreate, assignee: Optional[Profile] = None) -> Ticket:
        """Create a new ticket from request data."""
        # Find customer by email
        customer = await self.customer_repo.get_by_email(data.customer_email)
        if not customer:
            raise ValueError(f"Customer not found: {data.customer_email}")

        # Create ticket
        ticket = Ticket(
            subject=data.subject,
            body=data.body,
            channel=TicketChannel(data.channel),
            status=TicketStatus.NEW,
            customer_id=customer.id,
            assignee_id=assignee.id if assignee else None,
        )

        return await self.ticket_repo.create(ticket)

    async def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Get ticket by ID or display ID."""
        return await self.ticket_repo.get_by_display_id(ticket_id)

    async def list_tickets(
        self,
        pagination: PaginationParams,
        status: Optional[TicketStatus] = None,
        severity: Optional[str] = None,
        category: Optional[str] = None,
        assignee_id: Optional[str] = None,
        customer_id: Optional[str] = None,
    ) -> tuple[List[Ticket], int]:
        """List tickets with filters."""
        # Convert string enums
        severity_enum = None
        if severity:
            from app.models.entities import TicketSeverity
            try:
                severity_enum = TicketSeverity(severity)
            except ValueError:
                pass

        category_enum = None
        if category:
            from app.models.entities import TicketCategory
            try:
                category_enum = TicketCategory(category)
            except ValueError:
                pass

        return await self.ticket_repo.list_tickets(
            pagination=pagination,
            status=status,
            severity=severity_enum,
            category=category_enum,
            assignee_id=assignee_id,
            customer_id=customer_id,
        )

    async def update_ticket(self, ticket_id: str, data: TicketUpdate) -> Optional[Ticket]:
        """Update a ticket."""
        ticket = await self.ticket_repo.get_by_display_id(ticket_id)
        if not ticket:
            return None

        if data.status is not None:
            ticket.status = data.status
        if data.severity is not None:
            from app.models.entities import TicketSeverity
            ticket.severity = TicketSeverity(data.severity)
        if data.category is not None:
            from app.models.entities import TicketCategory
            ticket.category = TicketCategory(data.category)
        if data.assignee_id is not None:
            ticket.assignee_id = data.assignee_id

        return await self.ticket_repo.update(ticket)

    async def add_message(
        self,
        ticket_id: str,
        data: TicketMessageCreate,
        author: Optional[Profile] = None,
    ) -> Optional[TicketMessage]:
        """Add a message to a ticket."""
        ticket = await self.ticket_repo.get_by_display_id(ticket_id)
        if not ticket:
            return None

        message = TicketMessage(
            ticket_id=ticket.id,
            body=data.body,
            author_id=author.id if author else None,
            internal=data.internal,
        )

        return await self.ticket_repo.add_message(message)

    async def get_ticket_messages(self, ticket_id: str) -> List[TicketMessage]:
        """Get all messages for a ticket."""
        ticket = await self.ticket_repo.get_by_display_id(ticket_id)
        if not ticket:
            return []
        return await self.ticket_repo.get_messages(ticket.id)

    async def request_info(self, ticket_id: str, body: str, author: Optional[Profile] = None) -> Optional[Ticket]:
        """Request more information from customer."""
        ticket = await self.ticket_repo.get_by_display_id(ticket_id)
        if not ticket:
            return None

        # Add message
        message = TicketMessage(
            ticket_id=ticket.id,
            body=body,
            author_id=author.id if author else None,
            internal=False,
        )
        await self.ticket_repo.add_message(message)

        # Update status
        ticket.status = TicketStatus.WAITING_ON_CUSTOMER
        await self.ticket_repo.update(ticket)

        return ticket

    async def escalate_ticket(self, ticket_id: str, reason: str, team: str, author: Optional[Profile] = None) -> Optional[Ticket]:
        """Escalate a ticket."""
        ticket = await self.ticket_repo.get_by_display_id(ticket_id)
        if not ticket:
            return None

        # Add internal message
        message = TicketMessage(
            ticket_id=ticket.id,
            body=f"Escalated to {team}: {reason}",
            author_id=author.id if author else None,
            internal=True,
        )
        await self.ticket_repo.add_message(message)

        # Update status
        ticket.status = TicketStatus.ESCALATED
        await self.ticket_repo.update(ticket)

        return ticket