"""
Comprehensive Test Suite for Phase 11A: Intelligent Application Preparation & Recruiter Outreach Backend.

Validates all 33 required verification scenarios:
 1. Application preparation with valid inputs generates a complete package.
 2. Cover note is generated and grounded in candidate experience and job requirements.
 3. Common application questions are answered (3-4 questions) with citations or clarification requests.
 4. Application preparation with invalid or missing job ID returns appropriate error.
 5. Application preparation with inaccessible or unparsed resume returns appropriate error.
 6. User cannot prepare application package using another user's resume or job application.
 7. Application package is persisted with initial status 'draft'.
 8. Candidate can update/edit package (cover note, answers) and status transitions to 'edited'.
 9. Candidate editing resets candidate approval status.
10. Application preparation preserves original resume without mutation.
11. Candidate can approve application package (explicit approval gate).
12. Approval requires explicit human confirmation; cannot be bypassed.
13. Approval records audit log entry with timestamp and user ID.
14. Application is NOT automatically submitted upon approval.
15. User confirms completion of official application submission; status transitions to 'submitted'.
16. Submission confirmation is idempotent and records submission timestamp.
17. Recruiter outreach generation produces draft <= 90 words.
18. Outreach draft length validation rejects or truncates drafts exceeding 90 words.
19. Outreach draft contains NO fabricated contact info, recruiter names, or ungrounded claims.
20. Outreach draft is persisted with initial status 'draft'.
21. Maximum 3 outreach drafts per application enforced by backend.
22. Candidate can update/edit outreach draft.
23. Candidate editing resets outreach approval status.
24. Candidate can approve outreach draft (explicit approval gate).
25. Approved outreach draft provides manual handoff (mailto, profile URL, or copy text).
26. Recruiter outreach is NOT automatically sent upon approval.
27. User confirms recruiter outreach sent; status transitions to 'sent'.
28. Outreach draft deletion is restricted to owning user.
29. Cross-user access prevention: User A cannot view, edit, approve, or delete User B's application packages.
30. Cross-user access prevention: User A cannot view, edit, approve, or delete User B's outreach drafts.
31. AI provider failure during package preparation returns 503 and leaves no corrupt state.
32. AI provider failure during outreach drafting returns 503 and leaves no corrupt state.
33. Malformed AI responses are handled gracefully with appropriate error messages.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional, Tuple

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.factory import override_llm_provider, reset_llm_provider
from app.ai.mock_adapter import MockLLMProvider
from app.core.exceptions import ServiceUnavailableException
from app.db.seeds.gap_analysis_seeder import seed_skill_taxonomy_and_roles
from app.models.applications import Application, ApplicationPackage, RecruiterOutreachDraft
from app.models.audit import AuditLog
from app.models.career import CareerProfile, Experience, Project
from app.models.jobs import Job, JobSkill, JobSource
from app.models.resume import Resume, ResumeVersion
from app.models.skills import Skill, UserSkill


# ─── Fixtures and Test Helpers ───────────────────────────────────────────────

@pytest.fixture(autouse=True)
async def seed_base_data(test_session: AsyncSession):
    """Seeds taxonomy and job sources required for relational integrity."""
    await seed_skill_taxonomy_and_roles(test_session)
    for name, p_type in [("seed", "seed"), ("manual", "manual"), ("mock", "mock")]:
        source = await test_session.scalar(select(JobSource).where(JobSource.name == name))
        if not source:
            source = JobSource(name=name, provider_type=p_type, is_active=True)
            test_session.add(source)
    await test_session.commit()


async def register_and_login(client: AsyncClient, email: str, name: str) -> Tuple[str, uuid.UUID]:
    """Registers and logs in a test candidate, returning access token and user_id."""
    pw = "AppPrepPassword123!"
    r_reg = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": pw, "full_name": name},
    )
    assert r_reg.status_code == 201
    user_id = uuid.UUID(r_reg.json()["user_id"])

    r_login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": pw},
    )
    assert r_login.status_code == 200
    token = r_login.json()["access_token"]
    return token, user_id


async def create_parsed_test_resume(
    db: AsyncSession,
    user_id: uuid.UUID,
    status: str = "parsed",
) -> Resume:
    """Directly creates a verified parsed Resume in the database with known background entities."""
    extracted_data = {
        "personal_info": {
            "name": "Alex Mercer",
            "email": "alex.mercer@test.com",
            "phone": "+1-555-0199",
            "location": "San Francisco, CA",
        },
        "executive_summary": "Experienced backend engineer focused on distributed payment infrastructure.",
        "skills": [
            {"name": "Python", "category": "technical"},
            {"name": "FastAPI", "category": "technical"},
            {"name": "PostgreSQL", "category": "technical"},
            {"name": "Docker", "category": "technical"},
        ],
        "experience": [
            {
                "employer": "Acme Cloud Corp",
                "job_title": "Senior Backend Developer",
                "start_date": "2020-01",
                "end_date": "Present",
                "is_current": True,
                "responsibilities": ["Designed REST and gRPC microservices in Python."],
                "achievements": ["Maintained 99.99% service uptime across core payment APIs."],
            }
        ],
        "education": [
            {
                "institution": "University of California, Berkeley",
                "degree": "B.S. in Computer Science",
                "field_of_study": "Computer Science",
            }
        ],
        "projects": [
            {
                "name": "Cloud Gate",
                "description": "Payment Gateway built with FastAPI and Redis caching.",
                "technologies": ["Python", "FastAPI", "Redis"],
            }
        ],
        "certifications": [],
    }

    resume = Resume(
        id=uuid.uuid4(),
        user_id=user_id,
        file_name="Alex_Mercer_Resume.pdf",
        storage_path=f"uploads/{uuid.uuid4()}.pdf",
        file_size_bytes=2048,
        mime_type="application/pdf",
        status=status,
        parsed_text="Alex Mercer. Experienced backend engineer. Python, FastAPI, PostgreSQL, Docker.",
        extracted_data=extracted_data if status == "parsed" else None,
        is_primary=True,
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)
    return resume


async def create_test_tailored_version(
    db: AsyncSession,
    user_id: uuid.UUID,
    resume_id: uuid.UUID,
    job_id: uuid.UUID,
) -> ResumeVersion:
    """Creates an approved tailored ResumeVersion."""
    tailored_data = {
        "personal_info": {
            "name": "Alex Mercer",
            "email": "alex.mercer@test.com",
            "phone": "+1-555-0199",
            "location": "San Francisco, CA",
        },
        "executive_summary": "Lead Backend Engineer specializing in resilient Python architectures.",
        "skills": [{"name": "Python", "category": "technical"}, {"name": "PostgreSQL", "category": "technical"}],
        "experience": [
            {
                "employer": "Acme Cloud Corp",
                "job_title": "Senior Backend Developer",
                "start_date": "2020-01",
                "end_date": "Present",
                "is_current": True,
                "responsibilities": ["Engineered high-concurrency payment APIs."],
                "achievements": ["Achieved 99.99% uptime."],
            }
        ],
        "education": [],
        "projects": [],
        "certifications": [],
    }

    version = ResumeVersion(
        id=uuid.uuid4(),
        resume_id=resume_id,
        user_id=user_id,
        target_job_id=job_id,
        version_number=1,
        tailored_content=tailored_data,
        diff_summary={"additions": [], "rephrasings": [], "deletions": []},
        status="approved",
        anti_hallucination_verified=True,
    )
    db.add(version)
    await db.commit()
    await db.refresh(version)
    return version


async def create_test_job(
    db: AsyncSession,
    title: str = "Lead Backend Engineer",
    company: str = "FinTech Global",
) -> Job:
    """Creates a catalog Job record."""
    job = Job(
        id=uuid.uuid4(),
        external_id=f"job_{uuid.uuid4().hex[:8]}",
        source="seed",
        source_url="https://example.com/jobs/lead-backend",
        title=title,
        normalized_title=title.lower(),
        company_name=company,
        location="Remote",
        normalized_location="remote",
        remote_type="remote",
        employment_type="full_time",
        role_id="backend-developer",
        experience_level="mid",
        min_salary=140000,
        max_salary=180000,
        currency="USD",
        description_markdown=(
            "FinTech Global is seeking a Lead Backend Engineer to build resilient distributed payment gateways. "
            "Required Qualifications: 5+ years with Python, PostgreSQL, and Docker. Experience with microservices."
        ),
        responsibilities=["Build high-volume payment processing pipelines.", "Maintain database reliability."],
        required_qualifications=["Proficiency in Python and PostgreSQL.", "Docker container orchestration."],
        preferred_qualifications=["FastAPI experience."],
        application_url="https://fintechglobal.example.com/apply/123",
        is_active=True,
        freshness_status="active",
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


def mock_successful_ai_package() -> dict:
    """Builds realistic structured output matching AIApplicationPackageOutput."""
    return {
        "cover_note": (
            "Dear Hiring Team, I am excited to apply for the Lead Backend Engineer position at FinTech Global. "
            "With over four years of experience architecting distributed payment microservices in Python at Acme Cloud Corp, "
            "I have maintained 99.99% service uptime and managed mission-critical transactional pipelines with PostgreSQL and Docker. "
            "I look forward to discussing how my background aligns with your engineering goals."
        ),
        "application_questions": [
            {
                "id": "q_1",
                "question": "Why are you interested in this role and company?",
                "answer": "FinTech Global's mission to build resilient distributed payment gateways aligns directly with my engineering achievements at Acme Cloud Corp, where I designed high-concurrency payment APIs.",
                "supporting_evidence": "Acme Cloud Corp: Designed REST microservices in Python; 99.99% uptime",
                "needs_clarification": False,
                "clarification_prompt": None,
            },
            {
                "id": "q_2",
                "question": "Describe your experience with distributed systems and database reliability.",
                "answer": "At Acme Cloud Corp, I maintained 99.99% uptime across distributed payment services and scaled transactional PostgreSQL workloads under high concurrent load.",
                "supporting_evidence": "Acme Cloud Corp: Maintained 99.99% uptime; Skills: PostgreSQL, Docker",
                "needs_clarification": False,
                "clarification_prompt": None,
            },
            {
                "id": "q_3",
                "question": "What experience do you have with Kubernetes cluster administration?",
                "answer": "My primary containerization experience is centered on Docker orchestration in production; I have not yet managed bare Kubernetes clusters at enterprise scale.",
                "supporting_evidence": "Skills: Docker",
                "needs_clarification": True,
                "clarification_prompt": "Please verify if you have hands-on Kubernetes experience not listed in your resume.",
            },
        ],
        "evidence_references": [
            "Acme Cloud Corp: Senior Backend Developer (2020-Present)",
            "Skills: Python, FastAPI, PostgreSQL, Docker",
        ],
        "unsupported_claims": [
            "Kubernetes cluster administration",
        ],
    }


def mock_successful_ai_outreach(recruiter_name: Optional[str] = "Jane", word_count: int = 48) -> dict:
    """Builds realistic structured output matching AIRecruiterOutreachOutput with strictly <= 90 words."""
    message = (
        f"Hi {recruiter_name or 'there'}, I noticed the Lead Backend Engineer role at FinTech Global. "
        "With 4+ years designing high-uptime Python and PostgreSQL payment microservices at Acme Cloud Corp, "
        "I'd love to connect and share how my distributed systems experience can support your platform scalability."
    )
    words = len(message.split())
    return {
        "subject_line": "Lead Backend Engineer - Alex Mercer",
        "message_body": message,
        "word_count": words,
        "suggested_role_types": ["Technical Recruiter", "Engineering Hiring Manager"],
        "supporting_evidence": ["Acme Cloud Corp Python experience", "PostgreSQL uptime"],
        "needs_clarification": False,
        "clarification_prompt": None,
    }


# ─── Tests 1-10: Application Preparation Core & Invariants ───────────────────

@pytest.mark.asyncio
async def test_01_prepare_package_valid_inputs_complete_package(
    client: AsyncClient, test_session: AsyncSession
):
    """1. Application preparation with valid inputs generates a complete package."""
    token, user_id = await register_and_login(client, "prep.valid@test.com", "Valid User")
    resume = await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)
    version = await create_test_tailored_version(test_session, user_id, resume.id, job.id)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_package())
    override_llm_provider(mock)

    try:
        resp = await client.post(
            "/api/v1/applications/prepare",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "target_job_id": str(job.id),
                "tailored_resume_version_id": str(version.id),
            },
        )
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["id"] is not None
        assert data["user_id"] == str(user_id)
        assert data["target_job_id"] == str(job.id)
        assert data["tailored_resume_version_id"] == str(version.id)
        assert data["status"] == "draft"
        assert data["cover_note"] is not None
        assert len(data["question_answers"]) == 3
        assert data["is_candidate_approved"] is False
        assert data["user_confirmed_submission"] is False
    finally:
        reset_llm_provider()


@pytest.mark.asyncio
async def test_02_cover_note_grounded_in_candidate_experience(
    client: AsyncClient, test_session: AsyncSession
):
    """2. Cover note is generated and grounded in candidate experience and job requirements."""
    token, user_id = await register_and_login(client, "prep.covernote@test.com", "Cover Note User")
    resume = await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_package())
    override_llm_provider(mock)

    try:
        resp = await client.post(
            "/api/v1/applications/prepare",
            headers={"Authorization": f"Bearer {token}"},
            json={"target_job_id": str(job.id)},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "FinTech Global" in data["cover_note"]
        assert "Acme Cloud Corp" in data["cover_note"]
        assert "Python" in data["cover_note"]
    finally:
        reset_llm_provider()


@pytest.mark.asyncio
async def test_03_application_questions_with_citations_or_clarifications(
    client: AsyncClient, test_session: AsyncSession
):
    """3. Common application questions are answered (3-4 questions) with citations or clarification requests."""
    token, user_id = await register_and_login(client, "prep.questions@test.com", "QA User")
    resume = await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_package())
    override_llm_provider(mock)

    try:
        resp = await client.post(
            "/api/v1/applications/prepare",
            headers={"Authorization": f"Bearer {token}"},
            json={"target_job_id": str(job.id)},
        )
        assert resp.status_code == 201
        data = resp.json()
        qa_list = data["question_answers"]
        assert 3 <= len(qa_list) <= 4
        # Verify evidence citations present
        assert len(qa_list[0]["evidence_citations"]) > 0
        # Verify clarification request present when background does not fully match
        assert any(qa["requires_clarification"] is True for qa in qa_list)
        clarification_item = next(qa for qa in qa_list if qa["requires_clarification"])
        assert clarification_item["clarification_prompt"] is not None
    finally:
        reset_llm_provider()


@pytest.mark.asyncio
async def test_04_prepare_package_invalid_or_missing_job_returns_error(
    client: AsyncClient, test_session: AsyncSession
):
    """4. Application preparation with invalid or missing job ID returns appropriate error."""
    token, user_id = await register_and_login(client, "prep.missingjob@test.com", "Missing Job User")
    await create_parsed_test_resume(test_session, user_id)

    # Missing job ID & missing raw job text -> 422
    resp_empty = await client.post(
        "/api/v1/applications/prepare",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )
    assert resp_empty.status_code == 422

    # Non-existent job UUID -> 404
    fake_job_id = str(uuid.uuid4())
    resp_fake = await client.post(
        "/api/v1/applications/prepare",
        headers={"Authorization": f"Bearer {token}"},
        json={"target_job_id": fake_job_id},
    )
    assert resp_fake.status_code == 404


@pytest.mark.asyncio
async def test_05_prepare_package_unparsed_resume_returns_error(
    client: AsyncClient, test_session: AsyncSession
):
    """5. Application preparation with inaccessible or unparsed resume returns appropriate error."""
    token, user_id = await register_and_login(client, "prep.unparsed@test.com", "Unparsed User")
    # Resume is still in 'processing' status
    await create_parsed_test_resume(test_session, user_id, status="processing")
    job = await create_test_job(test_session)

    resp = await client.post(
        "/api/v1/applications/prepare",
        headers={"Authorization": f"Bearer {token}"},
        json={"target_job_id": str(job.id)},
    )
    assert resp.status_code == 400
    assert "No parsed active resume found" in resp.text


@pytest.mark.asyncio
async def test_06_cross_user_isolation_cannot_use_other_user_resume(
    client: AsyncClient, test_session: AsyncSession
):
    """6. User cannot prepare application package using another user's resume or version."""
    token_a, user_a = await register_and_login(client, "prep.userA@test.com", "User A")
    token_b, user_b = await register_and_login(client, "prep.userB@test.com", "User B")

    resume_a = await create_parsed_test_resume(test_session, user_a)
    job = await create_test_job(test_session)
    version_a = await create_test_tailored_version(test_session, user_a, resume_a.id, job.id)

    # User B attempts to use User A's tailored version -> 403 or 404
    resp = await client.post(
        "/api/v1/applications/prepare",
        headers={"Authorization": f"Bearer {token_b}"},
        json={
            "target_job_id": str(job.id),
            "tailored_resume_version_id": str(version_a.id),
        },
    )
    assert resp.status_code in (403, 404)


@pytest.mark.asyncio
async def test_07_package_persisted_with_initial_status_draft(
    client: AsyncClient, test_session: AsyncSession
):
    """7. Application package is persisted with initial status 'draft'."""
    token, user_id = await register_and_login(client, "prep.draftstatus@test.com", "Draft User")
    await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_package())
    override_llm_provider(mock)

    try:
        resp = await client.post(
            "/api/v1/applications/prepare",
            headers={"Authorization": f"Bearer {token}"},
            json={"target_job_id": str(job.id)},
        )
        assert resp.status_code == 201
        package_id = resp.json()["id"]

        # Fetch directly via GET /packages/{id}
        resp_get = await client.get(
            f"/api/v1/applications/packages/{package_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp_get.status_code == 200
        assert resp_get.json()["status"] == "draft"
    finally:
        reset_llm_provider()


@pytest.mark.asyncio
async def test_08_candidate_can_update_package_and_status_transitions_to_edited(
    client: AsyncClient, test_session: AsyncSession
):
    """8. Candidate can update/edit package (cover note, answers) and status transitions to 'edited'."""
    token, user_id = await register_and_login(client, "prep.edit@test.com", "Edit User")
    await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_package())
    override_llm_provider(mock)

    try:
        resp_create = await client.post(
            "/api/v1/applications/prepare",
            headers={"Authorization": f"Bearer {token}"},
            json={"target_job_id": str(job.id)},
        )
        package_id = resp_create.json()["id"]

        updated_note = "Custom edited cover note: Excited about FinTech Global's innovative platform."
        resp_update = await client.put(
            f"/api/v1/applications/packages/{package_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"cover_note": updated_note},
        )
        assert resp_update.status_code == 200
        data = resp_update.json()
        assert data["cover_note"] == updated_note
        assert data["status"] == "edited"
    finally:
        reset_llm_provider()


@pytest.mark.asyncio
async def test_09_candidate_editing_resets_approval_status(
    client: AsyncClient, test_session: AsyncSession
):
    """9. Candidate editing resets candidate approval status."""
    token, user_id = await register_and_login(client, "prep.resetapprove@test.com", "Reset User")
    await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_package())
    override_llm_provider(mock)

    try:
        resp_create = await client.post(
            "/api/v1/applications/prepare",
            headers={"Authorization": f"Bearer {token}"},
            json={"target_job_id": str(job.id)},
        )
        package_id = resp_create.json()["id"]

        # First approve it
        resp_approve = await client.post(
            f"/api/v1/applications/packages/{package_id}/approve",
            headers={"Authorization": f"Bearer {token}"},
            json={"user_confirmation": True},
        )
        assert resp_approve.status_code == 200
        assert resp_approve.json()["is_candidate_approved"] is True
        assert resp_approve.json()["status"] == "approved"

        # Now edit it -> approval must reset to False and status to 'edited'
        resp_edit = await client.put(
            f"/api/v1/applications/packages/{package_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"candidate_notes": "Added some personal notes"},
        )
        assert resp_edit.status_code == 200
        data = resp_edit.json()
        assert data["is_candidate_approved"] is False
        assert data["status"] == "edited"
    finally:
        reset_llm_provider()


@pytest.mark.asyncio
async def test_10_package_prep_preserves_original_resume_without_mutation(
    client: AsyncClient, test_session: AsyncSession
):
    """10. Application preparation preserves original resume without mutation."""
    token, user_id = await register_and_login(client, "prep.immutableresume@test.com", "Immutable User")
    resume = await create_parsed_test_resume(test_session, user_id)
    original_text = resume.parsed_text
    original_extracted = dict(resume.extracted_data)
    original_status = resume.status
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_package())
    override_llm_provider(mock)

    try:
        resp = await client.post(
            "/api/v1/applications/prepare",
            headers={"Authorization": f"Bearer {token}"},
            json={"target_job_id": str(job.id)},
        )
        assert resp.status_code == 201

        # Check resume in DB remains byte-for-byte identical
        await test_session.refresh(resume)
        assert resume.parsed_text == original_text
        assert resume.extracted_data == original_extracted
        assert resume.status == original_status
    finally:
        reset_llm_provider()


# ─── Tests 11-16: Application Approval Gate & Honest Submission ───────────────

@pytest.mark.asyncio
async def test_11_candidate_can_approve_application_package(
    client: AsyncClient, test_session: AsyncSession
):
    """11. Candidate can approve application package (explicit approval gate)."""
    token, user_id = await register_and_login(client, "prep.approve@test.com", "Approve User")
    await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_package())
    override_llm_provider(mock)

    try:
        resp_create = await client.post(
            "/api/v1/applications/prepare",
            headers={"Authorization": f"Bearer {token}"},
            json={"target_job_id": str(job.id)},
        )
        package_id = resp_create.json()["id"]

        resp_approve = await client.post(
            f"/api/v1/applications/packages/{package_id}/approve",
            headers={"Authorization": f"Bearer {token}"},
            json={"user_confirmation": True},
        )
        assert resp_approve.status_code == 200
        data = resp_approve.json()
        assert data["is_candidate_approved"] is True
        assert data["status"] == "approved"
        assert data["candidate_approved_at"] is not None
    finally:
        reset_llm_provider()


@pytest.mark.asyncio
async def test_12_approval_requires_explicit_confirmation(
    client: AsyncClient, test_session: AsyncSession
):
    """12. Approval requires explicit human confirmation; cannot be bypassed."""
    token, user_id = await register_and_login(client, "prep.bypass@test.com", "Bypass User")
    await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_package())
    override_llm_provider(mock)

    try:
        resp_create = await client.post(
            "/api/v1/applications/prepare",
            headers={"Authorization": f"Bearer {token}"},
            json={"target_job_id": str(job.id)},
        )
        package_id = resp_create.json()["id"]

        # Attempt approval with user_confirmation=False
        resp_fail = await client.post(
            f"/api/v1/applications/packages/{package_id}/approve",
            headers={"Authorization": f"Bearer {token}"},
            json={"user_confirmation": False},
        )
        assert resp_fail.status_code == 422
    finally:
        reset_llm_provider()


@pytest.mark.asyncio
async def test_13_approval_records_audit_log_entry(
    client: AsyncClient, test_session: AsyncSession
):
    """13. Approval records audit log entry with timestamp and user ID."""
    token, user_id = await register_and_login(client, "prep.audit@test.com", "Audit User")
    await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_package())
    override_llm_provider(mock)

    try:
        resp_create = await client.post(
            "/api/v1/applications/prepare",
            headers={"Authorization": f"Bearer {token}"},
            json={"target_job_id": str(job.id)},
        )
        package_id = uuid.UUID(resp_create.json()["id"])

        await client.post(
            f"/api/v1/applications/packages/{package_id}/approve",
            headers={"Authorization": f"Bearer {token}"},
            json={"user_confirmation": True},
        )

        # Check AuditLog table
        log_entry = await test_session.scalar(
            select(AuditLog).where(
                AuditLog.user_id == user_id,
                AuditLog.action_type == "APPLICATION_PACKAGE_APPROVED",
                AuditLog.target_entity_id == package_id,
            )
        )
        assert log_entry is not None
        assert log_entry.human_approved is True
        assert log_entry.created_at is not None
    finally:
        reset_llm_provider()


@pytest.mark.asyncio
async def test_14_application_not_automatically_submitted_upon_approval(
    client: AsyncClient, test_session: AsyncSession
):
    """14. Application is NOT automatically submitted upon approval."""
    token, user_id = await register_and_login(client, "prep.noautosub@test.com", "No Auto Sub")
    await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_package())
    override_llm_provider(mock)

    try:
        resp_create = await client.post(
            "/api/v1/applications/prepare",
            headers={"Authorization": f"Bearer {token}"},
            json={"target_job_id": str(job.id)},
        )
        package_id = resp_create.json()["id"]

        resp_approve = await client.post(
            f"/api/v1/applications/packages/{package_id}/approve",
            headers={"Authorization": f"Bearer {token}"},
            json={"user_confirmation": True},
        )
        assert resp_approve.status_code == 200
        data = resp_approve.json()
        assert data["status"] == "approved"
        assert data["user_confirmed_submission"] is False
        assert data["submitted_at"] is None
    finally:
        reset_llm_provider()


@pytest.mark.asyncio
async def test_15_candidate_confirms_external_submission(
    client: AsyncClient, test_session: AsyncSession
):
    """15. User confirms completion of official application submission; status transitions to 'submitted'."""
    token, user_id = await register_and_login(client, "prep.subconfirm@test.com", "Confirm Sub User")
    await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_package())
    override_llm_provider(mock)

    try:
        resp_create = await client.post(
            "/api/v1/applications/prepare",
            headers={"Authorization": f"Bearer {token}"},
            json={"target_job_id": str(job.id)},
        )
        package_id = resp_create.json()["id"]

        # Approve and handoff first
        await client.post(
            f"/api/v1/applications/packages/{package_id}/approve",
            headers={"Authorization": f"Bearer {token}"},
            json={"user_confirmation": True},
        )
        await client.post(
            f"/api/v1/applications/packages/{package_id}/handoff",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Confirm submission
        resp_confirm = await client.post(
            f"/api/v1/applications/packages/{package_id}/confirm-submission",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "user_confirmation": True,
                "notes": "Applied directly on FinTech Global careers portal.",
            },
        )
        assert resp_confirm.status_code == 200
        data = resp_confirm.json()
        assert data["status"] == "submitted"
        assert data["user_confirmed_submission"] is True
        assert data["submitted_at"] is not None

        # Check linked Application model is marked 'applied'
        app_record = await test_session.scalar(
            select(Application).where(Application.id == uuid.UUID(data["application_id"]))
        )
        assert app_record.current_status == "applied"
    finally:
        reset_llm_provider()


@pytest.mark.asyncio
async def test_16_submission_confirmation_idempotent(
    client: AsyncClient, test_session: AsyncSession
):
    """16. Submission confirmation is idempotent and records submission timestamp."""
    token, user_id = await register_and_login(client, "prep.idempotent@test.com", "Idempotent User")
    await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_package())
    override_llm_provider(mock)

    try:
        resp_create = await client.post(
            "/api/v1/applications/prepare",
            headers={"Authorization": f"Bearer {token}"},
            json={"target_job_id": str(job.id)},
        )
        package_id = resp_create.json()["id"]

        await client.post(
            f"/api/v1/applications/packages/{package_id}/approve",
            headers={"Authorization": f"Bearer {token}"},
            json={"user_confirmation": True},
        )

        # First confirm
        r1 = await client.post(
            f"/api/v1/applications/packages/{package_id}/confirm-submission",
            headers={"Authorization": f"Bearer {token}"},
            json={"user_confirmation": True},
        )
        assert r1.status_code == 200
        first_sub_at = r1.json()["submitted_at"]

        # Duplicate confirm should succeed idempotently
        r2 = await client.post(
            f"/api/v1/applications/packages/{package_id}/confirm-submission",
            headers={"Authorization": f"Bearer {token}"},
            json={"user_confirmation": True},
        )
        assert r2.status_code == 200
        assert r2.json()["submitted_at"] == first_sub_at
    finally:
        reset_llm_provider()


# ─── Tests 17-27: Recruiter Outreach & Bounded Length ────────────────────────

@pytest.mark.asyncio
async def test_17_recruiter_outreach_generation_under_90_words(
    client: AsyncClient, test_session: AsyncSession
):
    """17. Recruiter outreach generation produces draft <= 90 words."""
    token, user_id = await register_and_login(client, "outreach.under90@test.com", "Outreach User")
    await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_outreach(word_count=50))
    override_llm_provider(mock)

    try:
        resp = await client.post(
            "/api/v1/recruiters/outreach",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "job_id": str(job.id),
                "outreach_channel": "recruiter_inmail",
                "recruiter_name": "Jane",
            },
        )
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["word_count"] <= 90
        assert len(data["message_body"].split()) <= 90
        assert data["status"] == "draft"
    finally:
        reset_llm_provider()


@pytest.mark.asyncio
async def test_18_outreach_length_validation_rejects_exceeding_90_words(
    client: AsyncClient, test_session: AsyncSession
):
    """18. Outreach draft length validation rejects edits exceeding 90 words."""
    token, user_id = await register_and_login(client, "outreach.wordlimit@test.com", "Limit User")
    await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_outreach())
    override_llm_provider(mock)

    try:
        resp_create = await client.post(
            "/api/v1/recruiters/outreach",
            headers={"Authorization": f"Bearer {token}"},
            json={"job_id": str(job.id)},
        )
        draft_id = resp_create.json()["id"]

        # Attempt to edit with a 100-word body
        excessive_body = " ".join(["word"] * 105)
        resp_edit = await client.put(
            f"/api/v1/recruiters/outreach/{draft_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"message_body": excessive_body},
        )
        assert resp_edit.status_code == 422
        assert "must not exceed 90 words" in resp_edit.text
    finally:
        reset_llm_provider()


@pytest.mark.asyncio
async def test_19_outreach_no_fabricated_contact_or_names(
    client: AsyncClient, test_session: AsyncSession
):
    """19. Outreach draft contains NO fabricated contact info, recruiter names, or ungrounded claims."""
    token, user_id = await register_and_login(client, "outreach.nofake@test.com", "No Fake User")
    await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    # Provide outreach without candidate providing recruiter name/email
    mock.set_structured_response(mock_successful_ai_outreach(recruiter_name=None))
    override_llm_provider(mock)

    try:
        resp = await client.post(
            "/api/v1/recruiters/outreach",
            headers={"Authorization": f"Bearer {token}"},
            json={"job_id": str(job.id)},
        )
        assert resp.status_code == 201
        data = resp.json()
        # Backend must not invent a fabricated recruiter email or name
        assert data["recruiter_contact_info"] is None
        assert data["recruiter_name"] is None
        assert data["recruiter_profile_url"] is None
    finally:
        reset_llm_provider()


@pytest.mark.asyncio
async def test_20_outreach_draft_persisted_with_initial_status_draft(
    client: AsyncClient, test_session: AsyncSession
):
    """20. Outreach draft is persisted with initial status 'draft'."""
    token, user_id = await register_and_login(client, "outreach.persist@test.com", "Persist User")
    await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_outreach())
    override_llm_provider(mock)

    try:
        resp = await client.post(
            "/api/v1/recruiters/outreach",
            headers={"Authorization": f"Bearer {token}"},
            json={"job_id": str(job.id)},
        )
        draft_id = resp.json()["id"]

        resp_get = await client.get(
            f"/api/v1/recruiters/outreach/{draft_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp_get.status_code == 200
        assert resp_get.json()["status"] == "draft"
    finally:
        reset_llm_provider()


@pytest.mark.asyncio
async def test_21_maximum_3_outreach_drafts_enforced_by_backend(
    client: AsyncClient, test_session: AsyncSession
):
    """21. Maximum 3 outreach drafts per application enforced by backend."""
    token, user_id = await register_and_login(client, "outreach.max3@test.com", "Max3 User")
    await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_outreach())
    override_llm_provider(mock)

    try:
        # Create 3 drafts
        for _ in range(3):
            r = await client.post(
                "/api/v1/recruiters/outreach",
                headers={"Authorization": f"Bearer {token}"},
                json={"job_id": str(job.id)},
            )
            assert r.status_code == 201

        # Attempt to create 4th draft -> 422 limit exceeded
        r_fourth = await client.post(
            "/api/v1/recruiters/outreach",
            headers={"Authorization": f"Bearer {token}"},
            json={"job_id": str(job.id)},
        )
        assert r_fourth.status_code == 422
        assert "Maximum limit of 3 recruiter outreach drafts" in r_fourth.text
    finally:
        reset_llm_provider()


@pytest.mark.asyncio
async def test_22_candidate_can_update_outreach_draft(
    client: AsyncClient, test_session: AsyncSession
):
    """22. Candidate can update/edit outreach draft."""
    token, user_id = await register_and_login(client, "outreach.update@test.com", "Update User")
    await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_outreach())
    override_llm_provider(mock)

    try:
        resp_create = await client.post(
            "/api/v1/recruiters/outreach",
            headers={"Authorization": f"Bearer {token}"},
            json={"job_id": str(job.id)},
        )
        draft_id = resp_create.json()["id"]

        updated_msg = "Hi Sarah, saw the Lead Backend role at FinTech Global. Would love to connect regarding Python microservices."
        resp_update = await client.put(
            f"/api/v1/recruiters/outreach/{draft_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "message_body": updated_msg,
                "recruiter_name": "Sarah",
            },
        )
        assert resp_update.status_code == 200
        data = resp_update.json()
        assert data["message_body"] == updated_msg
        assert data["recruiter_name"] == "Sarah"
        assert data["word_count"] == len(updated_msg.split())
    finally:
        reset_llm_provider()


@pytest.mark.asyncio
async def test_23_candidate_editing_resets_outreach_approval(
    client: AsyncClient, test_session: AsyncSession
):
    """23. Candidate editing resets outreach approval status."""
    token, user_id = await register_and_login(client, "outreach.resetapp@test.com", "Reset App User")
    await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_outreach())
    override_llm_provider(mock)

    try:
        resp_create = await client.post(
            "/api/v1/recruiters/outreach",
            headers={"Authorization": f"Bearer {token}"},
            json={"job_id": str(job.id)},
        )
        draft_id = resp_create.json()["id"]

        # Approve
        await client.post(
            f"/api/v1/recruiters/outreach/{draft_id}/approve",
            headers={"Authorization": f"Bearer {token}"},
            json={"user_confirmation": True},
        )

        # Edit -> should transition status to awaiting_approval
        resp_edit = await client.put(
            f"/api/v1/recruiters/outreach/{draft_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"candidate_notes": "Added notes"},
        )
        assert resp_edit.status_code == 200
        assert resp_edit.json()["status"] == "awaiting_approval"
    finally:
        reset_llm_provider()


@pytest.mark.asyncio
async def test_24_candidate_can_approve_outreach_draft(
    client: AsyncClient, test_session: AsyncSession
):
    """24. Candidate can approve outreach draft (explicit approval gate)."""
    token, user_id = await register_and_login(client, "outreach.appr@test.com", "Appr User")
    await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_outreach())
    override_llm_provider(mock)

    try:
        resp_create = await client.post(
            "/api/v1/recruiters/outreach",
            headers={"Authorization": f"Bearer {token}"},
            json={"job_id": str(job.id)},
        )
        draft_id = resp_create.json()["id"]

        resp_approve = await client.post(
            f"/api/v1/recruiters/outreach/{draft_id}/approve",
            headers={"Authorization": f"Bearer {token}"},
            json={"user_confirmation": True},
        )
        assert resp_approve.status_code == 200
        data = resp_approve.json()
        assert data["status"] == "approved"
        assert data["approved_at"] is not None
    finally:
        reset_llm_provider()


@pytest.mark.asyncio
async def test_25_approved_outreach_draft_provides_manual_handoff(
    client: AsyncClient, test_session: AsyncSession
):
    """25. Approved outreach draft provides manual handoff (mailto, profile URL, or copy text)."""
    token, user_id = await register_and_login(client, "outreach.handoff@test.com", "Handoff User")
    await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_outreach())
    override_llm_provider(mock)

    try:
        resp_create = await client.post(
            "/api/v1/recruiters/outreach",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "job_id": str(job.id),
                "recruiter_contact_info": "recruiter@fintechglobal.example.com",
            },
        )
        draft_id = resp_create.json()["id"]

        # Handoff on unapproved draft -> 409 Conflict
        r_unapproved = await client.post(
            f"/api/v1/recruiters/outreach/{draft_id}/handoff",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r_unapproved.status_code == 409

        # Approve draft
        await client.post(
            f"/api/v1/recruiters/outreach/{draft_id}/approve",
            headers={"Authorization": f"Bearer {token}"},
            json={"user_confirmation": True},
        )

        # Handoff succeeds
        r_handoff = await client.post(
            f"/api/v1/recruiters/outreach/{draft_id}/handoff",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r_handoff.status_code == 200
        handoff_data = r_handoff.json()
        assert handoff_data["mailto_uri"] is not None
        assert "mailto:recruiter@fintechglobal.example.com" in handoff_data["mailto_uri"]
        assert handoff_data["clipboard_text"] is not None
        assert handoff_data["status"] in ("handoff_initiated", "handoff_ready")
    finally:
        reset_llm_provider()


@pytest.mark.asyncio
async def test_26_outreach_not_automatically_sent_upon_approval(
    client: AsyncClient, test_session: AsyncSession
):
    """26. Recruiter outreach is NOT automatically sent upon approval."""
    token, user_id = await register_and_login(client, "outreach.nosend@test.com", "No Send User")
    await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_outreach())
    override_llm_provider(mock)

    try:
        resp_create = await client.post(
            "/api/v1/recruiters/outreach",
            headers={"Authorization": f"Bearer {token}"},
            json={"job_id": str(job.id)},
        )
        draft_id = resp_create.json()["id"]

        resp_approve = await client.post(
            f"/api/v1/recruiters/outreach/{draft_id}/approve",
            headers={"Authorization": f"Bearer {token}"},
            json={"user_confirmation": True},
        )
        assert resp_approve.status_code == 200
        data = resp_approve.json()
        assert data["status"] == "approved"
        assert data["user_confirmed_sent"] is False
        assert data["sent_at"] is None
    finally:
        reset_llm_provider()


@pytest.mark.asyncio
async def test_27_candidate_confirms_outreach_sent(
    client: AsyncClient, test_session: AsyncSession
):
    """27. User confirms recruiter outreach sent; status transitions to 'sent'."""
    token, user_id = await register_and_login(client, "outreach.confirmsent@test.com", "Sent Confirm User")
    await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_outreach())
    override_llm_provider(mock)

    try:
        resp_create = await client.post(
            "/api/v1/recruiters/outreach",
            headers={"Authorization": f"Bearer {token}"},
            json={"job_id": str(job.id)},
        )
        draft_id = resp_create.json()["id"]

        await client.post(
            f"/api/v1/recruiters/outreach/{draft_id}/approve",
            headers={"Authorization": f"Bearer {token}"},
            json={"user_confirmation": True},
        )

        resp_sent = await client.post(
            f"/api/v1/recruiters/outreach/{draft_id}/confirm-sent",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "user_confirmation": True,
                "notes": "Sent via LinkedIn InMail.",
            },
        )
        assert resp_sent.status_code == 200
        data = resp_sent.json()
        assert data["status"] == "sent"
        assert data["user_confirmed_sent"] is True
        assert data["sent_at"] is not None
    finally:
        reset_llm_provider()


# ─── Tests 28-30: Deletion & Cross-User Security Isolations ──────────────────

@pytest.mark.asyncio
async def test_28_outreach_deletion_restricted_to_owner(
    client: AsyncClient, test_session: AsyncSession
):
    """28. Outreach draft deletion is restricted to owning user."""
    token_a, user_a = await register_and_login(client, "outreach.delA@test.com", "Del User A")
    token_b, user_b = await register_and_login(client, "outreach.delB@test.com", "Del User B")

    await create_parsed_test_resume(test_session, user_a)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_outreach())
    override_llm_provider(mock)

    try:
        resp_create = await client.post(
            "/api/v1/recruiters/outreach",
            headers={"Authorization": f"Bearer {token_a}"},
            json={"job_id": str(job.id)},
        )
        draft_id = resp_create.json()["id"]

        # User B attempts to delete User A's draft -> 404 or 403
        r_del_unauth = await client.delete(
            f"/api/v1/recruiters/outreach/{draft_id}",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert r_del_unauth.status_code in (403, 404)

        # User A deletes their own draft -> 204
        r_del_auth = await client.delete(
            f"/api/v1/recruiters/outreach/{draft_id}",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert r_del_auth.status_code == 204
    finally:
        reset_llm_provider()


@pytest.mark.asyncio
async def test_29_cross_user_isolation_packages(
    client: AsyncClient, test_session: AsyncSession
):
    """29. Cross-user access prevention: User A cannot view, edit, approve, or delete User B's application packages."""
    token_a, user_a = await register_and_login(client, "iso.pkgA@test.com", "Pkg User A")
    token_b, user_b = await register_and_login(client, "iso.pkgB@test.com", "Pkg User B")

    await create_parsed_test_resume(test_session, user_a)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_package())
    override_llm_provider(mock)

    try:
        resp_create = await client.post(
            "/api/v1/applications/prepare",
            headers={"Authorization": f"Bearer {token_a}"},
            json={"target_job_id": str(job.id)},
        )
        package_id = resp_create.json()["id"]

        # User B attempts GET
        r_get = await client.get(
            f"/api/v1/applications/packages/{package_id}",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert r_get.status_code in (403, 404)

        # User B attempts PUT
        r_put = await client.put(
            f"/api/v1/applications/packages/{package_id}",
            headers={"Authorization": f"Bearer {token_b}"},
            json={"cover_note": "Hacked cover note"},
        )
        assert r_put.status_code in (403, 404)

        # User B attempts APPROVE
        r_app = await client.post(
            f"/api/v1/applications/packages/{package_id}/approve",
            headers={"Authorization": f"Bearer {token_b}"},
            json={"user_confirmation": True},
        )
        assert r_app.status_code in (403, 404)
    finally:
        reset_llm_provider()


@pytest.mark.asyncio
async def test_30_cross_user_isolation_outreach(
    client: AsyncClient, test_session: AsyncSession
):
    """30. Cross-user access prevention: User A cannot view, edit, approve, or delete User B's outreach drafts."""
    token_a, user_a = await register_and_login(client, "iso.outA@test.com", "Out User A")
    token_b, user_b = await register_and_login(client, "iso.outB@test.com", "Out User B")

    await create_parsed_test_resume(test_session, user_a)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_outreach())
    override_llm_provider(mock)

    try:
        resp_create = await client.post(
            "/api/v1/recruiters/outreach",
            headers={"Authorization": f"Bearer {token_a}"},
            json={"job_id": str(job.id)},
        )
        draft_id = resp_create.json()["id"]

        # User B attempts GET
        r_get = await client.get(
            f"/api/v1/recruiters/outreach/{draft_id}",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert r_get.status_code in (403, 404)

        # User B attempts PUT
        r_put = await client.put(
            f"/api/v1/recruiters/outreach/{draft_id}",
            headers={"Authorization": f"Bearer {token_b}"},
            json={"message_body": "Hacked message"},
        )
        assert r_put.status_code in (403, 404)

        # User B attempts APPROVE
        r_app = await client.post(
            f"/api/v1/recruiters/outreach/{draft_id}/approve",
            headers={"Authorization": f"Bearer {token_b}"},
            json={"user_confirmation": True},
        )
        assert r_app.status_code in (403, 404)
    finally:
        reset_llm_provider()


# ─── Tests 31-33: AI Error Resilience & Malformed Output ────────────────────

@pytest.mark.asyncio
async def test_31_ai_provider_failure_package_prep_returns_503(
    client: AsyncClient, test_session: AsyncSession
):
    """31. AI provider failure during package preparation returns 503 and leaves no corrupt state."""
    token, user_id = await register_and_login(client, "resilience.failpkg@test.com", "Fail Pkg User")
    await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    class FailingProvider(MockLLMProvider):
        async def generate_structured(self, *args, **kwargs):
            raise ServiceUnavailableException("Gemini", "Inference deadline exceeded after 30s.")

    override_llm_provider(FailingProvider())

    try:
        resp = await client.post(
            "/api/v1/applications/prepare",
            headers={"Authorization": f"Bearer {token}"},
            json={"target_job_id": str(job.id)},
        )
        assert resp.status_code == 503
        assert "Service Unavailable" in resp.text or "Inference deadline exceeded" in resp.text

        # Verify no corrupt package was persisted
        packages = await test_session.scalars(
            select(ApplicationPackage).where(ApplicationPackage.user_id == user_id)
        )
        assert len(packages.all()) == 0
    finally:
        reset_llm_provider()


@pytest.mark.asyncio
async def test_32_ai_provider_failure_outreach_returns_503(
    client: AsyncClient, test_session: AsyncSession
):
    """32. AI provider failure during outreach drafting returns 503 and leaves no corrupt state."""
    token, user_id = await register_and_login(client, "resilience.failout@test.com", "Fail Out User")
    await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    class FailingProvider(MockLLMProvider):
        async def generate_structured(self, *args, **kwargs):
            raise ServiceUnavailableException("Gemini", "Quota limit exceeded (429).")

    override_llm_provider(FailingProvider())

    try:
        resp = await client.post(
            "/api/v1/recruiters/outreach",
            headers={"Authorization": f"Bearer {token}"},
            json={"job_id": str(job.id)},
        )
        assert resp.status_code == 503

        # Verify no draft was persisted
        drafts = await test_session.scalars(
            select(RecruiterOutreachDraft).where(RecruiterOutreachDraft.user_id == user_id)
        )
        assert len(drafts.all()) == 0
    finally:
        reset_llm_provider()


@pytest.mark.asyncio
async def test_33_malformed_ai_response_handled_gracefully(
    client: AsyncClient, test_session: AsyncSession
):
    """33. Malformed AI responses are handled gracefully with appropriate error messages."""
    token, user_id = await register_and_login(client, "resilience.malformed@test.com", "Malformed User")
    await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    # Missing required keys 'cover_note' and 'question_answers'
    mock.set_structured_response({"unrecognized_payload": "corrupted text"})
    override_llm_provider(mock)

    try:
        resp = await client.post(
            "/api/v1/applications/prepare",
            headers={"Authorization": f"Bearer {token}"},
            json={"target_job_id": str(job.id)},
        )
        assert resp.status_code == 503
        assert "SERVICE_UNAVAILABLE" in resp.text or "validation error" in resp.text

        # Verify zero corrupt packages were persisted
        packages = await test_session.scalars(
            select(ApplicationPackage).where(ApplicationPackage.user_id == user_id)
        )
        assert len(packages.all()) == 0
    finally:
        reset_llm_provider()
