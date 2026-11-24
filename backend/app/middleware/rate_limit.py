"""Rate limiting middleware for CloudDesk Support Platform."""

import time
from typing import Callable, Optional

from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Fixed-window rate limiting middleware."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.settings = get_settings()
        self._cache: dict = {}  # In-memory fallback
        self._redis = None

    async def _get_redis(self):
        """Get Redis client (lazy initialization)."""
        if self._redis is None:
            if self.settings.USE_FAKE_REDIS or not self.settings.REDIS_URL:
                # Use fakeredis
                try:
                    import fakeredis.aioredis
                    self._redis = fakeredis.aioredis.FakeRedis()
                except ImportError:
                    self._redis = None
            else:
                try:
                    import redis.asyncio as redis
                    self._redis = redis.from_url(
                        self.settings.REDIS_URL,
                        encoding="utf-8",
                        decode_responses=True,
                    )
                except Exception:
                    self._redis = None
        return self._redis

    def _get_client_key(self, request: Request) -> str:
        """Extract client identifier from request."""
        # Try to get user ID from auth
        if hasattr(request.state, "user") and request.state.user:
            return f"user:{request.state.user.id}"

        # Fall back to IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        return f"ip:{ip}"

    async def _check_rate_limit(self, key: str) -> tuple[bool, dict]:
        """Check if request is within rate limit. Returns (allowed, headers)."""
        redis = await self._get_redis()
        now = int(time.time())
        window_start = now - (now % 60)  # Current minute window
        cache_key = f"ratelimit:{key}:{window_start}"

        limit = self.settings.RATE_LIMIT_PER_MINUTE

        if redis:
            try:
                pipe = redis.pipeline()
                pipe.incr(cache_key)
                pipe.expire(cache_key, 120)  # Keep for 2 minutes
                results = await pipe.execute()
                current = results[0]
            except Exception:
                # Fallback to in-memory
                current = self._cache.get(cache_key, 0) + 1
                self._cache[cache_key] = current
        else:
            current = self._cache.get(cache_key, 0) + 1
            self._cache[cache_key] = current

        remaining = max(0, limit - current)
        reset_time = window_start + 60

        headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_time),
        }

        allowed = current <= limit
        return allowed, headers

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health endpoints
        if request.url.path in ("/health", "/health/live", "/health/ready"):
            return await call_next(request)

        # Skip for OPTIONS (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        client_key = self._get_client_key(request)
        allowed, headers = await self._check_rate_limit(client_key)

        if not allowed:
            logger.warning(
                "Rate limit exceeded",
                extra={"client_key": client_key, "path": request.url.path},
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={
                    **headers,
                    "Retry-After": "60",
                },
            )

        response = await call_next(request)

        # Add rate limit headers to response
        for key, value in headers.items():
            response.headers[key] = value

        return response