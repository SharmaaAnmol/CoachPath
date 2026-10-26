"""
CoachPath FastAPI Application Entrypoint.
Initializes middleware, routing, CORS policies, exception handlers, and database lifespans.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.router import api_router
from app.core.config import settings
from app.db.session import close_db_connection
from app.middleware.correlation import CorrelationIdMiddleware
from app.middleware.error_handler import register_exception_handlers

# Configure root logger
logging.basicConfig(
    level=settings.LOG_LEVEL.upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("coachpath.app")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application startup and graceful shutdown lifecycles."""
    logger.info(
        f"Starting {settings.PROJECT_NAME} v{settings.VERSION} "
        f"[{settings.ENVIRONMENT}]..."
    )
    # Ensure diagnostic assessments, skills taxonomy, and roles are seeded in the background
    # Non-blocking background task ensures Uvicorn binds port immediately for fast healthcheck response
    async def _run_baseline_seeding() -> None:
        try:
            from app.db.session import AsyncSessionLocal
            from app.db.seeds.assessment_seeder import seed_diagnostic_assessments
            from app.db.seeds.gap_analysis_seeder import seed_skill_taxonomy_and_roles
            async with AsyncSessionLocal() as db_session:
                await seed_skill_taxonomy_and_roles(db_session)
                await seed_diagnostic_assessments(db_session)
            logger.info("Database baseline seed check completed.")
        except Exception as exc:
            logger.warning("Database baseline auto-seeding skipped: %s", exc)

    import asyncio
    asyncio.create_task(_run_baseline_seeding())

    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}...")
    await close_db_connection()


def create_application() -> FastAPI:
    """Factory function initializing the configured FastAPI application."""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        docs_url=f"{settings.API_V1_PREFIX}/docs" if settings.DEBUG else None,
        redoc_url=f"{settings.API_V1_PREFIX}/redoc" if settings.DEBUG else None,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # 1. Register CORS Middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Process-Time-Ms"],
    )

    # 2. Register Correlation ID & Request Logging Middleware
    application.add_middleware(CorrelationIdMiddleware)

    # 3. Register Centralized RFC 7807 Exception Handlers
    register_exception_handlers(application)

    # 4. Root Welcome Route
    @application.get(
        "/",
        summary="API Root",
        status_code=status.HTTP_200_OK,
        tags=["System Health & Diagnostics"],
    )
    async def root() -> Dict[str, str]:
        return {
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "status": "operational",
            "docs_url": f"{settings.API_V1_PREFIX}/docs",
            "api_v1": settings.API_V1_PREFIX,
        }

    @application.get("/docs", include_in_schema=False)
    async def redirect_to_docs() -> RedirectResponse:
        return RedirectResponse(url=f"{settings.API_V1_PREFIX}/docs")

    @application.get("/redoc", include_in_schema=False)
    async def redirect_to_redoc() -> RedirectResponse:
        return RedirectResponse(url=f"{settings.API_V1_PREFIX}/redoc")

    # 5. Mount API v1 Master Router
    application.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return application


app = create_application()
