"""Workflow state for CloudDesk Support Platform."""

from typing import Any, Dict, List, Optional
from langgraph.graph import StateGraph, add_messages
from pydantic import BaseModel, Field

from app.schemas.workflow import (
    WorkflowState as WorkflowStateSchema,
    Classification,
    SeverityAssessment,
    CustomerContext,
    Evidence,
    PreviousCase,
    Diagnosis,
    ResolutionPlan,
    EscalationDecision,
    merge_usage,
    append_nodes,
    append_errors,
)


# LangGraph state (uses reducers)
class SupportState(BaseModel):
    """LangGraph state with reducers for accumulation."""
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
    risk_level: str = "low"
    escalation: Optional[EscalationDecision] = None
    approval_request_id: Optional[str] = None

    # Output
    summary: Optional[str] = None
    memory_updated: bool = False

    # Execution tracking
    completed_nodes: List[str] = Field(default_factory=list)
    current_node: Optional[str] = None
    errors: List[str] = Field(default_factory=list)

    # Token usage (accumulated via reducer)
    token_usage: Dict[str, int] = Field(default_factory=lambda: {"input": 0, "output": 0, "total": 0})

    # Metadata
    workflow_id: Optional[str] = None
    thread_id: Optional[str] = None


# Graph node names
NODE_UNDERSTAND = "understand_ticket"
NODE_CLASSIFY = "classify_severity"
NODE_CUSTOMER = "customer_context"
NODE_KNOWLEDGE = "knowledge_retrieval"
NODE_TROUBLESHOOT = "troubleshooting"
NODE_RESOLUTION = "resolution_planning"
NODE_RISK = "risk_check"
NODE_APPROVAL = "human_approval"
NODE_ESCALATION = "escalation"
NODE_EXECUTE = "execute_resolution"
NODE_SUMMARY = "ticket_summary"
NODE_MEMORY = "memory_update"

GRAPH_NODES = [
    NODE_UNDERSTAND,
    NODE_CLASSIFY,
    NODE_CUSTOMER,
    NODE_KNOWLEDGE,
    NODE_TROUBLESHOOT,
    NODE_RESOLUTION,
    NODE_RISK,
    NODE_APPROVAL,
    NODE_ESCALATION,
    NODE_EXECUTE,
    NODE_SUMMARY,
    NODE_MEMORY,
]


def create_initial_state(
    ticket_id: str,
    ticket_subject: str,
    ticket_body: str,
    ticket_channel: str,
    customer_id: str,
    workflow_id: str,
    thread_id: str,
) -> SupportState:
    """Create initial workflow state."""
    return SupportState(
        ticket_id=ticket_id,
        ticket_subject=ticket_subject,
        ticket_body=ticket_body,
        ticket_channel=ticket_channel,
        customer_id=customer_id,
        workflow_id=workflow_id,
        thread_id=thread_id,
    )