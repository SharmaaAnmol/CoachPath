"""
Comprehensive Integration & Security Tests for Phase 4A: AI-Powered Career Onboarding.
Verifies the complete onboarding lifecycle, AI conversation turns, Pydantic schema validation,
state transitions, truthfulness, profile merging, cross-user isolation, and failure resilience.
All tests use MockLLMProvider — zero external network or paid API calls.
"""

from __future__ import annotations

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base import LLMProvider
from app.ai.factory import override_llm_provider, reset_llm_provider
from app.ai.mock_adapter import MockLLMProvider
from app.ai.openai_adapter import OpenAIProviderAdapter
from app.models.career import CareerProfile, Role
from app.models.onboarding import OnboardingSession, OnboardingTurn
from app.schemas.onboarding import OnboardingStatus


# ─── Test Helpers & Mocks ───────────────────────────────────────────


async def register_and_login(client: AsyncClient, email: str, full_name: str) -> str:
    """Helper creating user account and returning valid JWT bearer token."""
    pw = "SecurePassword123!"
    reg_res = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": pw, "full_name": full_name},
    )
    assert reg_res.status_code == 201

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": pw},
    )
    assert login_res.status_code == 200
    return login_res.json()["access_token"]


def make_ai_question_response(
    next_question: str = "What is your highest level of completed education?",
    category: str = "education",
    ready: bool = False,
    extracted_field: str = "target_role",
    extracted_val: str = "Backend Developer",
) -> dict:
    return {
        "next_question": next_question,
        "question_category": category,
        "extracted_facts": [
            {"field": extracted_field, "value": extracted_val, "confidence": "user_stated"}
        ],
        "missing_information": ["education", "skills"],
        "ready_to_summarize": ready,
        "clarification_needed": None,
    }


def make_ai_summary_response(
    target_role: str = "Backend Developer",
    career_stage: str = "early_career",
    work_preference: str = "remote",
) -> dict:
    return {
        "target_role": target_role,
        "career_stage": career_stage,
        "current_education": "Bachelor of Technology",
        "education_field": "Computer Science",
        "years_of_experience": 1.5,
        "current_or_recent_role": "Junior Python Developer",
        "current_company": "Acme Corp",
        "skills": ["Python", "PostgreSQL", "Docker", "FastAPI"],
        "technologies": ["Git", "Linux", "Redis"],
        "notable_projects": ["Distributed task queue in Python"],
        "learning_hours_per_week": 12.0,
        "preferred_learning_resources": ["Official Documentation", "GitHub Repos"],
        "target_timeline_months": 6,
        "industries_of_interest": ["FinTech", "Developer Tooling"],
        "companies_of_interest": ["Stripe", "Datadog"],
        "min_salary_usd": 85000,
        "max_salary_usd": 110000,
        "career_goals": "Transition into mid-level backend architecture",
        "work_preference": work_preference,
        "target_locations": ["Bengaluru", "Remote"],
        "missing_areas": [],
        "uncertain_fields": [],
    }


@pytest.fixture(autouse=True)
def mock_llm_fixture():
    """Installs clean MockLLMProvider for every test and resets on teardown."""
    mock = MockLLMProvider()
    mock.set_structured_response(make_ai_question_response())
    override_llm_provider(mock)
    yield mock
    reset_llm_provider()


# ─── 1. Initiation & Session Lifecycle Tests ────────────────────────


@pytest.mark.asyncio
async def test_start_onboarding_fresh_session(client: AsyncClient, test_session: AsyncSession):
    """Verifies that a new candidate starts onboarding and receives turn 1."""
    token = await register_and_login(client, "start.fresh@test.com", "Aarav Gupta")

    res = await client.post(
        "/api/v1/onboarding/start",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()

    assert data["status"] == OnboardingStatus.IN_PROGRESS
    assert data["is_resumed"] is False
    assert "session_id" in data
    assert "target_role" in data["first_question_category"]
    assert len(data["first_question"]) > 10


@pytest.mark.asyncio
async def test_start_onboarding_resumes_existing_session(client: AsyncClient):
    """Verifies that calling /start again safely resumes the existing session."""
    token = await register_and_login(client, "start.resume@test.com", "Ananya Sen")

    # Call start first time
    res1 = await client.post(
        "/api/v1/onboarding/start",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res1.status_code == 200
    session_id_1 = res1.json()["session_id"]

    # Call start second time (simulate page refresh)
    res2 = await client.post(
        "/api/v1/onboarding/start",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res2.status_code == 200
    data2 = res2.json()

    assert data2["is_resumed"] is True
    assert data2["session_id"] == session_id_1
    assert data2["status"] == OnboardingStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_start_onboarding_unauthenticated(client: AsyncClient):
    """Verifies that unauthenticated access is rejected with 401."""
    res = await client.post("/api/v1/onboarding/start")
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"


@pytest.mark.asyncio
async def test_get_session_status_lifecycle(client: AsyncClient):
    """Verifies retrieval of session status when absent vs active."""
    token = await register_and_login(client, "session.status@test.com", "Rohan Verma")

    # Before starting: 404
    res_404 = await client.get(
        "/api/v1/onboarding/session",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_404.status_code == 404

    # After starting: 200 with details
    await client.post(
        "/api/v1/onboarding/start",
        headers={"Authorization": f"Bearer {token}"},
    )
    res_200 = await client.get(
        "/api/v1/onboarding/session",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_200.status_code == 200
    data = res_200.json()
    assert data["status"] == OnboardingStatus.IN_PROGRESS
    assert data["turn_count"] == 0
    assert data["current_question"] is not None


@pytest.mark.asyncio
async def test_get_onboarding_progress(client: AsyncClient):
    """Verifies tracking of covered vs remaining discovery areas."""
    token = await register_and_login(client, "progress.track@test.com", "Kavita Reddy")
    await client.post(
        "/api/v1/onboarding/start",
        headers={"Authorization": f"Bearer {token}"},
    )

    res = await client.get(
        "/api/v1/onboarding/progress",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == OnboardingStatus.IN_PROGRESS
    assert data["turn_count"] == 0
    assert len(data["areas_remaining"]) > 10
    assert data["ready_to_summarize"] is False


# ─── 2. Conversational Turns & Fact Extraction Tests ───────────────


@pytest.mark.asyncio
async def test_submit_response_extracts_facts_and_advances(
    client: AsyncClient,
    mock_llm_fixture: MockLLMProvider,
    test_session: AsyncSession,
):
    """Verifies answer persistence, AI fact extraction, and next question generation."""
    mock_llm_fixture.set_structured_response(
        make_ai_question_response(
            next_question="Which programming languages do you use most frequently?",
            category="skills",
            ready=False,
            extracted_field="target_role",
            extracted_val="Backend Developer",
        )
    )

    token = await register_and_login(client, "submit.turn@test.com", "Devendra Joshi")
    start_res = await client.post(
        "/api/v1/onboarding/start",
        headers={"Authorization": f"Bearer {token}"},
    )
    session_id = uuid.UUID(start_res.json()["session_id"])

    # Submit response to turn 1
    submit_res = await client.post(
        "/api/v1/onboarding/respond",
        headers={"Authorization": f"Bearer {token}"},
        json={"response_text": "I am aiming for a Backend Developer position."},
    )
    assert submit_res.status_code == 200
    data = submit_res.json()

    assert data["session_status"] == OnboardingStatus.IN_PROGRESS
    assert data["ready_to_summarize"] is False
    assert data["next_question"] == "Which programming languages do you use most frequently?"
    assert data["next_question_category"] == "skills"
    assert data["turn_completed"]["user_response"] == "I am aiming for a Backend Developer position."

    # Verify database persistence of turn 1 and turn 2
    session_db = await test_session.scalar(
        select(OnboardingSession).where(OnboardingSession.id == session_id)
    )
    assert session_db is not None
    assert session_db.turn_count == 1
    assert session_db.collected_facts.get("target_role") == "Backend Developer"
    assert "target_role" in session_db.areas_covered


@pytest.mark.asyncio
async def test_submit_response_skip_or_unknown_accepted(
    client: AsyncClient,
    mock_llm_fixture: MockLLMProvider,
):
    """Verifies that saying 'skip' or 'not sure' is accepted gracefully without errors."""
    mock_llm_fixture.set_structured_response(
        make_ai_question_response(
            next_question="No problem! What technologies have you built projects with?",
            category="technologies",
            ready=False,
        )
    )

    token = await register_and_login(client, "submit.skip@test.com", "Meera Nair")
    await client.post(
        "/api/v1/onboarding/start",
        headers={"Authorization": f"Bearer {token}"},
    )

    res = await client.post(
        "/api/v1/onboarding/respond",
        headers={"Authorization": f"Bearer {token}"},
        json={"response_text": "I don't know my exact timeline yet, please skip."},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["session_status"] == OnboardingStatus.IN_PROGRESS
    assert "technologies" in data["next_question_category"]


@pytest.mark.asyncio
async def test_submit_response_validation_rules(client: AsyncClient):
    """Verifies input length limits and empty response rejections."""
    token = await register_and_login(client, "submit.val@test.com", "Sunil Sethi")
    await client.post(
        "/api/v1/onboarding/start",
        headers={"Authorization": f"Bearer {token}"},
    )

    # Empty text: 422
    empty_res = await client.post(
        "/api/v1/onboarding/respond",
        headers={"Authorization": f"Bearer {token}"},
        json={"response_text": "   "},
    )
    assert empty_res.status_code == 422

    # Extra forbidden field: 422
    extra_field_res = await client.post(
        "/api/v1/onboarding/respond",
        headers={"Authorization": f"Bearer {token}"},
        json={"response_text": "Backend Dev", "injected_role": "admin"},
    )
    assert extra_field_res.status_code == 422


@pytest.mark.asyncio
async def test_conversation_history_chronological(client: AsyncClient):
    """Verifies full conversation turn history retrieval."""
    token = await register_and_login(client, "history.test@test.com", "Pooja Hegde")
    await client.post(
        "/api/v1/onboarding/start",
        headers={"Authorization": f"Bearer {token}"},
    )
    await client.post(
        "/api/v1/onboarding/respond",
        headers={"Authorization": f"Bearer {token}"},
        json={"response_text": "Backend Developer"},
    )

    res = await client.get(
        "/api/v1/onboarding/history",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    history = res.json()
    assert len(history) == 2  # turn 1 (answered) + turn 2 (pending)
    assert history[0]["turn_number"] == 1
    assert history[0]["user_response"] == "Backend Developer"
    assert history[1]["turn_number"] == 2
    assert history[1]["user_response"] is None


# ─── 3. AI Summary Generation & Confirmation Tests ──────────────────


@pytest.mark.asyncio
async def test_summary_unavailable_during_in_progress(client: AsyncClient):
    """Verifies that summary cannot be retrieved while the session is still in progress."""
    token = await register_and_login(client, "summary.early@test.com", "Varun Dhawan")
    await client.post(
        "/api/v1/onboarding/start",
        headers={"Authorization": f"Bearer {token}"},
    )

    res = await client.get(
        "/api/v1/onboarding/summary",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 409
    assert res.json()["error"]["code"] == "STATE_CONFLICT"


@pytest.mark.asyncio
async def test_ai_triggers_summary_readiness_and_confirmation(
    client: AsyncClient,
    mock_llm_fixture: MockLLMProvider,
    test_session: AsyncSession,
):
    """
    Verifies the end-to-end transition:
    AI indicates ready_to_summarize -> summary generated -> candidate confirms ->
    CareerProfile is updated -> session marked completed.
    """
    # Configure mock to transition to summary on the next turn
    mock_llm_fixture.set_structured_factory(
        lambda prompt, schema: (
            make_ai_summary_response(
                target_role="Backend Developer",
                career_stage="early_career",
                work_preference="remote",
            )
            if schema.__name__ == "OnboardingSummarySchema"
            else make_ai_question_response(ready=True)
        )
    )

    token = await register_and_login(client, "summary.complete@test.com", "Zara Khan")
    me = (await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})).json()
    user_id = uuid.UUID(me["id"])

    # 1. Start onboarding
    await client.post(
        "/api/v1/onboarding/start",
        headers={"Authorization": f"Bearer {token}"},
    )

    # 2. Submit response that triggers summary readiness
    submit_res = await client.post(
        "/api/v1/onboarding/respond",
        headers={"Authorization": f"Bearer {token}"},
        json={"response_text": "I have 1.5 years experience in Python and PostgreSQL."},
    )
    assert submit_res.status_code == 200
    assert submit_res.json()["session_status"] == OnboardingStatus.AWAITING_CONFIRMATION
    assert submit_res.json()["ready_to_summarize"] is True

    # 3. Retrieve summary
    summary_res = await client.get(
        "/api/v1/onboarding/summary",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert summary_res.status_code == 200
    summary_data = summary_res.json()
    assert summary_data["is_confirmed"] is False
    assert summary_data["summary"]["target_role"] == "Backend Developer"
    assert summary_data["summary"]["work_preference"] == "remote"

    # 4. Confirm summary
    confirm_res = await client.post(
        "/api/v1/onboarding/confirm",
        headers={"Authorization": f"Bearer {token}"},
        json={"confirmed": True},
    )
    assert confirm_res.status_code == 200
    assert confirm_res.json()["status"] == OnboardingStatus.COMPLETED

    # 5. Verify CareerProfile in database was updated
    career_profile = await test_session.scalar(
        select(CareerProfile).where(CareerProfile.user_id == user_id)
    )
    assert career_profile is not None
    assert career_profile.work_preference == "remote"
    assert career_profile.career_stage == "early_career"
    assert "Bengaluru" in career_profile.target_locations

    # 6. Verify starting again after completion is rejected with 409
    restart_res = await client.post(
        "/api/v1/onboarding/start",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert restart_res.status_code == 409
    assert restart_res.json()["error"]["code"] == "STATE_CONFLICT"


@pytest.mark.asyncio
async def test_confirm_summary_with_candidate_edits(
    client: AsyncClient,
    mock_llm_fixture: MockLLMProvider,
    test_session: AsyncSession,
):
    """Verifies that candidate overrides/edits supersede AI-generated summary."""
    mock_llm_fixture.set_structured_factory(
        lambda prompt, schema: (
            make_ai_summary_response(work_preference="remote")
            if schema.__name__ == "OnboardingSummarySchema"
            else make_ai_question_response(ready=True)
        )
    )

    token = await register_and_login(client, "summary.edits@test.com", "Kiran Desai")
    me = (await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})).json()
    user_id = uuid.UUID(me["id"])

    await client.post("/api/v1/onboarding/start", headers={"Authorization": f"Bearer {token}"})
    await client.post(
        "/api/v1/onboarding/respond",
        headers={"Authorization": f"Bearer {token}"},
        json={"response_text": "Ready to summarize"},
    )

    # Candidate overrides work_preference to "hybrid" and career_stage to "student"
    edited_summary = make_ai_summary_response(
        target_role="Backend Developer",
        career_stage="student",
        work_preference="hybrid",
    )
    confirm_res = await client.post(
        "/api/v1/onboarding/confirm",
        headers={"Authorization": f"Bearer {token}"},
        json={"confirmed": True, "edits": edited_summary},
    )
    assert confirm_res.status_code == 200

    # Verify CareerProfile received the candidate's corrected preferences
    profile = await test_session.scalar(
        select(CareerProfile).where(CareerProfile.user_id == user_id)
    )
    assert profile is not None
    assert profile.work_preference == "hybrid"
    assert profile.career_stage == "student"


@pytest.mark.asyncio
async def test_confirm_summary_with_false_rejected(
    client: AsyncClient,
    mock_llm_fixture: MockLLMProvider,
):
    """Verifies that calling /confirm with confirmed=False is rejected with 422."""
    mock_llm_fixture.set_structured_factory(
        lambda prompt, schema: (
            make_ai_summary_response()
            if schema.__name__ == "OnboardingSummarySchema"
            else make_ai_question_response(ready=True)
        )
    )

    token = await register_and_login(client, "summary.unconfirmed@test.com", "Ritu Phogat")
    await client.post("/api/v1/onboarding/start", headers={"Authorization": f"Bearer {token}"})
    await client.post(
        "/api/v1/onboarding/respond",
        headers={"Authorization": f"Bearer {token}"},
        json={"response_text": "Ready to summarize"},
    )

    res = await client.post(
        "/api/v1/onboarding/confirm",
        headers={"Authorization": f"Bearer {token}"},
        json={"confirmed": False},
    )
    assert res.status_code == 422


# ─── 4. Security & Multi-Tenant Isolation Tests ─────────────────────


@pytest.mark.asyncio
async def test_cross_user_isolation_prevented(client: AsyncClient):
    """Verifies Candidate B cannot access Candidate A's session or history."""
    token_a = await register_and_login(client, "user.alpha@test.com", "Alpha Candidate")
    token_b = await register_and_login(client, "user.beta@test.com", "Beta Candidate")

    # Alpha starts onboarding
    await client.post(
        "/api/v1/onboarding/start",
        headers={"Authorization": f"Bearer {token_a}"},
    )

    # Beta attempts to read session without starting one -> 404
    res_b = await client.get(
        "/api/v1/onboarding/session",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert res_b.status_code == 404

    # Beta attempts to submit response -> 404 (no active session for Beta)
    submit_b = await client.post(
        "/api/v1/onboarding/respond",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"response_text": "Malicious payload to hijack Alpha's session"},
    )
    assert submit_b.status_code == 404


# ─── 5. Provider Availability & Failure Handling Tests ──────────────


@pytest.mark.asyncio
async def test_unconfigured_ai_provider_returns_503(client: AsyncClient):
    """
    Verifies that when the live LLM provider is unconfigured,
    submitting a response cleanly returns 503 Service Unavailable,
    fulfilling the requirement: 'Do not pretend live AI functionality works'.
    """
    unconfigured_provider = OpenAIProviderAdapter(api_key="", model="gpt-4o-mini")
    assert unconfigured_provider.is_available is False
    override_llm_provider(unconfigured_provider)

    try:
        token = await register_and_login(client, "no.ai.key@test.com", "Offline User")
        await client.post(
            "/api/v1/onboarding/start",
            headers={"Authorization": f"Bearer {token}"},
        )

        res = await client.post(
            "/api/v1/onboarding/respond",
            headers={"Authorization": f"Bearer {token}"},
            json={"response_text": "Backend Developer"},
        )
        assert res.status_code == 503
        data = res.json()
        assert data["error"]["code"] == "SERVICE_UNAVAILABLE"
        assert "OpenAI" in data["error"]["message"]
    finally:
        reset_llm_provider()


# ─── 6. Maximum Turns Cap & Conversation Control ────────────────────


@pytest.mark.asyncio
async def test_max_turns_enforcement_forces_summary(
    client: AsyncClient,
    mock_llm_fixture: MockLLMProvider,
    test_session: AsyncSession,
):
    """
    Verifies that the conversation cannot loop infinitely.
    Reaching max turns automatically transitions to awaiting_confirmation.
    """
    mock_llm_fixture.set_structured_factory(
        lambda prompt, schema: (
            make_ai_summary_response()
            if schema.__name__ == "OnboardingSummarySchema"
            else make_ai_question_response(ready=False)
        )
    )

    token = await register_and_login(client, "max.turns@test.com", "Loop Tester")
    start_res = await client.post(
        "/api/v1/onboarding/start",
        headers={"Authorization": f"Bearer {token}"},
    )
    session_id = uuid.UUID(start_res.json()["session_id"])

    # Simulate fast-forwarding to turn 19 (one before cap of 20)
    session = await test_session.scalar(
        select(OnboardingSession).where(OnboardingSession.id == session_id)
    )
    assert session is not None
    session.turn_count = 19
    await test_session.commit()

    # Submit response on turn 20
    res = await client.post(
        "/api/v1/onboarding/respond",
        headers={"Authorization": f"Bearer {token}"},
        json={"response_text": "Final answer at max turn cap"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["session_status"] == OnboardingStatus.AWAITING_CONFIRMATION
    assert data["ready_to_summarize"] is True
    assert data["next_question"] is None


# ─── 7. AI Provider Adapter Unit Tests ──────────────────────────────


@pytest.mark.asyncio
async def test_mock_provider_unit_generate_structured():
    """Unit test for MockLLMProvider structured and text generation."""
    mock = MockLLMProvider()
    mock.set_structured_response({"field": "skills", "value": ["Python"], "confidence": "user_stated"})
    mock.set_text_response("Hello from mock")

    from app.schemas.onboarding import ExtractedCareerFact
    res = await mock.generate_structured("prompt", ExtractedCareerFact)
    assert res.field == "skills"
    assert res.value == ["Python"]

    text = await mock.generate_text("prompt")
    assert text == "Hello from mock"
    assert mock.call_count == 2
    assert mock.provider_name == "mock"
    assert mock.is_available is True


@pytest.mark.asyncio
async def test_openai_adapter_availability_and_missing_key():
    """Verifies that OpenAI adapter reports availability correctly and raises 503 if unconfigured."""
    from app.core.exceptions import ServiceUnavailableException
    from app.schemas.onboarding import ExtractedCareerFact

    adapter_no_key = OpenAIProviderAdapter(api_key="")
    assert adapter_no_key.is_available is False
    assert adapter_no_key.provider_name == "openai"

    with pytest.raises(ServiceUnavailableException, match="not configured"):
        await adapter_no_key.generate_structured("prompt", ExtractedCareerFact)

    with pytest.raises(ServiceUnavailableException, match="not configured"):
        await adapter_no_key.generate_text("prompt")


@pytest.mark.asyncio
async def test_anthropic_adapter_availability_and_missing_key():
    """Verifies that Anthropic adapter reports availability correctly and raises 503 if unconfigured."""
    from app.ai.anthropic_adapter import AnthropicProviderAdapter
    from app.core.exceptions import ServiceUnavailableException
    from app.schemas.onboarding import ExtractedCareerFact

    adapter_no_key = AnthropicProviderAdapter(api_key="")
    assert adapter_no_key.is_available is False
    assert adapter_no_key.provider_name == "anthropic"

    with pytest.raises(ServiceUnavailableException, match="not configured"):
        await adapter_no_key.generate_structured("prompt", ExtractedCareerFact)

    with pytest.raises(ServiceUnavailableException, match="not configured"):
        await adapter_no_key.generate_text("prompt")


@pytest.mark.asyncio
async def test_ai_factory_provider_creation():
    """Verifies create_llm_provider handles different provider configurations."""
    from app.ai.factory import create_llm_provider

    p_openai = create_llm_provider("openai")
    assert p_openai.provider_name == "openai"

    p_anthropic = create_llm_provider("anthropic")
    assert p_anthropic.provider_name == "anthropic"

    p_disabled = create_llm_provider("disabled")
    assert p_disabled.is_available is False

