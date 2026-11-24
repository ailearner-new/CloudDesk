"""Main application entry point for CloudDesk Support Platform."""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.database import close_engine, create_tables
from app.core.logging import setup_logging
from app.middleware.cors import add_cors_middleware
from app.middleware.request_id import RequestIdMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.audit import AuditMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    settings = get_settings()

    # Setup logging
    setup_logging("DEBUG" if settings.ENVIRONMENT == "development" else "INFO")

    # Create database tables
    await create_tables()

    # Bootstrap demo data if in demo mode
    if settings.DEMO_MODE:
        from app.services.seed_service import bootstrap_demo_data
        await bootstrap_demo_data()

    yield

    # Cleanup
    await close_engine()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="CloudDesk Support Platform",
        description="Autonomous Customer Support & Resolution Platform API",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    )

    # Add middleware (order matters: outermost last)
    # 1. CORS (outermost - handles preflight)
    add_cors_middleware(app)

    # 2. Request ID (binds request_id to logs and response headers)
    app.add_middleware(RequestIdMiddleware)

    # 3. Rate Limit
    app.add_middleware(RateLimitMiddleware)

    # 4. Audit (innermost - logs after request processing)
    app.add_middleware(AuditMiddleware)

    # Health endpoints (unprefixed)
    @app.get("/health")
    async def health():
        return {"status": "ok", "service": "clouddesk-support", "version": "0.1.0"}

    @app.get("/health/live")
    async def health_live():
        return {"status": "alive"}

    @app.get("/health/ready")
    async def health_ready():
        # Check dependencies
        checks = {
            "database": False,
            "redis": False,
            "vector_store": False,
            "llm": False,
        }

        # Database
        try:
            from app.core.database import get_engine
            engine = get_engine()
            async with engine.begin() as conn:
                await conn.execute("SELECT 1")
            checks["database"] = True
        except Exception:
            pass

        # Redis
        try:
            if settings.USE_FAKE_REDIS or not settings.REDIS_URL:
                import fakeredis.aioredis
                redis = fakeredis.aioredis.FakeRedis()
            else:
                import redis.asyncio as redis
                redis = redis.from_url(settings.REDIS_URL)
            await redis.ping()
            checks["redis"] = True
        except Exception:
            pass

        # Vector Store
        try:
            from rag.vector_store import get_vector_store
            vs = get_vector_store()
            await vs.health()
            checks["vector_store"] = True
        except Exception:
            pass

        # LLM
        try:
            from app.core.llm import get_llm
            llm = get_llm()
            # Just check it can be instantiated
            checks["llm"] = True
        except Exception:
            pass

        all_ready = all(checks.values())
        status_code = 200 if all_ready else 503

        return JSONResponse(
            status_code=status_code,
            content={"status": "ready" if all_ready else "degraded", "checks": checks},
        )

    # Mount API routers
    from app.api import auth, tickets, customers, knowledge, approvals, escalations, agents, audit, settings as settings_router, mcp

    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(tickets.router, prefix="/api/v1/tickets", tags=["tickets"])
    app.include_router(customers.router, prefix="/api/v1/customers", tags=["customers"])
    app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["knowledge"])
    app.include_router(approvals.router, prefix="/api/v1/approvals", tags=["approvals"])
    app.include_router(escalations.router, prefix="/api/v1/escalations", tags=["escalations"])
    app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
    app.include_router(audit.router, prefix="/api/v1/audit", tags=["audit"])
    app.include_router(settings_router.router, prefix="/api/v1/settings", tags=["settings"])
    app.include_router(mcp.router, prefix="/api/v1/mcp", tags=["mcp"])

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", None)
        from app.core.logging import get_logger
        logger = get_logger(__name__)
        logger.error(
            "Unhandled exception",
            extra={"request_id": request_id, "error": str(exc), "path": str(request.url)},
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
    )