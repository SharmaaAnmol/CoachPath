"""
Pydantic Schemas for Central Career Profile Management.
Implements request and response validation contracts matching /docs/api-specification.md Group 3.
"""

from __future__ import annotations

import decimal
import uuid
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Role Schemas
# ---------------------------------------------------------------------------

class RoleResponse(BaseModel):
    """Canonical role presentation model."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: Optional[str] = None
    category: Optional[str] = None


# ---------------------------------------------------------------------------
# Personal Profile Schemas
# ---------------------------------------------------------------------------

class UserProfileUpdate(BaseModel):
    """Payload to update candidate personal details and social links."""

    model_config = ConfigDict(extra="forbid")

    full_name: Optional[str] = Field(None, min_length=2, max_length=128)
    headline: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=128)
    phone_number: Optional[str] = Field(None, max_length=32)
    linkedin_url: Optional[str] = Field(None, max_length=255)
    github_url: Optional[str] = Field(None, max_length=255)
    portfolio_url: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = None


# ---------------------------------------------------------------------------
# Career Goals Schemas
# ---------------------------------------------------------------------------

class CareerGoalsUpdate(BaseModel):
    """Payload to update primary career target, stage, and workplace preferences."""

    model_config = ConfigDict(extra="forbid")

    primary_role_id: str = Field(..., min_length=2, max_length=64)
    secondary_role_id: Optional[str] = Field(None, max_length=64)
    career_stage: str = Field("student", description="'student', 'recent_graduate', 'early_career'")
    work_preference: str = Field("hybrid", description="'remote', 'hybrid', 'onsite', 'flexible'")
    target_locations: List[str] = Field(default_factory=list)
    years_of_experience: float = Field(0.0, ge=0.0, le=50.0)

    @field_validator("career_stage")
    @classmethod
    def validate_stage(cls, v: str) -> str:
        valid = {"student", "recent_graduate", "early_career"}
        val = v.strip().lower()
        if val not in valid:
            raise ValueError(f"career_stage must be one of: {', '.join(sorted(valid))}")
        return val

    @field_validator("work_preference")
    @classmethod
    def validate_work_pref(cls, v: str) -> str:
        valid = {"remote", "hybrid", "onsite", "flexible"}
        val = v.strip().lower()
        if val not in valid:
            raise ValueError(f"work_preference must be one of: {', '.join(sorted(valid))}")
        return val


class CareerGoalsResponse(BaseModel):
    """Response containing active career target goals."""

    model_config = ConfigDict(from_attributes=True)

    primary_role: Optional[RoleResponse] = None
    secondary_role: Optional[RoleResponse] = None
    career_stage: str
    work_preference: str
    target_locations: List[str]
    years_of_experience: float


# ---------------------------------------------------------------------------
# Education Schemas
# ---------------------------------------------------------------------------

class EducationBase(BaseModel):
    """Shared fields for academic credentials."""

    institution_name: str = Field(..., min_length=2, max_length=255)
    degree: str = Field(..., min_length=1, max_length=128)
    field_of_study: str = Field(..., min_length=1, max_length=128)
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, end_date: Optional[date], info) -> Optional[date]:
        start_date = info.data.get("start_date")
        if start_date and end_date and end_date < start_date:
            raise ValueError("end_date cannot be earlier than start_date")
        return end_date


class EducationCreate(EducationBase):
    """Payload to add an academic credential."""

    model_config = ConfigDict(extra="forbid")


class EducationUpdate(BaseModel):
    """Payload to modify an academic credential."""

    model_config = ConfigDict(extra="forbid")

    institution_name: Optional[str] = Field(None, min_length=2, max_length=255)
    degree: Optional[str] = Field(None, min_length=1, max_length=128)
    field_of_study: Optional[str] = Field(None, min_length=1, max_length=128)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)


class EducationResponse(BaseModel):
    """Academic credential response model."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    institution_name: str
    degree: str
    field_of_study: str
    start_date: date
    end_date: Optional[date] = None
    is_current: bool
    gpa: Optional[float] = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Experience Schemas
# ---------------------------------------------------------------------------

class ExperienceBase(BaseModel):
    """Shared fields for professional employment entries."""

    company_name: str = Field(..., min_length=1, max_length=255)
    role_title: str = Field(..., min_length=1, max_length=128)
    location: Optional[str] = Field(None, max_length=128)
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    bullet_points: List[str] = Field(default_factory=list)

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, end_date: Optional[date], info) -> Optional[date]:
        start_date = info.data.get("start_date")
        if start_date and end_date and end_date < start_date:
            raise ValueError("end_date cannot be earlier than start_date")
        return end_date


class ExperienceCreate(ExperienceBase):
    """Payload to create an employment entry."""

    model_config = ConfigDict(extra="forbid")


class ExperienceUpdate(BaseModel):
    """Payload to update an employment entry."""

    model_config = ConfigDict(extra="forbid")

    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    role_title: Optional[str] = Field(None, min_length=1, max_length=128)
    location: Optional[str] = Field(None, max_length=128)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None
    bullet_points: Optional[List[str]] = None


class ExperienceResponse(BaseModel):
    """Employment entry response model."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_name: str
    role_title: str
    location: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    is_current: bool
    bullet_points: List[str]
    created_at: datetime


# ---------------------------------------------------------------------------
# Project Schemas
# ---------------------------------------------------------------------------

class ProjectBase(BaseModel):
    """Shared fields for technical artifacts and software projects."""

    title: str = Field(..., min_length=1, max_length=128)
    description: str = Field(..., min_length=1)
    technologies: List[str] = Field(default_factory=list)
    github_url: Optional[str] = Field(None, max_length=255)
    live_url: Optional[str] = Field(None, max_length=255)
    bullet_points: List[str] = Field(default_factory=list)


class ProjectCreate(ProjectBase):
    """Payload to create a project entry."""

    model_config = ConfigDict(extra="forbid")


class ProjectUpdate(BaseModel):
    """Payload to update a project entry."""

    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = Field(None, min_length=1, max_length=128)
    description: Optional[str] = Field(None, min_length=1)
    technologies: Optional[List[str]] = None
    github_url: Optional[str] = Field(None, max_length=255)
    live_url: Optional[str] = Field(None, max_length=255)
    bullet_points: Optional[List[str]] = None


class ProjectResponse(BaseModel):
    """Project entry response model."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str
    technologies: List[str]
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    bullet_points: List[str]
    created_at: datetime


# ---------------------------------------------------------------------------
# Certification Schemas
# ---------------------------------------------------------------------------

class CertificationBase(BaseModel):
    """Shared fields for professional credentials and certificates."""

    name: str = Field(..., min_length=1, max_length=255)
    issuing_organization: str = Field(..., min_length=1, max_length=255)
    issue_date: date
    expiration_date: Optional[date] = None
    credential_id: Optional[str] = Field(None, max_length=128)
    credential_url: Optional[str] = Field(None, max_length=255)

    @field_validator("expiration_date")
    @classmethod
    def validate_dates(cls, exp_date: Optional[date], info) -> Optional[date]:
        issue_date = info.data.get("issue_date")
        if issue_date and exp_date and exp_date < issue_date:
            raise ValueError("expiration_date cannot be earlier than issue_date")
        return exp_date


class CertificationCreate(CertificationBase):
    """Payload to create a certification entry."""

    model_config = ConfigDict(extra="forbid")


class CertificationUpdate(BaseModel):
    """Payload to update a certification entry."""

    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    issuing_organization: Optional[str] = Field(None, min_length=1, max_length=255)
    issue_date: Optional[date] = None
    expiration_date: Optional[date] = None
    credential_id: Optional[str] = Field(None, max_length=128)
    credential_url: Optional[str] = Field(None, max_length=255)


class CertificationResponse(BaseModel):
    """Certification entry response model."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    issuing_organization: str
    issue_date: date
    expiration_date: Optional[date] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Master Career Profile Aggregation Schema
# ---------------------------------------------------------------------------

class CareerProfileMasterResponse(BaseModel):
    """
    Consolidated view of the candidate's career profile, personal metadata,
    and verified evidence graph.
    """

    model_config = ConfigDict(from_attributes=True)

    profile_id: uuid.UUID
    user_id: uuid.UUID
    email: str
    full_name: str
    headline: Optional[str] = None
    location: Optional[str] = None
    phone_number: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    bio: Optional[str] = None
    career_stage: str
    primary_role: Optional[RoleResponse] = None
    secondary_role: Optional[RoleResponse] = None
    work_preference: str
    target_locations: List[str]
    years_of_experience: float
    education: List[EducationResponse]
    experience: List[ExperienceResponse]
    projects: List[ProjectResponse]
    certifications: List[CertificationResponse]
    verified_skills_count: int
    completeness_score: float
