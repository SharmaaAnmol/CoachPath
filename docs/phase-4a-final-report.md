# Phase 4A Final Engineering Report: AI-Powered Career Onboarding Backend

**Phase**: Phase 4A — AI-Powered Personalized Onboarding (Backend Implementation)  
**Date**: October 21, 2026  
**Status**: **PHASE 4A COMPLETE**  
**Author**: Lead Software Architect & AI Engineering Lead  

---

## 1. Implementation Summary

Phase 4A delivers the backend and AI intelligence layer for CoachPath's conversational career discovery and onboarding system. Rather than using hardcoded chatbot responses or rigid static wizards, the system orchestrates a dynamic, adaptive discovery interview powered by foundation models, constrained by deterministic business rules and Pydantic v2 schemas.

Key achievements:
- **Resumable State Machine**: Manages candidate onboarding through strictly validated states: `not_started` $\to$ `in_progress` $\to$ `awaiting_confirmation` $\to$ `completed`.
- **Truthfulness & Data Provenance**: Only user-stated facts are extracted and persisted; the system prohibits LLM fabrication of degrees, employers, or skills.
- **Human Approval Gate**: An AI-synthesized career summary must be reviewed and explicitly confirmed (with optional user edits) before merging into the central `CareerProfile`.
- **Decoupled AI Architecture**: Complete provider abstraction (`LLMProvider`) supporting OpenAI (`gpt-4o-mini`, `gpt-4o`), Anthropic Claude (`claude-3-haiku`), and test mocks (`MockLLMProvider`).
- **Prompt Injection Defense**: Untrusted candidate input is strictly quarantined within `<<<USER_INPUT>>>` delimiters and treated as passive extraction target data.
- **Production Truth in Configuration**: If no live AI provider API key is configured, endpoints report `HTTP 503 Service Unavailable` rather than faking AI responses.

---

## 2. Files Created and Modified

### Created Files
| File Path | Description |
|---|---|
| `backend/app/ai/__init__.py` | Package initializer for AI intelligence module. |
| `backend/app/ai/base.py` | Abstract `LLMProvider` protocol interface. |
| `backend/app/ai/openai_adapter.py` | OpenAI provider adapter supporting structured outputs. |
| `backend/app/ai/anthropic_adapter.py` | Anthropic Claude provider adapter. |
| `backend/app/ai/mock_adapter.py` | Deterministic `MockLLMProvider` for test isolation. |
| `backend/app/ai/factory.py` | Provider instantiation factory and test overrides. |
| `backend/app/ai/prompts/__init__.py` | Package initializer for versioned prompt registry. |
| `backend/app/ai/prompts/onboarding_v1.py` | Version-controlled prompt templates with delimiter quarantine. |
| `backend/app/schemas/onboarding.py` | Pydantic v2 schemas for all requests, responses, and AI outputs. |
| `backend/app/models/onboarding.py` | SQLAlchemy domain models: `OnboardingSession` and `OnboardingTurn`. |
| `backend/app/services/onboarding.py` | Core business logic orchestrating turns, AI, constraints, and profile updates. |
| `backend/alembic/versions/a1b2c3d4e5f6_phase_4a_onboarding_tables.py` | Alembic migration for `onboarding_sessions` and `onboarding_turns`. |
| `backend/tests/test_onboarding.py` | Comprehensive integration and security test suite (20 test cases). |
| `backend/.env.example` | Template environment configuration documenting AI provider keys. |
| `docs/onboarding-architecture.md` | Formal architecture document for conversational onboarding. |
| `docs/phase-4a-final-report.md` | This completion report. |

### Modified Files
| File Path | Changes Applied |
|---|---|
| `backend/app/core/config.py` | Added AI provider settings (`AI_PROVIDER`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.) and tightened production key validator. |
| `backend/app/models/auth.py` | Added `onboarding_session` 1:1 relationship to `User` model. |
| `backend/app/models/__init__.py` | Exported `OnboardingSession` and `OnboardingTurn` for discovery. |
| `backend/app/api/routes/onboarding.py` | Replaced placeholder with 7 production endpoints. |
| `backend/requirements.txt` | Added `openai>=1.50.0` and `anthropic>=0.36.0`. |
| `backend/.env` | Added development AI provider configuration placeholders. |
| `docs/api-specification.md` | Updated Group 2 endpoints to reflect conversational discovery contract. |
| `docs/development-roadmap.md` | Updated Phase 4 to document Phase 4A completion and Phase 4B frontend scope. |

---

## 3. Database Changes and Migrations

Alembic migration `a1b2c3d4e5f6_phase_4a_onboarding_tables` was authored and executed successfully against PostgreSQL 15:

1. **`onboarding_sessions` Table**:
   - `id`: UUID (Primary Key)
   - `user_id`: UUID (Foreign Key $\to$ `users.id`, `ON DELETE CASCADE`, `UNIQUE`)
   - `status`: `VARCHAR(32)` (`'not_started'`, `'in_progress'`, `'awaiting_confirmation'`, `'completed'`)
   - `current_question`: `TEXT` (Nullable)
   - `current_question_category`: `VARCHAR(64)` (Nullable)
   - `turn_count`: `INTEGER` (Default `0`)
   - `collected_facts`: `JSONB` (Default `'{}'`)
   - `areas_covered`: `JSONB` (Default `'[]'`)
   - `ai_summary`: `JSONB` (Nullable)
   - `summary_generated_at`: `TIMESTAMPTZ` (Nullable)
   - `is_summary_confirmed`: `BOOLEAN` (Default `FALSE`)
   - `summary_confirmed_at`: `TIMESTAMPTZ` (Nullable)
   - `last_activity_at`: `TIMESTAMPTZ` (Default `CURRENT_TIMESTAMP`)
   - `completed_at`: `TIMESTAMPTZ` (Nullable)
   - `created_at`, `updated_at`: `TIMESTAMPTZ`

2. **`onboarding_turns` Table**:
   - `id`: UUID (Primary Key)
   - `session_id`: UUID (Foreign Key $\to$ `onboarding_sessions.id`, `ON DELETE CASCADE`)
   - `turn_number`: `INTEGER` (Monotonic turn index)
   - `question`: `TEXT`
   - `question_category`: `VARCHAR(64)`
   - `user_response`: `TEXT` (Nullable while question pending)
   - `extracted_facts`: `JSONB` (Nullable)
   - `responded_at`: `TIMESTAMPTZ` (Nullable)
   - `created_at`: `TIMESTAMPTZ`
   - Unique Index: `(session_id, turn_number)`

---

## 4. APIs Implemented

All endpoints require JWT Bearer or HttpOnly cookie authentication and enforce candidate ownership:

| HTTP Method | Route URL | Purpose |
|---|---|---|
| `GET` | `/api/v1/onboarding` | Structural module status check (`operational`). |
| `POST` | `/api/v1/onboarding/start` | Creates new session or resumes existing active session. |
| `GET` | `/api/v1/onboarding/session` | Returns active session state and pending question. |
| `GET` | `/api/v1/onboarding/progress` | Returns covered vs. remaining discovery categories. |
| `POST` | `/api/v1/onboarding/respond` | Submits candidate answer; AI extracts facts & returns next question. |
| `GET` | `/api/v1/onboarding/history` | Chronological log of all conversation turns. |
| `GET` | `/api/v1/onboarding/summary` | Returns AI-generated summary (in `awaiting_confirmation`). |
| `POST` | `/api/v1/onboarding/confirm` | Confirms summary (with optional edits), merges into `CareerProfile`. |

---

## 5. AI Provider and Configuration Status

- **Configured Providers**: OpenAI and Anthropic Claude adapters implemented and tested.
- **Production Transparency**: `settings.AI_PROVIDER = "openai"`. If `OPENAI_API_KEY` is not populated in `.env`, the system reports `HTTP 503 Service Unavailable` with a clear explanation: `"OpenAI provider is not configured. Set OPENAI_API_KEY in your .env file."`
- **Zero Hallucination Testing**: The automated test suite utilizes `MockLLMProvider`, completely decoupled from third-party networks or API keys.

---

## 6. Tests Executed and Results

The full backend test suite was executed:
```bash
backend/.venv/bin/pytest tests/ -v
======================== 83 passed, 4 warnings in 8.01s ========================
```

### Breakdown of Passing Tests
- **Onboarding Integration & Security Tests**: 20 passing (`tests/test_onboarding.py`)
  - Fresh session start & turn 1 generation
  - Browser refresh session resumption
  - Unauthenticated access rejection (401)
  - Lifecycle status retrieval & 404 handling
  - Discovery category progress tracking
  - AI fact extraction and turn advancement
  - Graceful skipping / "I don't know" handling
  - Input validation (empty text rejection, length capping)
  - Chronological conversation history
  - Early summary request conflict (409)
  - End-to-end readiness trigger $\to$ summary $\to$ confirmation $\to$ profile merge
  - Candidate summary edits override
  - `confirmed=False` rejection (422)
  - Cross-user multi-tenant isolation (User B cannot read/write User A's session)
  - Unconfigured AI provider transparency (503)
  - Maximum conversation turns cap enforcement (20 turns)
  - Mock provider unit tests (structured + text generation)
  - OpenAI adapter unconfigured key handling
  - Anthropic adapter unconfigured key handling
  - AI Factory provider creation logic
- **Authentication & Security Tests**: 18 passing (`tests/test_auth.py`)
- **Career Profile & Evidence Tests**: 11 passing (`tests/test_profile.py`)
- **Model Integrity & Constraints**: 18 passing (`tests/test_models.py`, `tests/test_db.py`)
- **Health & Structural Routers**: 16 passing (`tests/test_health.py`, `tests/test_errors.py`, `tests/test_routers_structure.py`)

---

## 7. Errors Discovered and Fixed During Implementation

1. **Missing `CareerProfile` for Fresh Signups**:
   - *Problem*: In `test_ai_triggers_summary_readiness_and_confirmation`, newly registered users who went directly to onboarding did not yet have a `CareerProfile` record in the database.
   - *Fix*: Enhanced `_apply_summary_to_career_profile` to auto-initialize the candidate's `CareerProfile` if not yet seeded, using fallback default roles, before applying the confirmed preferences.
2. **Production `SECRET_KEY` Validator Conflict in Tests**:
   - *Problem*: `test_production_environment_security` checked that default keys are rejected in production. When `.env` was introduced with a `dev-secret-key...` prefix, Pydantic settings read `.env` instead of the default string.
   - *Fix*: Updated `Settings.validate_production_environment` to check `self.SECRET_KEY.startswith(("insecure-default", "dev-secret-key"))`.
3. **Router Mounting Compatibility**:
   - *Problem*: `tests/test_routers_structure.py` expected `GET /api/v1/onboarding` to return a 200 operational status.
   - *Fix*: Retained the root `GET ""` endpoint returning `{"module": "onboarding", "status": "operational", "phase": "Phase 4A"}`.

---

## 8. Security Checks

1. **Authentication Enforcement**: Every functional onboarding endpoint is guarded by `Depends(require_active_user)`.
2. **Multi-Tenant Ownership Scoping**: `_enforce_ownership` verifies that `session.user_id == current_user.id`. Cross-user access is impossible and returns 404 (if not found for user) or 403 (if attempting unauthorized modifications).
3. **Prompt Injection Quarantine**: Candidate answers are placed strictly within `<<<USER_INPUT>>>...<<<END_USER_INPUT>>>` tags with explicit system instructions to ignore embedded commands.
4. **Input Constraints**: Answers are constrained to 2,000 characters and stripped of whitespace before passing to LLM or DB.
5. **No Direct Database Writes by LLM**: The LLM outputs pure Pydantic models; all database queries and updates are performed through explicit SQLAlchemy ORM transactions.

---

## 9. Outstanding Issues

- **Live OpenAI/Anthropic API Key**: To experience live generative onboarding in a local browser session, add an active `OPENAI_API_KEY=sk-...` to `backend/.env`. In the absence of a key, the backend cleanly surfaces HTTP 503.

---

## 10. Exact Prerequisites for Phase 4B (Frontend Onboarding UI)

Phase 4A backend provides all contracts needed for Phase 4B:
1. **Frontend Client Hook / SDK**: Create `onboardingClient` in `frontend/src/lib/onboarding-client.ts` consuming the 7 backend endpoints.
2. **Conversational Chat UI**: Create `/onboarding` page in Next.js displaying AI message bubbles, typing indicators, quick-reply suggestion chips, and an answer input bar.
3. **Progress Meter**: Display progress across the 15 discovery categories utilizing `GET /api/v1/onboarding/progress`.
4. **Summary Review & Confirmation Modal**: When `ready_to_summarize=true`, fetch `GET /api/v1/onboarding/summary`, render an editable review card, and submit `POST /api/v1/onboarding/confirm`.
5. **Post-Confirmation Redirect**: Redirect confirmed candidate to `/dashboard`.

---

## 11. Verdict

### **PHASE 4A COMPLETE**

The backend implementation for AI-powered personalized onboarding is complete, tested with 83 passing tests, migrated to PostgreSQL, and halted pending Phase 4B instructions.
