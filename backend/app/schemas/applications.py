"""
Pydantic Schemas for Phase 11A: Intelligent Application Preparation & Recruiter Outreach.
Defines request payloads, AI-grounded outputs, explicit candidate confirmation gates,
and external handoff structures matching CoachPath production architecture.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ─── Application Preparation Schemas ─────────────────────────────────────────

class ApplicationQuestionAnswer(BaseModel):
    """Structured question-and-answer item grounded in candidate profile evidence."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: Optional[str] = None
    question: str = Field(..., description="Common application question")
    answer: str = Field(..., description="Evidence-grounded response text")
    supporting_evidence: Optional[str] = Field(None, description="Candidate profile or resume citations")
    evidence_citations: List[str] = Field(
        default_factory=list,
        description="Source citations from parsed resume or career profile",
    )
    needs_clarification: bool = Field(
        default=False,
        description="True if experience does not fully support the question requirement",
    )
    requires_clarification: bool = Field(
        default=False,
        description="Alias for needs_clarification",
    )
    clarification_prompt: Optional[str] = Field(
        None,
        description="Prompt asking candidate to supply missing facts or clarify details",
    )

    @model_validator(mode="before")
    @classmethod
    def reconcile_qa_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "needs_clarification" in data and "requires_clarification" not in data:
                data["requires_clarification"] = bool(data["needs_clarification"])
            elif "requires_clarification" in data and "needs_clarification" not in data:
                data["needs_clarification"] = bool(data["requires_clarification"])
            if not data.get("evidence_citations") and data.get("supporting_evidence"):
                data["evidence_citations"] = [data["supporting_evidence"]]
            elif data.get("evidence_citations") and not data.get("supporting_evidence"):
                data["supporting_evidence"] = "; ".join(data["evidence_citations"])
        return data


class ApplicationPackageCreateRequest(BaseModel):
    """Request payload to prepare an application package."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    job_id: Optional[uuid.UUID] = Field(None, description="Target job UUID from catalog")
    target_job_id: Optional[uuid.UUID] = Field(None, description="Alias for job_id")
    job_description_text: Optional[str] = Field(None, description="Direct pasted job description (minimum 50 chars)")
    job_title: Optional[str] = Field(None, description="Target job title (required if using direct text)")
    company_name: Optional[str] = Field(None, description="Employer company name (required if using direct text)")
    tailored_resume_version_id: Optional[uuid.UUID] = Field(None, description="Explicit tailored resume variant UUID")
    source_resume_id: Optional[uuid.UUID] = Field(None, description="Source master resume UUID")
    user_notes: Optional[str] = Field(None, description="Optional custom candidate notes or focus points")

    @model_validator(mode="before")
    @classmethod
    def reconcile_job_id_and_target_job_id(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if data.get("job_id") is None and data.get("target_job_id") is not None:
                data["job_id"] = data["target_job_id"]
            elif data.get("target_job_id") is None and data.get("job_id") is not None:
                data["target_job_id"] = data["job_id"]
        return data

    @field_validator("job_description_text")
    @classmethod
    def validate_job_desc(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v.strip()) < 50:
            raise ValueError("Direct job description text must be at least 50 characters.")
        return v


class ApplicationPackageUpdateRequest(BaseModel):
    """Request payload to edit draft cover note or question answers."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    cover_note: Optional[str] = Field(None, description="User-modified cover note")
    application_questions: Optional[List[ApplicationQuestionAnswer]] = Field(None, description="Modified question answers")
    user_notes: Optional[str] = Field(None, description="Candidate private notes")
    candidate_notes: Optional[str] = Field(None, description="Alias for user_notes")

    @model_validator(mode="before")
    @classmethod
    def reconcile_notes(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if data.get("user_notes") is None and data.get("candidate_notes") is not None:
                data["user_notes"] = data["candidate_notes"]
            elif data.get("candidate_notes") is None and data.get("user_notes") is not None:
                data["candidate_notes"] = data["user_notes"]
        return data


class ApplicationPackageApproveRequest(BaseModel):
    """Explicit candidate approval gate for an application package."""
    model_config = ConfigDict(from_attributes=True)

    user_confirmation: bool = Field(
        ...,
        description="Mandatory candidate confirmation certifying package accuracy and grounding",
    )
    accepted_sections: Optional[List[str]] = Field(
        default=None,
        description="Optional list of accepted sections (e.g. ['cover_note', 'questions'])",
    )


class ApplicationSubmissionConfirmRequest(BaseModel):
    """Candidate confirmation that official external employer submission has completed."""
    model_config = ConfigDict(from_attributes=True)

    user_confirmation: bool = Field(
        ...,
        description="Mandatory confirmation that user completed submission on employer's careers portal",
    )
    notes: Optional[str] = Field(None, description="Optional candidate submission notes")


class ApplicationPackageResponse(BaseModel):
    """Response payload representing a prepared application package."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    job_id: uuid.UUID
    target_job_id: Optional[uuid.UUID] = None
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    application_id: Optional[uuid.UUID] = None
    source_resume_id: uuid.UUID
    tailored_resume_version_id: uuid.UUID
    status: str
    cover_note: str
    application_questions: List[ApplicationQuestionAnswer]
    question_answers: Optional[List[ApplicationQuestionAnswer]] = None
    evidence_references: List[str]
    generated_metadata: Dict[str, Any]
    user_notes: Optional[str] = None
    approved_at: Optional[datetime] = None
    candidate_approved_at: Optional[datetime] = None
    is_candidate_approved: bool = False
    handoff_initiated_at: Optional[datetime] = None
    application_url: Optional[str] = None
    application_url_source: Optional[str] = None
    user_confirmed_submission: bool
    submitted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def populate_aliases(self) -> ApplicationPackageResponse:
        if self.target_job_id is None:
            self.target_job_id = self.job_id
        if self.question_answers is None:
            self.question_answers = self.application_questions
        self.is_candidate_approved = self.status in ("approved", "handoff_initiated", "submitted")
        if self.candidate_approved_at is None:
            self.candidate_approved_at = self.approved_at
        return self


class ApplicationPackageHandoffResponse(BaseModel):
    """Instructions and preserved employer link for external application handoff."""
    model_config = ConfigDict(from_attributes=True)

    package_id: uuid.UUID
    status: str
    application_url: Optional[str] = None
    instructions: str
    handoff_initiated_at: datetime


class ApplicationPackageListResponse(BaseModel):
    """List of application packages owned by candidate."""
    model_config = ConfigDict(from_attributes=True)

    packages: List[ApplicationPackageResponse]
    total: int


# ─── Recruiter Outreach Schemas ──────────────────────────────────────────────

class RecruiterOutreachCreateRequest(BaseModel):
    """Request payload to draft a bounded recruiter outreach message."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    job_id: Optional[uuid.UUID] = Field(None, description="Target job UUID from catalog")
    target_job_id: Optional[uuid.UUID] = Field(None, description="Alias for job_id")
    application_package_id: Optional[uuid.UUID] = Field(None, description="Associated application package UUID")
    application_id: Optional[uuid.UUID] = Field(None, description="Associated application UUID")
    outreach_channel: str = Field(
        default="recruiter_inmail",
        description="Channel type: 'recruiter_inmail', 'email', 'general_inquiry'",
    )
    recruiter_name: Optional[str] = Field(None, description="Recruiter first/full name if identified by candidate")
    recruiter_role_type: Optional[str] = Field(None, description="Role: 'technical_recruiter', 'engineering_manager', 'talent_lead'")
    recruiter_profile_url: Optional[str] = Field(None, description="Direct LinkedIn or recruiter profile link")
    recruiter_contact_info: Optional[str] = Field(None, description="Recruiter email or handle if candidate has it")
    candidate_notes: Optional[str] = Field(None, description="Candidate-provided focus areas or tone guidance")

    @model_validator(mode="before")
    @classmethod
    def reconcile_job_id(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if data.get("job_id") is None and data.get("target_job_id") is not None:
                data["job_id"] = data["target_job_id"]
            elif data.get("target_job_id") is None and data.get("job_id") is not None:
                data["target_job_id"] = data["job_id"]
        return data


class RecruiterOutreachUpdateRequest(BaseModel):
    """Request payload to edit draft recruiter message (enforcing <= 90 words)."""
    model_config = ConfigDict(from_attributes=True)

    subject_line: Optional[str] = Field(None, description="Modified subject line")
    message_body: Optional[str] = Field(None, description="Modified message text (must not exceed 90 words)")
    recruiter_name: Optional[str] = Field(None, description="Updated recruiter name")
    recruiter_role_type: Optional[str] = Field(None, description="Updated role category")
    recruiter_profile_url: Optional[str] = Field(None, description="Updated profile URL")
    recruiter_contact_info: Optional[str] = Field(None, description="Updated contact info")
    candidate_notes: Optional[str] = Field(None, description="Updated private notes")


class RecruiterOutreachApproveRequest(BaseModel):
    """Human approval gate for finalizing a recruiter outreach message."""
    model_config = ConfigDict(from_attributes=True)

    user_confirmation: bool = Field(
        ...,
        description="Mandatory candidate confirmation that outreach message has been reviewed for factual accuracy",
    )


class RecruiterOutreachSentConfirmRequest(BaseModel):
    """Candidate confirmation that outreach message was manually dispatched."""
    model_config = ConfigDict(from_attributes=True)

    user_confirmation: bool = Field(
        ...,
        description="Mandatory candidate confirmation that message was sent via email or LinkedIn",
    )
    notes: Optional[str] = Field(None, description="Optional dispatch notes")


class RecruiterOutreachResponse(BaseModel):
    """Response payload representing a recruiter outreach message draft."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    job_id: uuid.UUID
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    application_package_id: Optional[uuid.UUID] = None
    recruiter_name: Optional[str] = None
    recruiter_role_type: Optional[str] = None
    recruiter_profile_url: Optional[str] = None
    recruiter_contact_info: Optional[str] = None
    candidate_notes: Optional[str] = None
    subject_line: str
    message_body: str
    word_count: int
    suggested_role_types: List[str]
    status: str
    approved_at: Optional[datetime] = None
    handoff_initiated_at: Optional[datetime] = None
    handoff_type: Optional[str] = None
    sent_at: Optional[datetime] = None
    user_confirmed_sent: bool
    created_at: datetime
    updated_at: datetime


class RecruiterOutreachHandoffResponse(BaseModel):
    """Structured clipboard and link payload for candidate-controlled manual outreach."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    draft_id: Optional[uuid.UUID] = None
    outreach_id: Optional[uuid.UUID] = None
    status: str
    outreach_channel: Optional[str] = "recruiter_inmail"
    handoff_type: Optional[str] = None
    mailto_uri: Optional[str] = None
    mailto_url: Optional[str] = None
    recruiter_profile_url: Optional[str] = None
    profile_url: Optional[str] = None
    clipboard_text: Optional[str] = None
    copy_text: Optional[str] = None
    subject_line: Optional[str] = None
    handoff_instructions: Optional[str] = None
    instructions: Optional[str] = None
    handoff_initiated_at: Optional[datetime] = None

    @model_validator(mode="before")
    @classmethod
    def reconcile_handoff_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if data.get("draft_id") is None and data.get("outreach_id") is not None:
                data["draft_id"] = data["outreach_id"]
            elif data.get("outreach_id") is None and data.get("draft_id") is not None:
                data["outreach_id"] = data["draft_id"]

            if data.get("clipboard_text") is None and data.get("copy_text") is not None:
                data["clipboard_text"] = data["copy_text"]
            elif data.get("copy_text") is None and data.get("clipboard_text") is not None:
                data["copy_text"] = data["clipboard_text"]

            if data.get("mailto_uri") is None and data.get("mailto_url") is not None:
                data["mailto_uri"] = data["mailto_url"]
            elif data.get("mailto_url") is None and data.get("mailto_uri") is not None:
                data["mailto_url"] = data["mailto_uri"]

            if data.get("recruiter_profile_url") is None and data.get("profile_url") is not None:
                data["recruiter_profile_url"] = data["profile_url"]
            elif data.get("profile_url") is None and data.get("recruiter_profile_url") is not None:
                data["profile_url"] = data["recruiter_profile_url"]

            if data.get("handoff_instructions") is None and data.get("instructions") is not None:
                data["handoff_instructions"] = data["instructions"]
            elif data.get("instructions") is None and data.get("handoff_instructions") is not None:
                data["instructions"] = data["handoff_instructions"]
        return data


class RecruiterOutreachListResponse(BaseModel):
    """List of recruiter outreach drafts owned by candidate."""
    model_config = ConfigDict(from_attributes=True)

    drafts: List[RecruiterOutreachResponse]
    total: int
