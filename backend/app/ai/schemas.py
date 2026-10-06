from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class OnboardingMessageRequest(BaseModel):
    user_id: str
    message: str
    step: int = 1
    current_profile: Dict[str, Any] = Field(default_factory=dict)

class OnboardingStepResponse(BaseModel):
    next_question: str
    extracted_fields: Dict[str, Any]
    progress_step: int
    total_steps: int = 11
    quick_replies: List[str] = Field(default_factory=list)
    is_complete: bool = False

class AssessmentQuestion(BaseModel):
    id: str
    qtype: str # mcq, bug_fix, code, sql
    prompt: str
    dimension: str # Knowledge, Problem Solving, Practical Skills, Industry Readiness
    options: Optional[List[str]] = None
    code_template: Optional[str] = None
    answer_key: Optional[str] = None
    explanation: Optional[str] = None

class AssessmentAnswerSubmission(BaseModel):
    user_id: str
    assessment_id: str
    question_id: str
    user_answer: str

class AssessmentGradingResult(BaseModel):
    score: int # 0 - 100
    dimension_scores: Dict[str, int] # Knowledge, Problem Solving, Practical Skills, Industry Readiness
    assessed_level: str # beginner, intermediate, advanced
    feedback: str
    strengths: List[str]
    growth_areas: List[str]

class ResumeTailorRequest(BaseModel):
    user_id: str
    job_id: str
    target_role_variant: Optional[str] = None # e.g. "ML Engineer", "Data Scientist", "AI Engineer"

class ResumeTailorResponse(BaseModel):
    resume_id: str
    variant: str
    tailored_content: Dict[str, Any]
    ats_score: int
    diff_summary: Dict[str, List[str]] # reworded, reordered, untouched
    truthfulness_verified: bool
    verified_claims_count: int
    missing_skills_to_learn: List[str]

class OutreachDraftRequest(BaseModel):
    user_id: str
    application_id: str
    recruiter_name: Optional[str] = "Hiring Team"
    recruiter_role: Optional[str] = "Technical Recruiter"
    channel: str = "LinkedIn"

class OutreachDraftResponse(BaseModel):
    draft_id: str
    message: str
    word_count: int
    highlighted_skills: List[str]
    status: str = "draft" # awaiting user approval

class ApplicationPrepareRequest(BaseModel):
    user_id: str
    job_id: str

class ApplicationPackageResponse(BaseModel):
    application_id: str
    job_title: str
    company: str
    apply_url: str
    tailored_resume_version: str
    cover_note: str
    screening_qna: List[Dict[str, str]]
    status: str # "pending_user_approval"
