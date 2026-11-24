"""Workflow state schemas for CloudDesk Support Platform."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, ConfigDict


# Specialist Agent Output Schemas

class Classification(BaseModel):
    """Ticket classification output."""
    category: str  # One of the 10 valid categories
    summary: str  # One-line summary
    confidence: float = Field(ge=0.0, le=1.0)


class SeverityAssessment(BaseModel):
    """Severity assessment output."""
    level: str  # low, medium, high, critical
    reason: str


class CustomerContext(BaseModel):
    """Customer context output."""
    customer: Dict[str, Any]
    subscription: Optional[Dict[str, Any]] = None
    workspace: Optional[Dict[str, Any]] = None
    previous_tickets: List[Dict[str, Any]] = []
    memory_notes: List[Dict[str, Any]] = []


class Evidence(BaseModel):
    """Evidence from knowledge retrieval."""
    id: str
    title: str
    source: str  # kb://slug#section
    snippet: str
    score: float
    url: str
    article_id: str


class PreviousCase(BaseModel):
    """Similar previous case."""
    ticket_id: str
    title: str
    resolution_summary: str
    similarity: float


class KnowledgeOutput(BaseModel):
    """Knowledge agent output."""
    evidence: List[Evidence] = []
    similar_cases: List[PreviousCase] = []


class Diagnosis(BaseModel):
    """Troubleshooting diagnosis output."""
    probable_causes: List[str] = []
    steps: List[str] = []


class PlannedAction(BaseModel):
    """Planned action in resolution plan."""
    tool: str
    args: Dict[str, Any]


class ResolutionPlan(BaseModel):
    """Resolution plan output."""
    summary: str
    customer_reply: str
    internal_notes: str
    actions: List[PlannedAction] = []
    grounding_score: float = Field(ge=0.0, le=1.0, default=0.0)


class EscalationDecision(BaseModel):
    """Escalation decision output."""
    escalation_required: bool
    team: Optional[str] = None
    reason: str
    confidence: float = Field(ge=0.0, le=1.0)


# Workflow State (LangGraph state)

class WorkflowState(BaseModel):
    """Complete workflow state for LangGraph."""
    # Input
    ticket_id: str
    ticket_subject: str
    ticket_body: str
    ticket_channel: str
    customer_id: str

    # Classification
    classification: Optional[Classification] = None
    severity: Optional[SeverityAssessment] = None

    # Customer context
    customer_context: Optional[CustomerContext] = None

    # Knowledge
    evidence: List[Evidence] = []
    similar_cases: List[PreviousCase] = []

    # Troubleshooting
    diagnosis: Optional[Diagnosis] = None

    # Resolution
    resolution_plan: Optional[ResolutionPlan] = None

    # Risk & Escalation
    risk_level: str = "low"  # low, medium, high
    escalation: Optional[EscalationDecision] = None
    approval_request_id: Optional[str] = None

    # Output
    summary: Optional[str] = None
    memory_updated: bool = False

    # Execution tracking
    completed_nodes: List[str] = []
    current_node: Optional[str] = None
    errors: List[str] = []

    # Token usage (accumulated)
    token_usage: Dict[str, int] = Field(default_factory=lambda: {"input": 0, "output": 0, "total": 0})

    # Metadata
    workflow_id: Optional[str] = None
    thread_id: Optional[str] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


# Reducers for LangGraph state

def merge_usage(existing: Dict[str, int], new: Dict[str, int]) -> Dict[str, int]:
    """Merge token usage by summing."""
    return {
        "input": existing.get("input", 0) + new.get("input", 0),
        "output": existing.get("output", 0) + new.get("output", 0),
        "total": existing.get("total", 0) + new.get("total", 0),
    }


def append_nodes(existing: List[str], new: List[str]) -> List[str]:
    """Append completed nodes."""
    return existing + new


def append_errors(existing: List[str], new: List[str]) -> List[str]:
    """Append errors."""
    return existing + new


# Node output types (partial state updates)

class UnderstandTicketOutput(BaseModel):
    """Output from understand_ticket node."""
    classification: Classification
    token_usage: Dict[str, int]


class ClassifySeverityOutput(BaseModel):
    """Output from classify_severity node."""
    severity: SeverityAssessment
    token_usage: Dict[str, int]


class CustomerContextOutput(BaseModel):
    """Output from customer_context node."""
    customer_context: CustomerContext


class KnowledgeRetrievalOutput(BaseModel):
    """Output from knowledge_retrieval node."""
    evidence: List[Evidence]
    similar_cases: List[PreviousCase]


class TroubleshootingOutput(BaseModel):
    """Output from troubleshooting node."""
    diagnosis: Diagnosis
    token_usage: Dict[str, int]


class ResolutionPlanningOutput(BaseModel):
    """Output from resolution_planning node."""
    resolution_plan: ResolutionPlan
    token_usage: Dict[str, int]


class RiskCheckOutput(BaseModel):
    """Output from risk_check node."""
    risk_level: str
    escalation: Optional[EscalationDecision] = None
    approval_request_id: Optional[str] = None


class EscalationOutput(BaseModel):
    """Output from escalation node."""
    escalation: EscalationDecision


class ExecuteResolutionOutput(BaseModel):
    """Output from execute_resolution node."""
    # Actions are executed, results stored in resolution_actions table


class TicketSummaryOutput(BaseModel):
    """Output from ticket_summary node."""
    summary: str


class MemoryUpdateOutput(BaseModel):
    """Output from memory_update node."""
    memory_updated: bool