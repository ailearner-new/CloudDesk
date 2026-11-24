"""LangGraph workflow for CloudDesk Support Platform."""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from agents.state import (
    SupportState,
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
    GRAPH_NODES,
)
from agents.nodes import (
    understand_ticket_node,
    classify_severity_node,
    customer_context_node,
    knowledge_retrieval_node,
    troubleshooting_node,
    resolution_planning_node,
    risk_check_node,
    human_approval_node,
    escalation_node,
    execute_resolution_node,
    ticket_summary_node,
    memory_update_node,
)
from agents.checkpointer import get_checkpointer


def create_workflow() -> StateGraph:
    """Create the LangGraph workflow."""
    workflow = StateGraph(SupportState)

    # Add nodes
    workflow.add_node(NODE_UNDERSTAND, understand_ticket_node)
    workflow.add_node(NODE_CLASSIFY, classify_severity_node)
    workflow.add_node(NODE_CUSTOMER, customer_context_node)
    workflow.add_node(NODE_KNOWLEDGE, knowledge_retrieval_node)
    workflow.add_node(NODE_TROUBLESHOOT, troubleshooting_node)
    workflow.add_node(NODE_RESOLUTION, resolution_planning_node)
    workflow.add_node(NODE_RISK, risk_check_node)
    workflow.add_node(NODE_APPROVAL, human_approval_node)
    workflow.add_node(NODE_ESCALATION, escalation_node)
    workflow.add_node(NODE_EXECUTE, execute_resolution_node)
    workflow.add_node(NODE_SUMMARY, ticket_summary_node)
    workflow.add_node(NODE_MEMORY, memory_update_node)

    # Add edges
    workflow.set_entry_point(NODE_UNDERSTAND)

    workflow.add_edge(NODE_UNDERSTAND, NODE_CLASSIFY)
    workflow.add_edge(NODE_CLASSIFY, NODE_CUSTOMER)
    workflow.add_edge(NODE_CUSTOMER, NODE_KNOWLEDGE)
    workflow.add_edge(NODE_KNOWLEDGE, NODE_TROUBLESHOOT)
    workflow.add_edge(NODE_TROUBLESHOOT, NODE_RESOLUTION)
    workflow.add_edge(NODE_RESOLUTION, NODE_RISK)

    # Conditional edges from risk_check
    workflow.add_conditional_edges(
        NODE_RISK,
        route_after_risk,
        {
            "approval": NODE_APPROVAL,
            "escalation": NODE_ESCALATION,
            "execute": NODE_EXECUTE,
        },
    )

    # Human approval edges
    workflow.add_conditional_edges(
        NODE_APPROVAL,
        route_after_approval,
        {
            "approved": NODE_EXECUTE,
            "rejected": NODE_ESCALATION,
        },
    )

    # Tail
    workflow.add_edge(NODE_ESCALATION, NODE_SUMMARY)
    workflow.add_edge(NODE_EXECUTE, NODE_SUMMARY)
    workflow.add_edge(NODE_SUMMARY, NODE_MEMORY)
    workflow.add_edge(NODE_MEMORY, END)

    return workflow


def route_after_risk(state: SupportState) -> str:
    """Route after risk check."""
    if state.risk_level == "high":
        if state.approval_request_id:
            return "approval"
        elif state.escalation and state.escalation.escalation_required:
            return "escalation"
    return "execute"


def route_after_approval(state: SupportState) -> str:
    """Route after human approval."""
    # The interrupt/resume mechanism handles this
    # This is a fallback - actual routing is via Command(resume=...)
    return "approved"


def compile_workflow(checkpointer=None):
    """Compile the workflow with checkpointer."""
    if checkpointer is None:
        checkpointer = get_checkpointer()

    workflow = create_workflow()
    return workflow.compile(checkpointer=checkpointer)


# For API exposure
def get_graph_nodes():
    """Get graph nodes for /api/v1/agents."""
    return [
        {"id": node, "label": node.replace("_", " ").title(), "description": f"{node} node"}
        for node in GRAPH_NODES
    ]


def get_graph_edges():
    """Get graph edges for /api/v1/agents."""
    edges = [
        {"from": NODE_UNDERSTAND, "to": NODE_CLASSIFY},
        {"from": NODE_CLASSIFY, "to": NODE_CUSTOMER},
        {"from": NODE_CUSTOMER, "to": NODE_KNOWLEDGE},
        {"from": NODE_KNOWLEDGE, "to": NODE_TROUBLESHOOT},
        {"from": NODE_TROUBLESHOOT, "to": NODE_RESOLUTION},
        {"from": NODE_RESOLUTION, "to": NODE_RISK},
        {"from": NODE_RISK, "to": NODE_APPROVAL, "condition": "approval_required"},
        {"from": NODE_RISK, "to": NODE_ESCALATION, "condition": "escalation_required"},
        {"from": NODE_RISK, "to": NODE_EXECUTE, "condition": "low_risk"},
        {"from": NODE_APPROVAL, "to": NODE_EXECUTE, "condition": "approved"},
        {"from": NODE_APPROVAL, "to": NODE_ESCALATION, "condition": "rejected"},
        {"from": NODE_ESCALATION, "to": NODE_SUMMARY},
        {"from": NODE_EXECUTE, "to": NODE_SUMMARY},
        {"from": NODE_SUMMARY, "to": NODE_MEMORY},
        {"from": NODE_MEMORY, "to": "END"},
    ]
    return edges