from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.db import init_db
from app.routers import (
    auth,
    onboarding,
    assessments,
    gap,
    roadmap,
    market,
    jobs,
    resume,
    applications,
    outreach,
    interviews,
    readiness,
    privacy
)

# Initialize database schema
init_db()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION
)

# CORS configuration for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all feature routers
app.include_router(auth.router)
app.include_router(onboarding.router)
app.include_router(assessments.router)
app.include_router(gap.router)
app.include_router(roadmap.router)
app.include_router(market.router)
app.include_router(jobs.router)
app.include_router(resume.router)
app.include_router(applications.router)
app.include_router(outreach.router)
app.include_router(interviews.router)
app.include_router(readiness.router)
app.include_router(privacy.router)

@app.get("/health")
def health_check():
    """System health check and Bharat Hackathon deployment status."""
    return {
        "status": "healthy",
        "service": "CoachPath API",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)
