"""
Health and Readiness Probes for CoachPath API.
Used by container orchestrators, monitoring agents, and integration smoke tests.
"""

from typing import Any, Dict
from fastapi import APIRouter, Response, status
from app.core.config import settings
from app.db.session import check_db_connectivity

router = APIRouter(tags=["System Health & Diagnostics"])


@router.get(
    "/health",
    summary="Liveness Probe",
    description="Confirms that the FastAPI service runtime is running and responsive.",
    status_code=status.HTTP_200_OK,
)
async def health_check() -> Dict[str, Any]:
    """Basic service liveness probe."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@router.get(
    "/ready",
    summary="Readiness Probe",
    description="Validates that required infrastructure components (e.g. PostgreSQL database) are reachable.",
)
async def readiness_check(response: Response) -> Dict[str, Any]:
    """Service readiness probe checking database connectivity."""
    db_connected = await check_db_connectivity()

    if db_connected:
        return {
            "status": "ready",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "database": "connected",
        }

    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {
        "status": "unhealthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "disconnected",
        "detail": "Database connectivity check failed.",
    }
