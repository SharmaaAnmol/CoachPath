"""
CoachPath FastAPI Application Entrypoint.
Initializes middleware, routing, CORS policies, exception handlers, and database lifespans.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

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
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}...")
    await close_db_connection()


def create_application() -> FastAPI:
    """Factory function initializing the configured FastAPI application."""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        redoc_url=f"{settings.API_V1_PREFIX}/redoc",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
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

    # 5. Mount API v1 Master Router
    application.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return application


app = create_application()
