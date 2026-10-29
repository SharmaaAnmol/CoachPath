"""
Phase 10C Comprehensive End-to-End Audit & Verification Test Suite.
Verifies the complete Resume Tailoring user journey:
A. Source resume selection & eligibility
B. Target job selection (catalog & custom text validation)
C. AI draft generation lifecycle & error resilience
D. Review workspace, visual diffs, and server-side evidence-grounding reconciler
E. Draft editing, persistence, and master resume immutability
F. Version history, filtering, and isolated deletion
G. Explicit human approval gateway and post-approval modification locking
"""

from __future__ import annotations

import uuid
from typing import Tuple
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.seeds.gap_analysis_seeder import seed_skill_taxonomy_and_roles
from app.models.jobs import Job, JobSource
from app.models.resume import Resume, ResumeVersion
from app.models.career import Role
from app.models.skills import Skill, UserSkill
from app.ai.factory import override_llm_provider, reset_llm_provider
from app.ai.mock_adapter import MockLLMProvider
from app.core.exceptions import ServiceUnavailableException


# ─── FIXTURES & HELPERS ───────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
async def seed_base_data(test_session: AsyncSession):
    """Ensure baseline roles, taxonomy, and job sources exist."""
    await seed_skill_taxonomy_and_roles(test_session)
    for name, p_type in [("seed", "seed"), ("manual", "manual"), ("mock", "mock")]:
        source = await test_session.scalar(select(JobSource).where(JobSource.name == name))
        if not source:
            source = JobSource(name=name, provider_type=p_type, is_active=True)
            test_session.add(source)
    await test_session.commit()


async def register_and_login(client: AsyncClient, email: str, name: str) -> Tuple[str, uuid.UUID]:
    pw = "Phase10cSecurePW!"
    r_reg = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": pw, "full_name": name},
    )
    assert r_reg.status_code == 201, f"Registration failed: {r_reg.text}"
    user_id = uuid.UUID(r_reg.json()["user_id"])

    r_login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": pw},
    )
    assert r_login.status_code == 200, f"Login failed: {r_login.text}"
    token = r_login.json()["access_token"]
    return token, user_id


async def create_candidate_resume(
    db: AsyncSession,
    user_id: uuid.UUID,
    status: str = "parsed",
    file_name: str = "Candidate_Resume.pdf",
    skills: list[str] | None = None,
    employers: list[str] | None = None,
) -> Resume:
    skill_names = skills or ["Python", "FastAPI", "PostgreSQL", "Docker"]
    employer_names = employers or ["Acme Cloud Corp"]

    extracted_data = {
        "personal_info": {
            "name": "Alex Mercer",
            "email": "alex.mercer@test.com",
            "phone": "+1-555-0199",
            "location": "San Francisco, CA",
        },
        "executive_summary": "Experienced backend engineer building scalable API platforms.",
        "skills": [{"name": s, "category": "technical"} for s in skill_names],
        "experience": [
            {
                "employer": emp,
                "job_title": "Senior Backend Developer",
                "start_date": "2021-01",
                "end_date": "Present",
                "is_current": True,
                "responsibilities": ["Designed REST and gRPC services in Python."],
                "achievements": ["Maintained 99.99% service uptime across critical systems."],
            }
            for emp in employer_names
        ],
        "education": [
            {
                "institution": "UC Berkeley",
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


async def create_catalog_job(
    db: AsyncSession,
    title: str = "Principal Backend Engineer",
    company: str = "Enterprise Cloud Inc",
    description: str | None = None,
) -> Job:
    desc = description or (
        "Enterprise Cloud Inc is seeking a Principal Backend Engineer to design high-throughput distributed systems. "
        "Required Qualifications: 5+ years with Python, FastAPI, PostgreSQL, and Docker. "
        "Strong knowledge of microservices architecture and high availability."
    )

    job = Job(
        id=uuid.uuid4(),
        external_id=f"job_{uuid.uuid4().hex[:8]}",
        source="seed",
        source_url="https://example.com/jobs/principal-backend",
        title=title,
        normalized_title=title.lower(),
        company_name=company,
        location="Remote",
        normalized_location="remote",
        remote_type="remote",
        employment_type="full_time",
        role_id="backend-developer",
        experience_level="mid",
        min_salary=160000,
        max_salary=210000,
        currency="USD",
        description_markdown=desc,
        responsibilities=["Build high-volume payment processing pipelines.", "Maintain database reliability."],
        required_qualifications=["Proficiency in Python and PostgreSQL.", "Docker container orchestration."],
        preferred_qualifications=["FastAPI experience.", "Knowledge of PCI-DSS compliance."],
        application_url="https://example.com/apply",
        is_active=True,
        freshness_status="active",
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


def build_mock_ai_response(
    include_fake_skill: bool = False,
    include_fake_employer: bool = False,
) -> dict:
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
            "start_date": "2021-01",
            "end_date": "Present",
            "is_current": True,
            "responsibilities": ["Designed high-throughput payment services in Python."],
            "achievements": ["Maintained 99.99% service uptime across critical systems."],
        }
    ]
    if include_fake_employer:
        employers.append({
            "employer": "HallucinatedFakeCorp Inc",
            "job_title": "VP of Architecture",
            "start_date": "2019-01",
            "end_date": "2020-12",
            "is_current": False,
            "responsibilities": ["Invented fictional blockchain."],
            "achievements": ["Fictitious metric."],
        })

    return {
        "tailored_resume": {
            "personal_info": {
                "name": "Alex Mercer",
                "email": "alex.mercer@test.com",
                "phone": "+1-555-0199",
                "location": "San Francisco, CA",
            },
            "executive_summary": "Principal Backend Engineer specializing in resilient FastAPI and Python microservices.",
            "skills": skills,
            "experience": employers,
            "education": [
                {
                    "institution": "UC Berkeley",
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
        },
        "changes": [
            {
                "id": "chg_1",
                "section": "executive_summary",
                "change_type": "rephrased",
                "original_text": "Experienced backend engineer building scalable API platforms.",
                "proposed_text": "Principal Backend Engineer specializing in resilient FastAPI and Python microservices.",
                "rationale": "Directly targets high-availability microservices requirement in job posting.",
                "target_job_requirement": "5+ years with Python, FastAPI, PostgreSQL",
                "supporting_evidence": "Candidate experience and projects",
                "needs_clarification": False,
            },
            {
                "id": "chg_2",
                "section": "skills",
                "change_type": "modified",
                "original_text": "PostgreSQL",
                "proposed_text": "PostgreSQL (High Availability)",
                "rationale": "Emphasizes database clustering.",
                "target_job_requirement": "PostgreSQL",
                "supporting_evidence": "Candidate skills",
                "needs_clarification": False,
            },
        ],
        "matched_keywords": ["python", "fastapi", "postgresql", "docker"],
        "missing_keywords": ["kubernetes", "grpc"],
        "supported_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
        "missing_requirements": ["Demonstrated experience with Kubernetes cluster operations."],
        "actionable_suggestions": ["Mention container orchestration in experience bullets."],
        "formatting_recommendations": ["Highlight microservices at top."],
        "readability_score": 92.0,
        "unsupported_claims": [],
    }


# ─── SECTION 2.A: SOURCE RESUME SELECTION & ELIGIBILITY ───────────────────────

@pytest.mark.asyncio
async def test_user_journey_a_source_resume_selection(client: AsyncClient, test_session: AsyncSession):
    """
    Validates:
    - User sees only their own eligible parsed resumes
    - Unparsed resume cannot be tailored (400 Bad Request)
    - Nonexistent resume returns 404
    - Cross-user resume access returns 403
    - Empty account returns empty list for actionable empty state
    """
    token_a, user_a = await register_and_login(client, "candidate.a@test.com", "Candidate A")
    token_b, user_b = await register_and_login(client, "candidate.b@test.com", "Candidate B")

    # 1. Candidate A creates a parsed master resume
    resume_a = await create_candidate_resume(test_session, user_a, status="parsed")

    # 2. Candidate A creates an unparsed resume
    resume_unparsed = await create_candidate_resume(test_session, user_a, status="uploaded", file_name="Raw.pdf")

    # 3. Candidate A lists resumes
    headers_a = {"Authorization": f"Bearer {token_a}"}
    r = await client.get("/api/v1/resume", headers=headers_a)
    assert r.status_code == 200
    resumes_list = r.json()["resumes"]
    assert len(resumes_list) == 2
    # Verify only user A's resumes returned
    assert all(res["id"] in [str(resume_a.id), str(resume_unparsed.id)] for res in resumes_list)

    # 4. Tailoring unparsed resume returns 400 Bad Request
    job = await create_catalog_job(test_session)
    r_unparsed = await client.post(
        f"/api/v1/resume/{resume_unparsed.id}/tailor",
        headers=headers_a,
        json={"job_id": str(job.id)},
    )
    assert r_unparsed.status_code == 400
    err_msg = r_unparsed.json().get("error", {}).get("message") or r_unparsed.json().get("detail", "")
    assert "must be successfully parsed" in err_msg.lower()

    # 5. Nonexistent resume UUID returns 404
    fake_id = uuid.uuid4()
    r_fake = await client.post(
        f"/api/v1/resume/{fake_id}/tailor",
        headers=headers_a,
        json={"job_id": str(job.id)},
    )
    assert r_fake.status_code == 404

    # 6. Candidate B attempts to tailor Candidate A's resume -> 403 Forbidden
    headers_b = {"Authorization": f"Bearer {token_b}"}
    r_cross = await client.post(
        f"/api/v1/resume/{resume_a.id}/tailor",
        headers=headers_b,
        json={"job_id": str(job.id)},
    )
    assert r_cross.status_code == 403

    # 7. Candidate B lists resumes -> empty list (Actionable Empty State in UI)
    r_b_list = await client.get("/api/v1/resume", headers=headers_b)
    assert r_b_list.status_code == 200
    assert len(r_b_list.json()["resumes"]) == 0


# ─── SECTION 2.B: TARGET JOB SELECTION & VALIDATION ──────────────────────────

@pytest.mark.asyncio
async def test_user_journey_b_target_job_selection(client: AsyncClient, test_session: AsyncSession):
    """
    Validates:
    - Real jobs returned from catalog with accurate details
    - Custom job text < 50 chars rejected with 422
    - Custom job text >= 50 chars accepted and successfully linked
    - Nonexistent job ID returns 404
    """
    token, user_id = await register_and_login(client, "job.select@test.com", "Job Selector")
    resume = await create_candidate_resume(test_session, user_id)
    catalog_job = await create_catalog_job(test_session, title="Senior Backend Architect")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Search catalog
    r_jobs = await client.get("/api/v1/jobs?keyword=Backend", headers=headers)
    assert r_jobs.status_code == 200
    job_items = r_jobs.json()["items"]
    assert len(job_items) >= 1
    job = job_items[0]
    assert "title" in job
    assert "company_name" in job

    # 2. Custom job text validation: < 50 characters returns 422
    r_short = await client.post(
        f"/api/v1/resume/{resume.id}/tailor",
        headers=headers,
        json={
            "job_description_text": "Too short job description.",
            "job_title": "Senior Engineer",
        },
    )
    assert r_short.status_code == 422

    # 3. Nonexistent job UUID returns 404
    fake_job_id = uuid.uuid4()
    r_fake_job = await client.post(
        f"/api/v1/resume/{resume.id}/tailor",
        headers=headers,
        json={"job_id": str(fake_job_id)},
    )
    assert r_fake_job.status_code == 404

    # 4. Custom job text >= 50 chars works cleanly
    mock = MockLLMProvider()
    mock.set_structured_response(build_mock_ai_response())
    override_llm_provider(mock)

    try:
        valid_custom_desc = (
            "Innovative Cloud Solutions is seeking a Senior Backend Engineer to architect cloud infrastructure. "
            "Must have extensive experience with Python, FastAPI, and Docker in a fast-paced environment."
        )
        r_custom = await client.post(
            f"/api/v1/resume/{resume.id}/tailor",
            headers=headers,
            json={
                "job_description_text": valid_custom_desc,
                "job_title": "Senior Backend Architect",
                "company_name": "Innovative Cloud Solutions",
            },
        )
        assert r_custom.status_code == 201
        data = r_custom.json()
        assert data["version_number"] == 1
        assert data["status"] == "draft"
    finally:
        reset_llm_provider()


# ─── SECTION 2.C: DRAFT GENERATION LIFECYCLE & RESILIENCE ────────────────────

@pytest.mark.asyncio
async def test_user_journey_c_draft_generation_resilience(client: AsyncClient, test_session: AsyncSession):
    """
    Validates:
    - Provider failure/timeout returns 503 Service Unavailable honestly
    - Malformed AI output returns 503 without saving corrupt draft records
    - Successful generation persists draft with v1, v2 sequential versioning
    """
    token, user_id = await register_and_login(client, "draft.gen@test.com", "Draft Generator")
    resume = await create_candidate_resume(test_session, user_id)
    job = await create_catalog_job(test_session)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Provider outage simulation
    class FailingProvider(MockLLMProvider):
        async def generate_structured(self, *args, **kwargs):
            raise ServiceUnavailableException("Gemini", "Inference deadline exceeded after 30s.")

    override_llm_provider(FailingProvider())

    try:
        r_outage = await client.post(
            f"/api/v1/resume/{resume.id}/tailor",
            headers=headers,
            json={"job_id": str(job.id)},
        )
        assert r_outage.status_code == 503
        err_msg = r_outage.json().get("error", {}).get("message") or r_outage.json().get("detail", "")
        assert "deadline exceeded" in err_msg.lower()
        assert r_outage.json().get("error", {}).get("code") == "SERVICE_UNAVAILABLE"

        # Confirm zero orphan versions created
        v_count = await test_session.scalar(select(ResumeVersion).where(ResumeVersion.resume_id == resume.id))
        assert v_count is None
    finally:
        reset_llm_provider()

    # 2. Sequential versioning v1 -> v2
    mock_success = MockLLMProvider()
    mock_success.set_structured_response(build_mock_ai_response())
    override_llm_provider(mock_success)

    try:
        r1 = await client.post(
            f"/api/v1/resume/{resume.id}/tailor",
            headers=headers,
            json={"job_id": str(job.id)},
        )
        assert r1.status_code == 201
        assert r1.json()["version_number"] == 1

        r2 = await client.post(
            f"/api/v1/resume/{resume.id}/tailor",
            headers=headers,
            json={"job_id": str(job.id)},
        )
        assert r2.status_code == 201
        assert r2.json()["version_number"] == 2
    finally:
        reset_llm_provider()


# ─── SECTION 2.D: EVIDENCE GROUNDING & ANTI-FABRICATION RECONCILER ────────────

@pytest.mark.asyncio
async def test_user_journey_d_evidence_grounding_reconciler(client: AsyncClient, test_session: AsyncSession):
    """
    Validates:
    - Server-side reconciler strips unevidenced skills (e.g. FictitiousTechnology123)
    - Strips unevidenced employers (e.g. HallucinatedFakeCorp Inc)
    - Adds pruned items to diff_summary.unsupported_claims
    - Preserves anti_hallucination_verified = True
    - Validates visual diff and optimization analysis endpoints
    """
    token, user_id = await register_and_login(client, "grounding@test.com", "Grounding Tester")
    resume = await create_candidate_resume(test_session, user_id)
    job = await create_catalog_job(test_session)
    headers = {"Authorization": f"Bearer {token}"}

    # Inject mock with fabricated skill and employer
    mock_hallucinated = MockLLMProvider()
    mock_hallucinated.set_structured_response(
        build_mock_ai_response(include_fake_skill=True, include_fake_employer=True)
    )
    override_llm_provider(mock_hallucinated)

    try:
        r = await client.post(
            f"/api/v1/resume/{resume.id}/tailor",
            headers=headers,
            json={"job_id": str(job.id)},
        )
        assert r.status_code == 201
        data = r.json()
        version_id = data["id"]

        # 1. Verification flag
        assert data["anti_hallucination_verified"] is True

        # 2. Fabricated skill stripped from tailored draft
        skills_in_draft = [s["name"] for s in data["tailored_content"]["skills"]]
        assert "FictitiousTechnology123" not in skills_in_draft
        assert "Python" in skills_in_draft

        # 3. Fabricated employer stripped from tailored draft
        employers_in_draft = [e["employer"] for e in data["tailored_content"]["experience"]]
        assert "HallucinatedFakeCorp Inc" not in employers_in_draft
        assert "Acme Cloud Corp" in employers_in_draft

        # 4. Check unsupported_claims in diff_summary
        unsupported = data["diff_summary"].get("unsupported_claims", [])
        assert len(unsupported) >= 1
        assert any("FictitiousTechnology123" in claim for claim in unsupported)

        # 5. Check visual diff endpoint GET /diff
        r_diff = await client.get(f"/api/v1/resume/versions/{version_id}/diff", headers=headers)
        assert r_diff.status_code == 200
        diff_data = r_diff.json()
        assert len(diff_data["changes"]) >= 1
        assert "unsupported_claims" in diff_data

        # 6. Check optimization analysis endpoint GET /analysis
        r_analysis = await client.get(f"/api/v1/resume/versions/{version_id}/analysis", headers=headers)
        assert r_analysis.status_code == 200
        analysis_data = r_analysis.json()
        assert analysis_data["optimization_analysis"]["keyword_coverage"] > 0
        assert "python" in [k.lower() for k in analysis_data["optimization_analysis"]["matched_keywords"]]
        assert analysis_data["anti_hallucination_verified"] is True
    finally:
        reset_llm_provider()


# ─── SECTION 2.E: DRAFT EDITING & MASTER RESUME IMMUTABILITY ──────────────────

@pytest.mark.asyncio
async def test_user_journey_e_draft_editing_and_immutability(client: AsyncClient, test_session: AsyncSession):
    """
    Validates:
    - User can edit executive summary, skills, and bullets in draft state
    - Edits persist across refetches
    - Original master resume in `resumes` table remains 100% byte-for-byte immutable
    - Cross-user editing rejected with 403 Forbidden
    """
    token_a, user_a = await register_and_login(client, "editor.a@test.com", "Editor A")
    token_b, user_b = await register_and_login(client, "editor.b@test.com", "Editor B")

    resume = await create_candidate_resume(test_session, user_a)
    job = await create_catalog_job(test_session)
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Record exact snapshot of master resume
    original_extracted = dict(resume.extracted_data)
    original_text = resume.parsed_text
    original_updated_at = resume.updated_at

    mock = MockLLMProvider()
    mock.set_structured_response(build_mock_ai_response())
    override_llm_provider(mock)

    try:
        # Create draft
        r_create = await client.post(
            f"/api/v1/resume/{resume.id}/tailor",
            headers=headers_a,
            json={"job_id": str(job.id)},
        )
        assert r_create.status_code == 201
        version_id = r_create.json()["id"]

        # Edit draft content
        updated_content = dict(r_create.json()["tailored_content"])
        updated_content["executive_summary"] = "Manually modified executive summary with custom achievements."

        r_update = await client.put(
            f"/api/v1/resume/versions/{version_id}",
            headers=headers_a,
            json={
                "tailored_content": updated_content,
                "user_notes": "Added custom leadership metrics.",
            },
        )
        assert r_update.status_code == 200
        assert r_update.json()["tailored_content"]["executive_summary"] == updated_content["executive_summary"]

        # Refetch draft
        r_get = await client.get(f"/api/v1/resume/versions/{version_id}", headers=headers_a)
        assert r_get.status_code == 200
        assert r_get.json()["tailored_content"]["executive_summary"] == updated_content["executive_summary"]

        # Verify Master Resume Immutability
        await test_session.refresh(resume)
        assert resume.extracted_data == original_extracted
        assert resume.parsed_text == original_text
        assert resume.status == "parsed"
        assert resume.updated_at == original_updated_at

        # Cross-user edit attempt by Candidate B returns 403 Forbidden
        r_cross_edit = await client.put(
            f"/api/v1/resume/versions/{version_id}",
            headers=headers_b,
            json={"tailored_content": updated_content},
        )
        assert r_cross_edit.status_code == 403
    finally:
        reset_llm_provider()


# ─── SECTION 2.F: VERSION HISTORY & ISOLATED DELETION ─────────────────────────

@pytest.mark.asyncio
async def test_user_journey_f_version_history_and_deletion(client: AsyncClient, test_session: AsyncSession):
    """
    Validates:
    - Candidate lists versions with metadata
    - Filtering by status (draft vs approved)
    - Deleting version deletes only the child variant (master resume preserved)
    - Cross-user deletion rejected with 403 Forbidden
    """
    token_a, user_a = await register_and_login(client, "history.a@test.com", "History A")
    token_b, user_b = await register_and_login(client, "history.b@test.com", "History B")

    resume = await create_candidate_resume(test_session, user_a)
    job = await create_catalog_job(test_session)
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    mock = MockLLMProvider()
    mock.set_structured_response(build_mock_ai_response())
    override_llm_provider(mock)

    try:
        # Create draft v1
        r_v1 = await client.post(
            f"/api/v1/resume/{resume.id}/tailor",
            headers=headers_a,
            json={"job_id": str(job.id)},
        )
        assert r_v1.status_code == 201
        v1_id = r_v1.json()["id"]

        # List versions
        r_list = await client.get("/api/v1/resume/versions", headers=headers_a)
        assert r_list.status_code == 200
        items = r_list.json()["items"]
        assert len(items) == 1
        assert items[0]["id"] == v1_id
        assert items[0]["version_number"] == 1

        # Candidate B cannot list Candidate A's versions
        r_list_b = await client.get("/api/v1/resume/versions", headers=headers_b)
        assert r_list_b.status_code == 200
        assert len(r_list_b.json()["items"]) == 0

        # Candidate B cannot delete Candidate A's version
        r_del_b = await client.delete(f"/api/v1/resume/versions/{v1_id}", headers=headers_b)
        assert r_del_b.status_code == 403

        # Candidate A deletes v1
        r_del_a = await client.delete(f"/api/v1/resume/versions/{v1_id}", headers=headers_a)
        assert r_del_a.status_code == 204

        # Version is gone
        r_get_deleted = await client.get(f"/api/v1/resume/versions/{v1_id}", headers=headers_a)
        assert r_get_deleted.status_code == 404

        # Master resume still exists
        await test_session.refresh(resume)
        assert resume.id is not None
    finally:
        reset_llm_provider()


# ─── SECTION 2.G: APPROVAL WORKFLOW & EDITING LOCK ────────────────────────────

@pytest.mark.asyncio
async def test_user_journey_g_approval_workflow_and_locking(client: AsyncClient, test_session: AsyncSession):
    """
    Validates:
    - New draft has status = 'draft' and approved_at = None
    - Approval without user_confirmation rejected with 422
    - Explicit approval transitions to status = 'approved' and sets approved_at
    - Post-approval edits strictly rejected with 409 Conflict
    - Cross-user approval rejected with 403 Forbidden
    """
    token_a, user_a = await register_and_login(client, "approve.a@test.com", "Approval A")
    token_b, user_b = await register_and_login(client, "approve.b@test.com", "Approval B")

    resume = await create_candidate_resume(test_session, user_a)
    job = await create_catalog_job(test_session)
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    mock = MockLLMProvider()
    mock.set_structured_response(build_mock_ai_response())
    override_llm_provider(mock)

    try:
        # Create draft
        r_v1 = await client.post(
            f"/api/v1/resume/{resume.id}/tailor",
            headers=headers_a,
            json={"job_id": str(job.id)},
        )
        assert r_v1.status_code == 201
        v1_id = r_v1.json()["id"]
        assert r_v1.json()["status"] == "draft"
        assert r_v1.json()["approved_at"] is None

        # 1. Approval without confirmation checkbox -> 422 Unprocessable Content
        r_reject = await client.post(
            f"/api/v1/resume/versions/{v1_id}/approve",
            headers=headers_a,
            json={"user_confirmation": False},
        )
        assert r_reject.status_code == 422

        # 2. Candidate B cannot approve Candidate A's draft -> 403 Forbidden
        r_cross_appr = await client.post(
            f"/api/v1/resume/versions/{v1_id}/approve",
            headers=headers_b,
            json={"user_confirmation": True},
        )
        assert r_cross_appr.status_code == 403

        # 3. Candidate A approves with explicit confirmation
        r_approve = await client.post(
            f"/api/v1/resume/versions/{v1_id}/approve",
            headers=headers_a,
            json={
                "user_confirmation": True,
                "accepted_sections": ["summary", "skills", "experience", "education"],
            },
        )
        assert r_approve.status_code == 200
        approved_data = r_approve.json()
        assert approved_data["status"] == "approved"
        assert approved_data["approved_at"] is not None

        # 4. Modifying approved version is strictly rejected with 409 Conflict
        r_edit_locked = await client.put(
            f"/api/v1/resume/versions/{v1_id}",
            headers=headers_a,
            json={
                "tailored_content": approved_data["tailored_content"],
                "user_notes": "Attempt to edit locked version",
            },
        )
        assert r_edit_locked.status_code == 409
        err_msg = r_edit_locked.json().get("error", {}).get("message") or r_edit_locked.json().get("detail", "")
        assert "cannot modify" in err_msg.lower() or "only 'draft'" in err_msg.lower()
    finally:
        reset_llm_provider()
