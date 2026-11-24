"""Customers API routes for CloudDesk Support Platform."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.security import get_current_user, require_viewer, User
from app.schemas.common import (
    PaginationParams,
    CustomerResponse,
    CustomerDetail,
    CustomerMemoryResponse,
    SubscriptionResponse,
    WorkspaceResponse,
    TicketSummary,
)
from app.services.customer_service import CustomerService
from app.core.database import get_session

router = APIRouter(prefix="/customers", tags=["customers"])


def get_customer_service(session=Depends(get_session)) -> CustomerService:
    return CustomerService(session)


@router.get("", response_model=dict)
async def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    plan: Optional[str] = None,
    current_user: User = Depends(require_viewer),
    service: CustomerService = Depends(get_customer_service),
):
    """List customers with pagination."""
    pagination = PaginationParams(page=page, page_size=page_size)
    customers, total = await service.list_customers(pagination, plan)

    return {
        "items": [
            CustomerResponse(
                id=c.id,
                name=c.name,
                email=c.email,
                plan=c.plan.value,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in customers
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
    }


@router.get("/{customer_id}", response_model=CustomerDetail)
async def get_customer(
    customer_id: str,
    current_user: User = Depends(require_viewer),
    service: CustomerService = Depends(get_customer_service),
):
    """Get customer with all related data."""
    customer = await service.get_customer_detail(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Get subscription
    from app.repositories.customer_repository import CustomerRepository
    customer_repo = CustomerRepository(service.session)
    subscription = await customer_repo.get_subscription(customer_id)
    workspaces = await customer_repo.get_workspaces(customer_id)
    memory_notes = await customer_repo.get_memory_notes(customer_id)
    tickets = await customer_repo.get_tickets(customer_id)

    return CustomerDetail(
        id=customer.id,
        name=customer.name,
        email=customer.email,
        plan=customer.plan.value,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
        subscription=SubscriptionResponse(
            id=subscription.id,
            customer_id=subscription.customer_id,
            plan=subscription.plan.value,
            seats=subscription.seats,
            status=subscription.status.value,
            renewal_at=subscription.renewal_at,
            created_at=subscription.created_at,
            updated_at=subscription.updated_at,
        ) if subscription else None,
        workspaces=[
            WorkspaceResponse(
                id=w.id,
                customer_id=w.customer_id,
                name=w.name,
                storage_gb_used=w.storage_gb_used,
                storage_gb_limit=w.storage_gb_limit,
                created_at=w.created_at,
                updated_at=w.updated_at,
            )
            for w in workspaces
        ],
        memory_notes=[
            CustomerMemoryResponse(
                id=m.id,
                customer_id=m.customer_id,
                type=m.type.value,
                content=m.content,
                source_ticket_id=m.source_ticket_id,
                workflow_id=m.workflow_id,
                created_at=m.created_at,
            )
            for m in memory_notes
        ],
        tickets=[
            TicketSummary(
                id=t.id,
                subject=t.subject,
                status=t.status.value,
                severity=t.severity.value if t.severity else None,
                category=t.category.value if t.category else None,
                customer_id=t.customer_id,
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
            for t in tickets
        ],
    )


@router.get("/{customer_id}/memory", response_model=List[CustomerMemoryResponse])
async def get_customer_memory(
    customer_id: str,
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(require_viewer),
    service: CustomerService = Depends(get_customer_service),
):
    """Get customer memory notes."""
    customer = await service.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    notes = await service.get_memory_notes(customer_id, limit)
    return [
        CustomerMemoryResponse(
            id=n.id,
            customer_id=n.customer_id,
            type=n.type.value,
            content=n.content,
            source_ticket_id=n.source_ticket_id,
            workflow_id=n.workflow_id,
            created_at=n.created_at,
        )
        for n in notes
    ]