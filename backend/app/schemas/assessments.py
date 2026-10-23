"""
Pydantic Schemas for Diagnostic Skill Assessments Module.
Defines strict validation for category listings, multi-question attempts,
server-side deterministic grading, and structured pedagogical results.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class AssessmentCategoryListItem(BaseModel):
    """Public summary of a diagnostic assessment category for card displays."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    skill_id: str
    title: str
    description: str
    time_limit_minutes: int
    passing_threshold: float
    question_count: int
    user_status: str = Field(
        default="available",
        description="'available' | 'in_progress' | 'completed'"
    )
    user_best_score: Optional[float] = None
    last_attempt_at: Optional[datetime] = None
    attempt_count: int = 0


class AssessmentDetailResponse(BaseModel):
    """Detailed category specifications and syllabus metadata."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    skill_id: str
    title: str
    description: str
    time_limit_minutes: int
    passing_threshold: float
    total_bank_questions: int
    attempt_question_count: int = 20
    difficulty_breakdown: Dict[str, int]
    topics: List[str]


class AttemptQuestionPublic(BaseModel):
    """
    Public representation of a question within an active attempt.
    CRITICAL: Never includes correct_option_index or explanation prior to completion.
    """
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    index: int = Field(description="1-based question number in this attempt (1 to 20)")
    prompt_text: str
    code_snippet: Optional[str] = None
    options: List[str]
    difficulty: str
    topic: str


class AttemptSessionResponse(BaseModel):
    """Full session state returned when starting or resuming an assessment attempt."""
    model_config = ConfigDict(from_attributes=True)

    attempt_id: uuid.UUID
    assessment_id: uuid.UUID
    assessment_title: str
    skill_id: str
    skill_name: str
    status: str
    total_questions: int = 20
    time_limit_minutes: int
    started_at: datetime
    questions: List[AttemptQuestionPublic]
    current_answers: Dict[str, int] = Field(
        default_factory=dict,
        description="Mapping of question UUID string to user's currently selected option index"
    )


class SubmitAnswerRequest(BaseModel):
    """Request payload when a user selects or updates an answer choice."""
    model_config = ConfigDict(extra="forbid")

    question_id: uuid.UUID
    selected_option_index: int = Field(
        ...,
        ge=0,
        le=3,
        description="Zero-based index of the chosen option (0, 1, 2, or 3)"
    )
    response_time_seconds: int = Field(
        default=0,
        ge=0,
        description="Elapsed seconds spent on this question"
    )


class SubmitAnswerResponse(BaseModel):
    """Acknowledgement of an updated answer submission."""
    attempt_id: uuid.UUID
    question_id: uuid.UUID
    selected_option_index: int
    answered_count: int
    total_questions: int


class TopicScore(BaseModel):
    """Aggregated performance within a specific subtopic domain."""
    topic: str
    total: int
    correct: int
    percentage: float


class DifficultyScore(BaseModel):
    """Aggregated performance at a difficulty tier."""
    total: int
    correct: int
    percentage: float


class GradedQuestionResult(BaseModel):
    """Complete graded breakdown of an individual question post-completion."""
    id: uuid.UUID
    index: int
    prompt_text: str
    code_snippet: Optional[str] = None
    options: List[str]
    selected_option_index: Optional[int] = None
    correct_option_index: int
    is_correct: bool
    explanation: str
    difficulty: str
    topic: str


class AssessmentResultResponse(BaseModel):
    """Comprehensive diagnostic result containing scores, proficiency band, and review."""
    model_config = ConfigDict(from_attributes=True)

    attempt_id: uuid.UUID
    assessment_id: uuid.UUID
    assessment_title: str
    skill_id: str
    skill_name: str
    status: str
    score_percentage: float
    passed: bool
    passing_threshold: float
    proficiency_band: str = Field(
        description="'Foundational' (0-49) | 'Developing' (50-69) | 'Proficient' (70-84) | 'Strong' (85-100)"
    )
    strengths_summary: str
    weaknesses_summary: str
    remedial_milestones: List[Dict[str, Any]] = Field(default_factory=list)
    topic_breakdown: List[TopicScore] = Field(default_factory=list)
    difficulty_breakdown: Dict[str, DifficultyScore] = Field(default_factory=dict)
    total_questions: int = 20
    correct_count: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    questions: List[GradedQuestionResult] = Field(default_factory=list)


class AttemptHistoryItem(BaseModel):
    """Summary item for a candidate's past diagnostic assessment history."""
    model_config = ConfigDict(from_attributes=True)

    attempt_id: uuid.UUID
    assessment_id: uuid.UUID
    assessment_title: str
    skill_id: str
    skill_name: str
    status: str
    score_percentage: Optional[float] = None
    passed: Optional[bool] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
