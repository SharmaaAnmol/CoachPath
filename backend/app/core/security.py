"""
Security, Password Hashing, and JWT Token Utilities.
Implements Argon2id password hashing, verification, password complexity rules,
and HS256 JWT access and refresh token lifecycle management.
"""

from __future__ import annotations

import re
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple
import argon2
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
import jwt

from app.core.config import settings
from app.core.exceptions import UnauthorizedException, ValidationException

# Initialize Argon2id password hasher with documented architectural parameters
# (time_cost=3, memory_cost=65536 KiB, parallelism=4, hash_len=32, type=Argon2id)
_ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    type=argon2.Type.ID,
)


def hash_password(password: str) -> str:
    """Hashes a plaintext password using Argon2id."""
    return _ph.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against an Argon2id hash."""
    try:
        return _ph.verify(hashed_password, password)
    except (VerifyMismatchError, VerificationError):
        return False
    except Exception:
        return False


def validate_password_strength(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validates password complexity against architectural requirements:
    - Minimum 8 characters, maximum 128 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 numeric digit
    - At least 1 special character
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if len(password) > 128:
        return False, "Password cannot exceed 128 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one numeric digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>\-_+=\[\]\\/`~;']", password):
        return False, "Password must contain at least one special character."

    return True, None


def create_access_token(
    user_id: uuid.UUID,
    email: str,
    role: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Creates a short-lived signed JWT access token."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "jti": str(uuid.uuid4()),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException("Authentication token has expired.")
    except jwt.InvalidTokenError:
        raise UnauthorizedException("Invalid authentication token.")


def generate_refresh_token() -> str:
    """Generates an opaque, cryptographically random refresh token string."""
    return secrets.token_urlsafe(48)


def hash_token(token: str) -> str:
    """Computes a SHA-256 hash of an opaque token for secure database storage."""
    import hashlib
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
