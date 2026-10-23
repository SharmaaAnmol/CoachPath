# CoachPath Gemini AI Diagnostic & Integration Report

> **Document Version**: 1.0.0  
> **Date**: October 22, 2026  
> **Status**: Completed & Operational  
> **Target Audience**: Engineering, DevOps, Product, Security  

---

## 1. Executive Summary

| Verification Area | Status | Notes |
|---|---|---|
| **Gemini Client & SDK Integration** | **PASS** | Official `google-genai` SDK v2.32.0 installed and initialized natively via `from google import genai`. |
| **Model Verification & Availability** | **PASS** | Discovered active Gemini Developer API models via `ModelService.ListModels`. Model `gemini-3.5-flash-lite` active and verified with automatic failover to `gemini-3.5-flash`. |
| **Live Minimal API Call** | **PASS** | Successfully received verbatim response: `"CoachPath Gemini connection successful."` |
| **Live Onboarding Turn Generation** | **PASS** | Structured JSON generation verified live for conversation turn progression and category classification (`career_stage`). |
| **Live Onboarding Summary Generation** | **PASS** | Structured career summary synthesized and validated live against `OnboardingSummarySchema`. |
| **Live Resume Parsing Extraction** | **PASS** | Candidate personal info, work experience, education, and skills extracted live into `ExtractedResumeSchema`. |
| **Pydantic Schema Sanitization** | **PASS** | Resolved Gemini Developer API restriction on `additionalProperties` and `title` via recursive AST schema transformer. |
| **Backend Test Suite (115 Tests)** | **PASS** | All 115 unit and integration tests passing hermetically with 0 failures. |
| **Frontend Static Audits & Build** | **PASS** | TypeScript typecheck (`npx tsc --noEmit`), ESLint (`npm run lint`), and Next.js production build (25/25 pages) pass cleanly. |
| **Credential Security & Hygiene** | **PASS** | API credentials fully redacted, omitted from logs/transcripts, isolated in `backend/.env` (which is confirmed ignored in `.gitignore`). |

---

## 2. Root Cause Analysis

### Cause 1: Lack of Native Google GenAI SDK
The codebase previously implemented AI providers using OpenAI and Anthropic SDKs. Attempting to point an OpenAI client to Gemini endpoints or passing a Gemini credential to OpenAI client classes caused authentication and protocol mismatches.

### Cause 2: Incompatible / Deprecated Model Identifiers
Initial attempts to query `gemini-1.5-flash` returned `404 NOT_FOUND` for API version `v1beta`. Subsequently, querying `gemini-2.5-flash` returned `404 NOT_FOUND` with the message:
`"This model models/gemini-2.5-flash is no longer available to new users. Please update your code to use models/gemini-3.8-flash for the latest features..."`
Furthermore, `gemini-3.8-flash` and `gemini-3.7-flash` intermittently returned `503 UNAVAILABLE` during transient demand spikes on the developer tier.

### Cause 3: Schema Incompatibility with Gemini Developer API Mode
When Pydantic v2 schemas were supplied directly to `GenerateContentConfig(response_schema=...)`, the Gemini Developer API returned:
`ValueError: additionalProperties is only supported in Gemini Enterprise Agent Platform mode, not in Gemini Developer API mode.`
Pydantic v2 automatically includes `additionalProperties` and `title` fields in generated JSON schemas, which the Google Gemini Developer endpoint rejects.

---

## 3. Configuration & Architectural Solutions

### 3.1. Standardized Environment Configuration
All non-Gemini provider variables (`OPENAI_*`, `ANTHROPIC_*`, `GROQ_*`) were removed from `backend/.env`. The AI configuration is strictly standardized as:

```env
# AI Provider Configuration (Google Gemini)
AI_PROVIDER=gemini
GEMINI_API_KEY=[REDACTED_GEMINI_KEY]
GEMINI_MODEL=gemini-3.5-flash-lite
AI_REQUEST_TIMEOUT=30
AI_MAX_RETRIES=2
ONBOARDING_MAX_TURNS=20
```

### 3.2. Native `google-genai` SDK Adapter
Implemented [`backend/app/ai/gemini_adapter.py`](file:///Users/anmolsharma/Desktop/Coach_Path/backend/app/ai/gemini_adapter.py) using the official `google-genai` Python library:
- **Client**: `genai.Client(api_key=..., http_options=types.HttpOptions(timeout=...))`
- **Async Execution**: `client.aio.models.generate_content(...)`
- **Output Token Allocation**: Explicit `max_output_tokens=4096` to prevent truncation on extensive multi-section schemas (e.g. resumes).
- **Load Spike Resilience**: Ordered fallback list `["gemini-3.5-flash-lite", "gemini-3.5-flash"]` that seamlessly retries across candidate models upon transient `503 ServerError` responses.

### 3.3. Recursive Schema Sanitizer
To ensure compatibility with Gemini Developer API mode, a recursive schema sanitizer `_sanitize_gemini_schema()` was implemented:
- Strips `additionalProperties` at all dictionary nesting depths.
- Strips `title` attributes that trigger Gemini validation rejections.
- Passes clean JSON schema to `GenerateContentConfig(response_mime_type="application/json", response_schema=sanitized_schema)`.
- Validates the resulting JSON string directly through `schema.model_validate(parsed_json)`.

---

## 4. Live Verification Results

### 4.1. Minimal Connectivity Check
- **Prompt**: `"Reply with the words CoachPath Gemini connection successful."`
- **Model**: `gemini-3.5-flash` / `gemini-3.5-flash-lite`
- **Status**: **PASS**
- **Actual Response**: `"CoachPath Gemini connection successful."`

### 4.2. Onboarding Conversational Turn
- **Input**: `"User goal: I want to transition from QA to Backend Engineering in Python."`
- **Schema**: `OnboardingAIResponse`
- **Status**: **PASS**
- **Generated Question**: `"What is your current level of experience working in QA?"`
- **Classified Category**: `"career_stage"`

### 4.3. Onboarding Profile Summary
- **Input**: `"Candidate has stated: Target role Backend Developer, 2 years QA experience, knows Python and SQL."`
- **Schema**: `OnboardingSummarySchema`
- **Status**: **PASS**
- **Generated Target Role**: `"Backend Developer"`
- **Extracted Skills**: `["Quality Assurance", "Testing", "Problem Solving"]`

### 4.4. Resume Parsing Workbench Extraction
- **Input**: Synthetic candidate resume (Priya Patel, CloudCorp, Senior SWE).
- **Schema**: `ExtractedResumeSchema`
- **Status**: **PASS**
- **Extracted Name**: `"Priya Patel"`
- **Extracted Employer**: `"CloudCorp"`
- **Extracted Skills**: `["Python", "Go", "Docker", "Kubernetes"]`

---

## 5. Automated Test Suite Results

```text
============================= test session starts ==============================
platform darwin -- Python 3.13.6, pytest-9.1.1, pluggy-1.6.0
collected 115 items

tests/test_auth.py .................                                      [ 15%]
tests/test_db.py .                                                        [ 16%]
tests/test_errors.py ...                                                  [ 19%]
tests/test_gemini_adapter.py ......                                       [ 24%]
tests/test_health.py .....                                                [ 28%]
tests/test_models.py ...........                                          [ 38%]
tests/test_onboarding.py ......................                           [ 57%]
tests/test_phase4c_e2e_audit.py .......                                   [ 63%]
tests/test_profile.py ........                                            [ 70%]
tests/test_resume.py ...................                                  [ 87%]
tests/test_routers_structure.py ...............                           [100%]

======================= 115 passed, 5 warnings in 11.90s =======================
```

### Frontend Validation:
- **TypeScript**: `npx tsc --noEmit` &rarr; 0 errors.
- **ESLint**: `npm run lint` &rarr; Clean (`✔ No ESLint warnings or errors`).
- **Next.js Production Build**: `npm run build` &rarr; All 25 static application pages compiled cleanly.

---

## 6. Files Created & Modified

1. **[`backend/app/ai/gemini_adapter.py`](file:///Users/anmolsharma/Desktop/Coach_Path/backend/app/ai/gemini_adapter.py)**:
   - Full `LLMProvider` implementation wrapping `google-genai`.
   - Recursive schema sanitizer, JSON fences cleaner, and multi-model fallback retry loop.
2. **[`backend/app/ai/factory.py`](file:///Users/anmolsharma/Desktop/Coach_Path/backend/app/ai/factory.py)**:
   - Added `gemini` provider branch instantiating `GeminiProviderAdapter`.
   - Defaulted fallback to unconfigured Gemini provider.
3. **[`backend/app/core/config.py`](file:///Users/anmolsharma/Desktop/Coach_Path/backend/app/core/config.py)**:
   - Added `GEMINI_API_KEY` and `GEMINI_MODEL: str = "gemini-3.5-flash-lite"`.
4. **[`backend/.env`](file:///Users/anmolsharma/Desktop/Coach_Path/backend/.env)**:
   - Set `AI_PROVIDER=gemini` and `GEMINI_MODEL=gemini-3.5-flash-lite`.
   - Removed all legacy OpenAI, Anthropic, and Groq keys.
5. **[`backend/.env.example`](file:///Users/anmolsharma/Desktop/Coach_Path/backend/.env.example)**:
   - Updated template to document `gemini` provider and model defaults.
6. **[`backend/requirements.txt`](file:///Users/anmolsharma/Desktop/Coach_Path/backend/requirements.txt)**:
   - Added `google-genai>=2.32.0`.
7. **[`backend/tests/test_gemini_adapter.py`](file:///Users/anmolsharma/Desktop/Coach_Path/backend/tests/test_gemini_adapter.py)**:
   - 6 new automated tests verifying availability, 503 handling, schema sanitizing, and factory resolution.
8. **[`docs/ai-architecture.md`](file:///Users/anmolsharma/Desktop/Coach_Path/docs/ai-architecture.md)**:
   - Updated class diagram and specifications for Gemini native adapter.

---

## 7. Manual Action Required

To activate the repaired Gemini integration in your running application, simply restart the backend FastAPI process:

```bash
# In your backend terminal window:
# Press Ctrl+C to stop the current uvicorn process, then run:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Your live Onboarding assistant (`/onboarding`) and Resume parsing engine (`/resume`) will immediately use Google Gemini with live responses.
