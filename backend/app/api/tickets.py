"""Tickets API routes for CloudDesk Support Platform."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.security import get_current_user, require_agent, require_viewer, User
from app.schemas.common import (
    PaginationParams,
    TicketCreate,
    TicketUpdate,
    TicketResponse,
    TicketSummary,
    TicketMessageCreate,
    TicketMessageResponse,
)
from app.services.ticket_service import TicketService
from app.core.database import get_session

router = APIRouter(prefix="/tickets", tags=["tickets"])


def get_ticket_service(session=Depends(get_session)) -> TicketService:
    return TicketService(session)


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    data: TicketCreate,
    current_user: User = Depends(require_agent),
    service: TicketService = Depends(get_ticket_service),
):
    """Create a new ticket."""
    ticket = await service.create_ticket(data, assignee=current_user)
    return TicketResponse(
        id=ticket.id,
        subject=ticket.subject,
        body=ticket.body,
        channel=ticket.channel.value,
        status=ticket.status.value,
        severity=ticket.severity.value if ticket.severity else None,
        category=ticket.category.value if ticket.category else None,
        customer_id=ticket.customer_id,
        assignee_id=ticket.assignee_id,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
    )


@router.get("", response_model=dict)
async def list_tickets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    severity: Optional[str] = None,
    category: Optional[str] = None,
    assignee_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    current_user: User = Depends(require_viewer),
    service: TicketService = Depends(get_ticket_service),
):
    """List tickets with filters."""
    pagination = PaginationParams(page=page, page_size=page_size)
    tickets, total = await service.list_tickets(
        pagination=pagination,
        status=status,
        severity=severity,
        category=category,
        assignee_id=assignee_id,
        customer_id=customer_id,
    )

    return {
        "items": [
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
        "page": page,
        "page_size": page_size,
        "total": total,
    }


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: str,
    current_user: User = Depends(require_viewer),
    service: TicketService = Depends(get_ticket_service),
):
    """Get ticket by ID or display ID."""
    ticket = await service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Load customer
    from app.repositories.customer_repository import CustomerRepository
    customer_repo = CustomerRepository(service.session)
    customer = await customer_repo.get_by_id(ticket.customer_id)

    return TicketResponse(
        id=ticket.id,
        subject=ticket.subject,
        body=ticket.body,
        channel=ticket.channel.value,
        status=ticket.status.value,
        severity=ticket.severity.value if ticket.severity else None,
        category=ticket.category.value if ticket.category else None,
        customer_id=ticket.customer_id,
        assignee_id=ticket.assignee_id,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        customer=customer,
    )


@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: str,
    data: TicketUpdate,
    current_user: User = Depends(require_agent),
    service: TicketService = Depends(get_ticket_service),
):
    """Update a ticket."""
    ticket = await service.update_ticket(ticket_id, data)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return TicketResponse(
        id=ticket.id,
        subject=ticket.subject,
        body=ticket.body,
        channel=ticket.channel.value,
        status=ticket.status.value,
        severity=ticket.severity.value if ticket.severity else None,
        category=ticket.category.value if ticket.category else None,
        customer_id=ticket.customer_id,
        assignee_id=ticket.assignee_id,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
    )


@router.get("/{ticket_id}/messages", response_model=List[TicketMessageResponse])
async def get_ticket_messages(
    ticket_id: str,
    current_user: User = Depends(require_viewer),
    service: TicketService = Depends(get_ticket_service),
):
    """Get all messages for a ticket."""
    ticket = await service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    messages = await service.get_ticket_messages(ticket.id)
    return [
        TicketMessageResponse(
            id=m.id,
            ticket_id=m.ticket_id,
            body=m.body,
            author_id=m.author_id,
            internal=m.internal,
            created_at=m.created_at,
        )
        for m in messages
    ]


@router.post("/{ticket_id}/reply", response_model=TicketMessageResponse, status_code=status.HTTP_201_CREATED)
async def reply_to_ticket(
    ticket_id: str,
    data: TicketMessageCreate,
    current_user: User = Depends(require_agent),
    service: TicketService = Depends(get_ticket_service),
):
    """Send a reply to the customer."""
    message = await service.add_message(ticket_id, data, author=current_user)
    if not message:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return TicketMessageResponse(
        id=message.id,
        ticket_id=message.ticket_id,
        body=message.body,
        author_id=message.author_id,
        internal=message.internal,
        created_at=message.created_at,
    )


@router.post("/{ticket_id}/request-info", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def request_info(
    ticket_id: str,
    data: TicketMessageCreate,
    current_user: User = Depends(require_agent),
    service: TicketService = Depends(get_ticket_service),
):
    """Request more information from the customer."""
    ticket = await service.request_info(ticket_id, data.body, author=current_user)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return TicketResponse(
        id=ticket.id,
        subject=ticket.subject,
        body=ticket.body,
        channel=ticket.channel.value,
        status=ticket.status.value,
        severity=ticket.severity.value if ticket.severity else None,
        category=ticket.category.value if ticket.category else None,
        customer_id=ticket.customer_id,
        assignee_id=ticket.assignee_id,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
    )


@router.post("/{ticket_id}/escalate", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def escalate_ticket(
    ticket_id: str,
    reason: str,
    team: str,
    current_user: User = Depends(require_agent),
    service: TicketService = Depends(get_ticket_service),
):
    """Escalate a ticket to a team."""
    ticket = await service.escalate_ticket(ticket_id, reason, team, author=current_user)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return TicketResponse(
        id=ticket.id,
        subject=ticket.subject,
        body=ticket.body,
        channel=ticket.channel.value,
        status=ticket.status.value,
        severity=ticket.severity.value if ticket.severity else None,
        category=ticket.category.value if ticket.category else None,
        customer_id=ticket.customer_id,
        assignee_id=ticket.assignee_id,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
    )