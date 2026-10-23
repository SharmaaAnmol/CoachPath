"""
Career Profile & Evidence Graph Router for CoachPath.
Implements authenticated master profile viewing and editing, career goals calibration,
and scoped CRUD for education, experience, projects, and certifications matching /docs/api-specification.md Group 3.
"""

from __future__ import annotations

import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_session
from app.models.auth import User
from app.schemas.profile import (
    CareerGoalsResponse,
    CareerGoalsUpdate,
    CareerProfileMasterResponse,
    CertificationCreate,
    CertificationResponse,
    CertificationUpdate,
    EducationCreate,
    EducationResponse,
    EducationUpdate,
    ExperienceCreate,
    ExperienceResponse,
    ExperienceUpdate,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    RoleResponse,
    UserProfileUpdate,
)
from app.services.profile import profile_service

router = APIRouter(prefix="/profile", tags=["Group 3: Career Profile"])


# ---------------------------------------------------------------------------
# Master Profile & Personal Metadata
# ---------------------------------------------------------------------------

@router.get(
    "",
    response_model=CareerProfileMasterResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Central Career Profile",
    description="Retrieves the consolidated career profile, personal metadata, and evidence graph for the authenticated candidate.",
)
async def get_master_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> CareerProfileMasterResponse:
    """Returns the authenticated candidate's career profile."""
    return await profile_service.get_master_profile(db=db, user=current_user)


@router.put(
    "",
    response_model=CareerProfileMasterResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Personal Profile Details",
    description="Updates candidate demographic information, headline, location, contact, and public portfolio links.",
)
async def update_personal_profile(
    payload: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> CareerProfileMasterResponse:
    """Updates candidate personal profile and returns master view."""
    return await profile_service.update_user_profile(
        db=db, user=current_user, payload=payload
    )


# ---------------------------------------------------------------------------
# Career Goals
# ---------------------------------------------------------------------------

@router.get(
    "/career-goals",
    response_model=CareerGoalsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Career Goals",
    description="Retrieves active target benchmark roles, stage, workplace preferences, and target metropolitan markets.",
)
async def get_career_goals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> CareerGoalsResponse:
    """Returns candidate's target career goals."""
    return await profile_service.get_career_goals(db=db, user=current_user)


@router.put(
    "/career-goals",
    response_model=CareerGoalsResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Career Goals",
    description="Updates primary and secondary target benchmark roles, stage, work preferences, and locations.",
)
async def update_career_goals(
    payload: CareerGoalsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> CareerGoalsResponse:
    """Calibrates candidate target roles and preferences."""
    return await profile_service.update_career_goals(
        db=db, user=current_user, payload=payload
    )


@router.get(
    "/roles",
    response_model=List[RoleResponse],
    status_code=status.HTTP_200_OK,
    summary="List Supported Target Roles",
    description="Retrieves the canonical benchmark roles supported by CoachPath.",
)
async def list_supported_roles(
    db: AsyncSession = Depends(get_session),
) -> List[RoleResponse]:
    """Returns canonical benchmark roles."""
    return await profile_service.list_roles(db=db)


# ---------------------------------------------------------------------------
# Education CRUD
# ---------------------------------------------------------------------------

@router.get(
    "/education",
    response_model=List[EducationResponse],
    status_code=status.HTTP_200_OK,
    summary="List Education Entries",
    description="Retrieves all academic credentials for the authenticated candidate ordered chronologically.",
)
async def list_education(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> List[EducationResponse]:
    return await profile_service.list_education(db=db, user=current_user)


@router.post(
    "/education",
    response_model=EducationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Academic Credential",
    description="Adds a new degree, university, or program of study to the candidate's career profile.",
)
async def create_education(
    payload: EducationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> EducationResponse:
    return await profile_service.create_education(
        db=db, user=current_user, payload=payload
    )


@router.put(
    "/education/{education_id}",
    response_model=EducationResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Academic Credential",
    description="Modifies an existing academic credential belonging to the authenticated candidate.",
)
async def update_education(
    education_id: uuid.UUID,
    payload: EducationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> EducationResponse:
    return await profile_service.update_education(
        db=db, user=current_user, education_id=education_id, payload=payload
    )


@router.delete(
    "/education/{education_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Academic Credential",
    description="Deletes an academic credential belonging to the authenticated candidate.",
)
async def delete_education(
    education_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> None:
    await profile_service.delete_education(
        db=db, user=current_user, education_id=education_id
    )


# ---------------------------------------------------------------------------
# Experience CRUD
# ---------------------------------------------------------------------------

@router.get(
    "/experience",
    response_model=List[ExperienceResponse],
    status_code=status.HTTP_200_OK,
    summary="List Experience Entries",
    description="Retrieves all employment and internship history entries for the authenticated candidate.",
)
async def list_experience(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> List[ExperienceResponse]:
    return await profile_service.list_experience(db=db, user=current_user)


@router.post(
    "/experience",
    response_model=ExperienceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Experience Entry",
    description="Adds a new employment, internship, or work experience record to the profile.",
)
async def create_experience(
    payload: ExperienceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> ExperienceResponse:
    return await profile_service.create_experience(
        db=db, user=current_user, payload=payload
    )


@router.put(
    "/experience/{experience_id}",
    response_model=ExperienceResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Experience Entry",
    description="Modifies an existing work experience record belonging to the authenticated candidate.",
)
async def update_experience(
    experience_id: uuid.UUID,
    payload: ExperienceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> ExperienceResponse:
    return await profile_service.update_experience(
        db=db, user=current_user, experience_id=experience_id, payload=payload
    )


@router.delete(
    "/experience/{experience_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Experience Entry",
    description="Deletes a work experience record belonging to the authenticated candidate.",
)
async def delete_experience(
    experience_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> None:
    await profile_service.delete_experience(
        db=db, user=current_user, experience_id=experience_id
    )


# ---------------------------------------------------------------------------
# Projects CRUD
# ---------------------------------------------------------------------------

@router.get(
    "/projects",
    response_model=List[ProjectResponse],
    status_code=status.HTTP_200_OK,
    summary="List Technical Projects",
    description="Retrieves all software projects, capstones, and open-source artifacts for the candidate.",
)
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> List[ProjectResponse]:
    return await profile_service.list_projects(db=db, user=current_user)


@router.post(
    "/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Technical Project",
    description="Adds a technical software project to the candidate's career profile.",
)
async def create_project(
    payload: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> ProjectResponse:
    return await profile_service.create_project(
        db=db, user=current_user, payload=payload
    )


@router.put(
    "/projects/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Technical Project",
    description="Modifies an existing software project belonging to the authenticated candidate.",
)
async def update_project(
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> ProjectResponse:
    return await profile_service.update_project(
        db=db, user=current_user, project_id=project_id, payload=payload
    )


@router.delete(
    "/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Technical Project",
    description="Deletes a software project belonging to the authenticated candidate.",
)
async def delete_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> None:
    await profile_service.delete_project(
        db=db, user=current_user, project_id=project_id
    )


# ---------------------------------------------------------------------------
# Certifications CRUD
# ---------------------------------------------------------------------------

@router.get(
    "/certifications",
    response_model=List[CertificationResponse],
    status_code=status.HTTP_200_OK,
    summary="List Certifications",
    description="Retrieves all professional credentials and certificates for the authenticated candidate.",
)
async def list_certifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> List[CertificationResponse]:
    return await profile_service.list_certifications(db=db, user=current_user)


@router.post(
    "/certifications",
    response_model=CertificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Certification",
    description="Adds a professional certification or credential to the candidate's profile.",
)
async def create_certification(
    payload: CertificationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> CertificationResponse:
    return await profile_service.create_certification(
        db=db, user=current_user, payload=payload
    )


@router.put(
    "/certifications/{cert_id}",
    response_model=CertificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Certification",
    description="Modifies an existing certification belonging to the authenticated candidate.",
)
async def update_certification(
    cert_id: uuid.UUID,
    payload: CertificationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> CertificationResponse:
    return await profile_service.update_certification(
        db=db, user=current_user, cert_id=cert_id, payload=payload
    )


@router.delete(
    "/certifications/{cert_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Certification",
    description="Deletes a certification belonging to the authenticated candidate.",
)
async def delete_certification(
    cert_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> None:
    await profile_service.delete_certification(
        db=db, user=current_user, cert_id=cert_id
    )
