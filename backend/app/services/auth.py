"""
Authentication and Session Service.
Implements user registration, credential verification, JWT access tokens,
refresh token rotation, session revocation, and security audit logging.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.exceptions import (
    ConflictException,
    ForbiddenException,
    UnauthorizedException,
    ValidationException,
)
from app.core.rate_limit import auth_rate_limiter
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_token,
    validate_password_strength,
    verify_password,
)
from app.models.audit import ActivityLog
from app.models.auth import User, UserProfile, UserSession
from app.schemas.auth import UserLoginRequest, UserRegisterRequest
from app.schemas.error import ErrorDetail


class AuthService:
    """Service handling candidate authentication, registration, and sessions."""

    async def register(
        self,
        db: AsyncSession,
        payload: UserRegisterRequest,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[User, UserProfile]:
        """
        Registers a new candidate user, enforces password strength,
        creates initial profile, and records registration activity.
        """
        email = payload.email.strip().lower()

        # 1. Enforce password complexity
        is_valid, error_msg = validate_password_strength(payload.password)
        if not is_valid:
            raise ValidationException(
                message=error_msg or "Password does not meet complexity requirements.",
                details=[ErrorDetail(field="password", issue=error_msg or "Weak password")],
            )

        # 2. Prevent duplicate account creation
        existing_user = await db.scalar(select(User).where(User.email == email))
        if existing_user is not None:
            raise ConflictException(
                message="An account with this email address already exists.",
                details=[ErrorDetail(field="email", issue="Email is already registered.")],
            )

        # 3. Hash password securely with Argon2id
        hashed_pw = hash_password(payload.password)

        # 4. Create User entity (default role='candidate', status='pending_verification')
        user = User(
            email=email,
            password_hash=hashed_pw,
            role="candidate",
            status="pending_verification",
        )
        db.add(user)
        await db.flush()

        # 5. Create initial UserProfile entity
        profile = UserProfile(
            user_id=user.id,
            full_name=payload.full_name,
        )
        db.add(profile)

        # 6. Record activity audit log
        activity = ActivityLog(
            user_id=user.id,
            activity_type="ACCOUNT_REGISTERED",
            title="Candidate account created",
            metadata_json={"email": email, "ip": client_ip or "unknown"},
        )
        db.add(activity)

        await db.commit()
        await db.refresh(user)
        await db.refresh(profile)
        user.profile = profile

        return user, profile

    async def login(
        self,
        db: AsyncSession,
        payload: UserLoginRequest,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[User, str, str]:
        """
        Verifies credentials, checks abuse thresholds, establishes session,
        and returns (user, access_token, raw_refresh_token).
        """
        email = payload.email.strip().lower()
        rate_key = f"{client_ip or 'ip'}:{email}"

        # 1. Check rate limit
        auth_rate_limiter.check(rate_key)

        # 2. Fetch candidate record
        stmt = (
            select(User)
            .options(selectinload(User.profile))
            .where(User.email == email)
        )
        user = await db.scalar(stmt)

        # 3. Verify user existence and password hash
        if user is None or user.deleted_at is not None or user.status == "deleted":
            auth_rate_limiter.record_failure(rate_key)
            raise UnauthorizedException("Invalid email or password.")

        if not verify_password(payload.password, user.password_hash):
            auth_rate_limiter.record_failure(rate_key)
            raise UnauthorizedException("Invalid email or password.")

        # 4. Check account status
        if user.status == "suspended":
            raise ForbiddenException("Account has been suspended. Please contact support.")

        # 5. Successful login: reset failed attempts
        auth_rate_limiter.record_success(rate_key)

        # 6. Generate access token and opaque refresh token
        access_token = create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role,
        )
        raw_refresh_token = generate_refresh_token()
        refresh_hash = hash_token(raw_refresh_token)

        # 7. Record session and last login timestamp
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        session = UserSession(
            user_id=user.id,
            refresh_token_hash=refresh_hash,
            user_agent=user_agent,
            ip_address=client_ip,
            is_revoked=False,
            expires_at=expires_at,
        )
        user.last_login_at = now
        db.add(session)

        # 8. Record login activity
        activity = ActivityLog(
            user_id=user.id,
            activity_type="USER_LOGIN",
            title="User signed in",
            metadata_json={"ip": client_ip or "unknown"},
        )
        db.add(activity)

        await db.commit()

        return user, access_token, raw_refresh_token

    async def refresh(
        self,
        db: AsyncSession,
        raw_refresh_token: str,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[User, str, str]:
        """
        Validates refresh token, executes atomic rotation, and issues a new access token.
        Detects token replay attacks and revokes the session family if compromised.
        """
        if not raw_refresh_token:
            raise UnauthorizedException("Refresh token is required.")

        refresh_hash = hash_token(raw_refresh_token)
        stmt = select(UserSession).where(UserSession.refresh_token_hash == refresh_hash)
        session = await db.scalar(stmt)

        if session is None:
            raise UnauthorizedException("Invalid or unrecognized refresh token.")

        # Replay attack detection
        if session.is_revoked:
            await db.execute(
                update(UserSession)
                .where(UserSession.user_id == session.user_id)
                .values(is_revoked=True)
            )
            await db.commit()
            raise UnauthorizedException("Revoked refresh token detected. Session terminated for security.")

        now = datetime.now(timezone.utc)
        expires_at = session.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < now:
            session.is_revoked = True
            await db.commit()
            raise UnauthorizedException("Refresh token has expired.")

        # Fetch associated user
        user = await db.scalar(
            select(User)
            .options(selectinload(User.profile))
            .where(User.id == session.user_id)
        )
        if user is None or user.deleted_at is not None or user.status in ("deleted", "suspended"):
            raise UnauthorizedException("Account is inactive or suspended.")

        # Atomic Token Rotation: revoke current, issue new
        session.is_revoked = True

        new_access_token = create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role,
        )
        new_raw_refresh = generate_refresh_token()
        new_refresh_hash = hash_token(new_raw_refresh)
        new_expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        new_session = UserSession(
            user_id=user.id,
            refresh_token_hash=new_refresh_hash,
            user_agent=user_agent,
            ip_address=client_ip,
            is_revoked=False,
            expires_at=new_expires_at,
        )
        db.add(new_session)
        await db.commit()

        return user, new_access_token, new_raw_refresh

    async def logout(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        raw_refresh_token: Optional[str] = None,
    ) -> None:
        """Revokes the active refresh token session and logs the logout event."""
        if raw_refresh_token:
            refresh_hash = hash_token(raw_refresh_token)
            stmt = select(UserSession).where(
                UserSession.user_id == user_id,
                UserSession.refresh_token_hash == refresh_hash,
            )
            session = await db.scalar(stmt)
            if session:
                session.is_revoked = True

        activity = ActivityLog(
            user_id=user_id,
            activity_type="USER_LOGOUT",
            title="User signed out",
            metadata_json={},
        )
        db.add(activity)
        await db.commit()


auth_service = AuthService()
