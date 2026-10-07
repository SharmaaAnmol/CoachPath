"""
FastAPI Route Dependencies for CoachPath.
Provides reusable dependency injection for database sessions, authentication, and authorization.
"""

from __future__ import annotations

import uuid
from typing import AsyncGenerator, Callable, List, Optional, Union
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import Settings, get_settings
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.auth import User

# Optional bearer scheme to populate OpenAPI UI correctly without forcing 403 on missing headers
bearer_security = HTTPBearer(auto_error=False)


def get_current_request_id(request: Request) -> str:
    """Dependency returning the correlation request ID."""
    return getattr(request.state, "request_id", "req_unknown")


async def get_session(
    session: AsyncSession = Depends(get_db),
) -> AsyncGenerator[AsyncSession, None]:
    """Dependency providing an active asynchronous database session."""
    yield session


async def get_current_user(
    request: Request,
    auth_credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_security),
    db: AsyncSession = Depends(get_session),
) -> User:
    """
    Extracts, validates JWT access token from Authorization header or HttpOnly cookie,
    and returns the active User entity with profile loaded.
    """
    token: Optional[str] = None

    # 1. Check Authorization: Bearer <token>
    if auth_credentials is not None:
        token = auth_credentials.credentials
    elif "Authorization" in request.headers:
        auth_header = request.headers["Authorization"]
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()

    # 2. Fallback to HttpOnly cookie
    if not token and "access_token" in request.cookies:
        token = request.cookies["access_token"]

    if not token:
        raise UnauthorizedException("Authentication credentials were not provided.")

    # 3. Decode & validate JWT
    payload = decode_access_token(token)
    if payload is None:
        raise UnauthorizedException("Invalid or expired authentication token.")

    user_id_raw = payload.get("sub")
    if not user_id_raw:
        raise UnauthorizedException("Malformed token claims.")

    try:
        user_id = uuid.UUID(str(user_id_raw))
    except ValueError:
        raise UnauthorizedException("Invalid user identity in token claims.")

    # 4. Lookup user from database with eager loaded profile
    stmt = (
        select(User)
        .options(selectinload(User.profile))
        .where(User.id == user_id)
    )
    user = await db.scalar(stmt)

    if user is None or user.deleted_at is not None or user.status == "deleted":
        raise UnauthorizedException("User account not found or deactivated.")

    return user


async def require_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Validates that authenticated user has not been suspended or restricted.
    """
    if current_user.status == "suspended":
        raise ForbiddenException("Account has been suspended. Please contact support.")
    return current_user


def require_role(required_role: Union[str, List[str]]) -> Callable:
    """
    Role-based authorization dependency factory.
    Admins are always granted permission.
    """
    allowed_roles = [required_role] if isinstance(required_role, str) else required_role

    async def role_checker(
        current_user: User = Depends(require_active_user),
    ) -> User:
        if current_user.role not in allowed_roles and current_user.role != "admin":
            raise ForbiddenException(
                f"Action requires one of the following roles: {', '.join(allowed_roles)}."
            )
        return current_user

    return role_checker


def ensure_resource_ownership(
    current_user: User,
    resource_user_id: Union[uuid.UUID, str],
) -> None:
    """
    Verifies that the current user owns the specified resource or has administrative rights.
    """
    try:
        target_id = (
            resource_user_id
            if isinstance(resource_user_id, uuid.UUID)
            else uuid.UUID(str(resource_user_id))
        )
    except ValueError:
        raise ForbiddenException("Invalid resource ownership context.")

    if current_user.id != target_id and current_user.role != "admin":
        raise ForbiddenException("You do not have permission to access or modify this resource.")
