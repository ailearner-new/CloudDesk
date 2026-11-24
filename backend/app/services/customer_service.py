"""Customer service for CloudDesk Support Platform."""

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Customer, CustomerMemory, MemoryType
from app.repositories.customer_repository import CustomerRepository
from app.schemas.common import PaginationParams


class CustomerService:
    """Service for customer operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.customer_repo = CustomerRepository(session)

    async def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Get customer by ID."""
        return await self.customer_repo.get_by_id(customer_id)

    async def list_customers(
        self,
        pagination: PaginationParams,
        plan: Optional[str] = None,
    ) -> tuple[List[Customer], int]:
        """List customers with pagination."""
        plan_enum = None
        if plan:
            from app.models.entities import PlanTier
            try:
                plan_enum = PlanTier(plan)
            except ValueError:
                pass

        return await self.customer_repo.list_customers(pagination, plan_enum)

    async def get_customer_detail(self, customer_id: str) -> Optional[Customer]:
        """Get customer with all related data."""
        return await self.customer_repo.get_by_id(customer_id)

    async def get_memory_notes(self, customer_id: str, limit: int = 10) -> List[CustomerMemory]:
        """Get customer memory notes."""
        return await self.customer_repo.get_memory_notes(customer_id, limit)

    async def add_memory_note(
        self,
        customer_id: str,
        note_type: MemoryType,
        content: str,
        source_ticket_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
    ) -> Optional[CustomerMemory]:
        """Add a memory note (with deduplication)."""
        # Check for duplicate
        is_duplicate = await self.customer_repo.check_duplicate_memory(
            customer_id, content, note_type.value
        )
        if is_duplicate:
            return None

        note = CustomerMemory(
            customer_id=customer_id,
            type=note_type,
            content=content,
            source_ticket_id=source_ticket_id,
            workflow_id=workflow_id,
        )
        return await self.customer_repo.create_memory_note(note)