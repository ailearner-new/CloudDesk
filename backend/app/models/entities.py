"""SQLAlchemy models for CloudDesk Support Platform.

Portable models: JSON columns, String(36) UUIDs for compatibility
with both SQLite (demo) and PostgreSQL (production).
"""

import enum
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


def gen_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())


def now_utc() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


# Enums

class UserRole(str, enum.Enum):
    """User roles."""
    VIEWER = "viewer"
    AGENT = "agent"
    ADMIN = "admin"


class TicketStatus(str, enum.Enum):
    """Ticket statuses."""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    WAITING_ON_CUSTOMER = "waiting_on_customer"
    WAITING_ON_APPROVAL = "waiting_on_approval"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketSeverity(str, enum.Enum):
    """Ticket severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketChannel(str, enum.Enum):
    """Ticket channels."""
    EMAIL = "email"
    CHAT = "chat"
    WEB = "web"
    API = "api"


class TicketCategory(str, enum.Enum):
    """Ticket categories (exactly 10)."""
    LOGIN_ISSUE = "login_issue"
    BILLING = "billing"
    API_FAILURE = "api_failure"
    WORKSPACE_PERMISSIONS = "workspace_permissions"
    STORAGE_QUOTA = "storage_quota"
    INTEGRATION = "integration"
    FEATURE_REQUEST = "feature_request"
    ACCOUNT = "account"
    SECURITY = "security"
    OTHER = "other"


class PlanTier(str, enum.Enum):
    """Subscription plan tiers."""
    FREE = "free"
    PRO = "pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, enum.Enum):
    """Subscription status."""
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    TRIALING = "trialing"


class IncidentStatus(str, enum.Enum):
    """Incident status."""
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MONITORING = "monitoring"
    RESOLVED = "resolved"


class IncidentSeverity(str, enum.Enum):
    """Incident severity."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WorkflowStatus(str, enum.Enum):
    """Workflow run status."""
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowEventType(str, enum.Enum):
    """Workflow event types."""
    NODE_STARTED = "node_started"
    NODE_COMPLETED = "node_completed"
    TOOL_CALLED = "tool_called"
    LLM_CALLED = "llm_called"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_RESOLVED = "approval_resolved"
    ERROR = "error"
    WORKFLOW_COMPLETED = "workflow_completed"


class ApprovalStatus(str, enum.Enum):
    """Approval request status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class EscalationStatus(str, enum.Enum):
    """Escalation status."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class MemoryType(str, enum.Enum):
    """Customer memory note types."""
    PREFERENCE = "preference"
    PAST_ISSUE = "past_issue"
    TROUBLESHOOTING = "troubleshooting"
    NOTE = "note"


class RiskLevel(str, enum.Enum):
    """Risk assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# Models

class Profile(Base):
    """User profile (extends Supabase auth.users)."""
    __tablename__ = "profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), default="")
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False),
        default=UserRole.VIEWER,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False
    )

    # Relationships
    customer: Mapped[Optional["Customer"]] = relationship(
        "Customer", back_populates="profile", uselist=False
    )
    tickets: Mapped[List["Ticket"]] = relationship("Ticket", back_populates="assignee")
    ticket_messages: Mapped[List["TicketMessage"]] = relationship("TicketMessage", back_populates="author")


class Customer(Base):
    """Customer account."""
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    plan: Mapped[PlanTier] = mapped_column(
        Enum(PlanTier, native_enum=False),
        default=PlanTier.FREE,
        nullable=False,
    )
    profile_id: Mapped[str] = mapped_column(String(36), ForeignKey("profiles.id"), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False
    )

    # Relationships
    profile: Mapped[Profile] = relationship("Profile", back_populates="customer")
    subscription: Mapped[Optional["Subscription"]] = relationship(
        "Subscription", back_populates="customer", uselist=False
    )
    workspaces: Mapped[List["Workspace"]] = relationship("Workspace", back_populates="customer")
    tickets: Mapped[List["Ticket"]] = relationship("Ticket", back_populates="customer")
    memory_notes: Mapped[List["CustomerMemory"]] = relationship("CustomerMemory", back_populates="customer")


class Subscription(Base):
    """Customer subscription."""
    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id"), nullable=False, index=True)
    plan: Mapped[PlanTier] = mapped_column(
        Enum(PlanTier, native_enum=False),
        nullable=False,
    )
    seats: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus, native_enum=False),
        default=SubscriptionStatus.ACTIVE,
        nullable=False,
    )
    renewal_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False
    )

    # Relationships
    customer: Mapped[Customer] = relationship("Customer", back_populates="subscription")


class Workspace(Base):
    """Customer workspace."""
    __tablename__ = "workspaces"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_gb_used: Mapped[float] = mapped_column(default=0.0, nullable=False)
    storage_gb_limit: Mapped[float] = mapped_column(default=10.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False
    )

    # Relationships
    customer: Mapped[Customer] = relationship("Customer", back_populates="workspaces")


class Product(Base):
    """Product catalog."""
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(100), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False
    )


class Ticket(Base):
    """Support ticket."""
    __tablename__ = "tickets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[TicketChannel] = mapped_column(
        Enum(TicketChannel, native_enum=False),
        nullable=False,
    )
    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus, native_enum=False),
        default=TicketStatus.NEW,
        nullable=False,
    )
    severity: Mapped[Optional[TicketSeverity]] = mapped_column(
        Enum(TicketSeverity, native_enum=False),
        nullable=True,
    )
    category: Mapped[Optional[TicketCategory]] = mapped_column(
        Enum(TicketCategory, native_enum=False),
        nullable=True,
    )
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id"), nullable=False, index=True)
    assignee_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("profiles.id"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False
    )

    # Relationships
    customer: Mapped[Customer] = relationship("Customer", back_populates="tickets")
    assignee: Mapped[Optional[Profile]] = relationship("Profile", back_populates="tickets")
    messages: Mapped[List["TicketMessage"]] = relationship("TicketMessage", back_populates="ticket")
    workflow_runs: Mapped[List["WorkflowRun"]] = relationship("WorkflowRun", back_populates="ticket")
    escalations: Mapped[List["Escalation"]] = relationship("Escalation", back_populates="ticket")


class TicketMessage(Base):
    """Ticket message/reply."""
    __tablename__ = "ticket_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    ticket_id: Mapped[str] = mapped_column(String(36), ForeignKey("tickets.id"), nullable=False, index=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("profiles.id"), nullable=True
    )
    internal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)

    # Relationships
    ticket: Mapped[Ticket] = relationship("Ticket", back_populates="messages")
    author: Mapped[Optional[Profile]] = relationship("Profile", back_populates="ticket_messages")


class SupportArticle(Base):
    """Knowledge base article."""
    __tablename__ = "support_articles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    category: Mapped[TicketCategory] = mapped_column(
        Enum(TicketCategory, native_enum=False),
        nullable=False,
    )
    tags: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    summary: Mapped[str] = mapped_column(Text, default="")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False
    )


class Incident(Base):
    """Service incident."""
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[IncidentStatus] = mapped_column(
        Enum(IncidentStatus, native_enum=False),
        default=IncidentStatus.INVESTIGATING,
        nullable=False,
    )
    severity: Mapped[IncidentSeverity] = mapped_column(
        Enum(IncidentSeverity, native_enum=False),
        default=IncidentSeverity.MEDIUM,
        nullable=False,
    )
    affected_components: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False
    )


class WorkflowRun(Base):
    """Workflow execution run."""
    __tablename__ = "workflow_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    ticket_id: Mapped[str] = mapped_column(String(36), ForeignKey("tickets.id"), nullable=False, index=True)
    status: Mapped[WorkflowStatus] = mapped_column(
        Enum(WorkflowStatus, native_enum=False),
        default=WorkflowStatus.RUNNING,
        nullable=False,
    )
    state: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    thread_id: Mapped[str] = mapped_column(String(36), default=gen_uuid, nullable=False)
    current_node: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    completed_nodes: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False
    )

    # Relationships
    ticket: Mapped[Ticket] = relationship("Ticket", back_populates="workflow_runs")
    events: Mapped[List["WorkflowEvent"]] = relationship("WorkflowEvent", back_populates="workflow_run")


class WorkflowEvent(Base):
    """Workflow event for observability."""
    __tablename__ = "workflow_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    workflow_id: Mapped[str] = mapped_column(String(36), ForeignKey("workflow_runs.id"), nullable=False, index=True)
    event_type: Mapped[WorkflowEventType] = mapped_column(
        Enum(WorkflowEventType, native_enum=False),
        nullable=False,
    )
    node: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    data: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # Relationships
    workflow_run: Mapped[WorkflowRun] = relationship("WorkflowRun", back_populates="events")


class ResolutionAction(Base):
    """Planned or executed resolution action."""
    __tablename__ = "resolution_actions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    workflow_id: Mapped[str] = mapped_column(String(36), ForeignKey("workflow_runs.id"), nullable=False, index=True)
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False)
    tool_args: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    approval_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("approval_requests.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)


class ApprovalRequest(Base):
    """Human approval request for consequential actions."""
    __tablename__ = "approval_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    workflow_id: Mapped[str] = mapped_column(String(36), ForeignKey("workflow_runs.id"), nullable=False, index=True)
    ticket_id: Mapped[str] = mapped_column(String(36), ForeignKey("tickets.id"), nullable=False, index=True)
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False)
    tool_args: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[ApprovalStatus] = mapped_column(
        Enum(ApprovalStatus, native_enum=False),
        default=ApprovalStatus.PENDING,
        nullable=False,
    )
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    decided_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    decided_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("profiles.id"), nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Escalation(Base):
    """Ticket escalation to a team."""
    __tablename__ = "escalations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    ticket_id: Mapped[str] = mapped_column(String(36), ForeignKey("tickets.id"), nullable=False, index=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    team: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[EscalationStatus] = mapped_column(
        Enum(EscalationStatus, native_enum=False),
        default=EscalationStatus.OPEN,
        nullable=False,
    )
    created_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("profiles.id"), nullable=True)
    assigned_to: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("profiles.id"), nullable=True)
    resolution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    ticket: Mapped[Ticket] = relationship("Ticket", back_populates="escalations")


class CustomerMemory(Base):
    """Long-term customer memory notes."""
    __tablename__ = "customer_memory"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id"), nullable=False, index=True)
    type: Mapped[MemoryType] = mapped_column(
        Enum(MemoryType, native_enum=False),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source_ticket_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("tickets.id"), nullable=True)
    workflow_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("workflow_runs.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)

    # Relationships
    customer: Mapped[Customer] = relationship("Customer", back_populates="memory_notes")


class AuditLog(Base):
    """Audit log for all state-changing requests."""
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("profiles.id"), nullable=True, index=True)
    user_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    request_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    ip: Mapped[str] = mapped_column(String(45), nullable=False)
    user_agent: Mapped[str] = mapped_column(Text, default="")
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False, index=True)


# Table-level indexes
Index("ix_tickets_customer_status", Ticket.customer_id, Ticket.status)
Index("ix_tickets_assignee_status", Ticket.assignee_id, Ticket.status)
Index("ix_workflow_runs_ticket_status", WorkflowRun.ticket_id, WorkflowRun.status)
Index("ix_workflow_events_workflow_type", WorkflowEvent.workflow_id, WorkflowEvent.event_type)
Index("ix_audit_logs_created", AuditLog.created_at)
Index("ix_audit_logs_user_action", AuditLog.user_id, AuditLog.action)