"""Audit logging middleware for CloudDesk Support Platform."""

import json
import time
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import get_settings
from app.core.database import get_session_factory
from app.core.logging import get_logger
from app.models.entities import AuditLog

logger = get_logger(__name__)

# Actions that should be audited (non-GET requests)
AUDIT_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

# Paths to skip auditing
SKIP_PATHS = {
    "/health", "/health/live", "/health/ready",
    "/api/v1/auth/login", "/api/v1/auth/refresh",
    "/docs", "/redoc", "/openapi.json",
}


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware to audit all state-changing requests."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    def _should_audit(self, request: Request) -> bool:
        """Determine if request should be audited."""
        if request.method not in AUDIT_METHODS:
            return False
        if request.url.path in SKIP_PATHS:
            return False
        if request.url.path.startswith("/docs") or request.url.path.startswith("/redoc"):
            return False
        return True

    def _get_user_info(self, request: Request) -> tuple[Optional[str], Optional[str]]:
        """Extract user ID and email from request."""
        user_id = None
        user_email = None

        if hasattr(request.state, "user") and request.state.user:
            user_id = request.state.user.id
            user_email = request.state.user.email

        return user_id, user_email

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _get_action_name(self, request: Request) -> str:
        """Generate a human-readable action name from the request."""
        path = request.url.path

        # Map common patterns
        if "/tickets/" in path and "/run" in path:
            return "ticket.run"
        elif "/tickets/" in path and "/reply" in path:
            return "ticket.reply"
        elif "/tickets/" in path and "/request-info" in path:
            return "ticket.request_info"
        elif "/tickets/" in path and "/escalate" in path:
            return "ticket.escalate"
        elif "/approvals/" in path and "/approve" in path:
            return "approval.approve"
        elif "/approvals/" in path and "/reject" in path:
            return "approval.reject"
        elif "/knowledge/reindex" in path:
            return "knowledge.reindex"

        # Generic: method + resource
        parts = path.strip("/").split("/")
        if len(parts) >= 3 and parts[0] == "api" and parts[1] == "v1":
            resource = parts[2]
            return f"{resource}.{request.method.lower()}"

        return f"{request.method.lower()}.{path}"

    def _get_resource_info(self, request: Request) -> tuple[Optional[str], Optional[str]]:
        """Extract resource type and ID from request path."""
        path = request.url.path

        # Common patterns
        if "/tickets/" in path:
            parts = path.split("/tickets/")
            if len(parts) > 1:
                ticket_id = parts[1].split("/")[0]
                return "ticket", ticket_id

        if "/customers/" in path:
            parts = path.split("/customers/")
            if len(parts) > 1:
                customer_id = parts[1].split("/")[0]
                return "customer", customer_id

        if "/approvals/" in path:
            parts = path.split("/approvals/")
            if len(parts) > 1:
                approval_id = parts[1].split("/")[0]
                return "approval", approval_id

        if "/escalations/" in path:
            parts = path.split("/escalations/")
            if len(parts) > 1:
                esc_id = parts[1].split("/")[0]
                return "escalation", esc_id

        if "/workspaces/" in path:
            parts = path.split("/workspaces/")
            if len(parts) > 1:
                ws_id = parts[1].split("/")[0]
                return "workspace", ws_id

        return None, None

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip if not auditable
        if not self._should_audit(request):
            return await call_next(request)

        start_time = time.time()
        request_id = getattr(request.state, "request_id", None)

        # Get user info before processing (may be set by auth middleware)
        user_id, user_email = self._get_user_info(request)
        client_ip = self._get_client_ip(request)
        action = self._get_action_name(request)
        resource_type, resource_id = self._get_resource_info(request)

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)

        # Create audit log entry (fire and forget - don't block response)
        try:
            session_factory = get_session_factory()
            async with session_factory() as session:
                audit_log = AuditLog(
                    user_id=user_id,
                    user_email=user_email,
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    request_id=request_id,
                    method=request.method,
                    path=str(request.url.path),
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                    ip=client_ip,
                    user_agent=request.headers.get("User-Agent", ""),
                    details={
                        "query_params": dict(request.query_params),
                    },
                )
                session.add(audit_log)
                await session.commit()
        except Exception as e:
            # Log but don't fail the request
            logger.error(
                "Failed to write audit log",
                extra={"error": str(e), "action": action},
            )

        return response