"""MCP API routes for CloudDesk Support Platform."""

from fastapi import APIRouter, Depends

from app.core.security import get_current_user, require_viewer, User
from app.schemas.common import MCPToolsResponse, MCPTool, MCPToolParameter

router = APIRouter(prefix="/mcp", tags=["mcp"])


# Read-only tools exposed via MCP
MCP_TOOLS = [
    MCPTool(
        name="get_customer",
        description="Get customer by ID",
        parameters=MCPToolParameter(
            type="object",
            properties={
                "customer_id": {"type": "string", "description": "Customer UUID"}
            },
            required=["customer_id"],
        ),
    ),
    MCPTool(
        name="get_subscription",
        description="Get subscription by customer ID",
        parameters=MCPToolParameter(
            type="object",
            properties={
                "customer_id": {"type": "string", "description": "Customer UUID"}
            },
            required=["customer_id"],
        ),
    ),
    MCPTool(
        name="get_ticket_history",
        description="Get previous tickets for a customer",
        parameters=MCPToolParameter(
            type="object",
            properties={
                "customer_id": {"type": "string", "description": "Customer UUID"},
                "limit": {"type": "integer", "description": "Max tickets to return", "default": 10}
            },
            required=["customer_id"],
        ),
    ),
    MCPTool(
        name="search_docs",
        description="Search knowledge base",
        parameters=MCPToolParameter(
            type="object",
            properties={
                "query": {"type": "string", "description": "Search query"},
                "category": {"type": "string", "description": "Category filter"},
                "mode": {"type": "string", "description": "Search mode: hybrid, semantic, keyword", "default": "hybrid"},
                "top_k": {"type": "integer", "description": "Max results", "default": 5}
            },
            required=["query"],
        ),
    ),
    MCPTool(
        name="check_service_status",
        description="Check service status for components",
        parameters=MCPToolParameter(
            type="object",
            properties={
                "components": {"type": "array", "items": {"type": "string"}, "description": "Components to check"}
            },
            required=["components"],
        ),
    ),
]


@router.get("/tools", response_model=MCPToolsResponse)
async def list_mcp_tools(
    current_user: User = Depends(require_viewer),
):
    """List available MCP tools."""
    return MCPToolsResponse(tools=MCP_TOOLS)