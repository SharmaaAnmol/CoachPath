"""
Tests verifying all 14 structural domain routers are properly mounted under /api/v1.
"""

import pytest
from httpx import AsyncClient

DOMAIN_ROUTES = [
    ("/api/v1/auth", "auth"),
    ("/api/v1/profile", "profile"),
    ("/api/v1/onboarding", "onboarding"),
    ("/api/v1/resume", "resume"),
    ("/api/v1/assessments", "assessments"),
    ("/api/v1/skills", "skills"),
    ("/api/v1/roadmap", "roadmap"),
    ("/api/v1/jobs", "jobs"),
    ("/api/v1/applications", "applications"),
    ("/api/v1/recruiters", "recruiters"),
    ("/api/v1/interviews", "interviews"),
    ("/api/v1/career-readiness", "career-readiness"),
    ("/api/v1/dashboard", "dashboard"),
    ("/api/v1/settings", "settings"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("route_path, expected_module", DOMAIN_ROUTES)
async def test_domain_router_structural_placeholder(
    client: AsyncClient, route_path: str, expected_module: str
):
    """Verifies that each domain router is registered and responds under /api/v1."""
    response = await client.get(route_path)
    assert response.status_code == 200
    data = response.json()
    assert data["module"] == expected_module
    assert data["status"] == "placeholder"
    assert "phase" in data
