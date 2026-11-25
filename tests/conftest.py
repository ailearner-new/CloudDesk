"""Pytest configuration for CloudDesk Support Platform.

Sets up offline test environment before importing the app.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set offline environment variables BEFORE importing the app
os.environ.setdefault("DEMO_MODE", "true")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("SUPABASE_JWT_SECRET", "")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("CHECKPOINT_DB_PATH", ":memory:")
os.environ.setdefault("REDIS_URL", "")
os.environ.setdefault("USE_FAKE_REDIS", "true")
os.environ.setdefault("LLM_PROVIDER", "fake")
os.environ.setdefault("LLM_API_KEY", "")
os.environ.setdefault("LLM_MODEL", "gpt-4o-mini")
os.environ.setdefault("EMBEDDING_PROVIDER", "fake")
os.environ.setdefault("EMBEDDING_MODEL", "text-embedding-3-small")
os.environ.setdefault("EMBEDDING_DIMENSIONS", "384")
os.environ.setdefault("VECTOR_STORE", "memory")
os.environ.setdefault("QDRANT_URL", "")
os.environ.setdefault("QDRANT_API_KEY", "")
os.environ.setdefault("QDRANT_COLLECTION", "clouddesk_knowledge")
os.environ.setdefault("APPROVAL_REQUIRED_FOR_REFUNDS", "true")
os.environ.setdefault("MAX_REFUND_WITHOUT_APPROVAL", "0")
os.environ.setdefault("TOOL_TIMEOUT_SECONDS", "30")
os.environ.setdefault("RATE_LIMIT_PER_MINUTE", "120")
os.environ.setdefault("SAMPLE_DATA_DIR", "sample_data")
os.environ.setdefault("LANGCHAIN_TRACING_V2", "false")
os.environ.setdefault("LANGCHAIN_API_KEY", "")
os.environ.setdefault("LANGCHAIN_PROJECT", "clouddesk-support-test")

# Now import after env vars are set
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from backend.app.main import create_app
from backend.app.core.database import Base, get_session_factory, close_engine
from backend.app.core.config import get_settings
from backend.app.core.security import create_demo_token, User


@pytest.fixture(scope="session")
def app():
    """Create FastAPI app for testing."""
    return create_app()


@pytest.fixture(scope="session")
async def async_client(app):
    """Create async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    settings = get_settings()
    engine = create_async_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=None,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_session(test_engine):
    """Create a test database session with transaction rollback."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def admin_headers():
    """Headers for admin user."""
    token = create_demo_token("admin@clouddesk.demo", "admin")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def agent_headers():
    """Headers for agent user."""
    token = create_demo_token("sam.agent@clouddesk.demo", "agent")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def viewer_headers():
    """Headers for viewer user."""
    token = create_demo_token("vic.viewer@clouddesk.demo", "viewer")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_user():
    """Admin user object."""
    return User(
        id="demo-admin-admin",
        email="admin@clouddesk.demo",
        role="admin",
        full_name="Demo Admin",
    )


@pytest.fixture
def agent_user():
    """Agent user object."""
    return User(
        id="demo-agent-sam.agent",
        email="sam.agent@clouddesk.demo",
        role="agent",
        full_name="Demo Agent",
    )


@pytest.fixture
def viewer_user():
    """Viewer user object."""
    return User(
        id="demo-viewer-vic.viewer",
        email="vic.viewer@clouddesk.demo",
        role="viewer",
        full_name="Demo Viewer",
    )


# Pytest configuration
def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: mark test as async")


# Ensure asyncio mode
pytest_asyncio_mode = "auto"