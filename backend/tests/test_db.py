"""
Tests for Database Session Lifecycle, Base Repository, and Base Service.
"""

import uuid
import pytest
from sqlalchemy import Column, String
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import Base, UUIDMixin, TimestampMixin
from app.repositories.base import BaseRepository
from app.services.base import BaseService
from app.core.exceptions import NotFoundException


class SampleEntity(Base, UUIDMixin, TimestampMixin):
    """Temporary test model for verifying repository and service abstractions."""

    __tablename__ = "test_sample_entities"
    name: str = Column(String(50), nullable=False)


@pytest.mark.asyncio
async def test_repository_and_service_crud(test_session: AsyncSession, test_engine):
    """Verifies that BaseRepository and BaseService execute CRUD correctly."""
    # Create the test table dynamically
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    repo = BaseRepository(SampleEntity, test_session)
    service = BaseService(repo)

    # 1. Create instance
    entity = SampleEntity(name="Test Candidate Record")
    created = await repo.create(entity)
    await test_session.commit()
    assert created.id is not None
    assert created.name == "Test Candidate Record"
    assert created.created_at is not None

    # 2. Get via service
    fetched = await service.get_or_404(created.id)
    assert fetched.id == created.id
    assert fetched.name == "Test Candidate Record"

    # 3. List via service
    items = await service.list_entities()
    assert len(items) >= 1

    # 4. Not found behavior
    random_id = uuid.uuid4()
    with pytest.raises(NotFoundException) as exc_info:
        await service.get_or_404(random_id)
    assert exc_info.value.status_code == 404
    assert str(random_id) in exc_info.value.message
