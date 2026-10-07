# System Architecture

> **Document Status**: Placeholder / Phase 0 Initialization  
> **Owner**: Lead Software Architect  
> **Last Updated**: Phase 0 Kickoff

---

## 1. Architectural Philosophy
- Modular, service-oriented design with clear domain boundaries.
- Continuous signal feedback loop centered on the user career profile.
- Strict separation of core business logic, AI orchestration, and persistence.
- Cloud-ready, containerized deployment topology.

## 2. High-Level Component Topology
- **Client Tier**: Next.js App Router (React, TypeScript, Tailwind CSS).
- **API & Application Tier**: FastAPI (Python), asynchronous event/task handling, structured schema validation (Pydantic v2).
- **Data & Storage Tier**:
  - PostgreSQL (Relational operational data, user profiles, application tracking).
  - pgvector (Vector embeddings for resumes, skills, target roles, and job postings).
  - Redis (Session cache, rate limiting, task queues).
  - Object/File Storage (Secure storage for uploaded resumes and generated artifacts).
- **AI & Intelligence Tier**:
  - Model abstraction layer (LLM provider adapters).
  - RAG & Embedding pipeline.
  - Skill extraction, evaluation, and recommendation engine.

## 3. Core Subsystems
1. Profile & Evidence Engine
2. Assessment & Scoring Service
3. Skill Gap & Roadmap Planner
4. Job Ingestion & Semantic Matcher
5. Resume Optimization Engine (Anti-fabrication constrained)
6. Audit & Human-in-the-Loop Approval Gateway

## 4. Scalability & Resilience Considerations
- Asynchronous task processing for heavy AI inference and document parsing.
- Rate limiting and caching strategies.
- Observability, telemetry, and structured logging.
