"""
Comprehensive Test Suite for CoachPath PostgreSQL Data Layer Models (Phase 2B).
Tests model creation, foreign key relations, constraints, cascade rules, and seed idempotency.
"""

import decimal
import uuid
from datetime import date, datetime, timezone
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.applications import (
    Application,
    ApplicationStatusHistory,
    Interview,
    InterviewPreparation,
    InterviewQuestion,
    Recruiter,
    RecruiterContact,
    RecruiterMessage,
)
from app.models.assessments import (
    Assessment,
    AssessmentAnswer,
    AssessmentAttempt,
    AssessmentQuestion,
    AssessmentResult,
)
from app.models.audit import ActivityLog, AuditLog
from app.models.auth import User, UserProfile, UserSession
from app.models.career import (
    CareerProfile,
    Certification,
    Education,
    Experience,
    Project,
    Role,
)
from app.models.jobs import Job, JobMatch, JobSkill
from app.models.readiness import CareerReadinessScore
from app.models.resume import Resume, ResumeVersion
from app.models.roadmap import Roadmap, RoadmapPhase, RoadmapTask
from app.models.skills import RoleRequirement, Skill, SkillGap, UserSkill
from scripts.seed import seed_canonical_data


@pytest.mark.asyncio
async def test_user_and_profile_creation_and_cascade(test_session: AsyncSession):
    """Verifies User, UserProfile, and UserSession persistence and cascade deletion."""
    user = User(
        email="candidate@example.com",
        password_hash="$argon2id$v=19$m=65536,t=3,p=4$fakehash",
        role="candidate",
        status="active",
    )
    test_session.add(user)
    await test_session.flush()

    profile = UserProfile(
        user_id=user.id,
        full_name="Jane Doe",
        headline="Aspiring Backend Engineer",
        location="San Francisco, CA",
        github_url="https://github.com/janedoe",
    )
    session = UserSession(
        user_id=user.id,
        refresh_token_hash="hash_token_12345",
        expires_at=datetime.now(timezone.utc),
    )
    test_session.add_all([profile, session])
    await test_session.commit()

    # Verify retrieval and relationships with selectinload
    stmt = (
        select(User)
        .options(selectinload(User.profile), selectinload(User.sessions))
        .where(User.id == user.id)
    )
    retrieved_user = await test_session.scalar(stmt)
    assert retrieved_user is not None
    assert retrieved_user.email == "candidate@example.com"
    assert retrieved_user.profile.full_name == "Jane Doe"
    assert len(retrieved_user.sessions) == 1

    # Verify cascade deletion
    await test_session.delete(retrieved_user)
    await test_session.commit()

    retrieved_profile = await test_session.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
    retrieved_session = await test_session.scalar(select(UserSession).where(UserSession.user_id == user.id))
    assert retrieved_profile is None
    assert retrieved_session is None


@pytest.mark.asyncio
async def test_user_unique_constraint(test_session: AsyncSession):
    """Verifies that duplicate user emails violate unique constraint."""
    u1 = User(email="dup@example.com", password_hash="hash1")
    u2 = User(email="dup@example.com", password_hash="hash2")
    test_session.add(u1)
    await test_session.commit()

    test_session.add(u2)
    with pytest.raises(IntegrityError):
        await test_session.commit()
    await test_session.rollback()


@pytest.mark.asyncio
async def test_career_profile_and_evidence_graph(test_session: AsyncSession):
    """Verifies CareerProfile and child evidence models (Education, Experience, Project, Certification)."""
    user = User(email="engineer@example.com", password_hash="hash")
    role = Role(
        id="backend-developer",
        title="Backend Developer",
        description="Builds APIs and databases",
        category="engineering",
    )
    test_session.add_all([user, role])
    await test_session.flush()

    profile = CareerProfile(
        user_id=user.id,
        primary_role_id=role.id,
        career_stage="early_career",
        work_preference="hybrid",
        target_locations=["San Francisco", "Remote"],
        years_of_experience=decimal.Decimal("1.5"),
    )
    test_session.add(profile)
    await test_session.flush()

    edu = Education(
        career_profile_id=profile.id,
        institution_name="UC Berkeley",
        degree="B.S.",
        field_of_study="Computer Science",
        start_date=date(2020, 8, 15),
        end_date=date(2024, 5, 20),
        gpa=decimal.Decimal("3.85"),
    )
    exp = Experience(
        career_profile_id=profile.id,
        company_name="Acme Tech",
        role_title="Backend Intern",
        start_date=date(2023, 6, 1),
        end_date=date(2023, 8, 31),
        bullet_points=["Built async FastAPI microservice", "Cut latency by 25%"],
    )
    proj = Project(
        career_profile_id=profile.id,
        title="Distributed Key-Value Store",
        description="Built in Go and Redis protocol",
        technologies=["Go", "Redis", "Docker"],
        bullet_points=["Implemented Raft consensus algorithm"],
    )
    cert = Certification(
        career_profile_id=profile.id,
        name="AWS Certified Solutions Architect",
        issuing_organization="Amazon Web Services",
        issue_date=date(2024, 1, 10),
    )
    test_session.add_all([edu, exp, proj, cert])
    await test_session.commit()

    # Query career profile with relations using selectinload
    stmt = (
        select(CareerProfile)
        .options(
            selectinload(CareerProfile.education),
            selectinload(CareerProfile.experience),
            selectinload(CareerProfile.projects),
            selectinload(CareerProfile.certifications),
        )
        .where(CareerProfile.id == profile.id)
    )
    retrieved = await test_session.scalar(stmt)
    assert retrieved is not None
    assert len(retrieved.education) == 1
    assert retrieved.education[0].institution_name == "UC Berkeley"
    assert len(retrieved.experience) == 1
    assert len(retrieved.projects) == 1
    assert len(retrieved.certifications) == 1

    # Cascade deletion on career profile delete
    await test_session.delete(retrieved)
    await test_session.commit()

    assert await test_session.scalar(select(Education).where(Education.career_profile_id == profile.id)) is None
    assert await test_session.scalar(select(Experience).where(Experience.career_profile_id == profile.id)) is None
    assert await test_session.scalar(select(Project).where(Project.career_profile_id == profile.id)) is None
    assert await test_session.scalar(select(Certification).where(Certification.career_profile_id == profile.id)) is None


@pytest.mark.asyncio
async def test_skills_taxonomy_and_user_skills(test_session: AsyncSession):
    """Verifies Skill master ontology, UserSkill confidence ratings, and SkillGap snapshot."""
    user = User(email="skills@example.com", password_hash="hash")
    role = Role(id="ai-engineer", title="AI Engineer", description="Builds AI models", category="ai")
    skill = Skill(
        id="fastapi",
        name="FastAPI",
        category="framework",
        description="Async web framework for Python",
        synonyms=["fast-api"],
    )
    test_session.add_all([user, role, skill])
    await test_session.flush()

    role_req = RoleRequirement(
        role_id=role.id,
        skill_id=skill.id,
        importance="mandatory",
        min_proficiency="proficient",
        weight=decimal.Decimal("1.5"),
    )
    profile = CareerProfile(
        user_id=user.id,
        primary_role_id=role.id,
        career_stage="student",
        work_preference="remote",
    )
    test_session.add_all([role_req, profile])
    await test_session.flush()

    user_skill = UserSkill(
        career_profile_id=profile.id,
        skill_id=skill.id,
        confidence_score=decimal.Decimal("0.85"),
        proficiency_tier="proficient",
        primary_source="assessment",
        is_verified=True,
    )
    gap = SkillGap(
        career_profile_id=profile.id,
        role_id=role.id,
        readiness_percentage=decimal.Decimal("82.5"),
        met_skills=["fastapi", "python"],
        developing_skills=[],
        missing_skills=["docker"],
        explanation_narrative="Candidate is proficient in core backend framework.",
    )
    test_session.add_all([user_skill, gap])
    await test_session.commit()

    retrieved_skill = await test_session.scalar(select(UserSkill).where(UserSkill.id == user_skill.id))
    assert retrieved_skill is not None
    assert retrieved_skill.confidence_score == decimal.Decimal("0.85")
    assert retrieved_skill.is_verified is True

    # Unique constraint violation: duplicate user_skill for same profile and skill
    dup_skill = UserSkill(
        career_profile_id=profile.id,
        skill_id=skill.id,
        primary_source="self_reported",
    )
    test_session.add(dup_skill)
    with pytest.raises(IntegrityError):
        await test_session.commit()
    await test_session.rollback()


@pytest.mark.asyncio
async def test_assessments_hierarchy_and_results(test_session: AsyncSession):
    """Verifies Assessment, AssessmentQuestion, AssessmentAttempt, AssessmentAnswer, and AssessmentResult."""
    user = User(email="quiz@example.com", password_hash="hash")
    skill = Skill(id="python", name="Python", category="language", description="General programming")
    test_session.add_all([user, skill])
    await test_session.flush()

    assessment = Assessment(
        skill_id=skill.id,
        title="Python Concurrency Diagnostic",
        description="Diagnostic test covering asyncio and threading",
        time_limit_minutes=20,
        passing_threshold=decimal.Decimal("75.0"),
    )
    test_session.add(assessment)
    await test_session.flush()

    q1 = AssessmentQuestion(
        assessment_id=assessment.id,
        prompt_text="What does asyncio.gather do?",
        options=["Runs awaitables concurrently", "Runs sequentially", "Spawns a thread", "None"],
        correct_option_index=0,
        explanation="asyncio.gather runs awaitable objects concurrently.",
        difficulty="intermediate",
    )
    test_session.add(q1)
    await test_session.flush()

    attempt = AssessmentAttempt(
        user_id=user.id,
        assessment_id=assessment.id,
        status="completed",
        score_percentage=decimal.Decimal("100.0"),
        passed=True,
    )
    test_session.add(attempt)
    await test_session.flush()

    answer = AssessmentAnswer(
        attempt_id=attempt.id,
        question_id=q1.id,
        selected_option_index=0,
        is_correct=True,
        response_time_seconds=12,
    )
    result = AssessmentResult(
        attempt_id=attempt.id,
        strengths_summary="Mastered event loops and coroutine gathering.",
        weaknesses_summary="None observed.",
        remedial_milestones=[],
        confidence_lift=decimal.Decimal("0.35"),
    )
    test_session.add_all([answer, result])
    await test_session.commit()

    stmt = (
        select(AssessmentAttempt)
        .options(selectinload(AssessmentAttempt.answers), selectinload(AssessmentAttempt.result))
        .where(AssessmentAttempt.id == attempt.id)
    )
    retrieved_attempt = await test_session.scalar(stmt)
    assert retrieved_attempt is not None
    assert retrieved_attempt.passed is True
    assert len(retrieved_attempt.answers) == 1
    assert retrieved_attempt.result.confidence_lift == decimal.Decimal("0.35")


@pytest.mark.asyncio
async def test_dynamic_roadmap_structure(test_session: AsyncSession):
    """Verifies Roadmap, RoadmapPhase, and RoadmapTask hierarchical creation and cascades."""
    user = User(email="roadmap@example.com", password_hash="hash")
    role = Role(id="fullstack-developer", title="Full Stack Developer", description="Full stack", category="engineering")
    test_session.add_all([user, role])
    await test_session.flush()

    profile = CareerProfile(user_id=user.id, primary_role_id=role.id, career_stage="student")
    test_session.add(profile)
    await test_session.flush()

    roadmap = Roadmap(
        career_profile_id=profile.id,
        target_role_id=role.id,
        title="Full Stack Mastery Curriculum",
        total_tasks=2,
        completed_tasks=1,
    )
    test_session.add(roadmap)
    await test_session.flush()

    phase = RoadmapPhase(
        roadmap_id=roadmap.id,
        title="Phase 1: Backend Fundamentals",
        description="Learn REST architecture and SQLAlchemy 2.0",
        order_index=0,
    )
    test_session.add(phase)
    await test_session.flush()

    task1 = RoadmapTask(
        phase_id=phase.id,
        title="Build Async REST Service",
        description="Implement standard RFC 7807 problem details",
        estimated_hours=6,
        order_index=0,
        status="completed",
    )
    task2 = RoadmapTask(
        phase_id=phase.id,
        title="Deploy with Docker Compose",
        description="Containerize FastAPI app and Postgres service",
        estimated_hours=4,
        order_index=1,
        status="pending",
    )
    test_session.add_all([task1, task2])
    await test_session.commit()

    stmt = (
        select(Roadmap)
        .options(selectinload(Roadmap.phases).selectinload(RoadmapPhase.tasks))
        .where(Roadmap.id == roadmap.id)
    )
    retrieved_roadmap = await test_session.scalar(stmt)
    assert retrieved_roadmap is not None
    assert len(retrieved_roadmap.phases) == 1
    assert len(retrieved_roadmap.phases[0].tasks) == 2

    # Cascade deletion on roadmap delete
    await test_session.delete(retrieved_roadmap)
    await test_session.commit()

    assert await test_session.scalar(select(RoadmapPhase).where(RoadmapPhase.id == phase.id)) is None
    assert await test_session.scalar(select(RoadmapTask).where(RoadmapTask.id == task1.id)) is None


@pytest.mark.asyncio
async def test_jobs_and_semantic_matching(test_session: AsyncSession):
    """Verifies Job postings, JobSkill tags, and JobMatch explainability records."""
    user = User(email="jobs@example.com", password_hash="hash")
    role = Role(id="backend-developer", title="Backend Developer", description="Backend", category="engineering")
    skill = Skill(id="postgresql", name="PostgreSQL", category="database", description="Relational DB")
    test_session.add_all([user, role, skill])
    await test_session.flush()

    profile = CareerProfile(user_id=user.id, primary_role_id=role.id, career_stage="early_career")
    test_session.add(profile)
    await test_session.flush()

    job = Job(
        title="Junior Backend Engineer",
        company_name="Stripe",
        location="Seattle, WA",
        remote_type="hybrid",
        role_id=role.id,
        experience_level="entry_level",
        description_markdown="Join our core infrastructure team building resilient ledger services.",
        application_url="https://stripe.com/jobs/123",
        embedding=[0.05] * 1536,
    )
    test_session.add(job)
    await test_session.flush()

    job_skill = JobSkill(job_id=job.id, skill_id=skill.id, is_mandatory=True)
    match = JobMatch(
        career_profile_id=profile.id,
        job_id=job.id,
        overall_score=decimal.Decimal("91.5"),
        skill_score=decimal.Decimal("95.0"),
        experience_score=decimal.Decimal("88.0"),
        vector_score=decimal.Decimal("92.0"),
        matched_skills=["postgresql"],
        missing_skills=[],
        explanation_json={"rationale": "High database competency alignment."},
    )
    test_session.add_all([job_skill, match])
    await test_session.commit()

    stmt = (
        select(Job)
        .options(selectinload(Job.skills), selectinload(Job.matches))
        .where(Job.id == job.id)
    )
    retrieved_job = await test_session.scalar(stmt)
    assert retrieved_job is not None
    assert len(retrieved_job.skills) == 1
    assert len(retrieved_job.matches) == 1
    assert retrieved_job.matches[0].overall_score == decimal.Decimal("91.5")


@pytest.mark.asyncio
async def test_resumes_and_truthful_tailoring(test_session: AsyncSession):
    """Verifies Resume master document and tailored ResumeVersion variants."""
    user = User(email="resume@example.com", password_hash="hash")
    role = Role(id="backend-developer", title="Backend Developer", description="Backend", category="engineering")
    test_session.add_all([user, role])
    await test_session.flush()

    job = Job(
        title="Software Engineer",
        company_name="Datadog",
        location="New York, NY",
        role_id=role.id,
        experience_level="junior",
        description_markdown="Observability engineering",
        application_url="https://datadog.com/jobs/456",
        embedding=[0.01] * 1536,
    )
    test_session.add(job)
    await test_session.flush()

    resume = Resume(
        user_id=user.id,
        file_name="jane_resume.pdf",
        storage_path="/resumes/user_1/original.pdf",
        file_size_bytes=102400,
        mime_type="application/pdf",
        status="parsed",
        parsed_text="Jane Doe Backend Engineer...",
        extracted_data={"skills": ["python", "sql"]},
    )
    test_session.add(resume)
    await test_session.flush()

    version = ResumeVersion(
        resume_id=resume.id,
        target_job_id=job.id,
        version_number=1,
        status="approved",
        tailored_content={"headline": "Observability Backend Engineer"},
        diff_summary={"additions": ["Datadog metrics integration"]},
        anti_hallucination_verified=True,
        approved_at=datetime.now(timezone.utc),
    )
    test_session.add(version)
    await test_session.commit()

    stmt = (
        select(Resume)
        .options(selectinload(Resume.versions))
        .where(Resume.id == resume.id)
    )
    retrieved_resume = await test_session.scalar(stmt)
    assert retrieved_resume is not None
    assert len(retrieved_resume.versions) == 1
    assert retrieved_resume.versions[0].anti_hallucination_verified is True


@pytest.mark.asyncio
async def test_applications_kanban_and_interviews(test_session: AsyncSession):
    """Verifies Application Kanban tracker, Recruiter outreach, and Interview drills."""
    user = User(email="app@example.com", password_hash="hash")
    role = Role(id="backend-developer", title="Backend Developer", description="Backend", category="engineering")
    test_session.add_all([user, role])
    await test_session.flush()

    job = Job(
        title="Backend Dev",
        company_name="Netflix",
        location="Los Gatos, CA",
        role_id=role.id,
        experience_level="mid",
        description_markdown="Streaming backend",
        application_url="https://netflix.com/jobs/789",
        embedding=[0.02] * 1536,
    )
    recruiter = Recruiter(
        full_name="Sarah Connor",
        company_name="Netflix",
        role_title="Lead Technical Recruiter",
    )
    iq = InterviewQuestion(
        role_id=role.id,
        question_text="How do you handle microservice timeouts?",
        category="system_design",
        talking_points_framework="Circuits, retries, exponential backoff",
        sample_high_performing_answer="Use circuit breakers and idempotency keys.",
    )
    test_session.add_all([job, recruiter, iq])
    await test_session.flush()

    app = Application(
        user_id=user.id,
        job_id=job.id,
        current_status="screening",
    )
    test_session.add(app)
    await test_session.flush()

    history = ApplicationStatusHistory(
        application_id=app.id,
        from_status="saved",
        to_status="screening",
    )
    contact = RecruiterContact(
        application_id=app.id,
        recruiter_id=recruiter.id,
    )
    test_session.add_all([history, contact])
    await test_session.flush()

    msg = RecruiterMessage(
        recruiter_contact_id=contact.id,
        intent="introduction",
        subject_line="Passionate about Netflix streaming architecture",
        message_body="Hi Sarah, I noticed the open backend position...",
    )
    interview = Interview(
        application_id=app.id,
        round_type="technical_coding",
        scheduled_at=datetime.now(timezone.utc),
    )
    test_session.add_all([msg, interview])
    await test_session.flush()

    prep = InterviewPreparation(
        interview_id=interview.id,
        question_id=iq.id,
        candidate_notes="Mention Hystrix/Resilience4j experience.",
        is_reviewed=True,
    )
    test_session.add(prep)
    await test_session.commit()

    stmt = (
        select(Application)
        .options(
            selectinload(Application.status_history),
            selectinload(Application.recruiter_contacts),
            selectinload(Application.interviews).selectinload(Interview.preparations),
        )
        .where(Application.id == app.id)
    )
    retrieved_app = await test_session.scalar(stmt)
    assert retrieved_app is not None
    assert retrieved_app.current_status == "screening"
    assert len(retrieved_app.status_history) == 1
    assert len(retrieved_app.recruiter_contacts) == 1
    assert len(retrieved_app.interviews) == 1
    assert len(retrieved_app.interviews[0].preparations) == 1


@pytest.mark.asyncio
async def test_readiness_and_audit_logging(test_session: AsyncSession):
    """Verifies CareerReadinessScore telemetry, ActivityLog, and AuditLog records."""
    user = User(email="audit@example.com", password_hash="hash")
    test_session.add(user)
    await test_session.flush()

    readiness = CareerReadinessScore(
        user_id=user.id,
        overall_score=decimal.Decimal("78.5"),
        profile_completeness_factor=decimal.Decimal("90.0"),
        skill_proficiency_factor=decimal.Decimal("75.0"),
        roadmap_progress_factor=decimal.Decimal("70.0"),
        application_velocity_factor=decimal.Decimal("80.0"),
        top_next_actions=[{"action": "Complete Docker diagnostic assessment"}],
        recorded_date=date(2026, 10, 7),
    )
    activity = ActivityLog(
        user_id=user.id,
        activity_type="ASSESSMENT_PASSED",
        title="Passed Python Concurrency Assessment with 100%",
        metadata_json={"score": 100},
    )
    audit = AuditLog(
        user_id=user.id,
        action_type="RESUME_TAILOR_APPROVED",
        target_entity_type="resume_version",
        target_entity_id=uuid.uuid4(),
        diff_payload={"status": "approved"},
        human_approved=True,
        client_ip_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        user_agent="Mozilla/5.0 Chrome/120.0",
    )
    test_session.add_all([readiness, activity, audit])
    await test_session.commit()

    stmt = (
        select(User)
        .options(
            selectinload(User.readiness_scores),
            selectinload(User.activity_logs),
            selectinload(User.audit_logs),
        )
        .where(User.id == user.id)
    )
    retrieved_user = await test_session.scalar(stmt)
    assert len(retrieved_user.readiness_scores) == 1
    assert retrieved_user.readiness_scores[0].overall_score == decimal.Decimal("78.5")
    assert len(retrieved_user.activity_logs) == 1
    assert len(retrieved_user.audit_logs) == 1
    assert retrieved_user.audit_logs[0].human_approved is True


@pytest.mark.asyncio
async def test_canonical_taxonomy_seeding_idempotence(test_session: AsyncSession):
    """Verifies that seed_canonical_data runs successfully and is completely idempotent."""
    # First seed execution
    await seed_canonical_data(test_session)

    roles = (await test_session.scalars(select(Role))).all()
    skills = (await test_session.scalars(select(Skill))).all()
    reqs = (await test_session.scalars(select(RoleRequirement))).all()

    assert len(roles) == 7
    assert len(skills) >= 15
    assert len(reqs) >= 15

    # Second seed execution (idempotency check)
    await seed_canonical_data(test_session)

    roles_after = (await test_session.scalars(select(Role))).all()
    skills_after = (await test_session.scalars(select(Skill))).all()
    assert len(roles_after) == 7
    assert len(skills_after) >= 15
