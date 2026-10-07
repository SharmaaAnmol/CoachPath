"""
Import all models here for Alembic target_metadata detection.
"""

from app.models.base import Base
# Future domain models will be registered here (e.g., User, Profile, Skill, etc.)

__all__ = ["Base"]
