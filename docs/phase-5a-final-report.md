# Phase 5A Final Engineering Report: Resume Upload & AI Parsing Backend

**Phase**: Phase 5A — Resume Upload and AI Parsing Backend  
**Date**: October 22, 2026  
**Status**: **PHASE 5A COMPLETE**  
**Author**: Lead Software Architect & AI Engineering Lead  

---

## 1. Implementation Summary

Phase 5A delivers CoachPath's secure document ingestion and AI-powered resume extraction backend. The module automates the conversion of unstructured candidate resumes (PDF and DOCX) into structured, reviewable career intelligence while strictly honoring zero-fabrication and candidate-consent invariants.

### Key Architectural Achievements:
1. **Multi-Layer File Validation & MIME Magic-Byte Verification**:
   - Rejects non-PDF/DOCX extensions before filesystem operations.
   - Inspects binary headers (`%PDF-` for PDF, `PK\x03\x04` with internal `word/document.xml` validation for DOCX) to block spoofed or malicious executables.
   - Enforces a 10MB ceiling (`MAX_RESUME_SIZE_BYTES = 10485760`) and immediately blocks empty 0-byte uploads.
2. **Path Traversal Guard & Atomic Storage**:
   - Persists files with server-generated UUID4 filenames under `uploads/resumes/{user_id}/`.
   - Uses `os.path.commonpath` checks to prevent directory traversal.
   - Employs atomic temp-write and replace operations to prevent read tearing.
   - Calculates and stores SHA-256 hashes for data integrity.
3. **Deterministic Text & Layout Extraction**:
   - Employs `pypdf` for PDF text extraction with layout and decryption checks.
   - Employs `python-docx` for structured paragraph and table text extraction.
   - Detects image-only or scanned PDFs (<50 characters) and flags `INSUFFICIENT_TEXT_OCR_REQUIRED` without fabricating fake parsing.
   - Captures malformed or corrupted documents as `CORRUPTED_DOCUMENT` without throwing 500 errors.
4. **Prompt-Quarantined AI Parsing & Zero Fabrication**:
   - Isolates candidate resume text inside `<<<RESUME_DOCUMENT_TEXT>>>` delimiters to neutralize prompt injection attacks.
   - Uses the `LLMProvider` abstraction to extract credentials into strongly validated Pydantic v2 schemas (`ExtractedResumeSchema`).
   - Prohibits LLM hallucination: missing fields default to `null` or empty arrays.
5. **Canonical Skill Normalization**:
   - Matches raw extracted skills against PostgreSQL's canonical `skills` taxonomy by ID, exact name, and synonym aliases.
   - Emits structured `NormalizedSkillItem` records distinguishing canonical matches from unmapped raw terms.
6. **Non-Destructive Review Draft (Profile Isolation)**:
   - Extracted data is saved as a reviewable JSONB draft on `Resume.extracted_data`.
   - **`CareerProfile` and `UserSkill` remain completely unmutated throughout Phase 5A.** All profile merging is explicitly reserved for Phase 5B human review and confirmation.
7. **Complete RESTful Endpoint Suite**:
   - Implemented upload, list, get metadata, get parsed draft, retry failed parsing, secure download, and delete endpoints on `/api/v1/resume`.

---

## 2. Files Created and Modified

### Created Files
| File Path | Description |
|---|---|
| `backend/alembic/versions/b2c3d4e5f6a1_phase_5a_resume_parsing_enhancements.py` | Alembic migration enhancing `resumes` table with error tracking and expanded status check. |
| `backend/app/schemas/resume.py` | Pydantic v2 schemas for document upload, extraction, normalization, and API responses. |
| `backend/app/services/storage.py` | Secure local file storage service with directory traversal and atomic write guards. |
| `backend/app/services/document_extractor.py` | Deterministic PDF and DOCX text extractor with scanned PDF and encryption detection. |
| `backend/app/services/skill_normalizer.py` | Canonical skill taxonomy matcher with exact, case-insensitive, and synonym resolution. |
| `backend/app/ai/prompts/resume_v1.py` | Versioned prompt template with prompt injection delimiter quarantine. |
| `backend/tests/test_resume.py` | Comprehensive test suite covering 17 test cases across upload, parsing, security, and edge cases. |
| `docs/resume-parsing-architecture.md` | Formal architecture specification for resume upload and AI parsing. |
| `docs/phase-5a-final-report.md` | This completion report. |

### Modified Files
| File Path | Changes Applied |
|---|---|
| `backend/app/core/config.py` | Added `UPLOAD_DIR`, `MAX_RESUME_SIZE_BYTES` (10MB), and `RESUME_EXTRACTION_TIMEOUT` (45s). |
| `backend/app/core/exceptions.py` | Added `BadRequestException` (HTTP 400). |
| `backend/app/models/resume.py` | Added `parsing_error`, `parsing_error_category`, `parsed_at`, `updated_at`, and expanded `resumes_status_check`. |
| `backend/app/services/resume.py` | Implemented complete resume orchestration service (`upload_and_parse`, `retry_parsing`, `delete_resume`, etc.). |
| `backend/app/api/routes/resume.py` | Implemented 7 production REST endpoints under `/api/v1/resume`. |
| `backend/requirements.txt` | Added `python-multipart>=0.0.20`, `pypdf>=5.0.0`, and `python-docx>=1.1.0`. |
| `backend/tests/test_routers_structure.py` | Updated router structural placeholder test to recognize `resume` as an authenticated domain. |

---

## 3. Database Changes and Migrations

### Migration `b2c3d4e5f6a1_phase_5a_resume_parsing_enhancements`
- **Revision ID**: `b2c3d4e5f6a1`
- **Down Revision**: `a1b2c3d4e5f6` (Phase 4A onboarding tables)
- **Table Altered**: `resumes`
- **Columns Added**:
  - `parsing_error` (`sa.Text`, nullable): Human-readable error description.
  - `parsing_error_category` (`sa.String(64)`, nullable): Categorized error code.
  - `parsed_at` (`sa.DateTime(timezone=True)`, nullable): Completion timestamp.
  - `updated_at` (`sa.DateTime(timezone=True)`, nullable, server default `CURRENT_TIMESTAMP`).
- **Constraint Updated**:
  - Replaced `resumes_status_check` constraint with:
    $$\text{status} \in \{\text{'uploaded'}, \text{'parsing'}, \text{'processing'}, \text{'parsed'}, \text{'needs\_review'}, \text{'failed'}\}$$
- **Database Status**: PostgreSQL head updated cleanly to `b2c3d4e5f6a1 (head)`.

---

## 4. API Endpoints Implemented

| Endpoint | Method | Auth | Summary |
|---|---|---|---|
| `/api/v1/resume/upload` | `POST` | Bearer | Upload and parse resume (`multipart/form-data`). Returns `201 Created`. |
| `/api/v1/resume` | `GET` | Bearer | List all uploaded resumes for the authenticated user. |
| `/api/v1/resume/{id}` | `GET` | Bearer | Get resume metadata, file info, and processing status. |
| `/api/v1/resume/{id}/parsed` | `GET` | Bearer | Get structured extraction draft with canonical skill matches. |
| `/api/v1/resume/{id}/retry` | `POST` | Bearer | Retry parsing for a previously failed resume document. |
| `/api/v1/resume/{id}/download` | `GET` | Bearer | Secure streaming download of original resume file. |
| `/api/v1/resume/{id}` | `DELETE` | Bearer | Permanently delete resume record and physical file from disk. |

---

## 5. Verification & Test Suite Results

### 1. Resume Test Suite (`test_resume.py`)
Executed: `python -m pytest tests/test_resume.py -v`
**Result: 17 Passed, 0 Failed (100% pass rate in 2.52s)**

Verified Scenarios:
- `test_upload_valid_pdf_success`: Valid PDF upload, text extraction, mock LLM parsing, status `'parsed'`.
- `test_upload_valid_docx_success`: Valid DOCX upload, XML paragraph/table extraction, mock LLM parsing.
- `test_upload_unsupported_file_extension_rejected`: Rejection of `.txt`, `.exe`, `.zip` with HTTP 400.
- `test_upload_spoofed_mime_type_rejected`: Rejection of `.pdf` containing plain text (magic byte failure).
- `test_upload_empty_file_rejected`: Rejection of 0-byte file uploads with HTTP 400.
- `test_upload_file_exceeding_size_limit_rejected`: Rejection of payloads > 10MB with HTTP 400.
- `test_upload_image_only_pdf_flags_ocr_required`: Scanned PDF correctly flagged with `INSUFFICIENT_TEXT_OCR_REQUIRED`.
- `test_upload_corrupt_pdf_file_flags_corrupted`: Malformed PDF structure flagged with `CORRUPTED_DOCUMENT`.
- `test_upload_ai_provider_failure_flags_service_unavailable`: Unconfigured LLM provider gracefully sets `status='failed'`, `parsing_error_category='AI_PROVIDER_UNAVAILABLE'`.
- `test_retry_parsing_recovers_failed_resume`: Retrying a failed resume after provider restoration transitions status to `'parsed'`.
- `test_skill_normalization_maps_canonical_skills`: Maps raw skills to canonical IDs/names in `skills` table; retains unmapped skills.
- `test_career_profile_is_not_mutated_on_parsing`: **Verifies that `CareerProfile` and `UserSkill` are untouched.**
- `test_list_and_get_resume_metadata`: Verifies list filtering and metadata retrieval.
- `test_download_original_resume_document`: Streams original file bytes with appropriate `Content-Disposition`.
- `test_delete_resume_cleans_db_and_storage`: Deletes database row and verifies file removed from filesystem.
- `test_cross_user_isolation_forbidden`: User A cannot access or download User B's resume (HTTP 403).
- `test_unauthenticated_requests_rejected`: Unauthenticated requests to all endpoints return HTTP 401.

### 2. Full Regression Suite
Executed: `python -m pytest tests/ -v`
**Result: 106 Passed, 0 Failed, 0 Regressions across all domain modules**

### 3. Frontend Static Verification
- TypeScript Check: `cd frontend && npx tsc --noEmit` $\to$ **Exit code 0 (No type errors)**
- ESLint Check: `cd frontend && npm run lint` $\to$ **Exit code 0 (✔ No ESLint warnings or errors)**

---

## 6. Security & Privacy Audit

1. **Anti-Traversal Protection**: Directory containment validated with `os.path.commonpath`.
2. **Access Control & Multi-Tenancy**: All routes enforce `require_active_user` and verify `resume.user_id == current_user.id` (or admin override).
3. **MIME Spoofing Prevention**: Binary magic-byte verification strictly required for PDF and DOCX.
4. **Prompt Injection Quarantine**: Input enclosed within delimiter tags with explicit anti-instruction meta-prompting.
5. **No Blind Overwriting**: Central profile data is fully isolated from automated parser writes.

---

## 7. Prerequisites & Handoff for Phase 5B

Phase 5A backend implementation is complete. The system is ready for **Phase 5B: Resume Review & Career Profile Integration (Frontend + Merging)**.

Prerequisites fulfilled for Phase 5B:
1. `GET /api/v1/resume/{id}/parsed` is live and returns structured `ExtractedResumeSchema` with normalized canonical skill matches.
2. `POST /api/v1/resume/upload` accepts drag-and-drop file uploads up to 10MB.
3. `POST /api/v1/resume/{id}/retry` enables one-click recovery when an AI provider returns an outage.
4. Extracted draft data sits safely in `resumes.extracted_data` awaiting human review, editing, and confirmation before profile assimilation.
