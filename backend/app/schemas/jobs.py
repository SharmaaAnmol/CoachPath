"""
Pydantic Schemas for Job Market Intelligence and Job Ingestion Engine.
Defines strict validation for job search, manual imports, pipeline runs,
and market-intelligence aggregates.
"""

from __future__ import annotations

import decimal
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ─────────────────────────────────────────────
# Job Skill Schemas
# ─────────────────────────────────────────────

class JobSkillItem(BaseModel):
    """Normalized skill tagged on a job listing."""
    model_config = ConfigDict(from_attributes=True)

    skill_id: str
    name: str
    category: Optional[str] = None
    is_mandatory: bool = True
    confidence_score: Optional[float] = 1.0
    source_phrase: Optional[str] = None


# ─────────────────────────────────────────────
# Job Listing Schemas
# ─────────────────────────────────────────────

class JobResponse(BaseModel):
    """Complete public representation of a curated job opportunity."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    external_id: Optional[str] = None
    source: str
    source_url: Optional[str] = None
    title: str
    normalized_title: Optional[str] = None
    company_name: str
    location: str
    normalized_location: Optional[str] = None
    remote_type: str
    employment_type: Optional[str] = "full_time"
    role_id: str
    experience_level: str
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    currency: str = "USD"
    description_markdown: str
    responsibilities: List[str] = Field(default_factory=list)
    required_qualifications: List[str] = Field(default_factory=list)
    preferred_qualifications: List[str] = Field(default_factory=list)
    application_url: str
    is_active: bool = True
    freshness_status: str = "active"
    last_verified_at: Optional[datetime] = None
    data_quality_score: Optional[float] = None
    posted_at: datetime
    created_at: datetime
    skills: List[JobSkillItem] = Field(default_factory=list)


class JobSearchResponse(BaseModel):
    """Paginated search response for job opportunities."""
    items: List[JobResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ─────────────────────────────────────────────
# Import & Ingestion Request Schemas
# ─────────────────────────────────────────────

class JobImportRequest(BaseModel):
    """Candidate or manual user submission of a job listing for processing."""
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=2, max_length=255, description="Job title")
    company_name: str = Field(..., min_length=2, max_length=255, description="Company or hiring organization")
    location: str = Field("Remote", min_length=2, max_length=128, description="Location or primary market")
    description_text: str = Field(..., min_length=20, max_length=50000, description="Full job description text")
    application_url: Optional[str] = Field(None, max_length=512, description="Target application URL")
    source_url: Optional[str] = Field(None, max_length=512, description="Original source listing URL")
    remote_type: str = Field("remote", description="'remote', 'hybrid', or 'onsite'")
    role_id: Optional[str] = Field(None, description="Optional target canonical role ID")
    experience_level: str = Field("entry_level", description="'internship', 'entry_level', 'junior', 'mid'")
    min_salary: Optional[int] = Field(None, ge=0, description="Minimum annualized salary")
    max_salary: Optional[int] = Field(None, ge=0, description="Maximum annualized salary")
    currency: str = Field("USD", min_length=3, max_length=8, description="Currency code")


class JobIngestRequest(BaseModel):
    """Execution trigger for a permitted job pipeline source."""
    model_config = ConfigDict(extra="forbid")

    source: str = Field("seed", description="Source provider name ('seed', 'arbeitnow', 'mock')")
    batch_size: int = Field(50, ge=1, le=200, description="Batch fetch size")
    force_refresh: bool = Field(False, description="Whether to re-parse existing jobs")


class JobIngestionSummary(BaseModel):
    """Audit metric summary of an ingestion run."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    run_id: Optional[uuid.UUID] = None
    source_name: str
    status: str
    items_fetched: int
    items_inserted: int
    items_updated: int
    items_skipped: int
    items_errored: int
    error_log: List[Dict[str, Any]] = Field(default_factory=list)
    started_at: datetime
    finished_at: Optional[datetime] = None

    def model_post_init(self, __context: Any) -> None:
        if self.run_id is None:
            self.run_id = self.id


# ─────────────────────────────────────────────
# Market Intelligence Schemas
# ─────────────────────────────────────────────

class TopSkillDemand(BaseModel):
    """Aggregated market demand metric for a canonical skill."""
    skill_id: str
    name: str
    category: str
    job_count: int
    percentage: float


class SalaryInsights(BaseModel):
    """Aggregated salary statistics across curated jobs."""
    sample_size: int
    average_min_salary: Optional[int] = None
    average_max_salary: Optional[int] = None
    median_salary: Optional[int] = None
    currency: str = "USD"


class MarketIntelligenceResponse(BaseModel):
    """Statistical market overview computed from verified job catalog."""
    total_active_jobs: int
    role_distribution: Dict[str, int] = Field(default_factory=dict)
    remote_distribution: Dict[str, int] = Field(default_factory=dict)
    experience_distribution: Dict[str, int] = Field(default_factory=dict)
    top_demanded_skills: List[TopSkillDemand] = Field(default_factory=list)
    salary_insights: SalaryInsights
    is_provisional: bool = False
    provisional_reason: Optional[str] = None
    generated_at: datetime
