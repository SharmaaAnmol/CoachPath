"""
FastAPI Route Dependencies for CoachPath.
Provides reusable dependency injection for database sessions, settings, and context.
"""

from typing import AsyncGenerator
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_db


def get_current_request_id(request: Request) -> str:
    """Dependency returning the correlation request ID."""
    return getattr(request.state, "request_id", "req_unknown")


async def get_session(
    session: AsyncSession = Depends(get_db),
) -> AsyncGenerator[AsyncSession, None]:
    """Dependency providing an active asynchronous database session."""
    yield session
