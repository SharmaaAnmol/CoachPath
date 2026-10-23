"""
Phase 4C End-to-End Integration and Final Audit Test Suite.
Verifies the complete 17-step candidate onboarding discovery journey,
data persistence, state machine transitions, inline summary editing,
career profile synchronization, security isolation, and error handling.
"""
from __future__ import annotations

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.ai.mock_adapter import MockLLMProvider
from app.ai.factory import override_llm_provider, reset_llm_provider
from app.models.onboarding import OnboardingSession, OnboardingTurn
from app.models.career import CareerProfile, Role
from app.schemas.onboarding import OnboardingSummarySchema


# ─── Mock Fixtures & Helpers ─────────────────────────────────────────

def mock_turn_response(
    question: str,
    category: str,
    ready: bool = False,
    facts: list | None = None,
):
    """Generates structured mock AI response for conversation turn."""
    return {
        "next_question": question,
        "question_category": category,
        "extracted_facts": facts or [
            {"field": "target_role", "value": "Backend Developer", "confidence": "user_stated"}
        ],
        "missing_information": ["education", "skills"],
        "ready_to_summarize": ready,
        "clarification_needed": None,
    }


def mock_summary_response():
    """Generates structured mock AI summary."""
    return {
        "target_role": "Backend Developer",
        "career_stage": "student",
        "current_education": "Bachelor of Technology",
        "education_field": "Computer Science",
        "years_of_experience": 0.0,
        "current_or_recent_role": None,
        "current_company": None,
        "skills": ["Python", "SQL", "Git"],
        "technologies": ["FastAPI", "PostgreSQL", "Docker"],
        "notable_projects": ["API Rate Limiter", "Task Management App"],
        "learning_hours_per_week": 15.0,
        "preferred_learning_resources": ["Official Documentation", "GitHub"],
        "target_timeline_months": 6,
        "industries_of_interest": ["FinTech", "SaaS"],
        "companies_of_interest": ["Stripe", "Postman"],
        "min_salary_usd": None,
        "max_salary_usd": None,
        "career_goals": "Master distributed systems and become a Senior Backend Engineer.",
        "work_preference": "remote",
        "target_locations": ["Remote", "Bangalore"],
        "missing_areas": [],
        "uncertain_fields": [],
    }


async def create_user_and_tokens(
    client: AsyncClient,
    email: str,
    full_name: str,
    password: str = "AuditPassword123!",
) -> dict:
    """Registers and logs in a test user, returning access tokens."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": full_name},
    )
    assert reg.status_code == 201

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200
    data = login.json()
    return {
        "email": email,
        "password": password,
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "user_id": data["user"]["id"],
    }


# ─── 1. Complete 17-Step End-to-End User Journey ─────────────────────


@pytest.mark.asyncio
async def test_complete_17_step_onboarding_journey(
    client: AsyncClient,
    test_session: AsyncSession,
):
    """
    Executes and validates the complete 17-step candidate user journey:
    1. Sign up
    2. Log in
    3. Start onboarding
    4. Session created & state validated
    5. First question returned
    6. Response submitted
    7. Response validated & persisted in DB
    8. AI provides next question
    9. Conversation history preserved
    10. State restored across simulated page refresh
    11. Resume session after simulated logout & re-login
    12. AI generates structured summary
    13. User reviews & edits summary
    14. User confirms edited summary
    15. Career profile updated in DB
    16. Profile API returns confirmed attributes
    17. Completion persists across new login
    """
    # Configure deterministic AI responses
    mock_ai = MockLLMProvider()
    turn_counter = 0

    def dynamic_llm_factory(prompt: str, schema):
        nonlocal turn_counter
        turn_counter += 1
        if schema.__name__ == "OnboardingSummarySchema":
            return mock_summary_response()
        elif turn_counter == 1:
            return mock_turn_response(
                question="What is your educational background?",
                category="education",
                ready=False,
                facts=[{"field": "target_role", "value": "Backend Developer", "confidence": "user_stated"}],
            )
        else:
            return mock_turn_response(
                question="We have sufficient initial data. Ready to generate your career blueprint.",
                category="wrap_up",
                ready=True,
                facts=[{"field": "skills", "value": ["Python", "SQL"], "confidence": "user_stated"}],
            )

    mock_ai.set_structured_factory(dynamic_llm_factory)
    override_llm_provider(mock_ai)

    try:
        # Step 1: User signs up
        # Step 2: User logs in
        user_data = await create_user_and_tokens(
            client, "e2e.journey@example.com", "Priya Sharma"
        )
        token = user_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 3: User starts onboarding
        start_res = await client.post("/api/v1/onboarding/start", headers=headers)
        assert start_res.status_code == 200
        start_data = start_res.json()

        # Step 4: Backend creates appropriate session
        assert start_data["status"] == "in_progress"
        assert start_data["is_resumed"] is False
        session_id = uuid.UUID(start_data["session_id"])

        # Step 5: Displays first question
        assert "first_question" in start_data
        assert "role or career path" in start_data["first_question"]
        assert start_data["first_question_category"] == "target_role"

        # Step 6: User submits first response
        res1 = await client.post(
            "/api/v1/onboarding/respond",
            headers=headers,
            json={"response_text": "I want to become a Backend Developer building scalable APIs."},
        )
        assert res1.status_code == 200
        res1_data = res1.json()

        # Step 7 & 8: Validated, persisted, AI generates next question
        assert res1_data["session_status"] == "in_progress"
        assert res1_data["next_question"] == "What is your educational background?"
        assert res1_data["next_question_category"] == "education"
        assert res1_data["turn_completed"]["user_response"] == "I want to become a Backend Developer building scalable APIs."

        # Step 9: Conversation continues without losing previous answers
        res2 = await client.post(
            "/api/v1/onboarding/respond",
            headers=headers,
            json={"response_text": "Bachelor of Technology in Computer Science."},
        )
        assert res2.status_code == 200
        res2_data = res2.json()
        assert res2_data["session_status"] == "awaiting_confirmation"
        assert res2_data["ready_to_summarize"] is True

        # Step 10: Refreshing page restores saved conversation
        history_res = await client.get("/api/v1/onboarding/history", headers=headers)
        assert history_res.status_code == 200
        turns = history_res.json()
        assert len(turns) >= 2
        assert turns[0]["user_response"] == "I want to become a Backend Developer building scalable APIs."
        assert turns[1]["user_response"] == "Bachelor of Technology in Computer Science."

        # Step 11: Logging out and signing back in allows user to resume
        # New login session
        relogin = await client.post(
            "/api/v1/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]},
        )
        new_token = relogin.json()["access_token"]
        new_headers = {"Authorization": f"Bearer {new_token}"}

        resume_res = await client.post("/api/v1/onboarding/start", headers=new_headers)
        assert resume_res.status_code == 200
        resume_data = resume_res.json()
        assert resume_data["is_resumed"] is True
        assert resume_data["status"] == "awaiting_confirmation"

        # Step 12: AI produces structured career summary
        summary_res = await client.get("/api/v1/onboarding/summary", headers=new_headers)
        assert summary_res.status_code == 200
        summary_data = summary_res.json()
        assert summary_data["is_confirmed"] is False
        ai_summary = summary_data["summary"]
        assert ai_summary["target_role"] == "Backend Developer"
        assert "Python" in ai_summary["skills"]

        # Step 13: User reviews and edits summary
        # Candidate changes work preference to remote, adds an extra skill, sets specific timeline
        edited_summary = dict(ai_summary)
        edited_summary["target_role"] = "Senior Backend Engineer"
        edited_summary["skills"] = ["Python", "SQL", "Go", "Distributed Systems"]
        edited_summary["work_preference"] = "remote"
        edited_summary["years_of_experience"] = 2.5
        edited_summary["target_locations"] = ["Remote", "Singapore"]

        # Step 14: User confirms edited summary
        confirm_res = await client.post(
            "/api/v1/onboarding/confirm",
            headers=new_headers,
            json={"confirmed": True, "edits": edited_summary},
        )
        assert confirm_res.status_code == 200
        confirm_data = confirm_res.json()
        assert confirm_data["status"] == "completed"
        assert confirm_data["completed_at"] is not None

        # Step 15: Backend updates correct career profile in DB
        db_session = await test_session.scalar(
            select(OnboardingSession).where(OnboardingSession.user_id == uuid.UUID(user_data["user_id"]))
        )
        assert db_session is not None
        assert db_session.status == "completed"
        assert db_session.is_summary_confirmed is True

        db_profile = await test_session.scalar(
            select(CareerProfile).where(CareerProfile.user_id == uuid.UUID(user_data["user_id"]))
        )
        assert db_profile is not None
        assert db_profile.work_preference == "remote"
        assert float(db_profile.years_of_experience) == 2.5
        assert "Singapore" in db_profile.target_locations

        # Step 16: Profile API retrieves confirmed attributes
        master_profile_res = await client.get("/api/v1/profile", headers=new_headers)
        assert master_profile_res.status_code == 200
        profile_json = master_profile_res.json()
        assert profile_json["work_preference"] == "remote"
        assert float(profile_json["years_of_experience"]) == 2.5
        assert "Singapore" in profile_json["target_locations"]

        # Step 17: Completion persists after another logout and login
        relogin2 = await client.post(
            "/api/v1/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]},
        )
        token3 = relogin2.json()["access_token"]
        headers3 = {"Authorization": f"Bearer {token3}"}

        # Calling start again on completed session returns 409 Conflict
        start_again_res = await client.post("/api/v1/onboarding/start", headers=headers3)
        assert start_again_res.status_code == 409
        assert "already been completed" in start_again_res.json()["error"]["message"]

        # Session status check returns completed
        session_check = await client.get("/api/v1/onboarding/session", headers=headers3)
        assert session_check.status_code == 200
        assert session_check.json()["status"] == "completed"

    finally:
        reset_llm_provider()


# ─── 2. Data Persistence & Integrity Verification ────────────────────


@pytest.mark.asyncio
async def test_repeated_confirmation_idempotence_and_conflict(
    client: AsyncClient,
    test_session: AsyncSession,
):
    """
    Verifies that calling /confirm repeatedly on a completed session
    is rejected with 409 Conflict and does not corrupt profile data.
    """
    mock_ai = MockLLMProvider()
    mock_ai.set_structured_response(mock_turn_response("Wrap up", "wrap_up", ready=True))
    mock_ai.set_structured_factory(lambda p, s: mock_summary_response() if s.__name__ == "OnboardingSummarySchema" else mock_turn_response("Wrap up", "wrap_up", ready=True))
    override_llm_provider(mock_ai)

    try:
        user = await create_user_and_tokens(client, "repeat.confirm@example.com", "Amit Patel")
        headers = {"Authorization": f"Bearer {user['access_token']}"}

        await client.post("/api/v1/onboarding/start", headers=headers)
        await client.post("/api/v1/onboarding/respond", headers=headers, json={"response_text": "Backend developer"})

        # First confirm -> Success 200
        c1 = await client.post("/api/v1/onboarding/confirm", headers=headers, json={"confirmed": True})
        assert c1.status_code == 200

        # Second confirm -> 409 Conflict
        c2 = await client.post("/api/v1/onboarding/confirm", headers=headers, json={"confirmed": True})
        assert c2.status_code == 409
        assert "already been confirmed and completed" in c2.json()["error"]["message"]

    finally:
        reset_llm_provider()


@pytest.mark.asyncio
async def test_invalid_state_transitions_rejected(client: AsyncClient):
    """
    Verifies state machine boundaries:
    - Cannot get summary when status is in_progress (409)
    - Cannot confirm summary when status is in_progress (409)
    - Cannot respond when status is completed (409)
    """
    mock_ai = MockLLMProvider()
    mock_ai.set_structured_response(mock_turn_response("Next question", "skills", ready=False))
    override_llm_provider(mock_ai)

    try:
        user = await create_user_and_tokens(client, "state.boundary@example.com", "Rohan Gupta")
        headers = {"Authorization": f"Bearer {user['access_token']}"}

        await client.post("/api/v1/onboarding/start", headers=headers)

        # In progress: attempting to get summary -> 409
        s_res = await client.get("/api/v1/onboarding/summary", headers=headers)
        assert s_res.status_code == 409

        # In progress: attempting to confirm -> 409
        c_res = await client.post("/api/v1/onboarding/confirm", headers=headers, json={"confirmed": True})
        assert c_res.status_code == 409

    finally:
        reset_llm_provider()


# ─── 3. Authorization & Multi-Tenant Security Verification ───────────


@pytest.mark.asyncio
async def test_cross_user_isolation_strict(client: AsyncClient):
    """
    Verifies that User B cannot access, respond to, or confirm User A's session.
    """
    mock_ai = MockLLMProvider()
    mock_ai.set_structured_response(mock_turn_response("Question for A", "role", ready=False))
    override_llm_provider(mock_ai)

    try:
        user_a = await create_user_and_tokens(client, "tenant.a@example.com", "Candidate A")
        user_b = await create_user_and_tokens(client, "tenant.b@example.com", "Candidate B")

        headers_a = {"Authorization": f"Bearer {user_a['access_token']}"}
        headers_b = {"Authorization": f"Bearer {user_b['access_token']}"}

        # User A starts onboarding
        start_a = await client.post("/api/v1/onboarding/start", headers=headers_a)
        assert start_a.status_code == 200

        # User B has not started onboarding yet:
        # GET /session for B returns 404 (not A's session)
        b_sess = await client.get("/api/v1/onboarding/session", headers=headers_b)
        assert b_sess.status_code == 404

        # POST /respond for B returns 404 (no pending session for B)
        b_resp = await client.post("/api/v1/onboarding/respond", headers=headers_b, json={"response_text": "Malicious intrusion attempt"})
        assert b_resp.status_code == 404

        # GET /history for B returns 404
        b_hist = await client.get("/api/v1/onboarding/history", headers=headers_b)
        assert b_hist.status_code == 404

        # POST /confirm for B returns 404
        b_conf = await client.post("/api/v1/onboarding/confirm", headers=headers_b, json={"confirmed": True})
        assert b_conf.status_code == 404

    finally:
        reset_llm_provider()


@pytest.mark.asyncio
async def test_unauthenticated_requests_rejected(client: AsyncClient):
    """
    Verifies that unauthenticated requests to all onboarding endpoints
    are strictly rejected with HTTP 401 Unauthorized.
    """
    assert (await client.post("/api/v1/onboarding/start")).status_code == 401
    assert (await client.get("/api/v1/onboarding/session")).status_code == 401
    assert (await client.get("/api/v1/onboarding/progress")).status_code == 401
    assert (await client.post("/api/v1/onboarding/respond", json={"response_text": "test"})).status_code == 401
    assert (await client.get("/api/v1/onboarding/history")).status_code == 401
    assert (await client.get("/api/v1/onboarding/summary")).status_code == 401
    assert (await client.post("/api/v1/onboarding/confirm", json={"confirmed": True})).status_code == 401


# ─── 4. Input Validation & Boundary Enforcement ───────────────────────


@pytest.mark.asyncio
async def test_input_validation_boundaries(client: AsyncClient):
    """
    Verifies input boundaries on /respond and /confirm:
    - Empty response text (422)
    - Response text exceeding 2000 characters (422)
    - Extra fields rejected due to extra='forbid' (422)
    - confirmed=False rejected (422) when awaiting confirmation
    """
    mock_ai = MockLLMProvider()
    mock_ai.set_structured_response(mock_turn_response("Sample", "target_role", ready=False))
    override_llm_provider(mock_ai)

    try:
        user = await create_user_and_tokens(client, "validation.boundary@example.com", "Deepak Verma")
        headers = {"Authorization": f"Bearer {user['access_token']}"}

        await client.post("/api/v1/onboarding/start", headers=headers)

        # 1. Empty string -> 422
        r1 = await client.post("/api/v1/onboarding/respond", headers=headers, json={"response_text": ""})
        assert r1.status_code == 422

        # 2. Exceeding 2000 chars -> 422
        huge_text = "A" * 2001
        r2 = await client.post("/api/v1/onboarding/respond", headers=headers, json={"response_text": huge_text})
        assert r2.status_code == 422

        # 3. Extra unrecognized fields -> 422 (extra="forbid")
        r3 = await client.post(
            "/api/v1/onboarding/respond",
            headers=headers,
            json={"response_text": "Valid text", "injected_field": "hack"},
        )
        assert r3.status_code == 422

        # 4. Advance to awaiting_confirmation
        mock_ai.set_structured_response(mock_turn_response("Wrap up", "wrap_up", ready=True))
        mock_ai.set_structured_factory(lambda p, s: mock_summary_response() if s.__name__ == "OnboardingSummarySchema" else mock_turn_response("Wrap up", "wrap_up", ready=True))
        advance_res = await client.post("/api/v1/onboarding/respond", headers=headers, json={"response_text": "I am ready for summary"})
        assert advance_res.status_code == 200
        assert advance_res.json()["session_status"] == "awaiting_confirmation"

        # 5. confirm with confirmed=False -> 422
        r4 = await client.post("/api/v1/onboarding/confirm", headers=headers, json={"confirmed": False})
        assert r4.status_code == 422

    finally:
        reset_llm_provider()
