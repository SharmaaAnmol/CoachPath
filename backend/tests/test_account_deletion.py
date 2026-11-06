"""Account deletion: Google Play requires users to be able to erase their account and data."""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select

from app.models.auth import User
from app.models.onboarding import OnboardingSession
from tests.test_onboarding import mock_llm_fixture, register_and_login  # noqa: F401  (fixture reuse)

PW = "SecurePassword123!"


async def _delete(client: AsyncClient, token: str, password: str = PW, confirm: str = "DELETE"):
    return await client.request(
        "DELETE",
        "/api/v1/settings/account",
        json={"password": password, "confirm": confirm},
        headers={"Authorization": f"Bearer {token}"},
    )


@pytest.mark.asyncio
async def test_delete_account_removes_user_and_their_rows(client: AsyncClient, test_session):
    token = await register_and_login(client, "gone@test.com", "Gone User")
    other = await register_and_login(client, "stays@test.com", "Stays User")
    for t in (token, other):
        assert (await client.post("/api/v1/onboarding/start", headers={"Authorization": f"Bearer {t}"})).status_code == 200

    res = await _delete(client, token)
    assert res.status_code == 204

    emails = set((await test_session.execute(select(User.email))).scalars())
    assert emails == {"stays@test.com"}
    assert (await test_session.execute(select(func.count()).select_from(OnboardingSession))).scalar() == 1
    login = await client.post("/api/v1/auth/login", json={"email": "gone@test.com", "password": PW})
    assert login.status_code == 401


@pytest.mark.asyncio
async def test_delete_account_needs_password_and_typed_confirmation(client: AsyncClient, test_session):
    token = await register_and_login(client, "keep@test.com", "Keep User")

    assert (await _delete(client, token, password="wrong")).status_code == 400
    assert (await _delete(client, token, confirm="delete")).status_code == 400
    client.cookies.clear()  # the login cookie would otherwise authenticate this request
    assert (await client.request("DELETE", "/api/v1/settings/account", json={"password": PW, "confirm": "DELETE"})).status_code == 401
    assert (await test_session.execute(select(func.count()).select_from(User))).scalar() == 1
