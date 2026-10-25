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
                "connect_args": {
                    "timeout": 10,
                    "statement_cache_size": 0,
                },
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


async def get_db_health_details() -> dict:
    """Returns database connection target metadata and sanitized error details if unreachable."""
    import re
    target_info = {
        "dialect": engine.url.drivername,
        "host": engine.url.host,
        "port": engine.url.port,
        "database": engine.url.database,
    }
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            if result.scalar() == 1:
                return {"connected": True, "target": target_info, "error": None}
            return {"connected": False, "target": target_info, "error": "Query returned unexpected result"}
    except Exception as exc:
        err_msg = f"{type(exc).__name__}: {str(exc)}"
        if "@" in err_msg and ":" in err_msg:
            err_msg = re.sub(r':([^@]+)@', ':***@', err_msg)
        return {"connected": False, "target": target_info, "error": err_msg}


async def close_db_connection() -> None:
    """Gracefully closes all connection pools on application shutdown."""
    logger.info("Closing database connection pool...")
    await engine.dispose()
    logger.info("Database connection pool closed.")
