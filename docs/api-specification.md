# API Specification & Contracts

> **Document Status**: Placeholder / Phase 0 Initialization  
> **Owner**: Lead Software Architect  
> **Last Updated**: Phase 0 Kickoff

---

## 1. API Architecture Principles
- **Style**: RESTful JSON API with OpenAPI 3.1 generation via FastAPI.
- **Prefix**: `/api/v1`
- **Standard Serialization**: Strict Pydantic v2 schemas for all requests and responses.
- **Error Handling**: Standardized error envelope (`{ "error": { "code": "...", "message": "...", "details": [...] } }`).
- **Pagination**: Consistent cursor-based or limit/offset pagination with standard meta headers.

## 2. Core Endpoint Modules (To be defined in Phase 0)

### 2.1 Authentication & User Management (`/api/v1/auth`, `/api/v1/users`)
- Registration, login, token refresh, logout.
- Current user profile fetching and account settings.

### 2.2 Career Profile & Resume Ingestion (`/api/v1/profile`, `/api/v1/resumes`)
- Resume document upload (`multipart/form-data`) and asynchronous parsing status.
- Career profile retrieval, partial updates, and structured verification.

### 2.3 Skill Assessment & Evidence (`/api/v1/assessments`)
- Fetch available assessments for target skill/domain.
- Submit answers, evaluate evidence, and return verified skill updates.

### 2.4 Skill Gap & Roadmap (`/api/v1/roadmap`)
- Trigger gap analysis against target role.
- Fetch active roadmap, mark milestones completed, regenerate/adjust roadmap based on new signals.

### 2.5 Job Search & Matching (`/api/v1/jobs`)
- Search and filter jobs.
- Match score explanation endpoint (`/api/v1/jobs/{id}/match-analysis`).

### 2.6 Resume Tailoring (`/api/v1/resumes/tailor`)
- Generate tailored resume draft against target job description.
- Review diffs, approve draft, and export to PDF/Markdown.

### 2.7 Application Tracker (`/api/v1/applications`)
- CRUD operations for tracking job application stages and metrics.

### 2.8 Readiness & Intelligence Dashboard (`/api/v1/readiness`)
- Aggregate career readiness score, milestone progress, and recommendation summary.

### 2.9 Consequential Actions & Auditing (`/api/v1/actions`)
- Pending approval queue retrieval.
- User approval/rejection submission.
- Audit history.
