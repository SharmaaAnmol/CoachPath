"""
Job Matching Domain Schemas.
Defines request/response contracts, explainability models, and recommendation structures
for CoachPath's deterministic job-matching engine.
"""

from __future__ import annotations

import decimal
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.jobs import JobResponse


class SkillMatchClassification(str, Enum):
    """Classification of candidate skill alignment against a job requirement."""
    MATCHED = "MATCHED"
    PARTIALLY_MATCHED = "PARTIALLY_MATCHED"
    MISSING = "MISSING"
    UNKNOWN = "UNKNOWN"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class SkillMatchItem(BaseModel):
    """Detailed evidence and alignment breakdown for a single job requirement."""
    model_config = ConfigDict(from_attributes=True)

    skill_id: str = Field(..., description="Canonical skill identifier")
    name: str = Field(..., description="Display name of the skill")
    category: str = Field("technical", description="Ontological category")
    is_mandatory: bool = Field(True, description="True if requirement is required/mandatory, False if preferred")
    classification: SkillMatchClassification = Field(..., description="MATCHED, PARTIALLY_MATCHED, MISSING, UNKNOWN, INSUFFICIENT_EVIDENCE")
    user_evidence_source: Optional[str] = Field(None, description="assessment, project_evidence, extracted, self_reported, or None")
    user_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Calibrated confidence score (0.0 to 1.0)")
    user_proficiency_tier: Optional[str] = Field(None, description="unverified, demonstrated, proficient, mastered")
    assessment_score: Optional[float] = Field(None, description="Diagnostic assessment score if verified via assessment")
    explanation: str = Field(..., description="Deterministic factual explanation of match status and evidence")


class MatchScoreBreakdown(BaseModel):
    """Component-level factor breakdown and normalization transparency."""
    model_config = ConfigDict(from_attributes=True)

    overall_score: float = Field(..., ge=0.0, le=100.0, description="Authoritative composite match score (0.0 - 100.0)")
    skill_score: float = Field(..., ge=0.0, le=100.0, description="Skill alignment score")
    experience_score: float = Field(..., ge=0.0, le=100.0, description="Experience alignment score")
    project_score: float = Field(..., ge=0.0, le=100.0, description="Project relevance score")
    location_score: float = Field(..., ge=0.0, le=100.0, description="Location and workplace flexibility score")
    preference_score: float = Field(..., ge=0.0, le=100.0, description="Career preferences and role alignment score")
    vector_score: float = Field(0.0, ge=0.0, le=100.0, description="Semantic vector similarity score (optional)")
    evidence_coverage: float = Field(..., ge=0.0, le=100.0, description="Data completeness and evidence coverage score (0.0 - 100.0)")
    is_provisional: bool = Field(False, description="True if evidence coverage is low (< 40%) or critical data is missing")
    weights: Dict[str, float] = Field(..., description="Configured factor weights utilized in calculation")
    evaluated_factors: List[str] = Field(default_factory=list, description="Factors successfully evaluated with available data")
    unevaluated_factors: List[str] = Field(default_factory=list, description="Factors normalized out due to missing listing or candidate data")


class JobMatchExplanation(BaseModel):
    """Natural language and structured explainability breakdown."""
    model_config = ConfigDict(from_attributes=True)

    summary: str = Field(..., description="Objective narrative summary of match fit grounded strictly in evidence")
    strengths: List[str] = Field(default_factory=list, description="Key alignment points and verified strengths")
    gaps: List[str] = Field(default_factory=list, description="Identified missing skills, experience gaps, or mismatches")
    recommended_actions: List[str] = Field(default_factory=list, description="Actionable next steps to bridge gaps and raise readiness")


class JobMatchResponse(BaseModel):
    """Complete match evaluation response for a single job opportunity."""
    model_config = ConfigDict(from_attributes=True)

    match_id: uuid.UUID
    job_id: uuid.UUID
    career_profile_id: uuid.UUID
    overall_score: float = Field(..., ge=0.0, le=100.0)
    breakdown: MatchScoreBreakdown
    matched_skills: List[str] = Field(default_factory=list, description="Required skills demonstrated by candidate")
    matched_preferred_skills: List[str] = Field(default_factory=list, description="Preferred skills demonstrated by candidate")
    missing_skills: List[str] = Field(default_factory=list, description="Required skills absent from candidate profile")
    unknown_skills: List[str] = Field(default_factory=list, description="Skills where evidence is unrecorded or uncertain")
    skills_detail: List[SkillMatchItem] = Field(default_factory=list, description="Detailed requirement-by-requirement evaluation")
    explanation: JobMatchExplanation
    scoring_version: str = Field("v1.0", description="Algorithm version identifier")
    is_stale: bool = Field(False, description="True if match should be refreshed due to upstream data changes")
    freshness_status: str = Field("active", description="Listing freshness status ('active', 'needs_refresh', 'expired', 'closed')")
    calculated_at: datetime


class JobMatchExplanationDrawerResponse(BaseModel):
    """Drawer response contract conforming to api-specification.md Section 8.2."""
    model_config = ConfigDict(from_attributes=True)

    job_id: uuid.UUID
    overall_score: float
    evidence_coverage: float
    breakdown: Dict[str, float]
    matched_skills: List[str]
    missing_skills: List[str]
    matched_preferred_skills: List[str]
    unknown_skills: List[str]
    hiring_rationale: str
    strengths: List[str]
    gaps: List[str]
    recommended_actions: List[str]
    skills_detail: List[SkillMatchItem]


class JobRecommendationItem(BaseModel):
    """A recommended job paired with its deterministic match score."""
    model_config = ConfigDict(from_attributes=True)

    job: JobResponse
    match: JobMatchResponse


class JobRecommendationResponse(BaseModel):
    """Paginated response containing personalized job recommendations ranked by match score."""
    model_config = ConfigDict(from_attributes=True)

    items: List[JobRecommendationItem]
    total: int
    page: int
    page_size: int
    total_pages: int
    scoring_version: str
    generated_at: datetime


class JobMatchRecalculateRequest(BaseModel):
    """Request payload to force recalculate an existing match."""
    force: bool = Field(False, description="Force recalculation even if cached result is fresh")


class JobMatchBatchRefreshResponse(BaseModel):
    """Summary of batch recommendation refresh."""
    recalculated_count: int
    status: str
    scoring_version: str
    message: str
