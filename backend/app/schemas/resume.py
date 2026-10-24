"""
Pydantic Schemas for Resume Ingestion, Extraction, and AI Parsing.
Defines strict request/response validation, evidence provenance, and structured extraction schemas.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ─── Status & Error Constants ────────────────────────────────────────

class ResumeStatus:
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PARSING = "parsing"
    PARSED = "parsed"
    NEEDS_REVIEW = "needs_review"
    FAILED = "failed"


class ParsingErrorCategory:
    UNSUPPORTED_FORMAT = "UNSUPPORTED_FORMAT"
    CORRUPTED_DOCUMENT = "CORRUPTED_DOCUMENT"
    DOCUMENT_ENCRYPTED = "DOCUMENT_ENCRYPTED"
    EMPTY_DOCUMENT = "EMPTY_DOCUMENT"
    INSUFFICIENT_TEXT_OCR_REQUIRED = "INSUFFICIENT_TEXT_OCR_REQUIRED"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    AI_PROVIDER_UNAVAILABLE = "AI_PROVIDER_UNAVAILABLE"
    AI_TIMEOUT = "AI_TIMEOUT"
    AI_OUTPUT_INVALID = "AI_OUTPUT_INVALID"
    STORAGE_ERROR = "STORAGE_ERROR"
    UNKNOWN = "UNKNOWN"


# ─── Evidence & Provenance ───────────────────────────────────────────

class EvidenceItem(BaseModel):
    """Data provenance record tracing an extracted claim back to document source."""
    model_config = ConfigDict(extra="forbid")

    section_name: Optional[str] = Field(None, max_length=128, description="Source section (e.g. 'Experience', 'Education')")
    page_number: Optional[int] = Field(None, ge=1, description="Source document page number (1-indexed)")
    supporting_excerpt: Optional[str] = Field(None, max_length=1000, description="Exact or normalized snippet from resume")


# ─── Structured Resume Extraction Schemas ────────────────────────────

class ExtractedPersonalInfo(BaseModel):
    """Candidate contact and personal identification details explicitly stated in resume."""
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = Field(None, max_length=128)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=64)
    location: Optional[str] = Field(None, max_length=255)
    linkedin_url: Optional[str] = Field(None, max_length=255)
    github_url: Optional[str] = Field(None, max_length=255)
    portfolio_url: Optional[str] = Field(None, max_length=255)


class ExtractedEducation(BaseModel):
    """Academic degree or qualification explicitly stated in resume."""
    model_config = ConfigDict(extra="forbid")

    institution: str = Field(..., min_length=1, max_length=255, description="College, university, or school name")
    degree: Optional[str] = Field(None, max_length=128, description="Degree title (e.g. B.S., M.S., High School)")
    field_of_study: Optional[str] = Field(None, max_length=128, description="Major or specialization")
    start_date: Optional[str] = Field(None, max_length=32, description="Start date as written (e.g. 'Aug 2018')")
    end_date: Optional[str] = Field(None, max_length=32, description="End date or expected graduation")
    grade_or_gpa: Optional[str] = Field(None, max_length=32, description="GPA or grade if stated")
    highlights: List[str] = Field(default_factory=list, description="Academic honors, coursework, or activities")
    evidence: Optional[EvidenceItem] = Field(None, description="Source section/page provenance")


class ExtractedExperience(BaseModel):
    """Work experience item explicitly stated in resume."""
    model_config = ConfigDict(extra="forbid")

    employer: str = Field(..., min_length=1, max_length=255, description="Company or organization name")
    job_title: str = Field(..., min_length=1, max_length=128, description="Designation or job title")
    start_date: Optional[str] = Field(None, max_length=32)
    end_date: Optional[str] = Field(None, max_length=32)
    is_current: bool = Field(default=False)
    location: Optional[str] = Field(None, max_length=128)
    responsibilities: List[str] = Field(default_factory=list, description="Explicit duties")
    achievements: List[str] = Field(default_factory=list, description="Quantified results or accomplishments")
    evidence: Optional[EvidenceItem] = Field(None, description="Source section/page provenance")


class ExtractedSkill(BaseModel):
    """Individual technical skill or capability explicitly listed in resume."""
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=64, description="Raw skill name from resume")
    category: Optional[str] = Field(
        None,
        description="Ontological category: language, framework, database, tool, cloud, architecture, concept",
    )
    confidence_source: str = Field(default="resume_stated", description="Origin flag")
    evidence: Optional[EvidenceItem] = None


class ExtractedProject(BaseModel):
    """Notable software or technical project listed in resume."""
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=128, description="Project title")
    description: Optional[str] = Field(None, max_length=2000, description="Project overview")
    technologies: List[str] = Field(default_factory=list, description="Tech stack or tools used")
    url: Optional[str] = Field(None, max_length=255, description="Repository or demo link")
    highlights: List[str] = Field(default_factory=list, description="Specific contributions or achievements")
    evidence: Optional[EvidenceItem] = None


class ExtractedCertification(BaseModel):
    """Professional certification or license explicitly listed."""
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=255, description="Certification title")
    issuing_organization: Optional[str] = Field(None, max_length=255)
    issue_date: Optional[str] = Field(None, max_length=32)
    expiration_date: Optional[str] = Field(None, max_length=32)
    credential_id: Optional[str] = Field(None, max_length=128)
    evidence: Optional[EvidenceItem] = None


class ExtractedResumeSchema(BaseModel):
    """
    Root AI structured extraction schema.
    Validated directly against the LLM's structured JSON output.
    Strictly forbids hallucinated or ungrounded attributes.
    """
    model_config = ConfigDict(extra="forbid")

    personal_info: Optional[ExtractedPersonalInfo] = None
    education: List[ExtractedEducation] = Field(default_factory=list)
    experience: List[ExtractedExperience] = Field(default_factory=list)
    skills: List[ExtractedSkill] = Field(default_factory=list)
    projects: List[ExtractedProject] = Field(default_factory=list)
    certifications: List[ExtractedCertification] = Field(default_factory=list)
    executive_summary: Optional[str] = Field(None, max_length=2000, description="Resume summary / objective statement")
    additional_sections: Dict[str, Any] = Field(default_factory=dict, description="Awards, publications, or other career items")
    uncertain_items: List[str] = Field(default_factory=list, description="Items where document text was ambiguous or partially unreadable")


# ─── Normalized Skills Preview ───────────────────────────────────────

class NormalizedSkillItem(BaseModel):
    """Skill normalized against the canonical CoachPath skill ontology."""
    model_config = ConfigDict(from_attributes=True)

    skill_id: str = Field(description="Canonical taxonomy identifier (e.g. 'postgresql')")
    name: str = Field(description="Canonical display name (e.g. 'PostgreSQL')")
    category: str = Field(description="Taxonomy category")
    raw_matched: str = Field(description="Original term found in resume")


class ParsedResumePreview(BaseModel):
    """Reviewable preview of parsed resume entities awaiting candidate approval."""
    model_config = ConfigDict(from_attributes=True)

    personal_info: Optional[ExtractedPersonalInfo] = None
    education: List[ExtractedEducation] = Field(default_factory=list)
    experience: List[ExtractedExperience] = Field(default_factory=list)
    projects: List[ExtractedProject] = Field(default_factory=list)
    certifications: List[ExtractedCertification] = Field(default_factory=list)
    detected_skills: List[str] = Field(default_factory=list, description="Raw skills found in document")
    normalized_skills: List[NormalizedSkillItem] = Field(default_factory=list, description="Skills matched to canonical taxonomy")
    raw_unmatched_skills: List[str] = Field(default_factory=list, description="Skills without exact canonical taxonomy match")
    executive_summary: Optional[str] = None


# ─── API Request / Response Schemas ───────────────────────────────────

class ResumeUploadResponse(BaseModel):
    """Response returned upon successful resume document upload."""
    model_config = ConfigDict(from_attributes=True)

    resume_id: uuid.UUID
    file_name: str
    file_size_bytes: int
    mime_type: str
    status: str
    message: str
    created_at: datetime


class ResumeListItem(BaseModel):
    """Summary item for candidate resume documents list."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    file_name: str
    file_size_bytes: int
    mime_type: str
    status: str
    is_primary: bool
    parsing_error: Optional[str] = None
    parsing_error_category: Optional[str] = None
    parsed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ResumeListResponse(BaseModel):
    """List response for candidate's uploaded resumes."""
    resumes: List[ResumeListItem]
    total: int


class ResumeDetailResponse(BaseModel):
    """Detailed metadata for a specific candidate resume document."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    file_name: str
    file_size_bytes: int
    mime_type: str
    status: str
    is_primary: bool
    parsing_error: Optional[str] = None
    parsing_error_category: Optional[str] = None
    parsed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ParsedResumeResponse(BaseModel):
    """Draft parsed information awaiting candidate review and approval."""
    model_config = ConfigDict(from_attributes=True)

    resume_id: uuid.UUID
    status: str
    file_name: str
    extracted_preview: Optional[ParsedResumePreview] = None
    requires_human_confirmation: bool = Field(
        default=True,
        description="True indicates extracted data is a draft requiring explicit candidate confirmation in Phase 5B",
    )
    parsed_at: Optional[datetime] = None
    parsing_error: Optional[str] = None
    parsing_error_category: Optional[str] = None


class RetryParsingResponse(BaseModel):
    """Response when re-initiating parsing for a failed or updated document."""
    resume_id: uuid.UUID
    status: str
    message: str


# ─── Confirmation & Profile Merge Schemas (Phase 5B) ──────────────────

class ConfirmPersonalInfo(BaseModel):
    """Optional candidate personal info updates approved during review."""
    model_config = ConfigDict(extra="forbid")

    headline: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=128)
    phone_number: Optional[str] = Field(None, max_length=32)
    linkedin_url: Optional[str] = Field(None, max_length=255)
    github_url: Optional[str] = Field(None, max_length=255)
    portfolio_url: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=2000)


class ConfirmEducationItem(BaseModel):
    """Approved education item to merge into career profile."""
    model_config = ConfigDict(extra="forbid")

    institution_name: str = Field(..., min_length=1, max_length=255)
    degree: str = Field(..., min_length=1, max_length=128)
    field_of_study: str = Field(..., min_length=1, max_length=128)
    start_date: str = Field(..., description="Start date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date or expected graduation")
    is_current: bool = Field(default=False)
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)


class ConfirmExperienceItem(BaseModel):
    """Approved work experience item to merge into career profile."""
    model_config = ConfigDict(extra="forbid")

    company_name: str = Field(..., min_length=1, max_length=255)
    role_title: str = Field(..., min_length=1, max_length=128)
    location: Optional[str] = Field(None, max_length=128)
    start_date: str = Field(..., description="Start date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date or current")
    is_current: bool = Field(default=False)
    bullet_points: List[str] = Field(default_factory=list)


class ConfirmProjectItem(BaseModel):
    """Approved project item to merge into career profile."""
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=128)
    description: str = Field(..., min_length=1, max_length=3000)
    technologies: List[str] = Field(default_factory=list)
    github_url: Optional[str] = Field(None, max_length=255)
    live_url: Optional[str] = Field(None, max_length=255)
    bullet_points: List[str] = Field(default_factory=list)


class ConfirmCertificationItem(BaseModel):
    """Approved certification item to merge into career profile."""
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=255)
    issuing_organization: str = Field(..., min_length=1, max_length=255)
    issue_date: str = Field(..., description="Issue date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    expiration_date: Optional[str] = Field(None)
    credential_id: Optional[str] = Field(None, max_length=128)
    credential_url: Optional[str] = Field(None, max_length=255)


class ResumeConfirmationRequest(BaseModel):
    """
    Candidate payload explicitly approving and editing extracted resume data.
    Only approved fields in this request are merged into the persistent profile.
    """
    model_config = ConfigDict(extra="forbid")

    personal_info: Optional[ConfirmPersonalInfo] = None
    education: List[ConfirmEducationItem] = Field(default_factory=list)
    experience: List[ConfirmExperienceItem] = Field(default_factory=list)
    projects: List[ConfirmProjectItem] = Field(default_factory=list)
    certifications: List[ConfirmCertificationItem] = Field(default_factory=list)
    confirmed_skills: List[str] = Field(
        default_factory=list,
        description="List of canonical skill identifiers or names approved to be linked",
    )
    make_primary: bool = Field(
        default=True,
        description="Whether to set this resume as candidate's primary resume",
    )


class ResumeMergeSummary(BaseModel):
    """Quantified breakdown of entities added to the profile."""
    education_added: int = 0
    experience_added: int = 0
    projects_added: int = 0
    certifications_added: int = 0
    skills_added: int = 0
    profile_updated: bool = False


class ResumeConfirmationResponse(BaseModel):
    """Confirmation result returned after transactional profile merge."""
    resume_id: uuid.UUID
    status: str
    message: str
    merged_summary: ResumeMergeSummary
    completeness_score: float


# ─── Phase 10A: Tailored Resume Schemas ───────────────────────────────

class StructuredChangeItem(BaseModel):
    """An individual structured edit, rephrasing, or addition suggested by tailoring."""
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Unique change identifier (e.g. 'chg_1')")
    section: str = Field(..., description="Target section: 'executive_summary', 'experience', 'skills', 'projects', 'education'")
    change_type: str = Field(..., description="Classification: 'addition', 'rephrasing', 'emphasis', 'reordering', 'omission'")
    original_text: Optional[str] = Field(None, description="Original source resume snippet or section")
    proposed_text: str = Field(..., description="Tailored replacement or emphasized text")
    rationale: str = Field(..., description="Grounding explanation linking this change to the target job")
    target_job_requirement: Optional[str] = Field(None, description="Specific job qualification or responsibility addressed")
    supporting_evidence: Optional[str] = Field(None, description="Authentic source resume or profile evidence supporting this change")
    needs_clarification: bool = Field(default=False, description="True if proposed point requires candidate input or clarification")


class OptimizationAnalysis(BaseModel):
    """Quantitative and diagnostic evaluation of resume alignment with target job."""
    model_config = ConfigDict(extra="forbid")

    keyword_coverage: float = Field(..., ge=0.0, le=100.0, description="Percentage of key technical job terms covered (0.0 - 100.0)")
    matched_keywords: List[str] = Field(default_factory=list, description="Target job keywords evidenced in the candidate background")
    missing_keywords: List[str] = Field(default_factory=list, description="Target job keywords not evidenced in candidate background")
    supported_skills: List[str] = Field(default_factory=list, description="Canonical skills validated in candidate's profile/resume")
    missing_requirements: List[str] = Field(default_factory=list, description="Job requirements that candidate currently lacks evidence for")
    readability_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="Readability and clarity index (0.0 - 100.0)")
    formatting_recommendations: List[str] = Field(default_factory=list, description="Suggestions for formatting, density, or organization")
    actionable_suggestions: List[str] = Field(default_factory=list, description="Next steps candidate can take to improve relevance")


class DiffSummarySchema(BaseModel):
    """Aggregate diff summary and optimization metadata for a tailored resume version."""
    model_config = ConfigDict(extra="ignore")

    changes: List[StructuredChangeItem] = Field(default_factory=list, description="Itemized before-and-after change list")
    additions_count: int = Field(default=0, ge=0)
    rephrasings_count: int = Field(default=0, ge=0)
    deletions_count: int = Field(default=0, ge=0)
    optimization_analysis: Optional[OptimizationAnalysis] = None
    unsupported_claims: List[str] = Field(
        default_factory=list,
        description="Candidate claims or job requirements omitted from the draft due to zero evidence",
    )
    model_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Provider, model identifier, and prompt version metadata (without API keys)",
    )
    candidate_notes: Optional[str] = None
    accepted_sections: List[str] = Field(default_factory=list)


class ResumeTailorRequest(BaseModel):
    """Payload to initiate AI-powered tailoring of a verified resume to a job."""
    model_config = ConfigDict(extra="forbid")

    job_id: Optional[uuid.UUID] = Field(None, description="Existing catalog Job UUID")
    job_description_text: Optional[str] = Field(
        None,
        min_length=50,
        max_length=50000,
        description="Direct pasted job posting text (used if job_id is omitted)",
    )
    job_title: Optional[str] = Field(None, max_length=255, description="Target job title (used with direct text)")
    company_name: Optional[str] = Field(None, max_length=255, description="Target company name (used with direct text)")
    target_emphasis: List[str] = Field(
        default_factory=list,
        description="Specific topics or skills candidate wishes to emphasize (e.g. ['distributed systems'])",
    )
    user_notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional additional candidate notes or context for tailoring",
    )

    @model_validator(mode="after")
    def validate_job_source(self) -> "ResumeTailorRequest":
        if not self.job_id and not (self.job_description_text and self.job_description_text.strip()):
            raise ValueError("Either job_id or job_description_text must be provided for resume tailoring.")
        return self


class TailoredResumeResponse(BaseModel):
    """Full representation of a persisted tailored resume version."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resume_id: uuid.UUID
    target_job_id: uuid.UUID
    version_number: int
    status: str = Field(description="'draft', 'approved', or 'archived'")
    anti_hallucination_verified: bool
    tailored_content: ExtractedResumeSchema
    diff_summary: DiffSummarySchema
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class TailoredResumeListItem(BaseModel):
    """Compact summary of a tailored resume version for list views."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resume_id: uuid.UUID
    target_job_id: uuid.UUID
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    version_number: int
    status: str
    anti_hallucination_verified: bool
    keyword_coverage: Optional[float] = None
    changes_count: int
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class TailoredResumeListResponse(BaseModel):
    """Paginated collection of tailored resume versions."""
    items: List[TailoredResumeListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class TailoredResumeUpdateRequest(BaseModel):
    """Payload to update editable draft content of a tailored resume version."""
    model_config = ConfigDict(extra="forbid")

    tailored_content: Optional[ExtractedResumeSchema] = Field(
        None,
        description="User-modified tailored resume content",
    )
    user_notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="User notes or review remarks",
    )


class TailoredResumeApprovalRequest(BaseModel):
    """Explicit human approval payload to certify a tailored resume version."""
    model_config = ConfigDict(extra="forbid")

    accepted_sections: List[str] = Field(
        default_factory=list,
        description="List of sections approved (e.g. ['executive_summary', 'experience', 'skills'])",
    )
    user_confirmation: bool = Field(
        ...,
        description="Mandatory explicit confirmation that candidate has reviewed and approved the draft",
    )


class TailoredResumeDiffResponse(BaseModel):
    """Structured view of original vs proposed changes for visual review."""
    version_id: uuid.UUID
    resume_id: uuid.UUID
    target_job_id: uuid.UUID
    status: str
    changes: List[StructuredChangeItem]
    additions_count: int
    rephrasings_count: int
    deletions_count: int
    unsupported_claims: List[str]


class TailoredResumeAnalysisResponse(BaseModel):
    """Structured view of optimization analysis, keyword coverage, and evidence gaps."""
    version_id: uuid.UUID
    target_job_id: uuid.UUID
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    optimization_analysis: OptimizationAnalysis
    anti_hallucination_verified: bool
    unsupported_claims: List[str]
