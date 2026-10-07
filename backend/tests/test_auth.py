"""
Comprehensive Integration Tests for Phase 3A: Authentication Backend.
Tests registration, credential verification, JWT access tokens, refresh token rotation,
replay attack detection, session revocation, rate limiting, and RBAC / ownership dependencies.
"""

from __future__ import annotations

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import ensure_resource_ownership, require_active_user, require_role
from app.core.exceptions import ForbiddenException
from app.core.rate_limit import auth_rate_limiter
from app.core.security import hash_token
from app.models.audit import ActivityLog
from app.models.auth import User, UserProfile, UserSession


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Ensures a clean rate limiter state between test runs."""
    auth_rate_limiter.reset_all()
    yield
    auth_rate_limiter.reset_all()


@pytest.mark.asyncio
async def test_register_candidate_success(client: AsyncClient, test_session: AsyncSession):
    """Verifies successful registration creates User, UserProfile, and ActivityLog."""
    payload = {
        "email": "aarav.sharma@example.com",
        "password": "SecurePassword123!",
        "full_name": "Aarav Sharma",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["email"] == "aarav.sharma@example.com"
    assert data["status"] == "pending_verification"
    assert "user_id" in data

    # Verify database persistence
    user_id = uuid.UUID(data["user_id"])
    user = await test_session.scalar(select(User).where(User.id == user_id))
    assert user is not None
    assert user.email == "aarav.sharma@example.com"
    assert user.role == "candidate"
    assert user.password_hash.startswith("$argon2id$")

    profile = await test_session.scalar(select(UserProfile).where(UserProfile.user_id == user_id))
    assert profile is not None
    assert profile.full_name == "Aarav Sharma"

    activity = await test_session.scalar(
        select(ActivityLog).where(
            ActivityLog.user_id == user_id,
            ActivityLog.activity_type == "ACCOUNT_REGISTERED",
        )
    )
    assert activity is not None


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Verifies registering with an existing email returns 409 Conflict."""
    payload = {
        "email": "duplicate@example.com",
        "password": "ValidPassword99#",
        "full_name": "Original User",
    }
    res1 = await client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    # Attempt registration with duplicate email in uppercase
    dup_payload = {
        "email": "DUPLICATE@example.com",
        "password": "AnotherPassword99#",
        "full_name": "Duplicate User",
    }
    res2 = await client.post("/api/v1/auth/register", json=dup_payload)
    assert res2.status_code == 409
    data = res2.json()
    assert data["error"]["code"] == "STATE_CONFLICT"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "weak_password, reason",
    [
        ("short1!", "Password must be at least 8 characters long."),
        ("alllowercase123!", "Password must contain at least one uppercase letter."),
        ("ALLUPPERCASE123!", "Password must contain at least one lowercase letter."),
        ("NoSpecialChar123", "Password must contain at least one special character"),
        ("NoNumbersHere!@", "Password must contain at least one digit."),
    ],
)
async def test_register_weak_password_rejected(
    client: AsyncClient, weak_password: str, reason: str
):
    """Verifies that password complexity rules are strictly enforced (422)."""
    payload = {
        "email": f"weak_{hash(weak_password)}@example.com",
        "password": weak_password,
        "full_name": "Weak Password Test",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_register_invalid_email_format(client: AsyncClient):
    """Verifies RFC 5322 email validation rejects invalid formats."""
    payload = {
        "email": "invalid-email-format",
        "password": "ValidPassword99#",
        "full_name": "Invalid Email",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_session: AsyncSession):
    """Verifies valid credentials authenticate, return tokens, and set secure cookies."""
    # Register candidate
    email = "login.test@example.com"
    password = "CorrectPassword123!"
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Login Tester"},
    )

    # Login
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 3600
    assert "refresh_token" in data
    assert data["user"]["email"] == email
    assert data["user"]["role"] == "candidate"
    assert data["user"]["full_name"] == "Login Tester"

    # Verify cookies
    cookies = response.cookies
    assert "access_token" in cookies
    assert "refresh_token" in cookies

    # Verify session persisted in DB
    user_id = uuid.UUID(data["user"]["id"])
    refresh_hash = hash_token(data["refresh_token"])
    session = await test_session.scalar(
        select(UserSession).where(
            UserSession.user_id == user_id,
            UserSession.refresh_token_hash == refresh_hash,
        )
    )
    assert session is not None
    assert session.is_revoked is False

    # Verify ActivityLog
    activity = await test_session.scalar(
        select(ActivityLog).where(
            ActivityLog.user_id == user_id,
            ActivityLog.activity_type == "USER_LOGIN",
        )
    )
    assert activity is not None


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Verifies login failure for wrong password and unknown email."""
    # Unknown email
    res1 = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "Password123!"},
    )
    assert res1.status_code == 401
    assert res1.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"

    # Existing user, incorrect password
    await client.post(
        "/api/v1/auth/register",
        json={"email": "wrongpw@example.com", "password": "CorrectPassword123!", "full_name": "Tester"},
    )
    res2 = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpw@example.com", "password": "WrongPassword99!"},
    )
    assert res2.status_code == 401


@pytest.mark.asyncio
async def test_login_rate_limiting(client: AsyncClient):
    """Verifies brute-force protection locks out after 5 consecutive failures."""
    email = "bruteforce@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "LegitPassword123!", "full_name": "Target User"},
    )

    # Trigger 5 failed attempts
    for _ in range(5):
        res = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "BadPassword123!"},
        )
        assert res.status_code == 401

    # 6th attempt must be rejected with 429 Too Many Requests
    res6 = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "LegitPassword123!"},
    )
    assert res6.status_code == 429
    assert res6.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"


@pytest.mark.asyncio
async def test_get_me_authenticated_via_bearer(client: AsyncClient):
    """Verifies /auth/me returns current user identity when authenticated with Bearer token."""
    email = "me.bearer@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!", "full_name": "Bearer User"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    access_token = login_res.json()["access_token"]

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert data["full_name"] == "Bearer User"
    assert data["role"] == "candidate"


@pytest.mark.asyncio
async def test_get_me_authenticated_via_cookie(client: AsyncClient):
    """Verifies /auth/me works seamlessly with HttpOnly cookie credentials."""
    email = "me.cookie@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!", "full_name": "Cookie User"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    access_cookie = login_res.cookies.get("access_token")

    # Request without Authorization header, only cookie
    response = await client.get(
        "/api/v1/auth/me",
        cookies={"access_token": access_cookie},
    )
    assert response.status_code == 200
    assert response.json()["email"] == email
    assert response.json()["full_name"] == "Cookie User"


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client: AsyncClient):
    """Verifies /auth/me rejects unauthenticated requests with 401."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"


@pytest.mark.asyncio
async def test_refresh_token_rotation(client: AsyncClient, test_session: AsyncSession):
    """Verifies refresh token rotation invalidates old token and issues fresh pair."""
    email = "refresh.rotation@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!", "full_name": "Rotation User"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    old_refresh_token = login_res.json()["refresh_token"]

    # Exchange refresh token
    refresh_res = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": old_refresh_token},
    )
    assert refresh_res.status_code == 200
    refresh_data = refresh_res.json()
    assert "access_token" in refresh_data
    new_refresh_token = refresh_data["refresh_token"]
    assert new_refresh_token != old_refresh_token

    # Verify old session revoked in DB
    old_hash = hash_token(old_refresh_token)
    old_session = await test_session.scalar(
        select(UserSession).where(UserSession.refresh_token_hash == old_hash)
    )
    assert old_session is not None
    assert old_session.is_revoked is True

    # Verify new session active in DB
    new_hash = hash_token(new_refresh_token)
    new_session = await test_session.scalar(
        select(UserSession).where(UserSession.refresh_token_hash == new_hash)
    )
    assert new_session is not None
    assert new_session.is_revoked is False


@pytest.mark.asyncio
async def test_refresh_token_replay_attack_detection(
    client: AsyncClient, test_session: AsyncSession
):
    """Verifies that reusing an already-rotated refresh token revokes all user sessions."""
    email = "replay.attack@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!", "full_name": "Replay User"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    first_refresh_token = login_res.json()["refresh_token"]
    user_id = uuid.UUID(login_res.json()["user"]["id"])

    # First valid rotation
    rotate_res = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": first_refresh_token},
    )
    assert rotate_res.status_code == 200

    # Attacker attempts to reuse first_refresh_token (REPLAY ATTACK)
    replay_res = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": first_refresh_token},
    )
    assert replay_res.status_code == 401

    # Verify ALL sessions for this user have been revoked
    sessions = (
        await test_session.scalars(select(UserSession).where(UserSession.user_id == user_id))
    ).all()
    assert len(sessions) > 0
    assert all(s.is_revoked is True for s in sessions)


@pytest.mark.asyncio
async def test_logout_session_invalidation(client: AsyncClient, test_session: AsyncSession):
    """Verifies logout revokes user session and clears authentication cookies."""
    email = "logout.test@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!", "full_name": "Logout Tester"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    access_token = login_res.json()["access_token"]
    refresh_token = login_res.json()["refresh_token"]
    user_id = uuid.UUID(login_res.json()["user"]["id"])

    # Execute logout
    logout_res = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"refresh_token": refresh_token},
    )
    assert logout_res.status_code == 200
    assert logout_res.json()["message"] == "Logged out successfully"

    # Verify session is revoked
    refresh_hash = hash_token(refresh_token)
    session = await test_session.scalar(
        select(UserSession).where(UserSession.refresh_token_hash == refresh_hash)
    )
    assert session is not None
    assert session.is_revoked is True

    # Verify activity log
    activity = await test_session.scalar(
        select(ActivityLog).where(
            ActivityLog.user_id == user_id,
            ActivityLog.activity_type == "USER_LOGOUT",
        )
    )
    assert activity is not None


@pytest.mark.asyncio
async def test_resource_ownership_and_role_helpers():
    """Unit tests the ensure_resource_ownership helper and require_active_user."""
    user_id = uuid.uuid4()
    other_id = uuid.uuid4()

    candidate = User(id=user_id, email="candidate@example.com", role="candidate", status="active")
    admin = User(id=uuid.uuid4(), email="admin@example.com", role="admin", status="active")
    suspended = User(
        id=uuid.uuid4(), email="suspended@example.com", role="candidate", status="suspended"
    )

    # 1. Owner can access own resource
    ensure_resource_ownership(candidate, user_id)
    ensure_resource_ownership(candidate, str(user_id))

    # 2. Non-owner candidate raises Forbidden
    with pytest.raises(ForbiddenException):
        ensure_resource_ownership(candidate, other_id)

    # 3. Admin can access any resource
    ensure_resource_ownership(admin, other_id)

    # 4. Active user check
    active_result = await require_active_user(candidate)
    assert active_result == candidate

    with pytest.raises(ForbiddenException):
        await require_active_user(suspended)
