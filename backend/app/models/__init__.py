"""
Model registry package for CoachPath.
All domain models are exported here to ensure clean mapper initialization
and complete Alembic metadata discovery.
"""

from app.models.applications import (
    Application,
    ApplicationStatusHistory,
    Interview,
    InterviewPreparation,
    InterviewQuestion,
    Recruiter,
    RecruiterContact,
    RecruiterMessage,
)
from app.models.assessments import (
    Assessment,
    AssessmentAnswer,
    AssessmentAttempt,
    AssessmentQuestion,
    AssessmentResult,
)
from app.models.audit import ActivityLog, AuditLog
from app.models.auth import User, UserProfile, UserSession
from app.models.base import (
    Base,
    Inet,
    JsonB,
    StringArray,
    TextArray,
    TimestampMixin,
    UUIDMixin,
    VectorType,
    utc_now,
)
from app.models.career import (
    CareerProfile,
    Certification,
    Education,
    Experience,
    Project,
    Role,
)
from app.models.jobs import Job, JobMatch, JobSkill
from app.models.readiness import CareerReadinessScore
from app.models.resume import Resume, ResumeVersion
from app.models.roadmap import Roadmap, RoadmapPhase, RoadmapTask
from app.models.skills import RoleRequirement, Skill, SkillGap, UserSkill

__all__ = [
    # Base and Mixins
    "Base",
    "UUIDMixin",
    "TimestampMixin",
    "StringArray",
    "TextArray",
    "JsonB",
    "Inet",
    "VectorType",
    "utc_now",
    # Auth Domain
    "User",
    "UserProfile",
    "UserSession",
    # Career Domain
    "Role",
    "CareerProfile",
    "Education",
    "Experience",
    "Project",
    "Certification",
    # Skills Domain
    "Skill",
    "RoleRequirement",
    "UserSkill",
    "SkillGap",
    # Assessments Domain
    "Assessment",
    "AssessmentQuestion",
    "AssessmentAttempt",
    "AssessmentAnswer",
    "AssessmentResult",
    # Roadmap Domain
    "Roadmap",
    "RoadmapPhase",
    "RoadmapTask",
    # Jobs Domain
    "Job",
    "JobSkill",
    "JobMatch",
    # Resume Domain
    "Resume",
    "ResumeVersion",
    # Applications Domain
    "Application",
    "ApplicationStatusHistory",
    "Recruiter",
    "RecruiterContact",
    "RecruiterMessage",
    "Interview",
    "InterviewQuestion",
    "InterviewPreparation",
    # Readiness Domain
    "CareerReadinessScore",
    # Audit Domain
    "ActivityLog",
    "AuditLog",
]
