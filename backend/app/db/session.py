"""
Database Engine and Async Session Management.
Provides connection pooling, session lifecycle dependency, and readiness probes.
"""

from typing import AsyncGenerator
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.core.config import settings

logger = logging.getLogger(__name__)


def create_engine_instance(database_url: str) -> AsyncEngine:
    """Creates a configured AsyncEngine instance based on database URL scheme."""
    is_sqlite = database_url.startswith("sqlite")

    engine_kwargs = {
        "echo": settings.DB_ECHO,
        "future": True,
    }

    if not is_sqlite:
        engine_kwargs.update(
            {
                "pool_size": settings.DB_POOL_SIZE,
                "max_overflow": settings.DB_MAX_OVERFLOW,
                "pool_timeout": settings.DB_POOL_TIMEOUT,
                "pool_recycle": settings.DB_POOL_RECYCLE,
                "pool_pre_ping": True,
            }
        )

    return create_async_engine(database_url, **engine_kwargs)


# Global async engine and session factory
engine: AsyncEngine = create_engine_instance(settings.DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an active database session.
    Automatically commits or rolls back on exceptions and closes session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_db_connectivity() -> bool:
    """
    Executes a lightweight query (SELECT 1) to verify database connectivity.
    Returns True if database is reachable, False otherwise.
    """
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as exc:
        logger.warning(f"Database connectivity check failed: {exc}")
        return False


async def close_db_connection() -> None:
    """Gracefully closes all connection pools on application shutdown."""
    logger.info("Closing database connection pool...")
    await engine.dispose()
    logger.info("Database connection pool closed.")
