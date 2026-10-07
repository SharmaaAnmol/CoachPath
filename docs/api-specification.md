# CoachPath REST API Specification & Contract

> **Document Version**: 1.0.0  
> **Lifecycle Phase**: Phase 0 — Inception & Architecture  
> **Status**: Approved for Engineering Implementation  
> **Framework**: Python 3.11+ / FastAPI with OpenAPI 3.1 & Pydantic v2  
> **Base URL**: `/api/v1`  
> **Target Audience**: Backend Engineering, Frontend Engineering, QA, API Consumers  

---

## 1. Global API Standards & Conventions

### 1.1 Architectural Style & Protocol
- **Architecture**: RESTful JSON API adhering to Level 2/3 Richardson Maturity Model.
- **Protocol**: HTTPS (TLS 1.3 in transit).
- **Encoding**: UTF-8 character encoding throughout all payloads and headers.
- **Media Types**:
  - Request/Response default: `application/json`
  - Document uploads: `multipart/form-data`
  - Document exports: `application/pdf`, `text/markdown`

### 1.2 Authentication & Session Tokens
- **Transport**: Authorization is transmitted via either:
  1. `Authorization: Bearer <JWT_ACCESS_TOKEN>` header, or
  2. Secure `HttpOnly`, `SameSite=Lax`, `Secure` cookie (`access_token`).
- **Token Lifecycles**:
  - Access Token: 60 minutes validity (contains `sub=user_id`, `role`, `jti`).
  - Refresh Token: 7 days validity (opaque string stored as SHA-256 in `user_sessions`).

### 1.3 Standard RFC 7807 Error Responses
All 4xx and 5xx responses strictly adhere to the **RFC 7807 Problem Details** specification:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters provided.",
    "status": 422,
    "details": [
      {
        "field": "confidence_score",
        "issue": "Confidence score must be a number between 0.0 and 1.0."
      }
    ],
    "request_id": "req_01HZX874A92KLP"
  }
}
```

#### Standard Error Code Mapping
| Status Code | Code String | Meaning & Trigger |
| :--- | :--- | :--- |
| **400 Bad Request** | `MALFORMED_REQUEST` | Syntax error, invalid JSON, or missing required headers. |
| **401 Unauthorized** | `AUTHENTICATION_REQUIRED` | Missing, expired, or blacklisted JWT access token. |
| **403 Forbidden** | `INSUFFICIENT_PERMISSIONS` | Authenticated user is not the owner of the target resource. |
| **404 Not Found** | `RESOURCE_NOT_FOUND` | Target entity ID does not exist or has been soft-deleted. |
| **409 Conflict** | `STATE_CONFLICT` | Duplicate email, active concurrent assessment, or idempotency clash. |
| **422 Unprocessable**| `VALIDATION_ERROR` | Schema validation failure (Pydantic validation errors). |
| **429 Too Many Req** | `RATE_LIMIT_EXCEEDED` | Request rate exceeds configured sliding window threshold. |
| **500 Internal Error**| `INTERNAL_SERVER_ERROR` | Unhandled server exception (sanitized in production with log trace ID). |

### 1.4 Correlation & Tracing Headers
Every incoming request must be associated with a correlation ID:
- Client can pass `X-Request-ID: <UUID>`. If omitted, FastAPI middleware generates one automatically.
- All HTTP responses return the header `X-Request-ID: <UUID>`.
- All structured application logs, error payloads, and AI telemetry log this ID.

### 1.5 Pagination Conventions
List endpoints support standardized query parameters and metadata envelope:
- **Query Parameters**:
  - `page`: Integer (1-indexed, default `1`, min `1`).
  - `page_size`: Integer (default `20`, min `1`, max `100`).
- **Response Meta Envelope**:
  ```json
  {
    "data": [ ... ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_items": 42,
      "total_pages": 3,
      "has_next": true,
      "has_prev": false
    }
  }
  ```

### 1.6 Filtering & Sorting Conventions
- **Sorting**: `sort_by=<field>&order=<asc|desc>` (e.g., `?sort_by=overall_score&order=desc`).
- **Filtering**: Query parameters matching resource attributes (e.g., `?role_id=backend-developer&remote_type=remote`).
- **Date Format**: Strict ISO-8601 UTC format: `YYYY-MM-DDTHH:MM:SSZ`.

### 1.7 Idempotency Requirements
All mutating, state-altering, or expensive operations (e.g., creating tailored resume versions, confirming applications, triggering roadmap regenerations) accept an optional or mandatory `Idempotency-Key: <UUID>` header.
- Cached in Redis for 60 seconds.
- Replaying the identical key with matching parameters returns the cached successful response without re-triggering AI generation or duplicate database mutations.

### 1.8 Rate Limiting Policies (Redis Sliding Window)
- **Public Auth (`/api/v1/auth/*`)**: 10 requests / minute per IP.
- **Standard Authenticated API**: 120 requests / minute per user ID.
- **AI-Heavy Inference (`/resumes/tailor`, `/assessments/*/start`)**: 10 requests / minute per user ID.
- **Exceeded Threshold**: Returns HTTP 429 with `Retry-After: <seconds>` header.

---

## 2. API Endpoint Groups (MVP Contract)

---

### Group 1: Authentication & Session Management (`/api/v1/auth`)

#### 1.1 Register User
- **Method / URL**: `POST /api/v1/auth/register`
- **Auth**: Public
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "Password123!",
    "full_name": "Aarav Mehta"
  }
  ```
- **Validation**: Email must be valid RFC 5322; password $\ge 8$ chars containing uppercase, lowercase, number, and special character.
- **Response (201 Created)**:
  ```json
  {
    "user_id": "8f1a23e9-c402-45e2-8d76-b94f11223344",
    "email": "user@example.com",
    "status": "pending_verification",
    "message": "Account created. Verification email sent."
  }
  ```
- **Errors**: 409 Conflict (`email already registered`), 422 Unprocessable Entity.

#### 1.2 Login User
- **Method / URL**: `POST /api/v1/auth/login`
- **Auth**: Public
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "Password123!"
  }
  ```
- **Response (200 OK)**:
  - Sets HttpOnly, Secure cookie `access_token` and `refresh_token`.
  - Body:
    ```json
    {
      "access_token": "eyJhbGciOi...",
      "token_type": "bearer",
      "expires_in": 3600,
      "user": {
        "id": "8f1a23e9-c402-45e2-8d76-b94f11223344",
        "email": "user@example.com",
        "role": "candidate"
      }
    }
    ```
- **Errors**: 401 Unauthorized (`invalid email or password`), 429 Too Many Requests.

#### 1.3 Refresh Token
- **Method / URL**: `POST /api/v1/auth/refresh`
- **Auth**: Public (Requires refresh token in cookie or body: `{"refresh_token": "..."}`)
- **Response (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "expires_in": 3600
  }
  ```
- **Errors**: 401 Unauthorized (`expired or revoked refresh token`).

#### 1.4 Logout
- **Method / URL**: `POST /api/v1/auth/logout`
- **Auth**: Authenticated (`candidate` or `admin`)
- **System Action**: Blacklists current JWT in Redis; revokes session in `user_sessions`; clears auth cookies.
- **Response (200 OK)**: `{"message": "Logged out successfully"}`

#### 1.5 Forgot Password & Reset
- **`POST /api/v1/auth/forgot-password`**: Request password reset email (`{"email": "..."}`). Always returns 200 OK to prevent account enumeration.
- **`POST /api/v1/auth/reset-password`**: Submit reset token and new password (`{"token": "...", "new_password": "..."}`). Returns 200 OK.

---

### Group 2: Personalized Onboarding (`/api/v1/onboarding`)

#### 2.1 Start Onboarding
- **Method / URL**: `POST /api/v1/onboarding/start`
- **Auth**: Authenticated
- **Response (200 OK)**:
  ```json
  {
    "current_step": "role_selection",
    "supported_roles": [
      {"id": "software-engineer", "title": "Software Engineer (Generalist)"},
      {"id": "backend-developer", "title": "Backend Developer"},
      {"id": "frontend-developer", "title": "Frontend Developer"},
      {"id": "data-analyst", "title": "Data Analyst"},
      {"id": "data-scientist", "title": "Data Scientist"},
      {"id": "ml-engineer", "title": "Machine Learning Engineer"},
      {"id": "ai-engineer", "title": "AI Engineer"}
    ]
  }
  ```

#### 2.2 Submit Onboarding Step
- **Method / URL**: `POST /api/v1/onboarding/step`
- **Auth**: Authenticated
- **Request Body**:
  ```json
  {
    "step": "role_selection",
    "payload": {
      "primary_role_id": "backend-developer",
      "secondary_role_id": "software-engineer",
      "career_stage": "student",
      "work_preference": "hybrid",
      "target_locations": ["San Francisco, CA", "Remote"]
    }
  }
  ```
- **Validation**: `primary_role_id` must match supported role taxonomy; max 2 roles.
- **Response (200 OK)**:
  ```json
  {
    "next_step": "resume_upload",
    "progress_percentage": 50
  }
  ```

#### 2.3 Retrieve Onboarding Progress
- **Method / URL**: `GET /api/v1/onboarding/progress`
- **Auth**: Authenticated
- **Response (200 OK)**: `{"is_completed": false, "current_step": "resume_upload", "completed_steps": ["role_selection"]}`

#### 2.4 Complete Onboarding
- **Method / URL**: `POST /api/v1/onboarding/complete`
- **Auth**: Authenticated
- **Response (200 OK)**: Transitions candidate into active state, recalculates initial readiness baseline, returns 200 OK.

---

### Group 3: Central Career Profile (`/api/v1/profile`)

#### 3.1 Get Central Career Profile
- **Method / URL**: `GET /api/v1/profile`
- **Auth**: Authenticated
- **Response (200 OK)**:
  ```json
  {
    "profile_id": "7b2c11e4-b801-44d3-a567-0e02b2c3d479",
    "user_id": "8f1a23e9-c402-45e2-8d76-b94f11223344",
    "full_name": "Aarav Mehta",
    "headline": "CS Senior | Aspiring Backend Developer",
    "career_stage": "student",
    "primary_role": {"id": "backend-developer", "title": "Backend Developer"},
    "secondary_role": {"id": "software-engineer", "title": "Software Engineer"},
    "work_preference": "hybrid",
    "target_locations": ["San Francisco, CA", "Remote"],
    "education": [
      {
        "id": "e1-uuid",
        "institution_name": "San Jose State University",
        "degree": "B.S.",
        "field_of_study": "Computer Science",
        "start_date": "2023-08-15",
        "end_date": "2027-05-20",
        "is_current": true,
        "gpa": 3.82
      }
    ],
    "experience": [],
    "projects": [
      {
        "id": "p1-uuid",
        "title": "E-Commerce Microservices",
        "description": "Asynchronous inventory management built with FastAPI and Redis",
        "technologies": ["Python", "FastAPI", "Redis", "PostgreSQL"],
        "github_url": "https://github.com/user/microservices",
        "live_url": null,
        "bullet_points": ["Achieved sub-50ms cache hits using Redis ZSETs"]
      }
    ],
    "verified_skills_count": 8,
    "completeness_score": 85.0
  }
  ```

#### 3.2 Update Career Goals
- **Method / URL**: `PUT /api/v1/profile/career-goals`
- **Auth**: Authenticated
- **Request Body**:
  ```json
  {
    "primary_role_id": "backend-developer",
    "secondary_role_id": null,
    "work_preference": "remote",
    "target_locations": ["Remote"]
  }
  ```
- **Response (200 OK)**: Returns updated goals and triggers asynchronous background gap/roadmap recalculation.

#### 3.3 Education CRUD
- `GET /api/v1/profile/education`: List education records.
- `POST /api/v1/profile/education`: Add education record (`201 Created`).
- `PUT /api/v1/profile/education/{id}`: Update education record (`200 OK`).
- `DELETE /api/v1/profile/education/{id}`: Delete education record (`204 No Content`).

#### 3.4 Experience CRUD
- `GET /api/v1/profile/experience`: List work experiences.
- `POST /api/v1/profile/experience`: Add work experience (`201 Created`).
- `PUT /api/v1/profile/experience/{id}`: Update work experience (`200 OK`).
- `DELETE /api/v1/profile/experience/{id}`: Delete work experience (`204 No Content`).

#### 3.5 Projects CRUD
- `GET /api/v1/profile/projects`: List projects.
- `POST /api/v1/profile/projects`: Add project (`201 Created`).
- `PUT /api/v1/profile/projects/{id}`: Update project (`200 OK`).
- `DELETE /api/v1/profile/projects/{id}`: Delete project (`204 No Content`).

#### 3.6 Certifications CRUD
- `GET /api/v1/profile/certifications`: List certifications.
- `POST /api/v1/profile/certifications`: Add certification (`201 Created`).
- `PUT /api/v1/profile/certifications/{id}`: Update certification (`200 OK`).
- `DELETE /api/v1/profile/certifications/{id}`: Delete certification (`204 No Content`).

#### 3.7 Profile Activity Log
- `GET /api/v1/profile/activity`: List chronological candidate activity events (`activity_logs`) with pagination (`page`, `page_size`).

---

### Group 4: Skills Taxonomy & Gap Analysis (`/api/v1/skills`)

#### 4.1 Get Current Profile Skills
- **Method / URL**: `GET /api/v1/skills`
- **Auth**: Authenticated
- **Query Params**: `category` (optional), `is_verified` (optional boolean)
- **Response (200 OK)**:
  ```json
  {
    "skills": [
      {
        "skill_id": "python",
        "name": "Python",
        "category": "language",
        "confidence_score": 0.85,
        "proficiency_tier": "proficient",
        "is_verified": true,
        "primary_source": "assessment",
        "last_evidence_at": "2026-10-07T12:00:00Z"
      },
      {
        "skill_id": "fastapi",
        "name": "FastAPI",
        "category": "framework",
        "confidence_score": 0.65,
        "proficiency_tier": "demonstrated",
        "is_verified": false,
        "primary_source": "project_evidence",
        "last_evidence_at": "2026-10-06T15:30:00Z"
      }
    ]
  }
  ```

#### 4.2 Get Skill-Gap Analysis
- **Method / URL**: `GET /api/v1/skills/gaps`
- **Auth**: Authenticated
- **Query Params**: `role_id` (optional, defaults to user's `primary_role_id`)
- **Response (200 OK)**:
  ```json
  {
    "role_id": "backend-developer",
    "role_title": "Backend Developer",
    "readiness_percentage": 78.5,
    "met_skills": [
      {"skill_id": "python", "name": "Python", "confidence": 0.85},
      {"skill_id": "postgresql", "name": "PostgreSQL", "confidence": 0.80}
    ],
    "developing_skills": [
      {"skill_id": "fastapi", "name": "FastAPI", "confidence": 0.65}
    ],
    "missing_skills": [
      {"skill_id": "redis", "name": "Redis", "importance": "mandatory"},
      {"skill_id": "docker", "name": "Docker", "importance": "preferred"}
    ],
    "explanation_narrative": "Solid Python and relational database foundation. Closing the Redis caching and Docker containerization gaps will raise market alignment above 90%."
  }
  ```

---

### Group 5: Resume Ingestion & Truthful Tailoring (`/api/v1/resumes`)

#### 5.1 Upload Resume
- **Method / URL**: `POST /api/v1/resumes/upload`
- **Auth**: Authenticated
- **Content-Type**: `multipart/form-data`
- **Body**: `file: UploadFile` (PDF or DOCX, $\le 10\text{MB}$)
- **Response (202 Accepted)**:
  ```json
  {
    "resume_id": "r1-uuid",
    "file_name": "Aarav_Mehta_Resume.pdf",
    "file_size_bytes": 142050,
    "status": "parsing",
    "task_id": "task_parse_8f1a",
    "message": "Resume uploaded. Parsing initiated asynchronously."
  }
  ```
- **Errors**: 400 Bad Request (`unsupported file format or > 10MB limit`).

#### 5.2 Get Parsed Extraction Status
- **Method / URL**: `GET /api/v1/resumes/{id}/parsed`
- **Auth**: Authenticated
- **Response (200 OK)**:
  ```json
  {
    "resume_id": "r1-uuid",
    "status": "parsed",
    "extracted_preview": {
      "education": [...],
      "experience": [...],
      "projects": [...],
      "detected_skills": ["Python", "SQL", "Git", "FastAPI"]
    },
    "requires_human_confirmation": true
  }
  ```

#### 5.3 Confirm Extracted Profile (Human Approval Gateway)
- **Method / URL**: `POST /api/v1/resumes/{id}/confirm`
- **Auth**: Authenticated
- **Request Body**:
  ```json
  {
    "approved_data": {
      "education": [...],
      "experience": [...],
      "projects": [...],
      "confirmed_skills": ["python", "sql", "git", "fastapi"]
    }
  }
  ```
- **Response (200 OK)**: Commits verified data to `career_profiles` and creates immutable audit log record.

#### 5.4 Create Tailored Resume Version
- **Method / URL**: `POST /api/v1/resumes/{id}/tailor`
- **Auth**: Authenticated
- **Header**: `Idempotency-Key: <UUID>` (Optional)
- **Request Body**:
  ```json
  {
    "job_id": "j1-uuid",
    "target_emphasis": ["asynchronous API design", "caching"]
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "tailored_version_id": "tv1-uuid",
    "job_id": "j1-uuid",
    "status": "draft",
    "anti_hallucination_verified": true,
    "diff_summary": {
      "additions_count": 4,
      "rephrasings_count": 6,
      "deletions_count": 2
    },
    "message": "Draft tailored version generated with zero hallucinations. Review required."
  }
  ```

#### 5.5 Get Visual Diff
- **Method / URL**: `GET /api/v1/resumes/versions/{version_id}/diff`
- **Auth**: Authenticated
- **Response (200 OK)**: Returns side-by-side structured diff with additions, deletions, and phrasing updates.

#### 5.6 Approve Tailored Version (Human Approval Gateway)
- **Method / URL**: `POST /api/v1/resumes/versions/{version_id}/approve`
- **Auth**: Authenticated
- **Request Body**:
  ```json
  {
    "accepted_sections": ["summary", "experience", "projects"],
    "user_edited_content": null
  }
  ```
- **Response (200 OK)**: Marks `resume_versions.status = 'approved'` and creates immutable audit log.

#### 5.7 Export Tailored Resume
- **Method / URL**: `GET /api/v1/resumes/versions/{version_id}/export?format=pdf`
- **Auth**: Authenticated
- **Query Params**: `format` (`pdf` or `markdown`)
- **Response (200 OK)**: Streams compiled PDF document with `Content-Disposition: attachment; filename="tailored_resume.pdf"`.

---

### Group 6: Objective Diagnostic Assessments (`/api/v1/assessments`)

#### 6.1 List Available Assessments
- **Method / URL**: `GET /api/v1/assessments`
- **Auth**: Authenticated
- **Query Params**: `skill_id` (optional)
- **Response (200 OK)**:
  ```json
  {
    "assessments": [
      {
        "id": "a1-uuid",
        "skill_id": "python",
        "skill_name": "Python",
        "title": "Python Backend Diagnostics",
        "time_limit_minutes": 15,
        "passing_threshold": 75.0,
        "questions_count": 10
      }
    ]
  }
  ```

#### 6.2 Start Assessment Attempt
- **Method / URL**: `POST /api/v1/assessments/{id}/start`
- **Auth**: Authenticated
- **Response (201 Created)**:
  ```json
  {
    "attempt_id": "att1-uuid",
    "assessment_id": "a1-uuid",
    "time_limit_minutes": 15,
    "expires_at": "2026-10-07T14:15:00Z",
    "questions": [
      {
        "id": "q1-uuid",
        "prompt_text": "What is the GIL behavior in Python 3.11 when handling CPU-bound asyncio tasks?",
        "code_snippet": null,
        "options": [
          "asyncio bypasses the GIL entirely",
          "asyncio runs cooperatively on a single thread and remains constrained by the GIL",
          "asyncio spawns separate OS processes per coroutine",
          "asyncio converts coroutines to kernel threads"
        ]
      }
    ]
  }
  ```
- **Security**: The correct answer is stripped from this response payload.

#### 6.3 Submit Assessment Answers
- **Method / URL**: `POST /api/v1/assessments/attempts/{attempt_id}/answers`
- **Auth**: Authenticated
- **Request Body**:
  ```json
  {
    "responses": [
      {"question_id": "q1-uuid", "selected_option_index": 1, "response_time_seconds": 18}
    ]
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "attempt_id": "att1-uuid",
    "score_percentage": 85.0,
    "passed": true,
    "new_skill_confidence": 0.85,
    "proficiency_tier": "proficient",
    "strengths_summary": "Demonstrated deep mastery of asyncio scheduling and concurrency primitives.",
    "weaknesses_summary": "Review memory management and reference counting nuances.",
    "career_readiness_lift": "+4%"
  }
  ```

---

### Group 7: Dynamic Personalized Roadmaps (`/api/v1/roadmap`)

#### 7.1 Get Active Roadmap
- **Method / URL**: `GET /api/v1/roadmap`
- **Auth**: Authenticated
- **Response (200 OK)**:
  ```json
  {
    "roadmap_id": "rm1-uuid",
    "target_role": "Backend Developer",
    "total_tasks": 12,
    "completed_tasks": 5,
    "completion_percentage": 41.6,
    "phases": [
      {
        "id": "phase1-uuid",
        "title": "Phase 1: In-Memory Caching & Distributed State",
        "order_index": 1,
        "tasks": [
          {
            "id": "task1-uuid",
            "skill_id": "redis",
            "title": "Implement Redis Sliding-Window Rate Limiting in FastAPI",
            "estimated_hours": 6,
            "status": "completed",
            "submission_url": "https://github.com/user/redis-rate-limiter"
          }
        ]
      }
    ]
  }
  ```

#### 7.2 Complete Roadmap Task
- **Method / URL**: `POST /api/v1/roadmap/tasks/{task_id}/complete`
- **Auth**: Authenticated
- **Request Body**:
  ```json
  {
    "submission_url": "https://github.com/user/redis-rate-limiter",
    "notes": "Verified sub-10ms rate limiter checks using Redis ZSETs."
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "task_id": "task1-uuid",
    "status": "completed",
    "overall_completion_percentage": 50.0,
    "readiness_lift": "+3%"
  }
  ```

#### 7.3 Request Roadmap Regeneration
- **Method / URL**: `POST /api/v1/roadmap/regenerate`
- **Auth**: Authenticated
- **Response (202 Accepted)**: Synthesizes updated roadmap aligned with newly verified skills and target roles.

---

### Group 8: Job Market Discovery & Matching (`/api/v1/jobs`)

#### 8.1 Search & Filter Jobs
- **Method / URL**: `GET /api/v1/jobs`
- **Auth**: Authenticated
- **Query Params**: `query`, `role_id`, `remote_type`, `min_score`, `page`, `page_size`
- **Response (200 OK)**:
  ```json
  {
    "data": [
      {
        "job_id": "j1-uuid",
        "title": "Junior Backend Engineer",
        "company_name": "Datastream Inc.",
        "location": "San Francisco, CA",
        "remote_type": "hybrid",
        "min_salary": 95000,
        "max_salary": 115000,
        "overall_match_score": 86.0,
        "posted_at": "2026-10-05T09:00:00Z"
      }
    ],
    "pagination": { ... }
  }
  ```

#### 8.2 Get Job Match Explainability Drawer
- **Method / URL**: `GET /api/v1/jobs/{id}/match-explanation`
- **Auth**: Authenticated
- **Response (200 OK)**:
  ```json
  {
    "job_id": "j1-uuid",
    "overall_score": 86.0,
    "breakdown": {
      "skill_score": 88.0,
      "experience_score": 80.0,
      "vector_semantic_score": 89.0
    },
    "matched_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
    "missing_skills": ["Redis"],
    "hiring_rationale": "High fit: Candidate verified Python and REST architecture meets primary hiring criteria. Acquiring Redis knowledge will boost score to 94%."
  }
  ```

---

### Group 9: Application Pipeline Tracker (`/api/v1/applications`)

#### 9.1 Save Job to Tracker
- **Method / URL**: `POST /api/v1/applications/save`
- **Auth**: Authenticated
- **Request Body**: `{"job_id": "j1-uuid"}`
- **Response (201 Created)**: Returns tracked application record with status `'saved'`.

#### 9.2 Prepare Application Checklist
- **Method / URL**: `GET /api/v1/applications/{id}/prepare`
- **Auth**: Authenticated
- **Response (200 OK)**:
  ```json
  {
    "application_id": "app1-uuid",
    "job_title": "Junior Backend Engineer",
    "company_name": "Datastream Inc.",
    "tailored_resume_available": true,
    "tailored_resume_id": "tv1-uuid",
    "external_application_url": "https://datastream.jobs/apply/123",
    "checklist": [
      {"item": "Review tailored resume diff", "completed": true},
      {"item": "Copy cover note", "completed": true},
      {"item": "Submit on company portal", "completed": false}
    ]
  }
  ```

#### 9.3 Update Application Status (Human Approval Gateway)
- **Method / URL**: `PUT /api/v1/applications/{id}/status`
- **Auth**: Authenticated
- **Request Body**:
  ```json
  {
    "new_status": "applied",
    "notes": "Applied via company greenhouse portal."
  }
  ```
- **Response (200 OK)**: Updates status, logs entry in `application_status_history` and `action_audits`.

---

### Group 10: Recruiter Networking & Message Drafting (`/api/v1/recruiters`)

#### 10.1 List Relevant Recruiters
- **Method / URL**: `GET /api/v1/recruiters`
- **Auth**: Authenticated
- **Query Params**: `company_name`, `page`, `page_size`
- **Response (200 OK)**: Returns list of public recruiter profiles matching target companies.

#### 10.2 Generate Outreach Message Draft
- **Method / URL**: `POST /api/v1/recruiters/{id}/draft-message`
- **Auth**: Authenticated
- **Request Body**:
  ```json
  {
    "application_id": "app1-uuid",
    "intent": "introduction"
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "message_id": "msg1-uuid",
    "recipient_name": "Sarah Jenkins",
    "subject_line": "Aarav Mehta - Passion for Backend Engineering at Datastream",
    "message_body": "Hi Sarah,\n\nI recently applied to the Junior Backend Engineer opening at Datastream. I noticed your team's focus on high-throughput microservices—my recent project benchmarked FastAPI caching pipelines with sub-50ms latency. I'd love to connect!\n\nBest,\nAarav",
    "status": "draft"
  }
  ```

#### 10.3 Log Manual Message Copy (Human Approval Gateway)
- **Method / URL**: `POST /api/v1/recruiters/messages/{message_id}/approve-dispatch`
- **Auth**: Authenticated
- **Response (200 OK)**: Marks `status = 'copied_manually'`, records timestamp, logs action in audit trail. **System never transmits unsolicited messages automatically.**

---

### Group 11: Interview Preparation (`/api/v1/interviews`)

#### 11.1 List / Create Scheduled Interviews
- `GET /api/v1/interviews`: List scheduled interviews with countdowns.
- `POST /api/v1/interviews`: Schedule interview (`201 Created` with `application_id`, `round_type`, `scheduled_at`).

#### 11.2 Get Gap-Targeted Practice Questions
- **Method / URL**: `GET /api/v1/interviews/{id}/questions`
- **Auth**: Authenticated
- **Response (200 OK)**:
  ```json
  {
    "interview_id": "int1-uuid",
    "questions": [
      {
        "question_id": "iq1-uuid",
        "category": "system_design",
        "question_text": "Design a distributed caching layer for real-time order processing.",
        "talking_points_framework": "1. Clarify throughput (RPS). 2. Cache invalidation strategies (Write-through vs Write-back). 3. Fallback mechanisms during Redis node partitions.",
        "candidate_project_anchors": ["Reference your E-Commerce Microservices project to substantiate experience."]
      }
    ]
  }
  ```

#### 11.3 Log Question Practice Drill
- **Method / URL**: `POST /api/v1/interviews/practice-log`
- **Auth**: Authenticated
- **Request Body**: `{"question_id": "iq1-uuid", "notes": "Practiced STAR story on cache invalidation", "is_reviewed": true}`
- **Response (200 OK)**: Increments interview preparation factor in Career Readiness score.

---

### Group 12: Career Readiness Intelligence (`/api/v1/readiness`)

#### 12.1 Get Current Readiness Score
- **Method / URL**: `GET /api/v1/readiness`
- **Auth**: Authenticated
- **Response (200 OK)**:
  ```json
  {
    "overall_score": 78.5,
    "status_tier": "Market Ready",
    "factors": {
      "profile_completeness": 85.0,
      "skill_proficiency": 80.0,
      "roadmap_progress": 72.0,
      "application_velocity": 75.0
    },
    "recommendations": [
      {"action": "Complete Docker Assessment", "lift": "+4 pts", "type": "assessment"},
      {"action": "Add 2 target applications this week", "lift": "+3 pts", "type": "application"}
    ]
  }
  ```

#### 12.2 Get 30-Day Historical Trend
- **Method / URL**: `GET /api/v1/readiness/history`
- **Auth**: Authenticated
- **Response (200 OK)**: Array of `{recorded_date, overall_score, factors}` representing 30-day velocity trajectory.

---

### Group 13: Command Center Dashboard (`/api/v1/dashboard`)

#### 13.1 Get Unified Dashboard Summary
- **Method / URL**: `GET /api/v1/dashboard/summary`
- **Auth**: Authenticated
- **Response (200 OK)**: Aggregates readiness score, top 3 matched jobs, active milestone task, upcoming interviews, and recent activity feed in a single sub-100ms query.

---

### Group 14: Settings & Data Privacy (`/api/v1/settings`)

#### 14.1 Update User Settings
- **Method / URL**: `PATCH /api/v1/settings`
- **Auth**: Authenticated
- **Request Body**: `{"notification_email_digest": true, "theme": "system"}`
- **Response (200 OK)**: Returns updated user settings.

#### 14.2 Export User Data (GDPR Portability)
- **Method / URL**: `POST /api/v1/settings/privacy/export`
- **Auth**: Authenticated
- **Response (200 OK)**: Compiles complete JSON archive of all candidate records across all 37 database tables.

#### 14.3 Permanent Account Deletion (Right to be Forgotten)
- **Method / URL**: `POST /api/v1/settings/privacy/delete-account`
- **Auth**: Authenticated
- **Request Body**: `{"confirmation": "DELETE", "password": "Password123!"}`
- **Response (200 OK)**: Executes atomic cascading delete across all database tables, vector embeddings, and object storage files; terminates active sessions.

---

## 3. Contradiction Analysis & Resolution

| Area | Potential Conflict | Architecture Resolution |
| :--- | :--- | :--- |
| **Resume Extraction vs Career Profile** | If resume parsing automatically wrote to the user's career profile, it would violate Rule 11 (strict user confirmation). | **Resolved**: Parsing produces a draft state (`status = 'parsed'`). No records are written to `career_profiles` or `user_skills` until the user calls `POST /api/v1/resumes/{id}/confirm`. |
| **Tailored Resume Versions** | Should tailoring alter the master resume? | **Resolved**: The master resume in `resumes` is immutable. Tailoring creates a new child record in `resume_versions` tied to the specific `job_id`, preserving full historical versions and visual diffs. |
| **Application & Recruiter Actions** | Risk of automated bot behavior violating Rule 14 (no blind auto-applications). | **Resolved**: Endpoints only prepare and log actions (`prepare`, `approve-dispatch`). Transmission is purely client-assisted with explicit user review and authorization. |

---

## 4. API Contract Sign-Off

This contract defines the complete, authoritative REST API for CoachPath. Implementation will be executed in FastAPI using strictly typed Pydantic v2 schemas mirroring the specifications above.
