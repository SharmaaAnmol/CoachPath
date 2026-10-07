"""
Generic Base Service.
Encapsulates business logic, domain rules, and orchestrates repository calls.
"""

from typing import Generic, List, Optional, TypeVar
import uuid
from app.core.exceptions import NotFoundException
from app.models.base import Base
from app.repositories.base import BaseRepository

ModelType = TypeVar("ModelType", bound=Base)


class BaseService(Generic[ModelType]):
    """Base application service implementing common domain logic."""

    def __init__(self, repository: BaseRepository[ModelType]) -> None:
        self.repository = repository

    async def get_or_404(self, id: uuid.UUID) -> ModelType:
        """Retrieves an entity by ID or raises standard NotFoundException."""
        entity = await self.repository.get_by_id(id)
        if not entity:
            raise NotFoundException(
                resource=self.repository.model.__name__,
                identifier=str(id),
            )
        return entity

    async def list_entities(
        self, offset: int = 0, limit: int = 20
    ) -> List[ModelType]:
        """Lists entities with pagination."""
        return await self.repository.list_all(offset=offset, limit=limit)
