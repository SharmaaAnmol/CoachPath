"""
Central Career Profile Service.
Implements personal details updates, career target goal calibration,
deterministic profile completeness scoring, and scoped CRUD for academic,
employment, project, and certification evidence graphs.
"""

from __future__ import annotations

import decimal
import uuid
from typing import List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import (
    ForbiddenException,
    NotFoundException,
    ValidationException,
)
from app.models.auth import User, UserProfile
from app.models.career import (
    CareerProfile,
    Certification,
    Education,
    Experience,
    Project,
    Role,
)
from app.models.skills import UserSkill
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


def calculate_profile_completeness(
    profile: Optional[UserProfile],
    career_profile: Optional[CareerProfile],
) -> float:
    """
    Computes deterministic profile completeness score (0.0 to 100.0%).
    Pure deterministic logic with zero LLM dependency.

    Section Weights:
    1. Personal Details (20.0 pts):
       - full_name present: 5.0
       - headline present: 5.0
       - location present: 5.0
       - bio OR contact link (linkedin/github/portfolio): 5.0
    2. Career Goals & Targets (20.0 pts):
       - primary target role selected: 10.0
       - career stage selected: 5.0
       - work preference or locations specified: 5.0
    3. Education History (20.0 pts):
       - at least 1 academic credential: 20.0
    4. Work Experience (20.0 pts):
       - at least 1 employment record: 20.0
    5. Technical Projects (15.0 pts):
       - at least 1 technical artifact/project: 15.0
    6. Certifications & Credentials (5.0 pts):
       - at least 1 professional certification: 5.0
    """
    score = 0.0

    # 1. Personal Details (20.0 pts)
    if profile:
        if profile.full_name and profile.full_name.strip():
            score += 5.0
        if profile.headline and profile.headline.strip():
            score += 5.0
        if profile.location and profile.location.strip():
            score += 5.0
        has_bio_or_links = (
            bool(profile.bio and profile.bio.strip())
            or bool(profile.linkedin_url and profile.linkedin_url.strip())
            or bool(profile.github_url and profile.github_url.strip())
            or bool(profile.portfolio_url and profile.portfolio_url.strip())
        )
        if has_bio_or_links:
            score += 5.0

    # 2. Career Targets (20.0 pts)
    if career_profile:
        if career_profile.primary_role_id:
            score += 10.0
        if career_profile.career_stage:
            score += 5.0
        if career_profile.work_preference or (
            career_profile.target_locations and len(career_profile.target_locations) > 0
        ):
            score += 5.0

        # 3. Education (20.0 pts)
        if career_profile.education and len(career_profile.education) > 0:
            score += 20.0

        # 4. Work Experience (20.0 pts)
        if career_profile.experience and len(career_profile.experience) > 0:
            score += 20.0

        # 5. Projects (15.0 pts)
        if career_profile.projects and len(career_profile.projects) > 0:
            score += 15.0

        # 6. Certifications (5.0 pts)
        if career_profile.certifications and len(career_profile.certifications) > 0:
            score += 5.0

    return round(min(score, 100.0), 1)


class ProfileService:
    """Service handling personal profile details, career targets, and evidence graphs."""

    async def get_or_create_career_profile(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> CareerProfile:
        """
        Retrieves active CareerProfile with eagerly joined evidence relations,
        or establishes a baseline career profile if one has not yet been provisioned.
        """
        stmt = (
            select(CareerProfile)
            .options(
                selectinload(CareerProfile.primary_role),
                selectinload(CareerProfile.secondary_role),
                selectinload(CareerProfile.education),
                selectinload(CareerProfile.experience),
                selectinload(CareerProfile.projects),
                selectinload(CareerProfile.certifications),
                selectinload(CareerProfile.user_skills),
            )
            .where(CareerProfile.user_id == user_id)
        )
        career_profile = await db.scalar(stmt)
        if career_profile is not None:
            return career_profile

        # Ensure default role exists
        default_role_id = "backend-developer"
        role = await db.scalar(select(Role).where(Role.id == default_role_id))
        if role is None:
            role = await db.scalar(select(Role))
            if role is None:
                role = Role(
                    id="backend-developer",
                    title="Backend Developer",
                    description="Server-side web applications and scalable APIs.",
                    category="engineering",
                )
                db.add(role)
                await db.flush()
            default_role_id = role.id

        career_profile = CareerProfile(
            user_id=user_id,
            primary_role_id=default_role_id,
            career_stage="student",
            work_preference="hybrid",
            target_locations=["Remote"],
            years_of_experience=decimal.Decimal("0.0"),
        )
        db.add(career_profile)
        await db.commit()

        # Re-fetch with loaded relationships
        return await db.scalar(stmt)

    async def get_master_profile(
        self, db: AsyncSession, user: User
    ) -> CareerProfileMasterResponse:
        """
        Returns consolidated master career profile view including completeness score
        and verified evidence graph.
        """
        # Ensure user profile exists
        user_profile = await db.scalar(
            select(UserProfile).where(UserProfile.user_id == user.id)
        )
        if user_profile is None:
            user_profile = UserProfile(
                user_id=user.id,
                full_name=user.email.split("@")[0].capitalize(),
            )
            db.add(user_profile)
            await db.commit()
            await db.refresh(user_profile)

        career_profile = await self.get_or_create_career_profile(db, user.id)
        completeness = calculate_profile_completeness(user_profile, career_profile)

        # Count verified skills
        verified_count = sum(
            1
            for s in career_profile.user_skills
            if getattr(s, "verification_status", None) == "verified"
            or getattr(s, "confidence_score", 0) >= 70.0
        )

        return CareerProfileMasterResponse(
            profile_id=career_profile.id,
            user_id=user.id,
            email=user.email,
            full_name=user_profile.full_name,
            headline=user_profile.headline,
            location=user_profile.location,
            phone_number=user_profile.phone_number,
            linkedin_url=user_profile.linkedin_url,
            github_url=user_profile.github_url,
            portfolio_url=user_profile.portfolio_url,
            bio=user_profile.bio,
            career_stage=career_profile.career_stage,
            primary_role=RoleResponse.model_validate(career_profile.primary_role)
            if career_profile.primary_role
            else None,
            secondary_role=RoleResponse.model_validate(career_profile.secondary_role)
            if career_profile.secondary_role
            else None,
            work_preference=career_profile.work_preference,
            target_locations=list(career_profile.target_locations or []),
            years_of_experience=float(career_profile.years_of_experience or 0.0),
            education=[EducationResponse.model_validate(e) for e in career_profile.education],
            experience=[ExperienceResponse.model_validate(e) for e in career_profile.experience],
            projects=[ProjectResponse.model_validate(p) for p in career_profile.projects],
            certifications=[
                CertificationResponse.model_validate(c) for c in career_profile.certifications
            ],
            verified_skills_count=verified_count,
            completeness_score=completeness,
        )

    async def update_user_profile(
        self, db: AsyncSession, user: User, payload: UserProfileUpdate
    ) -> CareerProfileMasterResponse:
        """Updates personal demographic and social links."""
        user_profile = await db.scalar(
            select(UserProfile).where(UserProfile.user_id == user.id)
        )
        if user_profile is None:
            user_profile = UserProfile(
                user_id=user.id,
                full_name=payload.full_name or user.email.split("@")[0].capitalize(),
            )
            db.add(user_profile)

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user_profile, field, value)

        await db.commit()
        return await self.get_master_profile(db, user)

    async def get_career_goals(
        self, db: AsyncSession, user: User
    ) -> CareerGoalsResponse:
        """Retrieves candidate's primary and secondary career targets."""
        career_profile = await self.get_or_create_career_profile(db, user.id)
        return CareerGoalsResponse(
            primary_role=RoleResponse.model_validate(career_profile.primary_role)
            if career_profile.primary_role
            else None,
            secondary_role=RoleResponse.model_validate(career_profile.secondary_role)
            if career_profile.secondary_role
            else None,
            career_stage=career_profile.career_stage,
            work_preference=career_profile.work_preference,
            target_locations=list(career_profile.target_locations or []),
            years_of_experience=float(career_profile.years_of_experience or 0.0),
        )

    async def update_career_goals(
        self, db: AsyncSession, user: User, payload: CareerGoalsUpdate
    ) -> CareerGoalsResponse:
        """Updates target roles, stage, and location preferences."""
        # 1. Validate primary role
        primary_role = await db.scalar(select(Role).where(Role.id == payload.primary_role_id))
        if primary_role is None:
            raise ValidationException(f"Invalid primary role '{payload.primary_role_id}'.")

        # 2. Validate secondary role if provided
        if payload.secondary_role_id:
            secondary_role = await db.scalar(
                select(Role).where(Role.id == payload.secondary_role_id)
            )
            if secondary_role is None:
                raise ValidationException(f"Invalid secondary role '{payload.secondary_role_id}'.")

        career_profile = await self.get_or_create_career_profile(db, user.id)
        career_profile.primary_role_id = payload.primary_role_id
        career_profile.secondary_role_id = payload.secondary_role_id
        career_profile.career_stage = payload.career_stage
        career_profile.work_preference = payload.work_preference
        career_profile.target_locations = payload.target_locations
        career_profile.years_of_experience = decimal.Decimal(str(payload.years_of_experience))

        await db.commit()
        return await self.get_career_goals(db, user)

    async def list_roles(self, db: AsyncSession) -> List[RoleResponse]:
        """Returns all canonical benchmark roles supported by CoachPath."""
        roles = (await db.scalars(select(Role).order_by(Role.title))).all()
        if not roles:
            default_roles = [
                Role(id="backend-developer", title="Backend Developer", category="engineering", description="Architects server-side applications and distributed systems."),
                Role(id="frontend-developer", title="Frontend Developer", category="engineering", description="Engineers client-side applications and responsive user interfaces."),
                Role(id="fullstack-developer", title="Full Stack Developer", category="engineering", description="Builds end-to-end features spanning client, server, and database."),
                Role(id="ai-engineer", title="AI Engineer", category="ai", description="Develops production AI systems, LLM agent workflows, and RAG pipelines."),
                Role(id="devops-cloud-engineer", title="DevOps & Cloud Engineer", category="infrastructure", description="Automates delivery pipelines and manages cloud infrastructure."),
                Role(id="data-engineer", title="Data Engineer", category="data", description="Designs large-scale data ingestion and transformation pipelines."),
            ]
            for r in default_roles:
                db.add(r)
            await db.commit()
            roles = (await db.scalars(select(Role).order_by(Role.title))).all()
        return [RoleResponse.model_validate(r) for r in roles]

    # -----------------------------------------------------------------------
    # Education CRUD
    # -----------------------------------------------------------------------

    async def list_education(
        self, db: AsyncSession, user: User
    ) -> List[EducationResponse]:
        career_profile = await self.get_or_create_career_profile(db, user.id)
        stmt = (
            select(Education)
            .where(Education.career_profile_id == career_profile.id)
            .order_by(Education.start_date.desc())
        )
        items = (await db.scalars(stmt)).all()
        return [EducationResponse.model_validate(i) for i in items]

    async def create_education(
        self, db: AsyncSession, user: User, payload: EducationCreate
    ) -> EducationResponse:
        career_profile = await self.get_or_create_career_profile(db, user.id)
        item = Education(
            career_profile_id=career_profile.id,
            institution_name=payload.institution_name,
            degree=payload.degree,
            field_of_study=payload.field_of_study,
            start_date=payload.start_date,
            end_date=payload.end_date,
            is_current=payload.is_current,
            gpa=decimal.Decimal(str(payload.gpa)) if payload.gpa is not None else None,
        )
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return EducationResponse.model_validate(item)

    async def update_education(
        self, db: AsyncSession, user: User, education_id: uuid.UUID, payload: EducationUpdate
    ) -> EducationResponse:
        career_profile = await self.get_or_create_career_profile(db, user.id)
        item = await db.scalar(select(Education).where(Education.id == education_id))
        if item is None:
            raise NotFoundException(resource="Education", identifier=education_id)
        if item.career_profile_id != career_profile.id:
            raise ForbiddenException("You do not have permission to modify this record.")

        update_data = payload.model_dump(exclude_unset=True)
        if "gpa" in update_data and update_data["gpa"] is not None:
            update_data["gpa"] = decimal.Decimal(str(update_data["gpa"]))

        for field, value in update_data.items():
            setattr(item, field, value)

        # Enforce date order after update
        if item.end_date and item.start_date and item.end_date < item.start_date:
            raise ValidationException("End date cannot precede start date.")

        await db.commit()
        await db.refresh(item)
        return EducationResponse.model_validate(item)

    async def delete_education(
        self, db: AsyncSession, user: User, education_id: uuid.UUID
    ) -> None:
        career_profile = await self.get_or_create_career_profile(db, user.id)
        item = await db.scalar(select(Education).where(Education.id == education_id))
        if item is None:
            raise NotFoundException(resource="Education", identifier=education_id)
        if item.career_profile_id != career_profile.id:
            raise ForbiddenException("You do not have permission to delete this record.")

        await db.delete(item)
        await db.commit()

    # -----------------------------------------------------------------------
    # Experience CRUD
    # -----------------------------------------------------------------------

    async def list_experience(
        self, db: AsyncSession, user: User
    ) -> List[ExperienceResponse]:
        career_profile = await self.get_or_create_career_profile(db, user.id)
        stmt = (
            select(Experience)
            .where(Experience.career_profile_id == career_profile.id)
            .order_by(Experience.start_date.desc())
        )
        items = (await db.scalars(stmt)).all()
        return [ExperienceResponse.model_validate(i) for i in items]

    async def create_experience(
        self, db: AsyncSession, user: User, payload: ExperienceCreate
    ) -> ExperienceResponse:
        career_profile = await self.get_or_create_career_profile(db, user.id)
        item = Experience(
            career_profile_id=career_profile.id,
            company_name=payload.company_name,
            role_title=payload.role_title,
            location=payload.location,
            start_date=payload.start_date,
            end_date=payload.end_date,
            is_current=payload.is_current,
            bullet_points=payload.bullet_points,
        )
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return ExperienceResponse.model_validate(item)

    async def update_experience(
        self, db: AsyncSession, user: User, experience_id: uuid.UUID, payload: ExperienceUpdate
    ) -> ExperienceResponse:
        career_profile = await self.get_or_create_career_profile(db, user.id)
        item = await db.scalar(select(Experience).where(Experience.id == experience_id))
        if item is None:
            raise NotFoundException(resource="Experience", identifier=experience_id)
        if item.career_profile_id != career_profile.id:
            raise ForbiddenException("You do not have permission to modify this record.")

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)

        if item.end_date and item.start_date and item.end_date < item.start_date:
            raise ValidationException("End date cannot precede start date.")

        await db.commit()
        await db.refresh(item)
        return ExperienceResponse.model_validate(item)

    async def delete_experience(
        self, db: AsyncSession, user: User, experience_id: uuid.UUID
    ) -> None:
        career_profile = await self.get_or_create_career_profile(db, user.id)
        item = await db.scalar(select(Experience).where(Experience.id == experience_id))
        if item is None:
            raise NotFoundException(resource="Experience", identifier=experience_id)
        if item.career_profile_id != career_profile.id:
            raise ForbiddenException("You do not have permission to delete this record.")

        await db.delete(item)
        await db.commit()

    # -----------------------------------------------------------------------
    # Projects CRUD
    # -----------------------------------------------------------------------

    async def list_projects(
        self, db: AsyncSession, user: User
    ) -> List[ProjectResponse]:
        career_profile = await self.get_or_create_career_profile(db, user.id)
        stmt = (
            select(Project)
            .where(Project.career_profile_id == career_profile.id)
            .order_by(Project.created_at.desc())
        )
        items = (await db.scalars(stmt)).all()
        return [ProjectResponse.model_validate(i) for i in items]

    async def create_project(
        self, db: AsyncSession, user: User, payload: ProjectCreate
    ) -> ProjectResponse:
        career_profile = await self.get_or_create_career_profile(db, user.id)
        item = Project(
            career_profile_id=career_profile.id,
            title=payload.title,
            description=payload.description,
            technologies=payload.technologies,
            github_url=payload.github_url,
            live_url=payload.live_url,
            bullet_points=payload.bullet_points,
        )
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return ProjectResponse.model_validate(item)

    async def update_project(
        self, db: AsyncSession, user: User, project_id: uuid.UUID, payload: ProjectUpdate
    ) -> ProjectResponse:
        career_profile = await self.get_or_create_career_profile(db, user.id)
        item = await db.scalar(select(Project).where(Project.id == project_id))
        if item is None:
            raise NotFoundException(resource="Project", identifier=project_id)
        if item.career_profile_id != career_profile.id:
            raise ForbiddenException("You do not have permission to modify this record.")

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)

        await db.commit()
        await db.refresh(item)
        return ProjectResponse.model_validate(item)

    async def delete_project(
        self, db: AsyncSession, user: User, project_id: uuid.UUID
    ) -> None:
        career_profile = await self.get_or_create_career_profile(db, user.id)
        item = await db.scalar(select(Project).where(Project.id == project_id))
        if item is None:
            raise NotFoundException(resource="Project", identifier=project_id)
        if item.career_profile_id != career_profile.id:
            raise ForbiddenException("You do not have permission to delete this record.")

        await db.delete(item)
        await db.commit()

    # -----------------------------------------------------------------------
    # Certifications CRUD
    # -----------------------------------------------------------------------

    async def list_certifications(
        self, db: AsyncSession, user: User
    ) -> List[CertificationResponse]:
        career_profile = await self.get_or_create_career_profile(db, user.id)
        stmt = (
            select(Certification)
            .where(Certification.career_profile_id == career_profile.id)
            .order_by(Certification.issue_date.desc())
        )
        items = (await db.scalars(stmt)).all()
        return [CertificationResponse.model_validate(i) for i in items]

    async def create_certification(
        self, db: AsyncSession, user: User, payload: CertificationCreate
    ) -> CertificationResponse:
        career_profile = await self.get_or_create_career_profile(db, user.id)
        item = Certification(
            career_profile_id=career_profile.id,
            name=payload.name,
            issuing_organization=payload.issuing_organization,
            issue_date=payload.issue_date,
            expiration_date=payload.expiration_date,
            credential_id=payload.credential_id,
            credential_url=payload.credential_url,
        )
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return CertificationResponse.model_validate(item)

    async def update_certification(
        self, db: AsyncSession, user: User, cert_id: uuid.UUID, payload: CertificationUpdate
    ) -> CertificationResponse:
        career_profile = await self.get_or_create_career_profile(db, user.id)
        item = await db.scalar(select(Certification).where(Certification.id == cert_id))
        if item is None:
            raise NotFoundException(resource="Certification", identifier=cert_id)
        if item.career_profile_id != career_profile.id:
            raise ForbiddenException("You do not have permission to modify this record.")

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)

        if item.expiration_date and item.issue_date and item.expiration_date < item.issue_date:
            raise ValidationException("Expiration date cannot precede issue date.")

        await db.commit()
        await db.refresh(item)
        return CertificationResponse.model_validate(item)

    async def delete_certification(
        self, db: AsyncSession, user: User, cert_id: uuid.UUID
    ) -> None:
        career_profile = await self.get_or_create_career_profile(db, user.id)
        item = await db.scalar(select(Certification).where(Certification.id == cert_id))
        if item is None:
            raise NotFoundException(resource="Certification", identifier=cert_id)
        if item.career_profile_id != career_profile.id:
            raise ForbiddenException("You do not have permission to delete this record.")

        await db.delete(item)
        await db.commit()


profile_service = ProfileService()
