# Phase 11A Technical Specification: Intelligent Application Preparation & Recruiter Outreach Backend

## 1. Executive Summary

Phase 11A establishes the backend service architecture, data models, AI grounding pipelines, security controls, and RESTful API endpoints for CoachPath's **Intelligent Application Preparation & Recruiter Outreach**. 

Building directly upon Phase 10's Tailored Resume engine, Phase 11A enables candidates to prepare comprehensive, evidence-grounded application packages and personalized, bounded recruiter outreach messages without fabricating background details, mutating master resumes, or taking automated actions on external portals.

### Core Architectural Invariants:
1. **Zero Fabrication**: Cover notes and answers to application questions cite verified achievements, skills, and projects from the candidate's authentic profile. Any missing experience triggers explicit clarification prompts rather than hallucinated claims.
2. **Resume Immutability**: Master resumes and approved tailored resume variants remain byte-for-byte immutable.
3. **Explicit Human Approval Gate**: Application packages and outreach drafts cannot transition to external handoff without mandatory, active human confirmation.
4. **Strict Outreach Bounding**: Recruiter outreach drafts strictly enforce a $\le 90$-word ceiling, zero fabricated identities/emails, and a backend rate limit of at most 3 active drafts per application.
5. **Honest Submission & Safe Handoff**: CoachPath never automatically submits forms or sends unauthorized emails. Applications transition to `submitted` only when the candidate explicitly confirms completion on the employer's official portal.

---

## 2. Data Models & Database Migration

### Alembic Migration
- **Revision ID**: `d5e6f7a2b3c4`
- **Down Revision**: `c4d5e6f7a2b3` (Phase 10A Resume Tailoring)
- **Tables Created**: `application_packages`, `recruiter_outreach_drafts`

### `ApplicationPackage` Model
Tracks full application packages containing tailored cover notes, question answers, grounding evidence citations, and multi-stage approval lifecycles:

| Column | Type | Constraints / Description |
| :--- | :--- | :--- |
| `id` | `UUID` | Primary Key, default UUIDv4 |
| `user_id` | `UUID` | FK `users.id` (CASCADE), Indexed |
| `job_id` | `UUID` | FK `jobs.id` (RESTRICT), Indexed |
| `application_id` | `UUID` | FK `applications.id` (SET NULL), Optional link to Kanban pipeline |
| `source_resume_id` | `UUID` | FK `resumes.id` (RESTRICT), Source master resume |
| `tailored_resume_version_id` | `UUID` | FK `resume_versions.id` (RESTRICT), Submitted resume variant |
| `status` | `VARCHAR(32)` | Check: `status IN ('draft', 'edited', 'reviewed', 'approved', 'handoff_initiated', 'submitted')` |
| `cover_note` | `TEXT` | Evidence-grounded candidate cover note |
| `application_questions` | `JSONB` | List of `{id, question, answer, supporting_evidence, needs_clarification, clarification_prompt}` |
| `evidence_references` | `JSONB` | List of verified candidate background facts supporting the package |
| `generated_metadata` | `JSONB` | Model metadata, word counts, omitted unsupported claims |
| `user_notes` | `TEXT` | Candidate private notes and annotations |
| `approved_at` | `TIMESTAMPTZ` | Timestamp candidate certified package |
| `handoff_initiated_at`| `TIMESTAMPTZ` | Timestamp candidate initiated external handoff |
| `application_url` | `VARCHAR(1024)` | Employer official portal link |
| `application_url_source` | `VARCHAR(64)` | Provenance of application URL (`catalog`, `direct_input`) |
| `user_confirmed_submission` | `BOOLEAN` | Server-side confirmation flag (default `FALSE`) |
| `submitted_at` | `TIMESTAMPTZ` | Timestamp candidate confirmed external completion |
| `created_at` / `updated_at` | `TIMESTAMPTZ` | Automatic UTC audit timestamps |

### `RecruiterOutreachDraft` Model
Tracks personalized recruiter networking messages bounded to $\le 90$ words:

| Column | Type | Constraints / Description |
| :--- | :--- | :--- |
| `id` | `UUID` | Primary Key, default UUIDv4 |
| `user_id` | `UUID` | FK `users.id` (CASCADE), Indexed |
| `job_id` | `UUID` | FK `jobs.id` (RESTRICT), Indexed |
| `application_package_id` | `UUID` | FK `application_packages.id` (SET NULL), Optional package link |
| `application_id` | `UUID` | FK `applications.id` (SET NULL), Pipeline application link |
| `recruiter_name` | `VARCHAR(128)` | Candidate-specified recruiter name (never fabricated) |
| `recruiter_role_type` | `VARCHAR(64)` | Category (e.g. `technical_recruiter`, `hiring_manager`) |
| `recruiter_profile_url` | `VARCHAR(512)` | Candidate-supplied LinkedIn/profile URL |
| `recruiter_contact_info` | `VARCHAR(255)` | Candidate-supplied email or communication handle |
| `subject_line` | `VARCHAR(255)` | Concise InMail/email subject |
| `message_body` | `TEXT` | Bounded message text ($\le 90$ words) |
| `word_count` | `INTEGER` | Check: `word_count <= 90` |
| `suggested_role_types`| `JSONB` | Recommended recruiter job titles to search for |
| `status` | `VARCHAR(32)` | Check: `status IN ('draft', 'awaiting_approval', 'approved', 'handoff_initiated', 'sent', 'cancelled')` |
| `approved_at` | `TIMESTAMPTZ` | Timestamp candidate certified outreach message |
| `handoff_initiated_at`| `TIMESTAMPTZ` | Timestamp manual dispatch handoff opened |
| `handoff_type` | `VARCHAR(32)` | `mailto`, `profile_link`, or `copy_text` |
| `sent_at` | `TIMESTAMPTZ` | Timestamp candidate confirmed manual dispatch |
| `user_confirmed_sent` | `BOOLEAN` | Server-side confirmed sent flag (default `FALSE`) |
| `candidate_notes` | `TEXT` | Candidate private focus points |
| `created_at` / `updated_at` | `TIMESTAMPTZ` | Automatic UTC audit timestamps |

---

## 3. API Endpoint Specifications

All endpoints are mounted under `/api/v1` and require authenticated Bearer tokens (`require_active_user`), enforcing multi-tenant isolation.

### Group 9: Applications Router (`/api/v1/applications`)

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Structural operational status check | `200 OK` |
| `POST` | `/prepare` | Prepares evidence-grounded application package | `201 Created` |
| `GET` | `/packages` | Lists candidate application packages (supports `job_id`, `status` filters) | `200 OK` |
| `GET` | `/packages/{id}` | Retrieves full application package by UUID | `200 OK` |
| `PUT` | `/packages/{id}` | Edits cover note or Q&A; resets status to `edited` and clears approval | `200 OK` |
| `POST` | `/packages/{id}/approve` | Human approval gate (`user_confirmation=True`); records `AuditLog` | `200 OK` |
| `POST` | `/packages/{id}/handoff` | Generates external submission checklist & preserved employer URL | `200 OK` |
| `POST` | `/packages/{id}/confirm-submission` | Explicit candidate confirmation of external application completion | `200 OK` |
| `POST` | `/packages/{id}/outreach` | Drafts recruiter outreach message linked to package | `201 Created` |
| `GET` | `/packages/{id}/outreach` | Lists recruiter outreach drafts linked to package | `200 OK` |

### Group 10: Recruiters Router (`/api/v1/recruiters`)

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Structural operational status check | `200 OK` |
| `POST` | `/outreach` | Generates recruiter outreach draft ($\le 90$ words; max 3 per app) | `201 Created` |
| `GET` | `/outreach` | Lists candidate outreach drafts (supports filters) | `200 OK` |
| `GET` | `/outreach/{id}` | Retrieves outreach draft by UUID | `200 OK` |
| `PUT` | `/outreach/{id}` | Edits message text ($\le 90$ words enforced); resets approval | `200 OK` |
| `POST` | `/outreach/{id}/approve` | Human approval gate (`user_confirmation=True`); records `AuditLog` | `200 OK` |
| `POST` | `/outreach/{id}/handoff` | Provides safe manual handoff (`mailto_uri`, `profile_url`, `clipboard_text`) | `200 OK` |
| `POST` | `/outreach/{id}/confirm-sent` | Candidate marks message as manually sent | `200 OK` |
| `POST` | `/outreach/{id}/cancel` | Cancels or discards outreach draft | `200 OK` |
| `DELETE`| `/outreach/{id}` | Permanently deletes unsubmitted outreach draft | `204 No Content`|

---

## 4. Anti-Hallucination & Evidence Grounding

The AI generation layer relies exclusively on Google Gemini via the quarantined prompt engine (`app.ai.prompts.application_prep_v1` and `app.ai.prompts.recruiter_outreach_v1`):

1. **Structured Input Quarantining**: User input, job descriptions, and candidate profile facts are placed inside strict XML delimiter blocks (`<candidate_profile>`, `<job_posting>`, `<tailored_resume>`), preventing prompt injection attacks.
2. **Explicit Fact Attribution**: The prompt strictly instructs Gemini to use only authentic facts present in the prompt. Every question answer includes `supporting_evidence` linking back to employer names, projects, or verified skills.
3. **Transparent Clarification Fallbacks**: When candidate experience is missing for a key job requirement (e.g. bare Kubernetes cluster management), the prompt forbids inventing experience and requires setting `needs_clarification=True` with a plain-English `clarification_prompt`.
4. **Unsupported Claims Omission**: Job qualifications not supported by candidate background are recorded under `unsupported_claims` and omitted from the cover note.

---

## 5. Outreach Word Count & Rate Limiting

1. **Word-Count Invariant**: InMail and cold networking outreach performance degrades rapidly past 90 words. Both the prompt schema and service validation reject or truncate messages exceeding 90 words.
2. **Backend Rate Limiting**: Candidates cannot generate endless recruiter spam. The backend strictly limits active drafts to **3 per job application**. Generating a 4th draft raises a `422 Unprocessable Entity` validation error requiring the user to cancel or delete an existing draft first.
3. **Zero Fabricated Identities**: If the candidate does not supply a recruiter name or email, CoachPath will NOT invent one. Instead, it suggests relevant role titles (e.g., "Technical Recruiter", "Engineering Hiring Manager") for the user to find on LinkedIn.

---

## 6. Audit Logging & Security Invariants

All approval and submission transitions record immutable events in the PostgreSQL `AuditLog` table:
- `APPLICATION_PACKAGE_APPROVED`
- `APPLICATION_HANDOFF_INITIATED`
- `APPLICATION_SUBMISSION_CONFIRMED`
- `RECRUITER_OUTREACH_APPROVED`
- `RECRUITER_OUTREACH_HANDOFF_INITIATED`
- `RECRUITER_OUTREACH_SENT_CONFIRMED`

Each record captures:
- `user_id`: Authenticated user UUID
- `human_approved`: `True`
- `diff_payload`: State transition payload and section flags
- `client_ip_hash`: SHA-256 hash of the client IP
- `user_agent`: Client user agent string
- `created_at`: UTC timestamp
