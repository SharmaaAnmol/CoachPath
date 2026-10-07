# Architecture Decision Records (ADR) Log

> **Document Status**: Placeholder / Phase 0 Initialization  
> **Owner**: Lead Software Architect  
> **Last Updated**: Phase 0 Kickoff

---

## 1. Overview
This log documents all foundational architectural decisions, technical choices, trade-offs, and rationale for CoachPath. Each significant architectural decision is maintained using standard ADR formatting (Context, Decision, Consequences, Status).

---

## 2. Decision Log Index (To be authored during Phase 0)

### ADR-001: Technology Stack Selection
- **Status**: Proposed
- **Context**: Choosing frontend, backend, and persistence stack that balances developer velocity, AI ecosystem integration, type safety, and production scalability.
- **Decision Preview**: Next.js (TypeScript) + FastAPI (Python) + PostgreSQL (with pgvector) + Redis.

### ADR-002: Vector Storage Strategy (pgvector vs. Dedicated Vector DB)
- **Status**: Proposed
- **Context**: Deciding whether to utilize PostgreSQL `pgvector` or a standalone vector database (e.g., Pinecone, Qdrant).
- **Decision Preview**: PostgreSQL with `pgvector` to ensure relational integrity, simplified transactional backups, and lower operational overhead for initial phases.

### ADR-003: LLM Integration & Structured Output Paradigm
- **Status**: Proposed
- **Context**: Ensuring reliable, type-safe, non-hallucinating outputs from LLMs across parsing, assessment, roadmapping, and tailoring.
- **Decision Preview**: Pydantic-first schema validation using structured outputs with multi-provider abstraction layer.

### ADR-004: Anti-Hallucination & Truthfulness Verification in Resume Optimization
- **Status**: Proposed
- **Context**: Strict product rule prohibiting fabrication of credentials, achievements, or skills.
- **Decision Preview**: Two-pass validation pipeline (generation constrained strictly to candidate profile facts + post-generation factual consistency checker).

### ADR-005: Consequential Action Approval Architecture
- **Status**: Proposed
- **Context**: Enforcing explicit human approval before any external-facing or state-altering actions (e.g. applications, outreach).
- **Decision Preview**: Preparation-Review-Approval-Execution lifecycle with immutable audit ledger.
