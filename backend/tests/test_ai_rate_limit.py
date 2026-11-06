"""Per-user caps on AI-backed endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.core.rate_limit import ai_rate_limiters
from tests.test_onboarding import mock_llm_fixture, register_and_login  # noqa: F401  (fixture reuse)


@pytest.mark.asyncio
async def test_ai_endpoint_returns_429_after_minute_cap(client: AsyncClient, monkeypatch):
    monkeypatch.setattr(ai_rate_limiters[0], "max_attempts", 2)
    token = await register_and_login(client, "ai.limit@test.com", "Rate Tester")
    headers = {"Authorization": f"Bearer {token}"}

    for _ in range(2):
        assert (await client.post("/api/v1/onboarding/start", headers=headers)).status_code == 200

    res = await client.post("/api/v1/onboarding/start", headers=headers)
    assert res.status_code == 429
    assert "too quickly" in res.text


@pytest.mark.asyncio
async def test_ai_cap_is_per_user(client: AsyncClient, monkeypatch):
    monkeypatch.setattr(ai_rate_limiters[0], "max_attempts", 1)
    a = await register_and_login(client, "ai.a@test.com", "User A")
    b = await register_and_login(client, "ai.b@test.com", "User B")

    assert (await client.post("/api/v1/onboarding/start", headers={"Authorization": f"Bearer {a}"})).status_code == 200
    assert (await client.post("/api/v1/onboarding/start", headers={"Authorization": f"Bearer {a}"})).status_code == 429
    assert (await client.post("/api/v1/onboarding/start", headers={"Authorization": f"Bearer {b}"})).status_code == 200


@pytest.mark.asyncio
async def test_unauthenticated_ai_call_is_401_not_counted(client: AsyncClient):
    res = await client.post("/api/v1/onboarding/start")
    assert res.status_code == 401
