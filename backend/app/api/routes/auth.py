"""
Authentication & Session Management Router for CoachPath.
Implements user registration, credential login, token rotation, session revocation,
and authenticated identity retrieval matching /docs/api-specification.md Group 1.
"""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Body, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_session
from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.models.auth import User
from app.schemas.auth import (
    LogoutResponse,
    RefreshTokenRequest,
    TokenRefreshResponse,
    TokenResponse,
    UserLoginRequest,
    UserPublic,
    UserRegisterRequest,
    UserRegisterResponse,
)
from app.services.auth import auth_service

router = APIRouter(prefix="/auth", tags=["Group 1: Authentication"])


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
) -> None:
    """Sets secure HttpOnly cookies for access and refresh tokens."""
    is_prod = settings.ENVIRONMENT == "production"

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_prod,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=is_prod,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/",
    )


def clear_auth_cookies(response: Response) -> None:
    """Clears authentication cookies upon user sign-out or session invalidation."""
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")


@router.get("", summary="Auth Module Status", include_in_schema=False)
async def auth_status() -> dict[str, str]:
    """Module status check endpoint."""
    return {"module": "auth", "status": "operational", "phase": "Phase 3A"}


@router.post(
    "/register",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register New Candidate",
    description="Registers a new candidate user account with password complexity validation.",
)
async def register(
    payload: UserRegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_session),
) -> UserRegisterResponse:
    """Creates a new candidate user and profile record."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    user, _ = await auth_service.register(
        db=db,
        payload=payload,
        client_ip=client_ip,
        user_agent=user_agent,
    )
    return UserRegisterResponse(
        user_id=user.id,
        email=user.email,
        status=user.status,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login Candidate",
    description="Authenticates candidate credentials and issues JWT access token and refresh token.",
)
async def login(
    payload: UserLoginRequest,
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_session),
) -> TokenResponse:
    """Authenticates candidate credentials and sets session cookies."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    user, access_token, raw_refresh_token = await auth_service.login(
        db=db,
        payload=payload,
        client_ip=client_ip,
        user_agent=user_agent,
    )

    set_auth_cookies(response, access_token=access_token, refresh_token=raw_refresh_token)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=raw_refresh_token,
        user=UserPublic.model_validate(user),
    )


@router.post(
    "/refresh",
    response_model=TokenRefreshResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh Access Token",
    description="Rotates opaque refresh token and issues a new access token.",
)
async def refresh(
    response: Response,
    request: Request,
    payload: Optional[RefreshTokenRequest] = Body(None),
    db: AsyncSession = Depends(get_session),
) -> TokenRefreshResponse:
    """Exchanges an active refresh token for a newly rotated token pair."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    raw_token: Optional[str] = None
    if payload and payload.refresh_token:
        raw_token = payload.refresh_token
    elif "refresh_token" in request.cookies:
        raw_token = request.cookies["refresh_token"]

    if not raw_token:
        raise UnauthorizedException("Refresh token is required.")

    _, new_access_token, new_refresh_token = await auth_service.refresh(
        db=db,
        raw_refresh_token=raw_token,
        client_ip=client_ip,
        user_agent=user_agent,
    )

    set_auth_cookies(response, access_token=new_access_token, refresh_token=new_refresh_token)

    return TokenRefreshResponse(
        access_token=new_access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=new_refresh_token,
    )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="Sign Out / Revoke Session",
    description="Revokes current refresh token session and clears authentication cookies.",
)
async def logout(
    response: Response,
    request: Request,
    payload: Optional[RefreshTokenRequest] = Body(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> LogoutResponse:
    """Invalidates active session and clears auth cookies."""
    raw_token: Optional[str] = None
    if payload and payload.refresh_token:
        raw_token = payload.refresh_token
    elif "refresh_token" in request.cookies:
        raw_token = request.cookies["refresh_token"]

    await auth_service.logout(
        db=db,
        user_id=current_user.id,
        raw_refresh_token=raw_token,
    )

    clear_auth_cookies(response)
    return LogoutResponse(message="Logged out successfully")


@router.get(
    "/me",
    response_model=UserPublic,
    status_code=status.HTTP_200_OK,
    summary="Retrieve Current User Identity",
    description="Returns sanitized profile details for the authenticated user.",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserPublic:
    """Returns authenticated user profile details."""
    return UserPublic.model_validate(current_user)
