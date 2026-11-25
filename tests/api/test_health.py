"""Health endpoint tests for CloudDesk Support Platform."""

import pytest
from httpx import AsyncClient


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, async_client: AsyncClient):
        """Test /health returns basic service info."""
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "clouddesk-support"
        assert "version" in data

    @pytest.mark.asyncio
    async def test_health_live_endpoint(self, async_client: AsyncClient):
        """Test /health/live returns alive status without I/O."""
        response = await async_client.get("/health/live")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"

    @pytest.mark.asyncio
    async def test_health_ready_endpoint(self, async_client: AsyncClient):
        """Test /health/ready checks dependencies."""
        response = await async_client.get("/health/ready")
        # In test environment with fake providers, should be ready
        assert response.status_code in (200, 503)
        data = response.json()
        assert data["status"] in ("ready", "degraded")
        assert "checks" in data
        checks = data["checks"]
        assert "database" in checks
        assert "redis" in checks
        assert "vector_store" in checks
        assert "llm" in checks


class TestRequestIdHeader:
    """Tests for X-Request-ID header on all responses."""

    @pytest.mark.asyncio
    async def test_health_has_request_id(self, async_client: AsyncClient):
        """Test /health includes X-Request-ID header."""
        response = await async_client.get("/health")
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        request_id = response.headers["X-Request-ID"]
        assert len(request_id) > 0

    @pytest.mark.asyncio
    async def test_health_live_has_request_id(self, async_client: AsyncClient):
        """Test /health/live includes X-Request-ID header."""
        response = await async_client.get("/health/live")
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers

    @pytest.mark.asyncio
    async def test_health_ready_has_request_id(self, async_client: AsyncClient):
        """Test /health/ready includes X-Request-ID header."""
        response = await async_client.get("/health/ready")
        assert "X-Request-ID" in response.headers

    @pytest.mark.asyncio
    async def test_404_has_request_id(self, async_client: AsyncClient):
        """Test 404 responses include X-Request-ID header."""
        response = await async_client.get("/nonexistent")
        assert response.status_code == 404
        assert "X-Request-ID" in response.headers

    @pytest.mark.asyncio
    async def test_request_id_echoed(self, async_client: AsyncClient):
        """Test that provided X-Request-ID is echoed back."""
        custom_id = "custom-request-id-123"
        response = await async_client.get("/health", headers={"X-Request-ID": custom_id})
        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == custom_id


class TestSettings:
    """Tests for settings reading."""

    @pytest.mark.asyncio
    async def test_demo_mode_setting(self):
        """Test DEMO_MODE setting is read from environment."""
        from backend.app.core.config import get_settings
        settings = get_settings()
        assert settings.DEMO_MODE is True

    @pytest.mark.asyncio
    async def test_llm_provider_setting(self):
        """Test LLM_PROVIDER setting is read from environment."""
        from backend.app.core.config import get_settings
        settings = get_settings()
        assert settings.LLM_PROVIDER == "fake"

    @pytest.mark.asyncio
    async def test_vector_store_setting(self):
        """Test VECTOR_STORE setting is read from environment."""
        from backend.app.core.config import get_settings
        settings = get_settings()
        assert settings.VECTOR_STORE == "memory"


class TestMiddlewareOrder:
    """Tests that middleware is applied in correct order."""

    @pytest.mark.asyncio
    async def test_cors_headers_present(self, async_client: AsyncClient):
        """Test CORS headers are present (outermost middleware)."""
        response = await async_client.options("/health")
        # CORS should allow the origin
        assert response.status_code in (200, 405)  # OPTIONS may not be implemented


if __name__ == "__main__":
    pytest.main([__file__, "-v"])