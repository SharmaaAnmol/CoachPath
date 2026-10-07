"""
Generic Base Repository.
Encapsulates SQLAlchemy database interactions away from service and route layers.
"""

from typing import Generic, List, Optional, Type, TypeVar
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic CRUD repository for SQLAlchemy models."""

    def __init__(self, model: Type[ModelType], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def get_by_id(self, id: uuid.UUID) -> Optional[ModelType]:
        """Fetches a single model instance by primary key."""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalars().first()

    async def list_all(
        self, offset: int = 0, limit: int = 20
    ) -> List[ModelType]:
        """Fetches a paginated list of records."""
        result = await self.session.execute(
            select(self.model).offset(offset).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, instance: ModelType) -> ModelType:
        """Adds and flushes a new model instance."""
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def delete(self, instance: ModelType) -> None:
        """Deletes a model instance from the session."""
        await self.session.delete(instance)
        await self.session.flush()
