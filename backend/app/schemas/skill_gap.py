"""
Pydantic Schemas for Phase 6A: Skill Gap Analysis Engine.
Defines strict validation contracts for Role Catalogs, Canonical Skills,
Competency Calibration, Deterministic Gap Analysis, and Evidence Provenance.
"""

from __future__ import annotations

import decimal
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ─── Canonical Skill Schemas ─────────────────────────────────────────

class SkillResponse(BaseModel):
    """Public presentation schema for a canonical skill."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    category: str
    description: str
    synonyms: List[str] = Field(default_factory=list)


# ─── Role & Requirement Schemas ──────────────────────────────────────

class RoleRequirementResponse(BaseModel):
    """Public presentation schema for a role skill requirement."""
    model_config = ConfigDict(from_attributes=True)

    skill_id: str
    skill_name: Optional[str] = None
    category: Optional[str] = None
    importance: str  # 'mandatory' | 'preferred' | 'bonus'
    min_proficiency: str  # 'basic' | 'demonstrated' | 'proficient' | 'mastered'
    required_level: int  # 1 to 4
    weight: float
    rationale: Optional[str] = None


class RoleDetailResponse(BaseModel):
    """Detailed role presentation model including curated requirements."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    category: str
    version: str
    source: str
    is_complete: bool
    requirements: List[RoleRequirementResponse] = Field(default_factory=list)


class RoleListResponse(BaseModel):
    """Paginated or listed roles collection."""
    roles: List[RoleDetailResponse]
    total: int


# ─── Evidence & Competency Detail Schemas ────────────────────────────

class EvidenceItem(BaseModel):
    """A single piece of calibrated career evidence supporting a skill."""
    source: str  # 'assessment' | 'resume' | 'profile' | 'project'
    title: str
    description: str
    score: Optional[float] = None
    confidence_score: float  # 0.00 to 1.00
    is_verified: bool
    date: Optional[str] = None


class SkillCompetencyDetail(BaseModel):
    """Per-skill granular competency breakdown within a gap analysis."""
    skill_id: str
    skill_name: str
    category: str
    importance: str  # 'mandatory' | 'preferred' | 'bonus'
    min_proficiency: str  # 'basic' | 'demonstrated' | 'proficient' | 'mastered'
    required_level: int  # 1 to 4
    current_level: int  # 0 to 4
    current_tier: str  # 'unverified' | 'demonstrated' | 'proficient' | 'mastered'
    coverage_ratio: float  # min(current_level / required_level, 1.0)
    status: str  # 'STRENGTH' | 'DEVELOPING' | 'GAP' | 'NOT_ASSESSED' | 'NOT_IN_PROFILE'
    weight: float
    rationale: Optional[str] = None
    evidence_count: int = 0
    evidence_items: List[EvidenceItem] = Field(default_factory=list)
    recommended_action: Optional[str] = None


class PrioritizedGap(BaseModel):
    """Deterministically ranked gap with actionable next steps."""
    rank: int
    skill_id: str
    skill_name: str
    priority: str  # 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'
    importance: str
    required_level: int
    current_level: int
    reason: str
    action_type: str  # 'TAKE_ASSESSMENT' | 'BUILD_PROJECT' | 'PRACTICE_TOPIC'
    action_description: str
    assessment_id: Optional[str] = None


class RecommendedAssessment(BaseModel):
    """Diagnostic assessment recommendation to verify unassessed or developing competencies."""
    assessment_id: str
    title: str
    skill_id: str
    reason: str
    estimated_minutes: int
    question_count: int


# ─── Gap Analysis Snapshot Schemas ───────────────────────────────────

class SkillGapAnalysisResponse(BaseModel):
    """Full deterministic skill gap analysis snapshot presentation schema."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    career_profile_id: uuid.UUID
    role_id: str
    role_title: str
    is_current: bool
    role_version: str
    algorithm_version: str
    role_alignment_score: float
    evidence_coverage_score: float
    status: str
    strongest_skills: List[str]
    developing_skills: List[str]
    skill_gaps: List[str]
    missing_skills: List[str]
    unassessed_skills: List[str]
    skill_details: Dict[str, SkillCompetencyDetail]
    prioritized_gaps: List[PrioritizedGap]
    recommended_assessments: List[RecommendedAssessment]
    explanation_narrative: str
    calculated_at: datetime


class SkillGapAnalysisSummary(BaseModel):
    """Lightweight historical snapshot summary."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role_id: str
    role_title: str
    is_current: bool
    role_alignment_score: float
    evidence_coverage_score: float
    status: str
    strongest_skills_count: int
    developing_skills_count: int
    skill_gaps_count: int
    missing_skills_count: int
    unassessed_skills_count: int
    calculated_at: datetime


class SkillGapAnalysisListResponse(BaseModel):
    """List of historical gap analyses for a user."""
    items: List[SkillGapAnalysisSummary]
    total: int


class SkillGapAnalysisRequest(BaseModel):
    """Request payload to trigger gap analysis calculation for a target role."""
    model_config = ConfigDict(extra="forbid")

    role_id: Optional[str] = Field(
        None,
        description="Optional target role ID. If omitted, uses candidate's primary_role_id.",
    )


class SkillEvidenceDetailResponse(BaseModel):
    """Granular evidence drill-down for a single canonical skill."""
    skill_id: str
    skill_name: str
    category: str
    current_level: int
    current_tier: str
    is_verified: bool
    evidence_items: List[EvidenceItem]


class LegacySkillGapResponse(BaseModel):
    """Legacy backward-compatible gap analysis response."""
    readiness_percentage: float
    met_skills: List[str]
    developing_skills: List[str]
    missing_skills: List[str]
    explanation_narrative: str
    calculated_at: datetime
