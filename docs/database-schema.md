# Database Schema Specification

> **Document Status**: Placeholder / Phase 0 Initialization  
> **Owner**: Lead Software Architect & Backend Engineering  
> **Last Updated**: Phase 0 Kickoff

---

## 1. Storage Architecture Overview
- **Primary Relational Store**: PostgreSQL 16+
- **Vector Extension**: `pgvector` for embedding storage, indexing (HNSW / IVFFlat), and cosine similarity search.
- **Cache & Ephemeral Store**: Redis for token blacklisting, session state, rate-limiting, and short-term job locks.

## 2. Core Entities & Domain Boundaries (To be detailed in Phase 0)

### 2.1 Identity & Authentication
- `users`: Core account identity, authentication credentials, security timestamps, role.
- `user_sessions` / `refresh_tokens`: Token management and device revocation.

### 2.2 Career Profile & Evidence
- `career_profiles`: Central continuously updated career representation.
- `work_experiences`: Verified/user-confirmed employment history.
- `education_records`: Academic background, degrees, certifications.
- `projects`: Concrete project experience and achievements.
- `skills`: Master taxonomy of skills.
- `profile_skills`: User skills with evidence links, confidence scores, and verification source.
- `skill_assessments` & `assessment_attempts`: Assessments taken, responses, and score breakdowns.

### 2.3 Roadmaps & Learning Plans
- `roadmaps`: Personalized milestone-based learning plans tied to target roles.
- `roadmap_milestones`: Discrete learning tasks, recommended resources, and completion statuses.

### 2.4 Jobs & Matching Engine
- `job_postings`: Ingested job listings, standardized metadata, requirements, and embeddings.
- `job_matches`: Calculated match scores, vector similarities, gap breakdowns, and explanation payloads.
- `job_applications`: Application tracker states (saved, applied, interview, offer, rejected), dates, and notes.

### 2.5 Resumes & Tailoring
- `resumes`: Original parsed documents, structured versions, and tailored variants.
- `tailored_resume_revisions`: Tailored drafts tied to specific job postings with audit diffs.

### 2.6 Audit & Action Logs
- `action_audits`: Immutable ledger of user approval events, system actions, and external interactions.

## 3. Migration & Versioning Strategy
- Database migrations managed via Alembic.
- Strict foreign keys, indexing strategies, and data retention policies.
