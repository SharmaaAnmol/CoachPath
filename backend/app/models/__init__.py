"""
Model registry package for CoachPath.
All future models must be imported here so Alembic can detect them automatically.
"""

from app.models.base import Base, UUIDMixin, TimestampMixin

__all__ = ["Base", "UUIDMixin", "TimestampMixin"]
