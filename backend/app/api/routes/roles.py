"""
Role Benchmark Catalog API Routes.
Provides endpoints for retrieving canonical target roles and their curated requirements.
"""

from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_session
from app.schemas.skill_gap import (
    RoleDetailResponse,
    RoleListResponse,
    RoleRequirementResponse,
)
from app.services.skill_gap_engine import SkillGapEngine

router = APIRouter(prefix="/roles", tags=["Group 6: Roles & Skills"])
_engine = SkillGapEngine()


@router.get(
    "",
    response_model=RoleListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Supported Target Roles",
    description="Retrieves all canonical benchmark target roles supported by CoachPath with requirement summaries.",
)
async def list_roles(
    db: AsyncSession = Depends(get_session),
) -> RoleListResponse:
    """Returns all supported canonical target roles."""
    return await _engine.get_roles(db=db)


@router.get(
    "/{role_id}",
    response_model=RoleDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Target Role Details",
    description="Retrieves a specific canonical target role with full requirement specifications.",
)
async def get_role(
    role_id: str,
    db: AsyncSession = Depends(get_session),
) -> RoleDetailResponse:
    """Returns role details with full requirement specifications."""
    return await _engine.get_role(role_id=role_id, db=db)


@router.get(
    "/{role_id}/requirements",
    response_model=List[RoleRequirementResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Role Requirements",
    description="Retrieves the curated skill requirements, weights, and rationales for a specific role.",
)
async def get_role_requirements(
    role_id: str,
    db: AsyncSession = Depends(get_session),
) -> List[RoleRequirementResponse]:
    """Returns curated skill requirements for the specified role."""
    role = await _engine.get_role(role_id=role_id, db=db)
    return role.requirements
