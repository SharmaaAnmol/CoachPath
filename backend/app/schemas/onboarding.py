"""
Pydantic Schemas for AI-Powered Onboarding Module.
Defines strict request/response validation contracts for onboarding endpoints and AI interactions.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


# ─────────────────────────────────────────────
# Canonical Lifecycle States
# ─────────────────────────────────────────────

class OnboardingStatus:
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    COMPLETED = "completed"


# ─────────────────────────────────────────────
# AI Structured Output Schemas (Internal LLM I/O)
# ─────────────────────────────────────────────

class ExtractedCareerFact(BaseModel):
    """A discrete career fact extracted from user input by the AI."""
    field: str = Field(..., description="Canonical profile property name")
    value: Any = Field(..., description="Fact value (string, list, number, boolean)")
    confidence: str = Field(
        default="user_stated",
        description="Data provenance: 'user_stated' | 'inferred'",
    )


class OnboardingAIResponse(BaseModel):
    """
    Structured output produced by the LLM during conversation orchestration.
    Validated by Pydantic before the application persists or acts on it.
    """
    next_question: str = Field(..., description="The next single interview question to present")
    question_category: str = Field(
        ...,
        description="Category: 'target_role' | 'career_stage' | 'education' | 'skills' | "
                    "'technologies' | 'projects' | 'experience' | 'learning_time' | "
                    "'learning_resources' | 'timeline' | 'industries' | 'companies' | "
                    "'salary' | 'goals' | 'preferences'",
    )
    extracted_facts: List[ExtractedCareerFact] = Field(
        default_factory=list,
        description="Facts extracted from the candidate's latest response",
    )
    missing_information: List[str] = Field(
        default_factory=list,
        description="Remaining profile areas requiring discovery",
    )
    ready_to_summarize: bool = Field(
        default=False,
        description="True if enough core facts have been gathered to synthesize a summary",
    )
    clarification_needed: Optional[str] = Field(
        default=None,
        description="Follow-up clarification prompt if the previous response was ambiguous",
    )


class OnboardingSummarySchema(BaseModel):
    """
    Truthful career profile summary synthesized by the AI from conversation facts.
    Must be reviewed, optionally edited, and explicitly confirmed by the candidate.
    """
    target_role: Optional[str] = None
    career_stage: Optional[str] = None
    current_education: Optional[str] = None
    education_field: Optional[str] = None
    years_of_experience: Optional[float] = None
    current_or_recent_role: Optional[str] = None
    current_company: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    notable_projects: List[str] = Field(default_factory=list)
    learning_hours_per_week: Optional[float] = None
    preferred_learning_resources: List[str] = Field(default_factory=list)
    target_timeline_months: Optional[int] = None
    industries_of_interest: List[str] = Field(default_factory=list)
    companies_of_interest: List[str] = Field(default_factory=list)
    min_salary_usd: Optional[int] = None
    max_salary_usd: Optional[int] = None
    career_goals: Optional[str] = None
    work_preference: Optional[str] = None
    target_locations: List[str] = Field(default_factory=list)
    missing_areas: List[str] = Field(default_factory=list)
    uncertain_fields: List[str] = Field(default_factory=list)


# ─────────────────────────────────────────────
# API Request / Response DTOs
# ─────────────────────────────────────────────

class StartOnboardingResponse(BaseModel):
    """Response returned when initiating or resuming an onboarding session."""
    session_id: uuid.UUID
    status: str
    is_resumed: bool
    first_question: str
    first_question_category: str
    message: str


class OnboardingSessionResponse(BaseModel):
    """Public read model for an onboarding session."""
    model_config = ConfigDict(from_attributes=True)

    session_id: uuid.UUID
    status: str
    current_question: Optional[str] = None
    current_question_category: Optional[str] = None
    turn_count: int
    started_at: datetime
    last_activity_at: datetime
    completed_at: Optional[datetime] = None


class OnboardingProgressResponse(BaseModel):
    """Progress report on covered discovery areas and readiness."""
    session_id: uuid.UUID
    status: str
    turn_count: int
    areas_covered: List[str]
    areas_remaining: List[str]
    ready_to_summarize: bool
    current_question: Optional[str] = None


class ConversationTurnResponse(BaseModel):
    """A recorded turn (AI question + candidate response) in the interview history."""
    model_config = ConfigDict(from_attributes=True)

    turn_id: uuid.UUID
    turn_number: int
    question: str
    question_category: str
    user_response: Optional[str] = None
    responded_at: Optional[datetime] = None
    created_at: datetime


class SubmitResponseRequest(BaseModel):
    """Request payload for submitting a response to the current question."""
    model_config = ConfigDict(extra="forbid")

    response_text: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Candidate answer text",
    )

    @field_validator("response_text")
    @classmethod
    def validate_not_blank(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("Response text cannot be empty or whitespace only.")
        return s


class SubmitResponseResult(BaseModel):
    """Result returned after submitting a response, including the next question or summary readiness."""
    turn_completed: ConversationTurnResponse
    next_question: Optional[str] = None
    next_question_category: Optional[str] = None
    session_status: str
    ready_to_summarize: bool


class OnboardingSummaryResponse(BaseModel):
    """Envelope holding the AI-synthesized career summary awaiting user confirmation."""
    session_id: uuid.UUID
    summary: OnboardingSummarySchema
    generated_at: datetime
    is_confirmed: bool
    confirmed_at: Optional[datetime] = None


class ConfirmSummaryRequest(BaseModel):
    """Request payload to finalize onboarding and apply summary to CareerProfile."""
    model_config = ConfigDict(extra="forbid")

    confirmed: bool = Field(..., description="Explicit confirmation flag; must be True")
    edits: Optional[OnboardingSummarySchema] = Field(
        None,
        description="Optional user-provided overrides or corrections to the AI summary",
    )
