"""Request ID middleware for CloudDesk Support Platform."""

import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.logging import log_context, request_id_var


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Middleware to ensure every request has a unique X-Request-ID."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get or generate request ID
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())

        # Bind to log context
        with log_context(request_id=request_id):
            # Add to request state for access in handlers
            request.state.request_id = request_id

            # Process request
            response = await call_next(request)

            # Add to response headers
            response.headers["X-Request-ID"] = request_id

            return response