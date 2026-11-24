"""Customer repository for CloudDesk Support Platform."""

from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.entities import Customer, Subscription, Workspace, CustomerMemory, Ticket, PlanTier
from app.schemas.common import PaginationParams


class CustomerRepository:
    """Repository for customer operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, customer_id: str) -> Optional[Customer]:
        """Get customer by ID."""
        result = await self.session.execute(
            select(Customer)
            .options(
                selectinload(Customer.profile),
                selectinload(Customer.subscription),
                selectinload(Customer.workspaces),
            )
            .where(Customer.id == customer_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[Customer]:
        """Get customer by email."""
        result = await self.session.execute(
            select(Customer)
            .options(selectinload(Customer.profile))
            .where(Customer.email == email)
        )
        return result.scalar_one_or_none()

    async def list_customers(
        self,
        pagination: PaginationParams,
        plan: Optional[PlanTier] = None,
    ) -> tuple[List[Customer], int]:
        """List customers with pagination."""
        query = select(Customer).options(
            selectinload(Customer.profile),
            selectinload(Customer.subscription),
        )

        if plan:
            query = query.where(Customer.plan == plan)

        query = query.order_by(Customer.created_at.desc())

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        # Apply pagination
        offset = (pagination.page - 1) * pagination.page_size
        query = query.offset(offset).limit(pagination.page_size)

        result = await self.session.execute(query)
        customers = result.scalars().all()

        return list(customers), total

    async def get_subscription(self, customer_id: str) -> Optional[Subscription]:
        """Get customer's subscription."""
        result = await self.session.execute(
            select(Subscription).where(Subscription.customer_id == customer_id)
        )
        return result.scalar_one_or_none()

    async def get_workspaces(self, customer_id: str) -> List[Workspace]:
        """Get customer's workspaces."""
        result = await self.session.execute(
            select(Workspace).where(Workspace.customer_id == customer_id)
        )
        return list(result.scalars().all())

    async def get_memory_notes(
        self,
        customer_id: str,
        limit: int = 10,
    ) -> List[CustomerMemory]:
        """Get customer's memory notes (most recent first)."""
        result = await self.session.execute(
            select(CustomerMemory)
            .where(CustomerMemory.customer_id == customer_id)
            .order_by(CustomerMemory.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_tickets(
        self,
        customer_id: str,
        limit: int = 20,
    ) -> List[Ticket]:
        """Get customer's recent tickets."""
        result = await self.session.execute(
            select(Ticket)
            .where(Ticket.customer_id == customer_id)
            .order_by(Ticket.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create_memory_note(self, note: CustomerMemory) -> CustomerMemory:
        """Create a memory note."""
        self.session.add(note)
        await self.session.flush()
        await self.session.refresh(note)
        return note

    async def check_duplicate_memory(
        self,
        customer_id: str,
        content: str,
        note_type: str,
    ) -> bool:
        """Check if an identical memory note already exists."""
        result = await self.session.execute(
            select(CustomerMemory).where(
                CustomerMemory.customer_id == customer_id,
                CustomerMemory.type == note_type,
                CustomerMemory.content == content,
            )
        )
        return result.scalar_one_or_none() is not None