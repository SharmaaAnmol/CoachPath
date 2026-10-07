"""
Pytest Fixtures and Test Environment Configuration.
Configures in-memory async SQLite for unit and integration testing.
"""

import os
from typing import AsyncGenerator
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Ensure testing environment variables before importing app
os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["DB_ECHO"] = "false"

from app.core.config import settings
from app.db.session import get_db
from app.main import create_application
from app.models.base import Base


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Creates a temporary in-memory async SQLite engine for each test."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provides a fresh isolated database session for testing."""
    session_maker = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_maker() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(test_session) -> AsyncGenerator[AsyncClient, None]:
    """Provides an AsyncClient bound to the application with overridden DB dependency."""
    app = create_application()

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield test_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
