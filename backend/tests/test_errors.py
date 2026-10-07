"""
Tests for Centralized Error Handling and RFC 7807 Problem Details Payloads.
"""

import pytest
from httpx import AsyncClient
from app.core.exceptions import (
    ConflictException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)
from app.schemas.error import ErrorDetail


@pytest.mark.asyncio
async def test_not_found_endpoint_rfc7807(client: AsyncClient):
    """Verifies unmapped endpoints return 404 with structured error envelope."""
    response = await client.get("/api/v1/non-existent-endpoint")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["status"] == 404
    assert "request_id" in data["error"]
    assert "X-Request-ID" in response.headers


@pytest.mark.asyncio
async def test_correlation_id_preservation(client: AsyncClient):
    """Verifies custom X-Request-ID passed by client is preserved."""
    custom_id = "req_custom_trace_98765"
    response = await client.get("/api/v1/health", headers={"X-Request-ID": custom_id})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == custom_id
    assert "X-Process-Time-Ms" in response.headers


@pytest.mark.asyncio
async def test_custom_app_exceptions():
    """Unit tests verifying custom exception status codes and codes."""
    exc_nf = NotFoundException(resource="CareerProfile", identifier="123")
    assert exc_nf.status_code == 404
    assert exc_nf.code == "RESOURCE_NOT_FOUND"
    assert "CareerProfile" in exc_nf.message

    exc_conflict = ConflictException(message="Duplicate email")
    assert exc_conflict.status_code == 409
    assert exc_conflict.code == "STATE_CONFLICT"

    exc_auth = UnauthorizedException()
    assert exc_auth.status_code == 401
    assert exc_auth.code == "AUTHENTICATION_REQUIRED"

    exc_forbidden = ForbiddenException()
    assert exc_forbidden.status_code == 403
    assert exc_forbidden.code == "INSUFFICIENT_PERMISSIONS"

    exc_val = ValidationException(
        message="Invalid score",
        details=[ErrorDetail(field="score", issue="Must be <= 100")],
    )
    assert exc_val.status_code == 422
    assert exc_val.code == "VALIDATION_ERROR"
    assert len(exc_val.details) == 1
