# Security and Privacy Architecture

> **Document Status**: Placeholder / Phase 0 Initialization  
> **Owner**: Lead Software Architect & Security Engineering  
> **Last Updated**: Phase 0 Kickoff

---

## 1. Principles & Objectives
- Security and privacy built-in from day zero, not retrofitted.
- Protection of sensitive candidate data (personally identifiable information, resumes, career goals, assessment outcomes).
- Defense-in-depth across transport, application, database, and AI service layers.

## 2. Key Security Areas to Specify in Phase 0

### 2.1 Authentication & Authorization
- Strong password hashing (Argon2id or bcrypt).
- Short-lived JWT access tokens with secure refresh token rotation stored in HttpOnly, SameSite cookies.
- Role-based and resource-ownership access controls (ensuring users can only query their own data).

### 2.2 Data Protection & Privacy
- Encryption in transit (TLS 1.3) and encryption at rest for databases and file storage.
- PII sanitization and masking policies when communicating with third-party LLM providers.
- Data retention, export, and complete user account deletion ("Right to be Forgotten").

### 2.3 Input Validation & Injection Defenses
- Strict schema validation at all API boundaries.
- Safe file parsing for resumes (mitigating PDF/DOCX macro or parsing exploit vectors).
- Prompt injection defenses and strict sanitization of untrusted text ingested from external job boards or resumes.

### 2.4 Human-in-the-Loop & Anti-Abuse Controls
- Mandatory user approval barrier prior to any external interaction (no unsolicited or mass applications/messages).
- Rate-limiting on sensitive endpoints (auth, AI generation, job ingestion).
- Immutable audit logging for security-relevant and approval-gated actions.
