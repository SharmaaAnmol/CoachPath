"""
Pydantic Schemas for Authentication and Session Management.
Defines strict request/response validation contracts matching /docs/api-specification.md.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRegisterRequest(BaseModel):
    """Payload for user account registration."""

    model_config = ConfigDict(extra="forbid")

    email: EmailStr = Field(..., description="Valid candidate email address")
    password: str = Field(..., min_length=8, max_length=128, description="Secure plaintext password")
    full_name: str = Field(..., min_length=2, max_length=128, description="Candidate full legal or professional name")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        name = v.strip()
        if not name:
            raise ValueError("Full name cannot be blank or whitespace.")
        return name


class UserRegisterResponse(BaseModel):
    """Response returned upon successful account registration."""

    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    email: str
    status: str
    message: str = "Account created. Verification email sent."


class UserLoginRequest(BaseModel):
    """Payload for user credentials authentication."""

    model_config = ConfigDict(extra="forbid")

    email: EmailStr = Field(..., description="Candidate email address")
    password: str = Field(..., description="Account password")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class UserPublic(BaseModel):
    """Safe, sanitized user representation with zero password or internal secrets."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    role: str
    status: str
    full_name: Optional[str] = None
    created_at: datetime


class TokenResponse(BaseModel):
    """Access token payload returned upon successful login."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    refresh_token: Optional[str] = None
    user: UserPublic


class RefreshTokenRequest(BaseModel):
    """Optional payload when refreshing without cookie support."""

    model_config = ConfigDict(extra="forbid")

    refresh_token: Optional[str] = Field(None, description="Opaque refresh token string")


class TokenRefreshResponse(BaseModel):
    """Response returned when access token is refreshed."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    refresh_token: Optional[str] = None


class LogoutResponse(BaseModel):
    """Response returned upon successful logout."""

    message: str = "Logged out successfully"
