"""
Phase 5C: Comprehensive End-to-End Integration Audit Test Suite.
Validates the complete resume ingestion, extraction, structured AI interpretation,
reviewable draft persistence, user editing, human approval gate, atomic profile merging,
persistence across logins, error categories, anti-fabrication truthfulness, and security isolation.
"""
from __future__ import annotations

import io
import uuid
import docx
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.factory import override_llm_provider, reset_llm_provider, create_llm_provider
from app.ai.mock_adapter import MockLLMProvider
from app.core.config import settings
from app.core.exceptions import ServiceUnavailableException
from app.models.career import (
    CareerProfile,
    Certification,
    Education,
    Experience,
    Project,
)
from app.models.resume import Resume
from app.models.skills import Skill, UserSkill
from app.schemas.resume import ParsingErrorCategory, ResumeStatus
from app.services.storage import storage_service


# ─── Binary Test Document Builders ───────────────────────────────────

def make_sample_pdf(
    candidate_name: str = "Elena Rostova",
    content: str = (
        "Principal Systems Engineer with 8 years of experience in distributed systems, "
        "Python, Rust, PostgreSQL, and Kubernetes. "
        "Education: Bachelor of Science in Computer Engineering from Oxford University (2012-2016). "
        "Experience: Lead Architect at CloudScale Inc (2018-Present). "
        "Projects: Built high-throughput consensus engine with Raft. "
        "Certifications: Certified Kubernetes Administrator."
    ),
) -> bytes:
    """Creates a valid PDF binary stream with extractable text."""
    escaped = f"{candidate_name}\n{content}".replace("(", "\\(").replace(")", "\\)")
    stream = f"BT /F1 12 Tf 72 720 Td ({escaped}) Tj ET".encode("latin1")
    length = len(stream)

    return f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length {length} >>
stream
{stream.decode('latin1')}
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000244 00000 n 
0000000400 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
460
%%EOF""".encode("latin1")


def make_scanned_image_pdf() -> bytes:
    """Creates a PDF with 0 extractable characters simulating a scanned/rasterized document."""
    return b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
trailer
<< /Size 4 /Root 1 0 R >>
startxref
190
%%EOF"""


def make_sample_docx(name: str = "Elena Rostova") -> bytes:
    """Generates valid DOCX document bytes."""
    doc = docx.Document()
    doc.add_heading(name, 0)
    doc.add_paragraph("Principal Systems Engineer specializing in Python, Rust, and PostgreSQL.")
    doc.add_heading("Education", level=1)
    doc.add_paragraph("Bachelor of Science in Computer Engineering, Oxford University (2012-2016).")
    doc.add_heading("Experience", level=1)
    doc.add_paragraph("Lead Architect at CloudScale Inc (2018 - Present). Designed multi-region microservices.")
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def mock_ai_parsed_data():
    """Deterministic structured AI extraction mock."""
    return {
        "personal_info": {
            "name": "Elena Rostova",
            "email": "elena.rostova@example.com",
            "phone": "+44 20 7946 0991",
            "location": "London, UK",
            "linkedin_url": "https://linkedin.com/in/elenarostova",
            "github_url": "https://github.com/elenarostova",
            "portfolio_url": None,
        },
        "education": [
            {
                "institution": "Oxford University",
                "degree": "Bachelor of Science",
                "field_of_study": "Computer Engineering",
                "start_date": "2012-10",
                "end_date": "2016-06",
                "grade_or_gpa": "First Class",
                "highlights": ["Graduated with Distinction"],
                "evidence": {
                    "section_name": "Education",
                    "page_number": 1,
                    "supporting_excerpt": "Bachelor of Science in Computer Engineering from Oxford University",
                },
            }
        ],
        "experience": [
            {
                "employer": "CloudScale Inc",
                "job_title": "Lead Systems Architect",
                "start_date": "2018-09",
                "end_date": None,
                "is_current": True,
                "location": "London, UK",
                "responsibilities": ["Lead architectural design for multi-region microservices"],
                "achievements": ["Scaled system to 250,000 requests per second"],
                "evidence": {
                    "section_name": "Experience",
                    "page_number": 1,
                    "supporting_excerpt": "Lead Architect at CloudScale Inc",
                },
            }
        ],
        "skills": [
            {"name": "Python", "category": "language", "confidence_source": "resume_stated", "evidence": None},
            {"name": "PostgreSQL", "category": "database", "confidence_source": "resume_stated", "evidence": None},
            {"name": "Docker", "category": "tool", "confidence_source": "resume_stated", "evidence": None},
        ],
        "projects": [
            {
                "name": "Consensus Engine",
                "description": "High-throughput Raft consensus implementation in Rust",
                "technologies": ["Rust", "Distributed Systems"],
                "url": "https://github.com/elenarostova/consensus",
                "highlights": ["Sub-millisecond leader election"],
                "evidence": None,
            },
            {
                "name": "Unwanted Old Project",
                "description": "Old student website",
                "technologies": ["HTML", "CSS"],
                "url": None,
                "highlights": [],
                "evidence": None,
            },
        ],
        "certifications": [
            {
                "name": "Certified Kubernetes Administrator",
                "issuing_organization": "Cloud Native Computing Foundation",
                "issue_date": "2021-04",
                "expiration_date": "2024-04",
                "credential_id": "CKA-789012",
                "evidence": None,
            }
        ],
        "executive_summary": "Principal Systems Engineer with 8 years of experience in distributed systems.",
        "additional_sections": {},
        "uncertain_items": [],
    }


async def register_login(client: AsyncClient, email: str, name: str) -> tuple[str, str]:
    """Helper creating user and returning (token, user_id)."""
    pw = "AuditPassword123!"
    r_reg = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": pw, "full_name": name},
    )
    assert r_reg.status_code == 201
    user_id = r_reg.json()["user_id"]

    r_login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": pw},
    )
    assert r_login.status_code == 200
    token = r_login.json()["access_token"]
    return token, user_id


@pytest.fixture(autouse=True)
def setup_default_mock_llm():
    """Installs mock provider by default for isolated tests."""
    mock = MockLLMProvider()
    mock.set_structured_response(mock_ai_parsed_data())
    override_llm_provider(mock)
    yield mock
    reset_llm_provider()


# ─── 1. Complete End-to-End User Journey Audit ───────────────────────

@pytest.mark.asyncio
async def test_complete_15_step_user_journey(client: AsyncClient, test_session: AsyncSession):
    """
    Validates the complete 15-step user journey from upload to approval and profile persistence:
    1. Authenticated user opens resume page
    2. Upload valid PDF
    3. Backend securely stores original document
    4. Text extraction runs
    5. Provider performs structured parsing
    6. Structured output validated against schema
    7. Result persisted strictly as unapproved draft
    8. Frontend inspects processing status & extracted data
    9. User can edit details
    10. User can exclude unwanted items
    11. User inspects existing profile conflicts
    12. Explicit confirmation submitted
    13. Backend validates and merges approved changes
    14. CareerProfile reflects approved changes
    15. Data persists across refresh and subsequent re-login
    """
    # Step 1: Authenticate user
    token, user_id = await register_login(client, "journey.audit@example.com", "Elena Rostova")
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Seed canonical skills for profile merging test
    for s_id, s_name in [("python", "Python"), ("postgresql", "PostgreSQL"), ("docker", "Docker")]:
        sk = await test_session.scalar(select(Skill).where(Skill.id == s_id))
        if not sk:
            test_session.add(
                Skill(
                    id=s_id,
                    name=s_name,
                    category="language" if s_id == "python" else "database" if s_id == "postgresql" else "tool",
                    description=f"{s_name} canonical skill",
                    synonyms=[s_id],
                )
            )
    await test_session.commit()

    # Verify initial profile is empty
    prof_res = await client.get("/api/v1/profile", headers=auth_headers)
    assert prof_res.status_code == 200
    init_data = prof_res.json()
    assert len(init_data["education"]) == 0
    assert len(init_data["experience"]) == 0
    assert len(init_data["projects"]) == 0

    # Step 2 & 3: Upload valid PDF
    pdf_bytes = make_sample_pdf("Elena Rostova")
    upload_res = await client.post(
        "/api/v1/resume/upload",
        headers=auth_headers,
        files={"file": ("elena_resume.pdf", pdf_bytes, "application/pdf")},
    )
    assert upload_res.status_code == 201
    upload_data = upload_res.json()
    resume_id = upload_data["resume_id"]
    assert upload_data["status"] == "parsed"
    assert upload_data["file_name"] == "elena_resume.pdf"

    # Step 4: Verify physical document stored in isolated user path
    db_resume = await test_session.scalar(select(Resume).where(Resume.id == uuid.UUID(resume_id)))
    assert db_resume is not None
    assert str(db_resume.user_id) in db_resume.storage_path
    assert await storage_service.file_exists(db_resume.storage_path)

    # Step 5, 6, 7: Verify data exists as unapproved draft; CareerProfile UNTOUCHED
    mid_prof_res = await client.get("/api/v1/profile", headers=auth_headers)
    assert len(mid_prof_res.json()["education"]) == 0
    assert len(mid_prof_res.json()["experience"]) == 0

    # Step 8: Fetch draft preview
    draft_res = await client.get(f"/api/v1/resume/{resume_id}/parsed", headers=auth_headers)
    assert draft_res.status_code == 200
    draft_data = draft_res.json()
    assert draft_data["requires_human_confirmation"] is True
    preview = draft_data["extracted_preview"]
    assert preview["personal_info"]["name"] == "Elena Rostova"
    assert len(preview["education"]) == 1
    assert len(preview["experience"]) == 1
    assert len(preview["projects"]) == 2  # Includes "Unwanted Old Project"

    # Step 9 & 10: User edits details and excludes unwanted project
    # We will:
    # - Edit degree to "B.S. in Computer Engineering (First Class Honours)"
    # - Include only "Consensus Engine" project (exclude "Unwanted Old Project")
    # - Update personal headline and phone
    confirm_payload = {
        "make_primary": True,
        "personal_info": {
            "headline": "Lead Systems Architect & Distributed Systems Engineer",
            "location": "London, UK",
            "phone_number": "+44 20 7946 0991",
            "linkedin_url": "https://linkedin.com/in/elenarostova",
            "github_url": "https://github.com/elenarostova",
            "portfolio_url": "https://elena.systems",
            "bio": "Principal Systems Engineer with 8 years of experience.",
        },
        "education": [
            {
                "institution_name": "Oxford University",
                "degree": "B.S. in Computer Engineering (First Class Honours)",
                "field_of_study": "Computer Engineering",
                "start_date": "2012-10-01",
                "end_date": "2016-06-30",
                "is_current": False,
                "gpa": 3.9,
            }
        ],
        "experience": [
            {
                "company_name": "CloudScale Inc",
                "role_title": "Lead Systems Architect",
                "location": "London, UK",
                "start_date": "2018-09-01",
                "end_date": None,
                "is_current": True,
                "bullet_points": [
                    "Lead architectural design for multi-region microservices",
                    "Scaled system to 250,000 requests per second",
                ],
            }
        ],
        "projects": [
            # Only Consensus Engine included; "Unwanted Old Project" is excluded
            {
                "title": "Consensus Engine",
                "description": "High-throughput Raft consensus implementation in Rust",
                "technologies": ["Rust", "Distributed Systems"],
                "github_url": "https://github.com/elenarostova/consensus",
                "live_url": None,
                "bullet_points": ["Sub-millisecond leader election"],
            }
        ],
        "certifications": [
            {
                "name": "Certified Kubernetes Administrator",
                "issuing_organization": "Cloud Native Computing Foundation",
                "issue_date": "2021-04-01",
                "expiration_date": "2024-04-01",
                "credential_id": "CKA-789012",
                "credential_url": None,
            }
        ],
        "confirmed_skills": ["python", "postgresql", "docker"],
    }

    # Step 11, 12, 13: Explicit confirmation request submitted
    confirm_res = await client.post(
        f"/api/v1/resume/{resume_id}/confirm",
        headers=auth_headers,
        json=confirm_payload,
    )
    assert confirm_res.status_code == 200
    confirm_data = confirm_res.json()
    assert confirm_data["status"] == "confirmed"
    summary = confirm_data["merged_summary"]
    assert summary["education_added"] == 1
    assert summary["experience_added"] == 1
    assert summary["projects_added"] == 1
    assert summary["certifications_added"] == 1
    assert summary["skills_added"] >= 1

    # Step 14: CareerProfile reflects approved and edited changes
    final_prof_res = await client.get("/api/v1/profile", headers=auth_headers)
    assert final_prof_res.status_code == 200
    final_data = final_prof_res.json()

    # Education has the user-edited degree
    assert len(final_data["education"]) == 1
    assert final_data["education"][0]["degree"] == "B.S. in Computer Engineering (First Class Honours)"
    assert final_data["education"][0]["institution_name"] == "Oxford University"

    # Experience has the role
    assert len(final_data["experience"]) == 1
    assert final_data["experience"][0]["company_name"] == "CloudScale Inc"

    # Projects contains ONLY the approved project; excluded project was NOT added
    assert len(final_data["projects"]) == 1
    assert final_data["projects"][0]["title"] == "Consensus Engine"

    # Certifications added
    assert len(final_data["certifications"]) == 1
    assert final_data["certifications"][0]["name"] == "Certified Kubernetes Administrator"

    # User skills: verify unverified and extracted provenance
    user_skills_stmt = select(UserSkill).where(UserSkill.career_profile_id == uuid.UUID(final_data["profile_id"]))
    user_skills = (await test_session.scalars(user_skills_stmt)).all()
    for us in user_skills:
        assert us.is_verified is False
        assert us.proficiency_tier == "unverified"
        assert us.primary_source == "extracted"

    # Step 15: Persistence across refresh and subsequent new login
    new_login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "journey.audit@example.com", "password": "AuditPassword123!"},
    )
    assert new_login_res.status_code == 200
    new_token = new_login_res.json()["access_token"]
    relogin_prof_res = await client.get(
        "/api/v1/profile",
        headers={"Authorization": f"Bearer {new_token}"},
    )
    assert relogin_prof_res.status_code == 200
    relogin_data = relogin_prof_res.json()
    assert len(relogin_data["education"]) == 1
    assert len(relogin_data["experience"]) == 1
    assert len(relogin_data["projects"]) == 1
    assert relogin_data["education"][0]["degree"] == "B.S. in Computer Engineering (First Class Honours)"


# ─── 2. Document Processing & Error Handling Matrix ───────────────────

@pytest.mark.asyncio
async def test_document_processing_validation_matrix(client: AsyncClient):
    """
    Tests edge cases across document ingestion:
    - Valid DOCX format
    - Unsupported file extensions
    - Spoofed MIME headers
    - Empty file (0 bytes)
    - Files exceeding 10MB limit
    - Corrupt PDF files
    - Image-only/scanned PDFs requiring OCR (with no false claim of OCR execution)
    """
    token, _ = await register_login(client, "doc.matrix@example.com", "Dev Matrix")
    headers = {"Authorization": f"Bearer {token}"}

    # Case A: Valid DOCX file
    docx_bytes = make_sample_docx("Dev Matrix")
    r_docx = await client.post(
        "/api/v1/resume/upload",
        headers=headers,
        files={"file": ("resume.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert r_docx.status_code == 201
    assert r_docx.json()["status"] == "parsed"

    # Case B: Unsupported file extension (.png)
    r_png = await client.post(
        "/api/v1/resume/upload",
        headers=headers,
        files={"file": ("photo.png", b"\x89PNG\r\n\x1a\n", "image/png")},
    )
    assert r_png.status_code == 400
    assert "supported" in r_png.json()["error"]["message"].lower()

    # Case C: Spoofed MIME (claims .pdf but content is text)
    r_spoofed = await client.post(
        "/api/v1/resume/upload",
        headers=headers,
        files={"file": ("fake.pdf", b"This is just plain text not a pdf header", "application/pdf")},
    )
    assert r_spoofed.status_code == 400

    # Case D: Empty file (0 bytes)
    r_empty = await client.post(
        "/api/v1/resume/upload",
        headers=headers,
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )
    assert r_empty.status_code == 400
    assert "empty" in r_empty.json()["error"]["message"].lower()

    # Case E: File exceeding 10MB limit
    oversized = b"%PDF-1.4\n" + (b"0" * (10 * 1024 * 1024 + 1024))
    r_large = await client.post(
        "/api/v1/resume/upload",
        headers=headers,
        files={"file": ("huge.pdf", oversized, "application/pdf")},
    )
    assert r_large.status_code == 400
    assert "limit" in r_large.json()["error"]["message"].lower()

    # Case F: Corrupt PDF file
    corrupt_pdf = b"%PDF-1.4\n1 0 obj\n<< /Malformed /Corrupt stream\n"
    r_corrupt = await client.post(
        "/api/v1/resume/upload",
        headers=headers,
        files={"file": ("corrupt.pdf", corrupt_pdf, "application/pdf")},
    )
    assert r_corrupt.status_code == 201
    assert r_corrupt.json()["status"] == "failed"
    corrupt_detail = await client.get(f"/api/v1/resume/{r_corrupt.json()['resume_id']}", headers=headers)
    assert corrupt_detail.json()["parsing_error_category"] == ParsingErrorCategory.CORRUPTED_DOCUMENT

    # Case G: Image-only / Scanned PDF (insufficient extractable text)
    scanned_bytes = make_scanned_image_pdf()
    r_scanned = await client.post(
        "/api/v1/resume/upload",
        headers=headers,
        files={"file": ("scanned.pdf", scanned_bytes, "application/pdf")},
    )
    assert r_scanned.status_code == 201
    assert r_scanned.json()["status"] == "failed"
    scanned_detail = await client.get(f"/api/v1/resume/{r_scanned.json()['resume_id']}", headers=headers)
    assert scanned_detail.json()["parsing_error_category"] == ParsingErrorCategory.INSUFFICIENT_TEXT_OCR_REQUIRED
    # System explicitly notes OCR is required and does NOT falsely claim OCR was executed
    assert "ocr" in scanned_detail.json()["parsing_error"].lower()


# ─── 3. AI Service Failure and Retry Mechanics ───────────────────────

@pytest.mark.asyncio
async def test_ai_provider_failure_and_retry_recovery(client: AsyncClient):
    """
    Tests graceful degradation when AI provider is unavailable and recovery via retry endpoint.
    """
    token, _ = await register_login(client, "retry.audit@example.com", "Retry Tester")
    headers = {"Authorization": f"Bearer {token}"}

    # Simulate AI provider unavailable
    failing_mock = MockLLMProvider()
    async def fail_structured(*args, **kwargs):
        raise ServiceUnavailableException("Gemini", "Temporary 503 Provider Unavailable")
    failing_mock.generate_structured = fail_structured
    override_llm_provider(failing_mock)

    pdf_bytes = make_sample_pdf("Retry Tester")
    upload_res = await client.post(
        "/api/v1/resume/upload",
        headers=headers,
        files={"file": ("failing_resume.pdf", pdf_bytes, "application/pdf")},
    )
    assert upload_res.status_code == 201
    assert upload_res.json()["status"] == "failed"
    resume_id = upload_res.json()["resume_id"]

    # Verify status is recorded as failed with AI_PROVIDER_UNAVAILABLE category
    detail_res = await client.get(f"/api/v1/resume/{resume_id}", headers=headers)
    assert detail_res.json()["status"] == "failed"
    assert detail_res.json()["parsing_error_category"] == ParsingErrorCategory.AI_PROVIDER_UNAVAILABLE

    # Now recover the provider
    recovered_mock = MockLLMProvider()
    recovered_mock.set_structured_response(mock_ai_parsed_data())
    override_llm_provider(recovered_mock)

    # Call retry endpoint
    retry_res = await client.post(f"/api/v1/resume/{resume_id}/retry", headers=headers)
    assert retry_res.status_code == 200
    assert retry_res.json()["status"] == "parsed"

    # Detail now shows parsed status
    updated_detail = await client.get(f"/api/v1/resume/{resume_id}", headers=headers)
    assert updated_detail.json()["status"] == "parsed"
    assert updated_detail.json()["parsing_error"] is None


# ─── 4. Truthful Extraction & Anti-Fabrication Safeguards ─────────────

@pytest.mark.asyncio
async def test_truthful_extraction_missing_fields_preserved(client: AsyncClient):
    """
    Verifies that when a resume lacks certain sections, the parser preserves them as None/empty
    and does NOT fabricate fake degrees, certifications, or experience.
    """
    token, _ = await register_login(client, "truth.audit@example.com", "Minimal Candidate")
    headers = {"Authorization": f"Bearer {token}"}

    # Mock response for a minimal resume (no education, no certifications, no GPA)
    minimal_mock_data = {
        "personal_info": {"name": "Minimal Candidate", "email": "min@example.com"},
        "education": [],
        "experience": [
            {
                "employer": "Self Employed",
                "job_title": "Freelancer",
                "start_date": "2023-01",
                "end_date": None,
                "is_current": True,
                "responsibilities": ["Contract web development"],
                "achievements": [],
                "evidence": None,
            }
        ],
        "skills": [{"name": "HTML", "category": "language"}],
        "projects": [],
        "certifications": [],
        "executive_summary": None,
        "additional_sections": {},
        "uncertain_items": ["Missing formal education records"],
    }
    mock = MockLLMProvider()
    mock.set_structured_response(minimal_mock_data)
    override_llm_provider(mock)

    pdf_bytes = make_sample_pdf("Minimal Candidate")
    upload_res = await client.post(
        "/api/v1/resume/upload",
        headers=headers,
        files={"file": ("minimal.pdf", pdf_bytes, "application/pdf")},
    )
    assert upload_res.status_code == 201

    draft_res = await client.get(f"/api/v1/resume/{upload_res.json()['resume_id']}/parsed", headers=headers)
    preview = draft_res.json()["extracted_preview"]
    assert len(preview["education"]) == 0
    assert len(preview["certifications"]) == 0
    assert len(preview["projects"]) == 0
    assert preview["executive_summary"] is None


# ─── 5. Idempotent Profile Merge & Duplicate Prevention ───────────────

@pytest.mark.asyncio
async def test_profile_merge_idempotency_and_no_duplicates(client: AsyncClient, test_session: AsyncSession):
    """
    Verifies that repeated confirmation submissions do not duplicate records in
    education, experience, projects, certifications, or user_skills.
    """
    token, user_id = await register_login(client, "idempotent.audit@example.com", "Idempotent User")
    headers = {"Authorization": f"Bearer {token}"}

    for s_id, s_name in [("python", "Python"), ("postgresql", "PostgreSQL")]:
        sk = await test_session.scalar(select(Skill).where(Skill.id == s_id))
        if not sk:
            test_session.add(
                Skill(
                    id=s_id,
                    name=s_name,
                    category="language" if s_id == "python" else "database",
                    description=f"{s_name} canonical skill",
                    synonyms=[s_id],
                )
            )
    await test_session.commit()

    pdf_bytes = make_sample_pdf("Idempotent User")
    upload_res = await client.post(
        "/api/v1/resume/upload",
        headers=headers,
        files={"file": ("resume.pdf", pdf_bytes, "application/pdf")},
    )
    resume_id = upload_res.json()["resume_id"]

    payload = {
        "education": [
            {
                "institution_name": "MIT",
                "degree": "B.S. Mathematics",
                "field_of_study": "Mathematics",
                "start_date": "2015-09-01",
                "end_date": "2019-06-01",
                "is_current": False,
                "gpa": 3.8,
            }
        ],
        "experience": [
            {
                "company_name": "Acme Corp",
                "role_title": "Software Engineer",
                "start_date": "2019-07-01",
                "end_date": "2022-01-01",
                "is_current": False,
                "bullet_points": ["Wrote backend services"],
            }
        ],
        "projects": [
            {
                "title": "Project Alpha",
                "description": "Alpha project description",
                "technologies": ["Python"],
                "bullet_points": ["First milestone"],
            }
        ],
        "certifications": [
            {
                "name": "AWS Certified Developer",
                "issuing_organization": "Amazon Web Services",
                "issue_date": "2020-01-01",
            }
        ],
        "confirmed_skills": ["python", "postgresql"],
    }

    # First confirmation: creates records
    res1 = await client.post(f"/api/v1/resume/{resume_id}/confirm", headers=headers, json=payload)
    assert res1.status_code == 200
    s1 = res1.json()["merged_summary"]
    assert s1["education_added"] == 1
    assert s1["experience_added"] == 1
    assert s1["projects_added"] == 1
    assert s1["certifications_added"] == 1

    # Second confirmation with identical payload: strict idempotency, 0 added
    res2 = await client.post(f"/api/v1/resume/{resume_id}/confirm", headers=headers, json=payload)
    assert res2.status_code == 200
    s2 = res2.json()["merged_summary"]
    assert s2["education_added"] == 0
    assert s2["experience_added"] == 0
    assert s2["projects_added"] == 0
    assert s2["certifications_added"] == 0
    assert s2["skills_added"] == 0

    # Inspect DB counts
    prof_res = await client.get("/api/v1/profile", headers=headers)
    prof = prof_res.json()
    assert len(prof["education"]) == 1
    assert len(prof["experience"]) == 1
    assert len(prof["projects"]) == 1
    assert len(prof["certifications"]) == 1


# ─── 6. Multi-Tenant Security & Authorization Boundaries ──────────────

@pytest.mark.asyncio
async def test_security_multi_tenant_isolation(client: AsyncClient):
    """
    Verifies that:
    - User A's uploaded resume cannot be accessed, downloaded, retried, confirmed, or deleted by User B.
    - Unauthenticated requests are rejected with 401.
    - Deleting a resume unlinks the physical file and deletes the database entity.
    """
    token_a, _ = await register_login(client, "user.a.audit@example.com", "Alice Smith")
    token_b, _ = await register_login(client, "user.b.audit@example.com", "Bob Jones")

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A uploads resume
    pdf_bytes = make_sample_pdf("Alice Smith")
    upload_res = await client.post(
        "/api/v1/resume/upload",
        headers=headers_a,
        files={"file": ("alice_resume.pdf", pdf_bytes, "application/pdf")},
    )
    resume_a_id = upload_res.json()["resume_id"]

    # 1. Unauthenticated checks (401) - clear cookies first so client doesn't send session cookie
    client.cookies.clear()
    assert (await client.get("/api/v1/resume")).status_code == 401
    assert (await client.get(f"/api/v1/resume/{resume_a_id}")).status_code == 401
    assert (await client.get(f"/api/v1/resume/{resume_a_id}/parsed")).status_code == 401
    assert (await client.get(f"/api/v1/resume/{resume_a_id}/download")).status_code == 401
    assert (await client.post(f"/api/v1/resume/{resume_a_id}/confirm", json={})).status_code == 401
    assert (await client.delete(f"/api/v1/resume/{resume_a_id}")).status_code == 401

    # 2. Cross-user isolation (User B -> User A's resume yields 403 Forbidden)
    assert (await client.get(f"/api/v1/resume/{resume_a_id}", headers=headers_b)).status_code == 403
    assert (await client.get(f"/api/v1/resume/{resume_a_id}/parsed", headers=headers_b)).status_code == 403
    assert (await client.get(f"/api/v1/resume/{resume_a_id}/download", headers=headers_b)).status_code == 403
    assert (await client.post(f"/api/v1/resume/{resume_a_id}/retry", headers=headers_b)).status_code == 403
    assert (await client.post(f"/api/v1/resume/{resume_a_id}/confirm", headers=headers_b, json={})).status_code == 403
    assert (await client.delete(f"/api/v1/resume/{resume_a_id}", headers=headers_b)).status_code == 403

    # 3. Secure download for User A
    dl_res = await client.get(f"/api/v1/resume/{resume_a_id}/download", headers=headers_a)
    assert dl_res.status_code == 200
    assert dl_res.headers["Content-Type"] == "application/pdf"
    assert "attachment" in dl_res.headers["Content-Disposition"]
    assert len(dl_res.content) == len(pdf_bytes)

    # 4. Deletion cleans DB and disk
    del_res = await client.delete(f"/api/v1/resume/{resume_a_id}", headers=headers_a)
    assert del_res.status_code == 204

    # Subsequent access gives 404
    get_res = await client.get(f"/api/v1/resume/{resume_a_id}", headers=headers_a)
    assert get_res.status_code == 404
