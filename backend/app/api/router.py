"""
Master API Router for CoachPath v1.
Assembles all domain routers under the /api/v1 prefix.
"""

from fastapi import APIRouter

from app.api.routes import (
    health,
    auth,
    profile,
    onboarding,
    resume,
    assessments,
    skills,
    roadmap,
    jobs,
    applications,
    recruiters,
    interviews,
    readiness,
    dashboard,
    settings,
)

api_router = APIRouter()

# Health & Infrastructure (Active in Phase 2A)
api_router.include_router(health.router)

# Domain Routers (Structural Placeholders for Phases 3-16)
api_router.include_router(auth.router)
api_router.include_router(profile.router)
api_router.include_router(onboarding.router)
api_router.include_router(resume.router)
api_router.include_router(assessments.router)
api_router.include_router(skills.router)
api_router.include_router(roadmap.router)
api_router.include_router(jobs.router)
api_router.include_router(applications.router)
api_router.include_router(recruiters.router)
api_router.include_router(interviews.router)
api_router.include_router(readiness.router)
api_router.include_router(dashboard.router)
api_router.include_router(settings.router)
