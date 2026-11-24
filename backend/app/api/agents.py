"""Agents API routes for CloudDesk Support Platform."""

from fastapi import APIRouter, Depends

from app.core.security import get_current_user, require_viewer, User
from app.schemas.common import AgentsResponse, AgentNode, AgentEdge

router = APIRouter(prefix="/agents", tags=["agents"])


# Graph definition (mirrors agents/graph.py)
GRAPH_NODES = [
    AgentNode(
        id="understand_ticket",
        label="Understand Ticket",
        description="Classify and summarize the ticket",
    ),
    AgentNode(
        id="classify_severity",
        label="Classify Severity",
        description="Assign severity with reason",
    ),
    AgentNode(
        id="customer_context",
        label="Customer Context",
        description="Load customer, subscription, history, memory",
    ),
    AgentNode(
        id="knowledge_retrieval",
        label="Knowledge Retrieval",
        description="Find cited evidence and similar cases",
    ),
    AgentNode(
        id="troubleshooting",
        label="Troubleshooting",
        description="Probable causes and numbered steps",
    ),
    AgentNode(
        id="resolution_planning",
        label="Resolution Planning",
        description="Summary, reply, notes, and actions",
    ),
    AgentNode(
        id="risk_check",
        label="Risk Check",
        description="Assess if approval or escalation needed",
    ),
    AgentNode(
        id="human_approval",
        label="Human Approval",
        description="Pause for approval on consequential actions",
    ),
    AgentNode(
        id="escalation",
        label="Escalation",
        description="File escalation to named team",
    ),
    AgentNode(
        id="execute_resolution",
        label="Execute Resolution",
        description="Run approved actions",
    ),
    AgentNode(
        id="ticket_summary",
        label="Ticket Summary",
        description="Write final summary",
    ),
    AgentNode(
        id="memory_update",
        label="Memory Update",
        description="Record resolution in customer memory",
    ),
]

GRAPH_EDGES = [
    AgentEdge(from_="understand_ticket", to="classify_severity"),
    AgentEdge(from_="classify_severity", to="customer_context"),
    AgentEdge(from_="customer_context", to="knowledge_retrieval"),
    AgentEdge(from_="knowledge_retrieval", to="troubleshooting"),
    AgentEdge(from_="troubleshooting", to="resolution_planning"),
    AgentEdge(from_="resolution_planning", to="risk_check"),
    AgentEdge(from_="risk_check", to="human_approval", condition="approval_required"),
    AgentEdge(from_="risk_check", to="escalation", condition="escalation_required"),
    AgentEdge(from_="risk_check", to="execute_resolution", condition="low_risk"),
    AgentEdge(from_="human_approval", to="execute_resolution", condition="approved"),
    AgentEdge(from_="human_approval", to="escalation", condition="rejected"),
    AgentEdge(from_="escalation", to="ticket_summary"),
    AgentEdge(from_="execute_resolution", to="ticket_summary"),
    AgentEdge(from_="ticket_summary", to="memory_update"),
    AgentEdge(from_="memory_update", to="END"),
]


@router.get("", response_model=AgentsResponse)
async def get_agents(
    current_user: User = Depends(require_viewer),
):
    """Get workflow graph metadata."""
    return AgentsResponse(nodes=GRAPH_NODES, edges=GRAPH_EDGES)