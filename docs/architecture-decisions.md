# Architecture Decision Records (ADR) Log

> **Document Version**: 1.0.0  
> **Lifecycle Phase**: Phase 0 — Inception & Architecture  
> **Status**: Active Reference Document  
> **Owner**: Lead Software Architect  

---

## 1. Overview
This log documents all foundational architectural decisions, technical choices, trade-offs, and rationale for CoachPath. In accordance with system architecture governance, every record explicitly specifies the **Decision**, **Reason**, **Alternatives Considered**, and **Tradeoffs**.

---

## 2. Decision Index

- **ADR-001**: Technology Stack Selection (Next.js + FastAPI + PostgreSQL + pgvector + Redis)
- **ADR-002**: Vector Storage Strategy (pgvector with HNSW vs. Dedicated Vector DB)
- **ADR-003**: AI Provider Abstraction Layer & Structured Output Validation
- **ADR-004**: Anti-Hallucination & Factual Consistency Verification in Resume Optimization
- **ADR-005**: Consequential Action Approval Architecture (Human-in-the-Loop Gateway)
- **ADR-006**: Asynchronous Signal Propagation & Event-Driven Profile Recalculation
- **ADR-007**: Two-Stage Visual Diff Approval Pattern for Generated Artifacts
- **ADR-008**: Hybrid Progressive Profiling (Conversational + Structured Ingestion)
- **ADR-009**: Pluggable External Job Data Ingestion Pipeline
- **ADR-010**: Standardized RFC 7807 API Error Handling and Correlation Tracking

---

## 3. Architecture Decision Records

---

### ADR-001: Technology Stack Selection
- **Status**: Accepted
- **Decision**: Select a decoupled stack comprising:
  - **Frontend**: Next.js (React 18/19, TypeScript, Tailwind CSS, TanStack Query)
  - **Backend**: Python 3.11+ with FastAPI, Pydantic v2, and asyncpg
  - **Database & Vectors**: PostgreSQL 16 with the `pgvector` extension
  - **Cache & Message Broker**: Redis 7
- **Reason**: 
  - FastAPI and Python natively support the state-of-the-art AI ecosystem (embeddings, Instructor, PyPDF, tokenizers) while offering asynchronous high-throughput concurrency.
  - Next.js and TypeScript provide industry-standard server-side rendering, type-safe contract consumption, and optimal client-side performance for complex visual diff and Kanban interfaces.
  - PostgreSQL provides rock-solid relational ACID consistency for complex career graphs, while `pgvector` eliminates the architectural sprawl of managing a separate database.
- **Alternatives**:
  1. *Full-Stack TypeScript (Next.js + Node.js/NestJS)*: Lacks mature Python-first AI tooling, necessitating child processes or external microservices for document parsing and embedding pipelines.
  2. *Full-Stack Python (Django / Django REST Framework)*: Heavier monolithic runtime, synchronous ORM bottlenecks, and lacks the modern reactive UX capabilities needed for real-time diff reviewers and dashboards.
- **Tradeoffs**:
  - *Gains*: Optimal alignment of language to domain (TypeScript for UI, Python for AI/Data); massive developer velocity; robust type safety across all tiers.
  - *Costs*: Requires managing two distinct runtimes (Node.js and Python) in local development and production container clusters; necessitates disciplined API contract synchronization (OpenAPI/Pydantic).

---

### ADR-002: Vector Storage Strategy (pgvector with HNSW vs Dedicated Vector DB)
- **Status**: Accepted
- **Decision**: Adopt PostgreSQL with the **`pgvector`** extension utilizing HNSW (Hierarchical Navigable Small World) indexing for vector similarity search, rather than provisioning a standalone vector database.
- **Reason**:
  - CoachPath's career matching requires hybrid queries that join relational filters (e.g., target role, experience stage, location, remote preference) directly with cosine vector similarity.
  - Relational integrity: a single database transaction guarantees that when a job posting is created, updated, or deleted, its vector embedding updates atomically.
  - GDPR and Privacy: user account deletion automatically cascades across all relational rows and vector embeddings in a single atomic transaction.
- **Alternatives**:
  1. *Standalone Vector DB (Pinecone, Qdrant, Milvus)*: Offers specialized vector indexing and filtering.
  2. *Redis with RediSearch Vector Search*: Fast in-memory similarity search.
- **Tradeoffs**:
  - *Gains*: Drastically reduced operational complexity; zero cross-database synchronization lag; unified automated backups and point-in-time recovery (PITR); zero extra hosting costs.
  - *Costs*: Higher RAM footprint on PostgreSQL for HNSW index graphs; at massive scale ($> 10\text{M}$ vectors), dedicated vector engines offer superior distributed horizontal scaling, but CoachPath's initial domain scale ($< 500\text{K}$ vectors) is well within `pgvector`'s sweet spot ($< 50\text{ms}$ latency).

---

### ADR-003: AI Provider Abstraction Layer & Structured Output Validation
- **Status**: Accepted
- **Decision**: Abstract all Generative AI interactions behind a protocol-based interface (`LLMProvider` and `EmbeddingProvider`), enforcing structured outputs strictly via **Pydantic v2 schemas** and provider JSON schema enforcement (Instructor / Tool Calling).
- **Reason**:
  - Eliminates tight vendor lock-in to OpenAI, Anthropic, or Google. Provider adapters can be hot-swapped via configuration without modifying business logic.
  - Eliminates brittle regular-expression parsing of unstructured LLM markdown text.
  - Guarantees type safety: if an LLM returns an invalid JSON payload, the adapter automatically retries with validation feedback or fails gracefully.
- **Alternatives**:
  1. *Direct Vendor SDK Calls in Routers*: Calling `openai.ChatCompletion` directly in API endpoints.
  2. *Heavy AI Monolith Frameworks (LangChain / LlamaIndex full-framework coupling)*: Rapidly shifting APIs, excessive abstractions, and unpredictable dependency churn.
- **Tradeoffs**:
  - *Gains*: Complete model portability; cost and latency optimization by routing simple extraction to fast models (e.g., `gpt-4o-mini`) and deep evaluation to frontier models (`gpt-4o`, `claude-3-5-sonnet`); testability via mock adapters.
  - *Costs*: Initial engineering overhead to author and maintain provider adapter classes and schema models.

---

### ADR-004: Anti-Hallucination & Factual Consistency Verification in Resume Optimization
- **Status**: Accepted
- **Decision**: Enforce a mandatory **Two-Pass Grounded Generation Pipeline** for all resume and profile tailoring:
  1. *Constrained Generation Pass*: The prompt is strictly restricted to the user's verified career profile facts. Explicit system prompts forbid inventing new facts, metrics, or technologies.
  2. *Automated Factual Verification Pass*: A secondary deterministic and semantic auditor validates that every entity (employer, degree, technology, date, quantitative metric) in the generated draft exists in the ground-truth profile before displaying it to the user.
- **Reason**:
  - Preserves platform integrity and candidate protection: ungrounded claims on resumes lead to immediate candidate disqualification during technical interviews and background checks.
  - Non-negotiable product rule: CoachPath must never fabricate credentials, projects, or achievements.
- **Alternatives**:
  1. *Prompt Engineering Alone*: Relying solely on system prompt warnings ("Do not hallucinate"). Empirical testing demonstrates LLMs still occasionally inject unverified technologies to match keywords.
  2. *Manual User Verification Only*: Burdening the candidate with catching subtle hallucinated bullet points in a rich text editor.
- **Tradeoffs**:
  - *Gains*: 100% verifiable truthfulness; defensible, ethical AI branding; candidate confidence.
  - *Costs*: Adds ~2–3 seconds of processing latency per tailoring generation; requires ongoing maintenance of the entity verification heuristic.

---

### ADR-005: Consequential Action Approval Architecture (Human-in-the-Loop Gateway)
- **Status**: Accepted
- **Decision**: Implement an unskippable **Human Approval Gateway** interceptor pattern. Every consequential external or state-altering action must follow:
  $$\text{AI Prepares} \longrightarrow \text{User Reviews \& Diffs} \longrightarrow \text{User Authorizes} \longrightarrow \text{System Executes} \longrightarrow \text{Audit Logged}$$
- **Reason**:
  - Autonomous agents that blindly send recruiter messages or mass-submit job applications trigger anti-spam filters, violate platform terms of service, and harm candidate reputations.
  - Retains human agency: the candidate is the ultimate decision-maker regarding their career presentation and communication.
  - Legal and audit compliance: every consequential action produces an immutable audit record in `action_audits`.
- **Alternatives**:
  1. *Fully Autonomous Bot Agents*: Auto-applying to dozens of jobs overnight without human review.
  2. *Passive Suggestions*: Displaying suggestions in static chat without a structured approval gateway.
- **Tradeoffs**:
  - *Gains*: Zero recruiter spam; zero erroneous job applications; clear audit trail; elevated user trust.
  - *Costs*: Requires building dedicated UI review surfaces (diff reviewers, approval modals) and state-machine approval checks in backend routers.

---

### ADR-006: Asynchronous Signal Propagation & Event-Driven Profile Recalculation
- **Status**: Accepted
- **Decision**: Decouple evidence submission (e.g., submitting an assessment or marking a milestone complete) from downstream global intelligence recalculations (skill gap delta, roadmap milestones, job match scores, career readiness index) using an asynchronous background event queue backed by Redis.
- **Reason**:
  - Synchronous cascading recalculation within a web request causes unacceptable API latency ($> 10\text{s}$) and threatens HTTP timeouts.
  - High responsiveness: the candidate receives an immediate assessment grading response ($\le 500\text{ms}$), while downstream re-computation occurs asynchronously in worker processes.
- **Alternatives**:
  1. *Synchronous Monolithic Execution*: Running all calculations in the HTTP request thread before responding.
  2. *Batch Nightly Recalculation*: Running a cron job every 24 hours to update scores. This destroys the real-time feedback loop where users see their readiness score improve immediately after demonstrating skills.
- **Tradeoffs**:
  - *Gains*: Sub-500ms API response times; decoupled fault tolerance (a failure in job match recalculation does not invalidate the assessment submission); smooth user experience.
  - *Costs*: Requires running background worker processes (ARQ/Celery) and managing optimistic state updates or polling/WebSockets in the frontend.

---

### ADR-007: Two-Stage Visual Diff Approval Pattern for Generated Artifacts
- **Status**: Accepted
- **Decision**: Mandate a **Two-Stage Visual Diff Interface** for all tailored resumes, cover notes, and profile modifications:
  - Stage 1: Side-by-side or inline color-coded diff (green for additions, strike-through red for deletions, blue for rephrasing) with granular per-bullet accept/reject controls.
  - Stage 2: Full preview of the assembled document with an explicit *"Approve & Commit"* action.
- **Reason**:
  - Traditional WYSIWYG text editors conceal changes made by AI, leading users to inadvertently accept phrasing they did not review or do not stand behind.
  - Gives candidates fine-grained editorial authority over every bullet point.
- **Alternatives**:
  1. *Standard Rich Text Editor*: Presenting the generated resume in a standard text area without diff visualization.
  2. *All-or-Nothing Acceptance*: Forcing the candidate to accept the entire AI draft or reject it completely.
- **Tradeoffs**:
  - *Gains*: Full candidate transparency; eliminates accidental adoption of unwanted text; empowers user co-creation.
  - *Costs*: Requires developing a specialized diff component in the frontend using `diff-match-patch`.

---

### ADR-008: Hybrid Progressive Profiling (Conversational + Structured Ingestion)
- **Status**: Accepted
- **Decision**: Adopt a **Hybrid Progressive Profiling Architecture**:
  1. *Fast-Track Path*: Resume upload parsed in under 15 seconds into a pre-filled structured verification screen.
  2. *Exploratory Path*: Optional conversational AI discovery for undecided candidates to explore target roles before uploading a document.
  3. *Zero-Blocker Fallback*: Manual profile editor accessible at all times.
- **Reason**:
  - Lengthy 20-field onboarding forms cause significant user drop-off ($\approx 45\%$).
  - Purely conversational chatbots struggle to extract structured database entities (chronological dates, GPAs, nested experience arrays).
  - Hybrid design accommodates both candidates with ready resumes and early students seeking career direction.
- **Alternatives**:
  1. *Pure Chatbot Onboarding*: Conducting the entire onboarding via a conversational chat assistant.
  2. *Mandatory Manual Multi-Step Wizard*: Forcing all candidates through 15 pages of form inputs before accessing the app.
- **Tradeoffs**:
  - *Gains*: Industry-leading onboarding conversion ($\ge 80\%$ target); high data quality; versatile entry points.
  - *Costs*: Requires maintaining both conversational and document parsing ingestion pathways.

---

### ADR-009: Pluggable External Job Data Ingestion Pipeline
- **Status**: Accepted
- **Decision**: Abstract all external job ingestion behind a standardized **`JobDataSource` interface**, decoupling the core job repository from specific third-party job board APIs, company career pages, and seed datasets.
- **Reason**:
  - External job board APIs change terms of service, rate limits, and pricing frequently.
  - Enables local and staging environments to operate seamlessly using rich offline seed datasets without hitting external paid APIs.
  - Facilitates adding new data providers (e.g., specialized university career boards, company ATS feeds) without altering the matching engine.
- **Alternatives**:
  1. *Direct API Integration*: Hardcoding specific job API requests inside the matching service.
  2. *Live Web Scraping on Demand*: Scraping company career pages during user search requests (brittle, slow, and violates website Terms of Service).
- **Tradeoffs**:
  - *Gains*: Compliance with website terms of service; high testability; resilience against external API outages; unified deduplication and normalization.
  - *Costs*: Requires maintaining an ingestion worker and normalization layer that maps diverse third-party schemas into the canonical `JobPosting` schema.

---

### ADR-010: Standardized RFC 7807 API Error Handling and Correlation Tracking
- **Status**: Accepted
- **Decision**: Adopt the **RFC 7807 Problem Details** standard for all API error responses, paired with a mandatory `x-request-id` correlation header propagated across frontend, API gateway, domain services, and structured logs.
- **Reason**:
  - Inconsistent error envelopes across different endpoints confuse frontend error handling and degrade user experience.
  - Correlation IDs allow immediate tracing of end-user issues through distributed backend logs and AI provider telemetry.
- **Alternatives**:
  1. *FastAPI Default Error Format*: Standard `{ "detail": "..." }` string or list of dicts.
  2. *Custom Ad-Hoc Error Envelopes*: Varying formats per service module.
- **Tradeoffs**:
  - *Gains*: Universal error handling on the frontend (single toast/error interceptor); immediate log traceability; production observability.
  - *Costs*: Requires wrapping all custom HTTPException classes and schema validation handlers in a unified middleware exception handler.
