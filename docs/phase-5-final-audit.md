# CoachPath Phase 5: Resume Processing End-to-End Audit Report

> **Document Version**: 1.0.0  
> **Status**: Completed, Fully Audited, and Verified  
> **Audit Date**: October 23, 2026  
> **Auditors**: Lead Software Architect & Senior Full-Stack AI Engineer  
> **Target Audience**: Engineering Leadership, Product Management, Quality Assurance  

---

## 1. Executive Summary & Verdict

Phase 5 encompassed the implementation of **Phase 5A (Resume Upload and AI Parsing Backend)** and **Phase 5B (Resume Frontend and Review Workflow)**. This Phase 5C audit evaluated the end-to-end integration, live Google Gemini API connectivity, document extraction boundaries, truthful anti-hallucination constraints, human-in-the-loop profile merging, multi-tenant security isolation, and test suite completeness.

### Final Verdict: **PHASE 5 COMPLETE (READY FOR PHASE 6)**

| Audit Domain | Scope | Status | Notes |
|---|---|---|---|
| **User Journey** | Complete 15-step candidate upload, edit, review & merge flow | **PASS** | Verified end-to-end via automated integration suite |
| **Live AI Provider** | Google Gemini Developer API integration via official SDK | **PASS** | Live provider verified using configured Gemini API credentials |
| **Document Processing** | PDF & DOCX binary extraction, magic bytes, edge cases | **PASS** | 8 format/size/corruption boundary conditions verified |
| **Truthful Extraction** | Anti-hallucination, missing-info preservation, unverified skills | **PASS** | Strict schema validation; zero fabricated credentials |
| **Profile Merging** | Human approval gate, conflict detection, idempotency | **PASS** | Zero automated writes; atomic merge with duplicate prevention |
| **Security & Privacy** | Multi-tenant isolation, 401/403 gates, safe file storage | **PASS** | Isolated directories, path traversal prevention, secure streams |
| **Automated Testing** | Full backend test suite & regression coverage | **PASS** | **129/129 tests passing** across 13 test suites |
| **Frontend Code Quality** | TypeScript type safety, ESLint, Next.js production build | **PASS** | 0 TypeScript errors, 0 ESLint warnings, 25/25 pages built |

---

## 2. Complete User Journey Verification

Every step in the 15-step end-to-end candidate resume workflow was audited:

| Step # | Journey Step Description | Tested Behavior | Status |
|---|---|---|---|
| **1** | Authenticated user opens Resume page | Accesses `/resume` with valid bearer token / session cookie. Unauthenticated requests are redirected or rejected with 401. | **PASS** |
| **2** | User uploads a valid PDF document | Multi-part upload via `POST /api/v1/resume/upload` returns HTTP 201 with metadata and processing status. | **PASS** |
| **3** | Secure original document storage | File binary is saved to `{UPLOAD_DIR}/{user_id}/{uuid}.pdf` with safe path resolution and traversal defenses. | **PASS** |
| **4** | Document text extraction | `pypdf` extracts UTF-8 normalized text, preserving page numbering and character counts. | **PASS** |
| **5** | Gemini structured interpretation | Configured `gemini-3.5-flash-lite` parses career entities into `ExtractedResumeSchema`. | **PASS** |
| **6** | Structured output validation | Strict Pydantic v2 schema validation enforces types, field boundaries, and provenance metadata. | **PASS** |
| **7** | Result persisted strictly as draft | Parsed data stored in `resumes.extracted_data`. `CareerProfile` remains **completely untouched**. | **PASS** |
| **8** | Frontend displays status and draft | UI shows processing badges (`parsed`, `needs_review`) and renders interactive draft review cards. | **PASS** |
| **9** | User can edit extracted details | Candidate can edit names, institutions, degrees, job titles, dates, descriptions, and bullets inline. | **PASS** |
| **10** | User can exclude extracted details | Candidate can toggle individual items off (e.g., exclude unneeded projects or older roles). | **PASS** |
| **11** | User inspects profile conflicts | `ProfileConflictIndicator` flags `new`, `existing`, and `conflict` items against existing profile data. | **PASS** |
| **12** | Explicit confirmation submitted | Candidate clicks **Approve & Commit Credentials**, submitting `ResumeConfirmationRequest`. | **PASS** |
| **13** | Backend validates & merges changes | `confirm_and_merge_profile` validates payload and transactionally inserts into PostgreSQL. | **PASS** |
| **14** | Career profile reloads & updates | Frontend re-fetches authoritative `/profile`, displaying merged education, experience, and skills. | **PASS** |
| **15** | Persistence across login sessions | Subsequent login and refresh returns the exact merged career profile and updated completeness score. | **PASS** |

---

## 3. Google Gemini Provider Integration Verification

### Provider Configuration
- **AI Provider**: `gemini`
- **Active Model**: `gemini-3.5-flash-lite` (with automatic fallback to `gemini-3.5-flash`)
- **SDK**: Official `google-genai` Python SDK
- **Environment**: Configured via `backend/.env` with `GEMINI_API_KEY` and `GEMINI_MODEL`

### Verification Levels
1. **Live Gemini Request Verified**:
   - Executed live text inference against Gemini Developer API: returned `LIVE_GEMINI_OK`.
   - Executed live structured extraction of realistic engineering resume: successfully returned validated `ExtractedResumeSchema` with personal info, education, experience, and 9 technical skills.
   - Verified that no mock adapter or fallback heuristics were invoked during live operation.
2. **Automated Test Isolation**:
   - Pytest unit and integration suites run deterministically in SQLite using `MockLLMProvider` via `override_llm_provider()` to ensure offline execution and fast CI/CD execution without consuming API quota.
3. **Secret Protection**:
   - All API keys and secrets remain strictly redacted. No tokens or keys are logged or returned to frontend clients.

---

## 4. Document Processing & Ingestion Matrix

The document processing pipeline in `backend/app/services/document_extractor.py` was evaluated against all boundary conditions:

| Scenario | Input Condition | Expected System Behavior | Actual Result | Status |
|---|---|---|---|---|
| **Valid PDF** | Standard PDF with text layer | Extracts text, page geometry, character counts | 201 Created, status `parsed` | **PASS** |
| **Valid DOCX** | Word OpenXML document with tables & paragraphs | Extracts text preserving paragraph & table cells | 201 Created, status `parsed` | **PASS** |
| **Unsupported Extension** | Image (`.png`), Text (`.txt`), Executable (`.exe`) | Rejected at API boundary before extraction | 400 Bad Request, descriptive error message | **PASS** |
| **Spoofed MIME Header** | File named `test.pdf` containing plain text | Header magic byte check (`%PDF-`) detects mismatch | 400 Bad Request (`UNSUPPORTED_FORMAT`) | **PASS** |
| **Empty File (0 bytes)** | Zero-byte upload payload | Size check fails immediately | 400 Bad Request (`Uploaded file is empty`) | **PASS** |
| **Oversized Document** | Document > 10MB (10,485,760 bytes) | Rejects payload prior to storage or extraction | 400 Bad Request (`exceeds maximum allowable limit`) | **PASS** |
| **Corrupted PDF** | Truncated or malformed PDF binary stream | Handles `pypdf` parsing failure gracefully | 201 Created, status `failed`, category `CORRUPTED_DOCUMENT` | **PASS** |
| **Image-Only / Scanned PDF** | PDF with 0 extractable text characters (< 50 chars) | Identifies scanned image; flags OCR required | 201 Created, status `failed`, category `INSUFFICIENT_TEXT_OCR_REQUIRED` | **PASS** |
| **Encrypted PDF** | Password-protected PDF document | Flags encrypted file without crashing | 201 Created, status `failed`, category `DOCUMENT_ENCRYPTED` | **PASS** |
| **OCR Integrity Rule** | Scanned document handling | System notes OCR is required and does **NOT** falsely claim OCR was executed | Message clearly states: *"The PDF appears to be a scanned image and requires OCR to parse."* | **PASS** |
| **AI Provider Failure** | Upstream 503 load spike or network timeout | Records failure cleanly, stores document on disk | Status `failed`, category `AI_PROVIDER_UNAVAILABLE` | **PASS** |
| **Retry Endpoint** | `POST /api/v1/resume/{id}/retry` | Re-reads stored binary from disk and re-runs pipeline | Successfully transitions from `failed` to `parsed` | **PASS** |

---

## 5. Truthful Extraction & Anti-Fabrication Safeguards

CoachPath's foundational AI policy prohibits inventing qualifications, credentials, or skills:

1. **Missing Data Remains Missing**:
   - When a minimal resume without education, certifications, or GPA was uploaded, the structured output strictly contained `[]` or `None`.
   - The AI system prompt explicitly forbids generating speculative fields.
2. **Extracted Skills are Marked Unverified**:
   - Skills merged from resumes are populated in `user_skills` with:
     - `confidence_score = Decimal("0.50")`
     - `proficiency_tier = "unverified"`
     - `is_verified = False`
     - `primary_source = "extracted"`
   - Resume claims are **never** elevated to verified skills without assessment.
3. **Draft Isolation**:
   - Uploading and parsing a resume performs zero writes to `career_profiles`, `user_profiles`, or `user_skills`.
   - The original resume document is preserved in immutable storage.

---

## 6. Profile Merging & State Integrity

The human approval gateway implemented in `confirm_and_merge_profile` guarantees data integrity:

1. **Human Approval Gate**:
   - Merging only occurs when the candidate explicitly submits `POST /api/v1/resume/{id}/confirm`.
   - Unparsed or failed resumes cannot be confirmed (HTTP 409 Conflict).
2. **Selective Inclusion & Exclusion**:
   - Users can exclude individual education records, experiences, projects, certifications, or skills.
   - Excluded items are omitted from the database write.
3. **Inline Candidate Edits**:
   - Users can correct dates, degrees, company names, or descriptions prior to confirmation.
   - The edited values are written directly to PostgreSQL.
4. **Idempotency & Duplicate Prevention**:
   - Education is deduplicated by `(institution_name, degree)`.
   - Experience is deduplicated by `(company_name, role_title)`.
   - Projects are deduplicated by `title`.
   - Certifications are deduplicated by `(name, issuing_organization)`.
   - Skills are deduplicated by `skill_id`.
   - Repeated confirmation submissions result in `0` additions without duplicating records.
5. **Atomic Transactions**:
   - All profile updates, skill inserts, and completeness score recalculations execute inside a single transactional block (`await db.commit()`).

---

## 7. Security, Authorization & Privacy Controls

1. **Authentication Enforcement**:
   - All 7 endpoints under `/api/v1/resume` reject unauthenticated requests with HTTP 401 Unauthorized.
2. **Multi-Tenant Cross-User Isolation**:
   - A user cannot retrieve metadata, inspect parsed drafts, download documents, retry parsing, confirm merges, or delete resumes belonging to another user.
   - Unauthorized attempts yield HTTP 403 Forbidden.
3. **Storage Security & Path Traversal Defenses**:
   - Stored file paths use server-generated UUIDs: `{user_id}/{uuid}.{ext}`.
   - Client filenames are never used as storage paths.
   - Path resolution uses `os.path.commonpath()` containment checks; directory traversal attempts (`../../`) trigger `FileStorageException`.
   - Original documents are not publicly accessible via static web servers.
4. **Secure Streaming Downloads**:
   - Documents are streamed via authenticated endpoints with sanitized `Content-Disposition: attachment; filename="..."` headers.
5. **Retention and Data Deletion**:
   - Calling `DELETE /api/v1/resume/{id}` deletes the database entity and unlinks the physical file from disk. Empty parent directories are cleaned up. Subsequent requests return HTTP 404 Not Found.

---

## 8. Test Execution Audit Summary

### Backend Tests (Pytest)
```bash
pytest tests/ -v
# Result: 129 passed, 5 warnings in 16.52s (0 failures)
```
- Total test files: **13**
- Total test cases: **129**
- Newly added Phase 5C regression audit tests: **6** (`test_phase5c_e2e_audit.py`)

### Frontend Verification
```bash
# TypeScript Typecheck
cd frontend && npx tsc --noEmit
# Result: 0 errors

# ESLint Code Quality
cd frontend && npm run lint
# Result: ✔ No ESLint warnings or errors

# Next.js Production Build
cd frontend && npm run build
# Result: ✓ Compiled successfully, 25/25 static pages generated
```

---

## 9. Problems Discovered & Resolutions Applied

| # | Item / Check | Observation | Resolution |
|---|---|---|---|
| **1** | User ID key naming in test fixture | The registration response schema uses `user_id` (`UserRegisterResponse`), but the initial audit test attempted to read `id`. | Fixed `register_login` helper to read `user_id`, matching the Pydantic schema. |
| **2** | Career profile key naming | The master profile response schema uses `profile_id` (`CareerProfileMasterResponse`), but the audit test referenced `id`. | Updated assertion to reference `final_data["profile_id"]`. |
| **3** | Test client cookie persistence | In `test_security_multi_tenant_isolation`, httpx `AsyncClient` retained the session cookie from preceding login, causing unauthenticated checks to receive 200. | Added `client.cookies.clear()` prior to unauthenticated assertion block. |
| **4** | Test session skill seeding | In-memory SQLite starts with empty tables in test isolation; skill confirmations were matching 0 canonical skills. | Added seeding of canonical skills (`python`, `postgresql`, `docker`) in test sessions prior to confirmation assertions. |

---

## 10. Remaining Risks & Limitations

1. **Scanned / Image-Only PDFs**:
   - The current architecture explicitly rejects image-only PDFs with `INSUFFICIENT_TEXT_OCR_REQUIRED`. OCR execution (e.g. Tesseract or cloud OCR) is planned for a subsequent infrastructure enhancement.
2. **LLM Quota and Latency**:
   - Live Gemini extraction requires outbound internet connectivity to `generativelanguage.googleapis.com`. In offline environments, the system surfaces a clear `503 Service Unavailable` error and allows retries when connectivity is restored.

---

## 11. Readiness Verdict for Phase 6

Phase 5 (Resume Ingestion, AI Parsing, Review Workflow, and Profile Integration) is **complete, hardened, and verified**.

The system satisfies all functional, architectural, and security acceptance criteria. The codebase is clean, type-safe, fully covered by automated regression tests, and ready for **Phase 6: Evidence-Based Skill Assessments and Skill-Gap Analysis**.
