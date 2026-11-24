"""Common schemas for CloudDesk Support Platform."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict


# Enums (mirroring database enums)

class UserRole(str):
    VIEWER = "viewer"
    AGENT = "agent"
    ADMIN = "admin"


class TicketStatus(str):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    WAITING_ON_CUSTOMER = "waiting_on_customer"
    WAITING_ON_APPROVAL = "waiting_on_approval"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketSeverity(str):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketChannel(str):
    EMAIL = "email"
    CHAT = "chat"
    WEB = "web"
    API = "api"


class TicketCategory(str):
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


# All valid categories (exactly 10)
VALID_CATEGORIES = [
    TicketCategory.LOGIN_ISSUE,
    TicketCategory.BILLING,
    TicketCategory.API_FAILURE,
    TicketCategory.WORKSPACE_PERMISSIONS,
    TicketCategory.STORAGE_QUOTA,
    TicketCategory.INTEGRATION,
    TicketCategory.FEATURE_REQUEST,
    TicketCategory.ACCOUNT,
    TicketCategory.SECURITY,
    TicketCategory.OTHER,
]


class PlanTier(str):
    FREE = "free"
    PRO = "pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    TRIALING = "trialing"


class IncidentStatus(str):
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MONITORING = "monitoring"
    RESOLVED = "resolved"


class IncidentSeverity(str):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WorkflowStatus(str):
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowEventType(str):
    NODE_STARTED = "node_started"
    NODE_COMPLETED = "node_completed"
    TOOL_CALLED = "tool_called"
    LLM_CALLED = "llm_called"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_RESOLVED = "approval_resolved"
    ERROR = "error"
    WORKFLOW_COMPLETED = "workflow_completed"


class ApprovalStatus(str):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class EscalationStatus(str):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class MemoryType(str):
    PREFERENCE = "preference"
    PAST_ISSUE = "past_issue"
    TROUBLESHOOTING = "troubleshooting"
    NOTE = "note"


class RiskLevel(str):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# Base schemas

class BaseSchema(BaseModel):
    """Base schema with common config."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# Pagination

class PaginationParams(BaseModel):
    """Pagination query parameters."""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    items: List[Any]
    page: int
    page_size: int
    total: int


# Health

class HealthCheck(BaseModel):
    """Health check response."""
    status: str
    service: str = "clouddesk-support"
    version: str = "0.1.0"


class ReadinessCheck(BaseModel):
    """Readiness check response."""
    status: str
    checks: Dict[str, bool]


# Error

class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str


# Auth

class LoginRequest(BaseModel):
    """Login request."""
    email: str
    password: str


class LoginResponse(BaseModel):
    """Login response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserResponse"


class RefreshResponse(BaseModel):
    """Token refresh response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User profile response."""
    id: str
    email: str
    role: str
    full_name: Optional[str] = None


# Customer

class CustomerBase(BaseSchema):
    """Base customer schema."""
    name: str
    email: str
    plan: PlanTier


class CustomerCreate(CustomerBase):
    """Create customer request."""
    pass


class CustomerUpdate(BaseModel):
    """Update customer request."""
    name: Optional[str] = None
    plan: Optional[PlanTier] = None


class CustomerResponse(CustomerBase):
    """Customer response."""
    id: str
    created_at: datetime
    updated_at: datetime


class CustomerDetail(CustomerResponse):
    """Customer detail with related data."""
    subscription: Optional["SubscriptionResponse"] = None
    workspaces: List["WorkspaceResponse"] = []
    memory_notes: List["CustomerMemoryResponse"] = []
    tickets: List["TicketSummary"] = []


# Subscription

class SubscriptionBase(BaseSchema):
    """Base subscription schema."""
    plan: PlanTier
    seats: int
    status: SubscriptionStatus
    renewal_at: Optional[datetime] = None


class SubscriptionResponse(SubscriptionBase):
    """Subscription response."""
    id: str
    customer_id: str
    created_at: datetime
    updated_at: datetime


# Workspace

class WorkspaceBase(BaseSchema):
    """Base workspace schema."""
    name: str
    storage_gb_used: float = 0.0
    storage_gb_limit: float = 10.0


class WorkspaceCreate(WorkspaceBase):
    """Create workspace request."""
    customer_id: str


class WorkspaceResponse(WorkspaceBase):
    """Workspace response."""
    id: str
    customer_id: str
    created_at: datetime
    updated_at: datetime


# Product

class ProductResponse(BaseSchema):
    """Product response."""
    id: str
    name: str
    description: str
    category: str
    created_at: datetime
    updated_at: datetime


# Ticket

class TicketBase(BaseSchema):
    """Base ticket schema."""
    subject: str = Field(..., min_length=1, max_length=500)
    body: str = Field(..., min_length=1)
    channel: TicketChannel


class TicketCreate(TicketBase):
    """Create ticket request."""
    customer_email: str


class TicketUpdate(BaseModel):
    """Update ticket request."""
    status: Optional[TicketStatus] = None
    severity: Optional[TicketSeverity] = None
    category: Optional[TicketCategory] = None
    assignee_id: Optional[str] = None


class TicketSummary(BaseSchema):
    """Ticket summary for lists."""
    id: str
    subject: str
    status: TicketStatus
    severity: Optional[TicketSeverity] = None
    category: Optional[TicketCategory] = None
    customer_id: str
    created_at: datetime
    updated_at: datetime


class TicketResponse(TicketSummary):
    """Full ticket response."""
    body: str
    channel: TicketChannel
    assignee_id: Optional[str] = None
    customer: Optional[CustomerResponse] = None


# Ticket Message

class TicketMessageCreate(BaseModel):
    """Create ticket message request."""
    body: str = Field(..., min_length=1)
    internal: bool = False


class TicketMessageResponse(BaseSchema):
    """Ticket message response."""
    id: str
    ticket_id: str
    body: str
    author_id: Optional[str] = None
    internal: bool
    created_at: datetime


# Support Article

class SupportArticleBase(BaseSchema):
    """Base support article schema."""
    title: str
    category: TicketCategory
    tags: List[str] = []
    summary: str = ""
    content: str


class SupportArticleCreate(SupportArticleBase):
    """Create article request."""
    pass


class SupportArticleResponse(SupportArticleBase):
    """Support article response."""
    id: str
    created_at: datetime
    updated_at: datetime


class KnowledgeSearchRequest(BaseModel):
    """Knowledge search request."""
    q: str = Field(..., min_length=1)
    category: Optional[TicketCategory] = None
    mode: str = "hybrid"  # hybrid, semantic, keyword
    top_k: int = Field(default=5, ge=1, le=20)


class KnowledgeSearchResult(BaseModel):
    """Knowledge search result."""
    id: str
    title: str
    source: str
    snippet: str
    score: float
    url: str
    article_id: str


class KnowledgeSearchResponse(BaseModel):
    """Knowledge search response."""
    query: str
    mode: str
    results: List[KnowledgeSearchResult]


class ReindexResponse(BaseModel):
    """Reindex response."""
    indexed: Dict[str, int]


# Incident

class IncidentResponse(BaseSchema):
    """Incident response."""
    id: str
    title: str
    status: IncidentStatus
    severity: IncidentSeverity
    affected_components: List[str]
    started_at: datetime
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# Approval

class ApprovalRequestResponse(BaseSchema):
    """Approval request response."""
    id: str
    workflow_id: str
    ticket_id: str
    tool_name: str
    tool_args: Dict[str, Any]
    status: ApprovalStatus
    requested_at: datetime
    decided_at: Optional[datetime] = None
    decided_by: Optional[str] = None
    reason: Optional[str] = None


class ApprovalDecision(BaseModel):
    """Approval decision request."""
    reason: Optional[str] = None


class ApprovalActionResponse(BaseModel):
    """Approval action response."""
    id: str
    status: ApprovalStatus
    decided_at: datetime
    decided_by: str
    reason: Optional[str] = None


# Escalation

class EscalationCreate(BaseModel):
    """Create escalation request."""
    reason: str = Field(..., min_length=1)
    team: str = Field(..., min_length=1)


class EscalationUpdate(BaseModel):
    """Update escalation request."""
    status: Optional[EscalationStatus] = None
    resolution: Optional[str] = None


class EscalationResponse(BaseSchema):
    """Escalation response."""
    id: str
    ticket_id: str
    reason: str
    team: str
    status: EscalationStatus
    created_by: Optional[str] = None
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None


# Workflow

class WorkflowRunResponse(BaseSchema):
    """Workflow run response."""
    id: str
    ticket_id: str
    status: WorkflowStatus
    current_node: Optional[str] = None
    completed_nodes: List[str] = []
    error: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


class WorkflowEventResponse(BaseSchema):
    """Workflow event response."""
    id: str
    workflow_id: str
    event_type: WorkflowEventType
    node: Optional[str] = None
    timestamp: datetime
    duration_ms: Optional[int] = None
    data: Dict[str, Any] = {}


# Agent Graph

class AgentNode(BaseModel):
    """Agent graph node."""
    id: str
    label: str
    description: str


class AgentEdge(BaseModel):
    """Agent graph edge."""
    from_: str = Field(..., alias="from")
    to: str
    condition: Optional[str] = None


class AgentsResponse(BaseModel):
    """Agents graph response."""
    nodes: List[AgentNode]
    edges: List[AgentEdge]


# Audit

class AuditLogResponse(BaseSchema):
    """Audit log response."""
    id: str
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    request_id: Optional[str] = None
    method: str
    path: str
    status_code: int
    duration_ms: int
    ip: str
    user_agent: str
    details: Dict[str, Any]
    created_at: datetime


# Settings

class SettingsResponse(BaseModel):
    """Settings response."""
    approval_required_for_refunds: bool
    max_refund_without_approval: int
    rate_limit_per_minute: int
    tool_timeout_seconds: int
    vector_store: str
    embedding_provider: str
    llm_provider: str


class SettingsUpdate(BaseModel):
    """Settings update request."""
    approval_required_for_refunds: Optional[bool] = None
    max_refund_without_approval: Optional[int] = None
    rate_limit_per_minute: Optional[int] = None
    tool_timeout_seconds: Optional[int] = None


# Customer Memory

class CustomerMemoryResponse(BaseSchema):
    """Customer memory response."""
    id: str
    customer_id: str
    type: MemoryType
    content: str
    source_ticket_id: Optional[str] = None
    workflow_id: Optional[str] = None
    created_at: datetime


# MCP

class MCPToolParameter(BaseModel):
    """MCP tool parameter schema."""
    type: str
    properties: Dict[str, Any]
    required: List[str]


class MCPTool(BaseModel):
    """MCP tool definition."""
    name: str
    description: str
    parameters: MCPToolParameter


class MCPToolsResponse(BaseModel):
    """MCP tools list response."""
    tools: List[MCPTool]


# Forward references resolution
UserResponse.model_rebuild()
CustomerDetail.model_rebuild()
SubscriptionResponse.model_rebuild()
WorkspaceResponse.model_rebuild()
TicketSummary.model_rebuild()
TicketResponse.model_rebuild()
CustomerMemoryResponse.model_rebuild()