"""
Comprehensive Test Suite for Phase 10A: Resume Tailoring & Optimization Backend.
Validates:
1. Successful tailored draft generation using controlled provider mock.
2. Real Gemini integration test (marked BLOCKED / NOT TESTED if API key/network unavailable).
3. Missing or invalid source resume.
4. Missing or insufficient target job description.
5. Cross-user access prevention (User A cannot view User B's resume or tailored draft).
6. Cross-user modification and deletion prevention (User A cannot edit or delete User B's draft).
7. Original resume immutability (source resume remains byte-for-byte identical).
8. Multiple tailored versions sequential numbering without overwriting.
9. Invalid structured AI output safely rejected.
10. Anti-hallucination verification: unsupported skills and fabricated employers pruned and flagged.
11. Gemini timeout, quota, and provider error handling (HTTP 503, zero corrupt records).
12. Draft lifecycle: starts as draft, never auto-approved, explicit approval gate required.
13. Draft editing permitted, prohibited once approved (HTTP 409).
14. Visual diff and optimization analysis endpoints return structured diagnostics.
15. Direct job description text tailoring (auto-ingestion workflow).
"""
from __future__ import annotations

import io
import os
import uuid
from typing import Any, Dict, List, Optional, Tuple
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.factory import override_llm_provider, reset_llm_provider
from app.ai.mock_adapter import MockLLMProvider
from app.core.config import settings
from app.core.exceptions import ServiceUnavailableException
from app.db.seeds.gap_analysis_seeder import seed_skill_taxonomy_and_roles
from app.models.jobs import Job, JobSkill, JobSource
from app.models.resume import Resume, ResumeVersion
from app.models.skills import Skill, UserSkill
from app.schemas.resume import (
    ExtractedEducation,
    ExtractedExperience,
    ExtractedPersonalInfo,
    ExtractedProject,
    ExtractedResumeSchema,
    ExtractedSkill,
    StructuredChangeItem,
)


# ─── Test Helpers ───────────────────────────────────────────────────

@pytest.fixture(autouse=True)
async def seed_base_data(test_session: AsyncSession):
    """Seeds canonical roles, skills, and job sources required for relational integrity."""
    await seed_skill_taxonomy_and_roles(test_session)
    for name, p_type in [("seed", "seed"), ("manual", "manual"), ("mock", "mock")]:
        source = await test_session.scalar(select(JobSource).where(JobSource.name == name))
        if not source:
            source = JobSource(
                name=name,
                provider_type=p_type,
                is_active=True,
            )
            test_session.add(source)
    await test_session.commit()


async def register_and_login(client: AsyncClient, email: str, name: str) -> Tuple[str, uuid.UUID]:
    """Registers and logs in a test candidate, returning access token and user_id."""
    pw = "TailorPassword123!"
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
    file_name: str = "Candidate_Resume.pdf",
    skills: list[str] | None = None,
    employers: list[str] | None = None,
) -> Resume:
    """Directly creates a verified parsed Resume in the database with known entities."""
    skill_names = skills or ["Python", "FastAPI", "PostgreSQL", "Docker"]
    employer_names = employers or ["Acme Cloud Corp"]

    extracted_data = {
        "personal_info": {
            "name": "Alex Mercer",
            "email": "alex.mercer@test.com",
            "phone": "+1-555-0199",
            "location": "San Francisco, CA",
        },
        "executive_summary": "Experienced backend engineer focused on high-scale distributed systems.",
        "skills": [{"name": s, "category": "technical"} for s in skill_names],
        "experience": [
            {
                "employer": emp,
                "job_title": "Senior Backend Developer",
                "start_date": "2020-01",
                "end_date": "Present",
                "is_current": True,
                "responsibilities": ["Designed REST and gRPC microservices in Python."],
                "achievements": ["Maintained 99.99% service uptime across core APIs."],
            }
            for emp in employer_names
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
                "description": "API Gateway built with FastAPI and Redis caching.",
                "technologies": ["Python", "FastAPI", "Redis"],
            }
        ],
        "certifications": [],
    }

    resume = Resume(
        id=uuid.uuid4(),
        user_id=user_id,
        file_name=file_name,
        storage_path=f"uploads/{uuid.uuid4()}.pdf",
        file_size_bytes=1024,
        mime_type="application/pdf",
        status="parsed",
        parsed_text="Alex Mercer. Experienced backend engineer. Python, FastAPI, PostgreSQL, Docker.",
        extracted_data=extracted_data,
        is_primary=True,
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)
    return resume


async def create_test_job(
    db: AsyncSession,
    title: str = "Lead Backend Engineer",
    company: str = "FinTech Global",
    description: str = (
        "FinTech Global is seeking a Lead Backend Engineer to build resilient distributed payment gateways. "
        "Required Qualifications: 5+ years with Python, PostgreSQL, and Docker. Experience with microservices."
    ),
    required_skills: list[str] | None = None,
) -> Job:
    """Creates a catalog Job record with skills."""
    req_skills = required_skills or ["python", "postgresql", "docker"]
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
        description_markdown=description,
        responsibilities=["Build high-volume payment processing pipelines.", "Maintain database reliability."],
        required_qualifications=["Proficiency in Python and PostgreSQL.", "Docker container orchestration."],
        preferred_qualifications=["FastAPI experience.", "Knowledge of PCI-DSS compliance."],
        application_url="https://example.com/apply",
        is_active=True,
        freshness_status="active",
    )
    db.add(job)
    await db.flush()

    for s_id in req_skills:
        js = JobSkill(
            job_id=job.id,
            skill_id=s_id,
            is_mandatory=True,
            confidence_score=1.0,
        )
        db.add(js)

    await db.commit()
    await db.refresh(job)
    return job


def mock_successful_ai_tailoring(
    include_fake_skill: bool = False,
    include_fake_employer: bool = False,
) -> dict:
    """Builds a realistic mock structured response matching AITailoredResumeOutput."""
    skills = [
        {"name": "Python", "category": "language"},
        {"name": "FastAPI", "category": "framework"},
        {"name": "PostgreSQL", "category": "database"},
        {"name": "Docker", "category": "tool"},
    ]
    if include_fake_skill:
        skills.append({"name": "FictitiousTechnology123", "category": "tool"})

    employers = [
        {
            "employer": "Acme Cloud Corp",
            "job_title": "Senior Backend Developer",
            "start_date": "2020-01",
            "end_date": "Present",
            "is_current": True,
            "responsibilities": ["Designed high-performance payment microservices in Python."],
            "achievements": ["Maintained 99.99% service uptime across core transaction APIs."],
        }
    ]
    if include_fake_employer:
        employers.append({
            "employer": "HallucinatedFakeCorp Inc",
            "job_title": "Lead Architect",
            "start_date": "2018-01",
            "end_date": "2019-12",
            "is_current": False,
            "responsibilities": ["Invented fictional blockchain."],
            "achievements": ["Fictitious revenue increase."],
        })

    return {
        "tailored_resume": {
            "personal_info": {
                "name": "Alex Mercer",
                "email": "alex.mercer@test.com",
                "phone": "+1-555-0199",
                "location": "San Francisco, CA",
            },
            "executive_summary": (
                "Backend engineer with deep expertise in Python, FastAPI, and PostgreSQL, "
                "specializing in resilient payment infrastructure."
            ),
            "skills": skills,
            "experience": employers,
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
                    "description": "High-throughput API Gateway with FastAPI and Redis caching.",
                    "technologies": ["Python", "FastAPI", "Redis"],
                }
            ],
            "certifications": [],
        },
        "changes": [
            {
                "id": "chg_1",
                "section": "executive_summary",
                "change_type": "rephrasing",
                "original_text": "Experienced backend engineer focused on high-scale distributed systems.",
                "proposed_text": "Backend engineer specializing in resilient payment infrastructure.",
                "rationale": "Directly highlights payment processing focus required by the role.",
                "target_job_requirement": "Build high-volume payment processing pipelines",
                "supporting_evidence": "Source resume summary and API experience",
                "needs_clarification": False,
            },
            {
                "id": "chg_2",
                "section": "experience",
                "change_type": "emphasis",
                "original_text": "Designed REST and gRPC microservices in Python.",
                "proposed_text": "Designed high-performance payment microservices in Python.",
                "rationale": "Clarifies payment domain relevance from candidate background.",
                "target_job_requirement": "Maintain database reliability and microservices",
                "supporting_evidence": "Acme Cloud Corp experience",
                "needs_clarification": False,
            },
        ],
        "matched_keywords": ["python", "postgresql", "docker", "fastapi", "microservices"],
        "missing_keywords": ["pci-dss", "kubernetes"],
        "supported_skills": ["Python", "PostgreSQL", "Docker", "FastAPI"],
        "missing_requirements": ["PCI-DSS Compliance Certification"],
        "readability_score": 92.0,
        "formatting_recommendations": ["Highlight payment pipeline achievements at the top of experience section."],
        "actionable_suggestions": ["Complete the Cloud Computing Diagnostic Assessment to confirm AWS competencies."],
        "unsupported_claims": [],
    }


# ─── 1. Successful Tailored Draft Generation (Mock) ───────────────────

@pytest.mark.asyncio
async def test_successful_tailored_draft_generation_mock(
    client: AsyncClient,
    test_session: AsyncSession,
):
    """Verifies end-to-end draft generation using MockLLMProvider."""
    token, user_id = await register_and_login(client, "tailor.success@test.com", "Alex Mercer")
    resume = await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_tailoring())
    override_llm_provider(mock)

    try:
        r = await client.post(
            f"/api/v1/resume/{resume.id}/tailor",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "job_id": str(job.id),
                "target_emphasis": ["payment systems", "high availability"],
                "user_notes": "Targeting senior backend position",
            },
        )
        assert r.status_code == 201
        data = r.json()

        assert "id" in data
        assert data["resume_id"] == str(resume.id)
        assert data["target_job_id"] == str(job.id)
        assert data["version_number"] == 1
        assert data["status"] == "draft"  # Starts in draft state
        assert data["approved_at"] is None  # Not auto-approved
        assert data["anti_hallucination_verified"] is True

        # Check tailored content
        tailored = data["tailored_content"]
        assert "payment infrastructure" in tailored["executive_summary"]
        assert len(tailored["skills"]) == 4

        # Check diff summary & optimization
        diff = data["diff_summary"]
        assert len(diff["changes"]) == 2
        assert diff["optimization_analysis"]["keyword_coverage"] > 0.0
        assert "pci-dss" in [k.lower() for k in diff["optimization_analysis"]["missing_keywords"]]

    finally:
        reset_llm_provider()


# ─── 2. Real Gemini Integration / Blocked Status ──────────────────────

@pytest.mark.asyncio
async def test_real_gemini_integration_or_blocked_status(
    client: AsyncClient,
    test_session: AsyncSession,
):
    """
    Attempts live Gemini integration if configured with valid key and network.
    If unconfigured or offline, explicitly records status as BLOCKED / NOT TESTED.
    """
    api_key = settings.GEMINI_API_KEY
    if not api_key or api_key.startswith("test-") or api_key == "":
        pytest.skip("GEMINI_API_KEY not configured in environment. Marked: BLOCKED / NOT TESTED for live Gemini calls.")

    # Live integration branch (if key is present)
    token, user_id = await register_and_login(client, "tailor.live@test.com", "Live User")
    resume = await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    r = await client.post(
        f"/api/v1/resume/{resume.id}/tailor",
        headers={"Authorization": f"Bearer {token}"},
        json={"job_id": str(job.id)},
    )
    if r.status_code == 503:
        pytest.skip(f"Live Gemini provider returned 503 in test sandbox ({r.json()}). Status: BLOCKED / NOT TESTED.")
    assert r.status_code == 201


# ─── 3. Missing or Invalid Source Resume ──────────────────────────────

@pytest.mark.asyncio
async def test_missing_or_invalid_source_resume(
    client: AsyncClient,
    test_session: AsyncSession,
):
    """Verifies clear HTTP 404 for nonexistent resume, and HTTP 400 for unparsed resume."""
    token, user_id = await register_and_login(client, "tailor.invalidres@test.com", "Invalid Res User")
    job = await create_test_job(test_session)
    nonexistent_id = uuid.uuid4()

    # Nonexistent resume
    r_nonexistent = await client.post(
        f"/api/v1/resume/{nonexistent_id}/tailor",
        headers={"Authorization": f"Bearer {token}"},
        json={"job_id": str(job.id)},
    )
    assert r_nonexistent.status_code == 404
    err_body = r_nonexistent.json()
    err_code = err_body.get("error", {}).get("code") or err_body.get("code", "")
    assert "NOT_FOUND" in err_code

    # Resume in 'uploaded' (not yet parsed) status
    unparsed_resume = Resume(
        id=uuid.uuid4(),
        user_id=user_id,
        file_name="raw.pdf",
        storage_path="uploads/raw.pdf",
        file_size_bytes=500,
        mime_type="application/pdf",
        status="uploaded",  # Not parsed!
    )
    test_session.add(unparsed_resume)
    await test_session.commit()

    r_unparsed = await client.post(
        f"/api/v1/resume/{unparsed_resume.id}/tailor",
        headers={"Authorization": f"Bearer {token}"},
        json={"job_id": str(job.id)},
    )
    assert r_unparsed.status_code == 400
    msg = r_unparsed.json().get("error", {}).get("message") or r_unparsed.json().get("detail", "")
    assert "status" in msg.lower()


# ─── 4. Missing or Insufficient Target Job Description ─────────────────

@pytest.mark.asyncio
async def test_missing_or_insufficient_target_job_description(
    client: AsyncClient,
    test_session: AsyncSession,
):
    """Verifies HTTP 404 for nonexistent job, and HTTP 422 for insufficient description."""
    token, user_id = await register_and_login(client, "tailor.badjob@test.com", "Bad Job User")
    resume = await create_parsed_test_resume(test_session, user_id)

    # 1. Nonexistent job
    r_no_job = await client.post(
        f"/api/v1/resume/{resume.id}/tailor",
        headers={"Authorization": f"Bearer {token}"},
        json={"job_id": str(uuid.uuid4())},
    )
    assert r_no_job.status_code == 404

    # 2. Insufficient job description (< 50 characters)
    short_job = Job(
        id=uuid.uuid4(),
        external_id=f"short_{uuid.uuid4().hex[:6]}",
        source="seed",
        source_url="https://example.com/jobs/short",
        title="Developer",
        company_name="Short Corp",
        location="Remote",
        normalized_location="remote",
        remote_type="remote",
        employment_type="full_time",
        role_id="backend-developer",
        experience_level="mid",
        description_markdown="Need dev.",  # Only 9 chars!
        application_url="https://example.com/apply",
        is_active=True,
    )
    test_session.add(short_job)
    await test_session.commit()

    r_short = await client.post(
        f"/api/v1/resume/{resume.id}/tailor",
        headers={"Authorization": f"Bearer {token}"},
        json={"job_id": str(short_job.id)},
    )
    assert r_short.status_code == 422
    err_msg = r_short.json().get("error", {}).get("message") or r_short.json().get("detail", "")
    assert "insufficient" in err_msg.lower()


# ─── 5. Cross-User Access Prevention ──────────────────────────────────

@pytest.mark.asyncio
async def test_cross_user_isolation_cannot_tailor_or_view_others(
    client: AsyncClient,
    test_session: AsyncSession,
):
    """User B cannot tailor User A's resume or view User A's tailored version."""
    token_a, user_a_id = await register_and_login(client, "candidate.a@test.com", "Candidate A")
    token_b, user_b_id = await register_and_login(client, "candidate.b@test.com", "Candidate B")

    resume_a = await create_parsed_test_resume(test_session, user_a_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_tailoring())
    override_llm_provider(mock)

    try:
        # User B attempts to tailor User A's resume -> 403 Forbidden
        r_tailor_unauth = await client.post(
            f"/api/v1/resume/{resume_a.id}/tailor",
            headers={"Authorization": f"Bearer {token_b}"},
            json={"job_id": str(job.id)},
        )
        assert r_tailor_unauth.status_code == 403

        # User A tailors their own resume
        r_tailor_auth = await client.post(
            f"/api/v1/resume/{resume_a.id}/tailor",
            headers={"Authorization": f"Bearer {token_a}"},
            json={"job_id": str(job.id)},
        )
        assert r_tailor_auth.status_code == 201
        version_id = r_tailor_auth.json()["id"]

        # User B attempts to view User A's tailored version -> 403 Forbidden
        r_view_unauth = await client.get(
            f"/api/v1/resume/versions/{version_id}",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert r_view_unauth.status_code == 403

    finally:
        reset_llm_provider()


# ─── 6. Cross-User Modification and Deletion Prevention ────────────────

@pytest.mark.asyncio
async def test_cross_user_isolation_cannot_modify_or_delete_others(
    client: AsyncClient,
    test_session: AsyncSession,
):
    """User B cannot update, delete, or approve User A's tailored version."""
    token_a, user_a_id = await register_and_login(client, "user.mod.a@test.com", "Mod User A")
    token_b, user_b_id = await register_and_login(client, "user.mod.b@test.com", "Mod User B")

    resume_a = await create_parsed_test_resume(test_session, user_a_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_tailoring())
    override_llm_provider(mock)

    try:
        # User A creates version
        r_create = await client.post(
            f"/api/v1/resume/{resume_a.id}/tailor",
            headers={"Authorization": f"Bearer {token_a}"},
            json={"job_id": str(job.id)},
        )
        version_id = r_create.json()["id"]

        # User B attempts to edit User A's draft -> 403
        r_edit = await client.put(
            f"/api/v1/resume/versions/{version_id}",
            headers={"Authorization": f"Bearer {token_b}"},
            json={"user_notes": "Malicious edit"},
        )
        assert r_edit.status_code == 403

        # User B attempts to approve User A's draft -> 403
        r_approve = await client.post(
            f"/api/v1/resume/versions/{version_id}/approve",
            headers={"Authorization": f"Bearer {token_b}"},
            json={"user_confirmation": True},
        )
        assert r_approve.status_code == 403

        # User B attempts to delete User A's draft -> 403
        r_delete = await client.delete(
            f"/api/v1/resume/versions/{version_id}",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert r_delete.status_code == 403

    finally:
        reset_llm_provider()


# ─── 7. Original Resume Immutability ──────────────────────────────────

@pytest.mark.asyncio
async def test_original_resume_immutability(
    client: AsyncClient,
    test_session: AsyncSession,
):
    """Verifies that source resume records, text, and extracted entities remain strictly unchanged."""
    token, user_id = await register_and_login(client, "tailor.immutable@test.com", "Immutable User")
    resume = await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    # Capture snapshot of original resume state
    original_extracted = dict(resume.extracted_data)
    original_text = resume.parsed_text
    original_status = resume.status
    original_updated_at = resume.updated_at

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_tailoring())
    override_llm_provider(mock)

    try:
        # Generate tailored version
        r_gen = await client.post(
            f"/api/v1/resume/{resume.id}/tailor",
            headers={"Authorization": f"Bearer {token}"},
            json={"job_id": str(job.id)},
        )
        assert r_gen.status_code == 201
        version_id = r_gen.json()["id"]

        # Update tailored version
        r_up = await client.put(
            f"/api/v1/resume/versions/{version_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"user_notes": "Updated candidate notes"},
        )
        assert r_up.status_code == 200

        # Refetch original resume from DB
        stmt = select(Resume).where(Resume.id == resume.id)
        refetched_resume = await test_session.scalar(stmt)

        assert refetched_resume is not None
        assert refetched_resume.extracted_data == original_extracted
        assert refetched_resume.parsed_text == original_text
        assert refetched_resume.status == original_status
        assert refetched_resume.updated_at == original_updated_at

    finally:
        reset_llm_provider()


# ─── 8. Multiple Tailored Versions Sequential Numbering ───────────────

@pytest.mark.asyncio
async def test_multiple_tailored_versions_sequential_numbering(
    client: AsyncClient,
    test_session: AsyncSession,
):
    """Creating multiple tailored drafts for the same job increments version_number (v1, v2) without overwriting."""
    token, user_id = await register_and_login(client, "tailor.multiver@test.com", "Multi Ver User")
    resume = await create_parsed_test_resume(test_session, user_id)
    job1 = await create_test_job(test_session, title="Job 1")
    job2 = await create_test_job(test_session, title="Job 2")

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_tailoring())
    override_llm_provider(mock)

    try:
        # Iteration 1 for Job 1 -> v1
        r1 = await client.post(
            f"/api/v1/resume/{resume.id}/tailor",
            headers={"Authorization": f"Bearer {token}"},
            json={"job_id": str(job1.id)},
        )
        assert r1.status_code == 201
        assert r1.json()["version_number"] == 1

        # Iteration 2 for Job 1 -> v2
        r2 = await client.post(
            f"/api/v1/resume/{resume.id}/tailor",
            headers={"Authorization": f"Bearer {token}"},
            json={"job_id": str(job1.id)},
        )
        assert r2.status_code == 201
        assert r2.json()["version_number"] == 2

        # Iteration 1 for Job 2 -> v1 (independent job scope)
        r3 = await client.post(
            f"/api/v1/resume/{resume.id}/tailor",
            headers={"Authorization": f"Bearer {token}"},
            json={"job_id": str(job2.id)},
        )
        assert r3.status_code == 201
        assert r3.json()["version_number"] == 1

        # Verify listing endpoint returns all 3 distinct versions
        r_list = await client.get(
            "/api/v1/resume/versions",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r_list.status_code == 200
        items = r_list.json()["items"]
        assert len(items) == 3

    finally:
        reset_llm_provider()


# ─── 9. Invalid Structured AI Output Handling ─────────────────────────

@pytest.mark.asyncio
async def test_invalid_structured_ai_output_handled_safely(
    client: AsyncClient,
    test_session: AsyncSession,
):
    """When LLM returns malformed or invalid schema output, API returns HTTP 503 safely."""
    token, user_id = await register_and_login(client, "tailor.badout@test.com", "Bad Out User")
    resume = await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    # Malformed response missing required tailored_resume
    mock.set_structured_response({"corrupted_key": 123})
    override_llm_provider(mock)

    try:
        r = await client.post(
            f"/api/v1/resume/{resume.id}/tailor",
            headers={"Authorization": f"Bearer {token}"},
            json={"job_id": str(job.id)},
        )
        assert r.status_code == 503
        err_data = r.json()
        assert err_data.get("error", {}).get("code") == "SERVICE_UNAVAILABLE" or r.status_code == 503

        # Verify zero corrupt ResumeVersion rows were persisted
        v_count = await test_session.scalar(select(ResumeVersion).where(ResumeVersion.resume_id == resume.id))
        assert v_count is None

    finally:
        reset_llm_provider()


# ─── 10. Anti-Hallucination & Truthfulness Reconciliation ──────────────

@pytest.mark.asyncio
async def test_anti_hallucination_and_truthfulness_reconciliation(
    client: AsyncClient,
    test_session: AsyncSession,
):
    """
    CRITICAL TEST: When AI injects unevidenced skills ('FictitiousTechnology123') or
    hallucinated employers ('HallucinatedFakeCorp Inc'), the server-side reconciler
    prunes them from the tailored draft and logs them under unsupported_claims.
    """
    token, user_id = await register_and_login(client, "tailor.truth@test.com", "Truthful Candidate")
    # Authentic skills: Python, FastAPI, PostgreSQL, Docker. Authentic employer: Acme Cloud Corp.
    resume = await create_parsed_test_resume(
        test_session,
        user_id,
        skills=["Python", "FastAPI", "PostgreSQL", "Docker"],
        employers=["Acme Cloud Corp"],
    )
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    # Inject hallucinated skill and employer
    mock.set_structured_response(
        mock_successful_ai_tailoring(include_fake_skill=True, include_fake_employer=True)
    )
    override_llm_provider(mock)

    try:
        r = await client.post(
            f"/api/v1/resume/{resume.id}/tailor",
            headers={"Authorization": f"Bearer {token}"},
            json={"job_id": str(job.id)},
        )
        assert r.status_code == 201
        data = r.json()

        tailored_skills = [s["name"] for s in data["tailored_content"]["skills"]]
        # FictitiousTechnology123 MUST be pruned!
        assert "FictitiousTechnology123" not in tailored_skills
        assert "Python" in tailored_skills

        tailored_employers = [e["employer"] for e in data["tailored_content"]["experience"]]
        # HallucinatedFakeCorp Inc MUST be pruned!
        assert "HallucinatedFakeCorp Inc" not in tailored_employers
        assert "Acme Cloud Corp" in tailored_employers

        # Check unsupported claims record
        unsupported = data["diff_summary"]["unsupported_claims"]
        assert any("FictitiousTechnology123" in u for u in unsupported)
        assert any("HallucinatedFakeCorp Inc" in u for u in unsupported)

        # Missing requirements should capture the unevidenced skill
        missing_reqs = data["diff_summary"]["optimization_analysis"]["missing_requirements"]
        assert "FictitiousTechnology123" in missing_reqs

    finally:
        reset_llm_provider()


# ─── 11. Gemini Timeout & Provider Error Handling ──────────────────────

@pytest.mark.asyncio
async def test_gemini_timeout_and_provider_error_handling(
    client: AsyncClient,
    test_session: AsyncSession,
):
    """Simulates Gemini timeout / 503 outage, verifying clean error response without DB corruption."""
    token, user_id = await register_and_login(client, "tailor.timeout@test.com", "Timeout User")
    resume = await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    class FailingProvider(MockLLMProvider):
        async def generate_structured(self, *args, **kwargs):
            raise ServiceUnavailableException("Gemini", "Inference deadline exceeded after 30s.")

    override_llm_provider(FailingProvider())

    try:
        r = await client.post(
            f"/api/v1/resume/{resume.id}/tailor",
            headers={"Authorization": f"Bearer {token}"},
            json={"job_id": str(job.id)},
        )
        assert r.status_code == 503
        err_msg = r.json().get("error", {}).get("message") or r.json().get("detail", "")
        assert "deadline exceeded" in err_msg.lower()

        # Verify no orphan resume version was created
        versions = (await test_session.scalars(select(ResumeVersion).where(ResumeVersion.user_id == user_id))).all()
        assert len(versions) == 0

    finally:
        reset_llm_provider()


# ─── 12. Draft Lifecycle & Explicit Human Approval Gate ───────────────

@pytest.mark.asyncio
async def test_draft_status_lifecycle_and_explicit_approval(
    client: AsyncClient,
    test_session: AsyncSession,
):
    """Drafts begin in 'draft' status and require explicit human confirmation to approve."""
    token, user_id = await register_and_login(client, "tailor.approve@test.com", "Approval User")
    resume = await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_tailoring())
    override_llm_provider(mock)

    try:
        r_create = await client.post(
            f"/api/v1/resume/{resume.id}/tailor",
            headers={"Authorization": f"Bearer {token}"},
            json={"job_id": str(job.id)},
        )
        assert r_create.status_code == 201
        version_id = r_create.json()["id"]
        assert r_create.json()["status"] == "draft"

        # Attempt to approve with user_confirmation=False -> HTTP 422 Validation Error
        r_reject = await client.post(
            f"/api/v1/resume/versions/{version_id}/approve",
            headers={"Authorization": f"Bearer {token}"},
            json={"user_confirmation": False},
        )
        assert r_reject.status_code == 422

        # Explicit approval with user_confirmation=True -> HTTP 200 OK
        r_approve = await client.post(
            f"/api/v1/resume/versions/{version_id}/approve",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "user_confirmation": True,
                "accepted_sections": ["executive_summary", "experience", "skills"],
            },
        )
        assert r_approve.status_code == 200
        approved_data = r_approve.json()
        assert approved_data["status"] == "approved"
        assert approved_data["approved_at"] is not None

        # Verify DB reflects approved state
        v_db = await test_session.scalar(select(ResumeVersion).where(ResumeVersion.id == uuid.UUID(version_id)))
        assert v_db is not None
        assert v_db.status == "approved"
        assert v_db.approved_at is not None

    finally:
        reset_llm_provider()


# ─── 13. Draft Editing Permitted, Prohibited After Approval ───────────

@pytest.mark.asyncio
async def test_update_tailored_draft_and_prohibit_editing_after_approval(
    client: AsyncClient,
    test_session: AsyncSession,
):
    """User can edit draft content; once approved, modifications return HTTP 409 Conflict."""
    token, user_id = await register_and_login(client, "tailor.editlock@test.com", "Edit Lock User")
    resume = await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_tailoring())
    override_llm_provider(mock)

    try:
        r_create = await client.post(
            f"/api/v1/resume/{resume.id}/tailor",
            headers={"Authorization": f"Bearer {token}"},
            json={"job_id": str(job.id)},
        )
        version_id = r_create.json()["id"]

        # 1. Update draft while status == 'draft' -> Success
        r_edit_draft = await client.put(
            f"/api/v1/resume/versions/{version_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"user_notes": "Added notes before final approval"},
        )
        assert r_edit_draft.status_code == 200
        assert r_edit_draft.json()["status"] == "draft"

        # 2. Approve draft
        r_approve = await client.post(
            f"/api/v1/resume/versions/{version_id}/approve",
            headers={"Authorization": f"Bearer {token}"},
            json={"user_confirmation": True},
        )
        assert r_approve.status_code == 200
        assert r_approve.json()["status"] == "approved"

        # 3. Attempt to update approved draft -> HTTP 409 Conflict
        r_edit_locked = await client.put(
            f"/api/v1/resume/versions/{version_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"user_notes": "Attempting to modify locked version"},
        )
        assert r_edit_locked.status_code == 409
        err_msg = r_edit_locked.json().get("error", {}).get("message") or r_edit_locked.json().get("detail", "")
        assert "cannot modify" in err_msg.lower()

    finally:
        reset_llm_provider()


# ─── 14. Visual Diff and Optimization Analysis Endpoints ───────────────

@pytest.mark.asyncio
async def test_visual_diff_and_optimization_analysis_endpoints(
    client: AsyncClient,
    test_session: AsyncSession,
):
    """Tests GET /versions/{id}/diff and GET /versions/{id}/analysis."""
    token, user_id = await register_and_login(client, "tailor.diffdiag@test.com", "Diff Diag User")
    resume = await create_parsed_test_resume(test_session, user_id)
    job = await create_test_job(test_session)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_tailoring())
    override_llm_provider(mock)

    try:
        r_create = await client.post(
            f"/api/v1/resume/{resume.id}/tailor",
            headers={"Authorization": f"Bearer {token}"},
            json={"job_id": str(job.id)},
        )
        version_id = r_create.json()["id"]

        # 1. Visual Diff endpoint
        r_diff = await client.get(
            f"/api/v1/resume/versions/{version_id}/diff",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r_diff.status_code == 200
        diff_data = r_diff.json()
        assert diff_data["version_id"] == version_id
        assert len(diff_data["changes"]) == 2
        assert diff_data["rephrasings_count"] >= 1

        # 2. Optimization Analysis endpoint
        r_analysis = await client.get(
            f"/api/v1/resume/versions/{version_id}/analysis",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r_analysis.status_code == 200
        analysis_data = r_analysis.json()
        assert analysis_data["version_id"] == version_id
        assert analysis_data["optimization_analysis"]["keyword_coverage"] > 0.0
        assert "python" in [k.lower() for k in analysis_data["optimization_analysis"]["matched_keywords"]]
        assert analysis_data["anti_hallucination_verified"] is True

    finally:
        reset_llm_provider()


# ─── 15. Direct Job Description Text Ingestion Workflow ───────────────

@pytest.mark.asyncio
async def test_direct_text_job_import_tailoring(
    client: AsyncClient,
    test_session: AsyncSession,
):
    """Candidate can tailor by pasting job description text directly without preexisting job_id."""
    token, user_id = await register_and_login(client, "tailor.directtext@test.com", "Direct Text User")
    resume = await create_parsed_test_resume(test_session, user_id)

    mock = MockLLMProvider()
    mock.set_structured_response(mock_successful_ai_tailoring())
    override_llm_provider(mock)

    pasted_job_text = (
        "Stripe is hiring a Senior Infrastructure Engineer to design scalable Python microservices. "
        "Must have proficiency with Docker, PostgreSQL, and distributed database systems."
    )

    try:
        r = await client.post(
            f"/api/v1/resume/{resume.id}/tailor",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "job_description_text": pasted_job_text,
                "job_title": "Senior Infrastructure Engineer",
                "company_name": "Stripe",
            },
        )
        assert r.status_code == 201
        data = r.json()
        assert data["version_number"] == 1
        assert data["status"] == "draft"

        # Check that target job was persisted and linked
        job_id = uuid.UUID(data["target_job_id"])
        job = await test_session.scalar(select(Job).where(Job.id == job_id))
        assert job is not None
        assert "Stripe" in job.company_name

    finally:
        reset_llm_provider()
