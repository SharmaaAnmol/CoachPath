"""
Tests for Application Root, Health, and Readiness Endpoints.
"""

from unittest.mock import patch
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Verifies GET / returns service metadata and operational status."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "CoachPath API"
    assert data["status"] == "operational"
    assert data["docs_url"] == "/api/v1/docs"
    assert "X-Request-ID" in response.headers


@pytest.mark.asyncio
async def test_health_liveness(client: AsyncClient):
    """Verifies GET /api/v1/health returns 200 healthy status."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "CoachPath API"
    assert "version" in data
    assert "environment" in data


@pytest.mark.asyncio
async def test_ready_endpoint_healthy(client: AsyncClient):
    """Verifies GET /api/v1/ready returns 200 when database connectivity succeeds."""
    with patch("app.api.routes.health.check_db_connectivity", return_value=True):
        response = await client.get("/api/v1/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["database"] == "connected"


@pytest.mark.asyncio
async def test_ready_endpoint_unhealthy(client: AsyncClient):
    """Verifies GET /api/v1/ready returns 503 when database connectivity fails."""
    with patch("app.api.routes.health.check_db_connectivity", return_value=False):
        response = await client.get("/api/v1/ready")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["database"] == "disconnected"


@pytest.mark.asyncio
async def test_production_environment_security():
    """Verifies that production environment forces DEBUG=False and disallows default secret key."""
    from app.core.config import Settings

    # Default insecure key in production must raise ValueError
    with pytest.raises(ValueError, match="Insecure default SECRET_KEY"):
        Settings(ENVIRONMENT="production")

    # Valid production settings forces DEBUG=False
    prod_settings = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="super-secret-secure-production-key-32-chars-long",
    )
    assert prod_settings.DEBUG is False
