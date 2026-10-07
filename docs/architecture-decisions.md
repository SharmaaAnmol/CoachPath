# Architecture Decision Records (ADR) Log

> **Document Version**: 1.0.0  
> **Lifecycle Phase**: Phase 0 — Inception & Architecture  
> **Status**: Active Reference Document  
> **Owner**: Lead Software Architect  

---

## 1. Overview
This log documents all foundational architectural decisions, technical choices, trade-offs, and rationale for CoachPath. Each decision is maintained using standard ADR formatting (*Context*, *Decision*, *Consequences*, *Status*).

---

## 2. Decision Index

- **ADR-001**: Technology Stack Selection (Next.js + FastAPI + PostgreSQL + pgvector + Redis)
- **ADR-002**: Vector Storage Strategy (pgvector vs. Dedicated Vector DB)
- **ADR-003**: LLM Integration & Structured Output Paradigm (Pydantic v2 + Instructor)
- **ADR-004**: Anti-Hallucination & Truthfulness Verification in Resume Optimization
- **ADR-005**: Consequential Action Approval Architecture (Human-in-the-Loop Gateway)
- **ADR-006**: Asynchronous Signal Propagation & Optimistic Event Bus in UX State
- **ADR-007**: Two-Stage Visual Diff Approval Pattern for Generated Artifacts
- **ADR-008**: Hybrid Progressive Profiling (Conversational + Structured Ingestion)

---

## 3. Architecture Decision Records

### ADR-001: Technology Stack Selection
- **Status**: Accepted
- **Context**: CoachPath requires high developer velocity, strict end-to-end type safety, modern reactive UI for complex diff and dashboard interfaces, asynchronous handling for AI workloads, and deep integration with Python's rich data and AI ecosystem.
- **Decision**:
  - **Frontend**: Next.js (React 18/19, TypeScript, Tailwind CSS, Lucide icons, TanStack Query).
  - **Backend**: Python 3.11+ with FastAPI, Pydantic v2, and asyncpg.
  - **Relational Data**: PostgreSQL 16+.
  - **Vector Storage**: `pgvector` extension within PostgreSQL.
  - **Cache & Queue**: Redis 7+ for caching, rate limiting, and async job queuing.
- **Consequences**:
  - Two distinct runtimes (Node.js for frontend, Python for backend) requiring clear API contracts (OpenAPI).
  - Unlocks first-class Python AI libraries (LangChain/LlamaIndex primitives, Instructor, PyPDF) while maintaining premier frontend performance.

---

### ADR-002: Vector Storage Strategy (pgvector vs Dedicated Vector DB)
- **Status**: Accepted
- **Context**: CoachPath matches candidate profile embeddings against job postings and taxonomy skills. We must decide between an integrated solution (PostgreSQL `pgvector`) versus a standalone vector database (Pinecone, Qdrant, Milvus).
- **Decision**: Adopt PostgreSQL with the `pgvector` extension utilizing HNSW (Hierarchical Navigable Small World) indexing for vector embeddings (1536 dimensions).
- **Consequences**:
  - Drastically simplifies operations: relational career graph, user data, and vector embeddings reside in a single database with unified transactions and ACID guarantees.
  - Simplifies atomic user data deletion (GDPR/privacy requirement): deleting a user cascades to their vector embeddings automatically.
  - For target scale ($\le 500,000$ job postings and candidate profiles), `pgvector` HNSW indexes provide sub-50ms query latency, matching dedicated vector engines without extra infrastructure costs.

---

### ADR-003: LLM Integration & Structured Output Paradigm
- **Status**: Accepted
- **Context**: Generative LLMs are prone to schema drift, markdown wrapping errors, and unstructured outputs that crash API boundaries. CoachPath requires rigid JSON schema adherence for resumes, assessments, roadmaps, and match breakdowns.
- **Decision**: Enforce structured outputs through **Pydantic v2** models combined with provider-native JSON Schema enforcement (`response_format={"type": "json_object"}` or OpenAI/Anthropic Tool Calling with Instructor).
- **Consequences**:
  - Zero manual regex parsing of LLM outputs.
  - Automatic runtime validation and descriptive validation errors on schema violations.
  - Vendor-agnostic model adapters: swapping between OpenAI, Anthropic, Gemini, or local models requires only adapter remapping without altering domain logic.

---

### ADR-004: Anti-Hallucination & Truthfulness Verification in Resume Optimization
- **Status**: Accepted
- **Context**: LLMs tend to invent accomplishments, degrees, companies, and metrics when instructed to "tailor" or "optimize" resumes. Fabricating credentials violates CoachPath's core ethics and puts candidates at legal/reputational risk.
- **Decision**: Implement a **Two-Pass Grounded Generation Pipeline**:
  1. *Constrained Generation Pass*: The prompt is strictly restricted to the user's verified career profile facts. Explicit instructions forbid inventing new facts.
  2. *Automated Factual Verification Pass*: A secondary deterministic/LLM auditor compares every claim, entity (employer, degree, technology), and metric in the generated draft against the ground-truth profile. Any ungrounded claim is flagged, highlighted, and blocked from automatic adoption.
- **Consequences**:
  - Adds ~2–3 seconds of processing time per tailoring generation.
  - Completely eliminates ungrounded hallucinations, guaranteeing that every resume revision remains 100% truthful.

---

### ADR-005: Consequential Action Approval Architecture
- **Status**: Accepted
- **Context**: In an AI career platform, actions like submitting an application, contacting a recruiter, or modifying verified credentials carry significant real-world consequences. Unchecked autonomous agents risk spamming recruiters or submitting flawed applications.
- **Decision**: Establish an immutable **Human Approval Gateway** interceptor pattern. Every consequential action must pass through:
  $$\text{AI Prepares} \longrightarrow \text{User Reviews \& Diffs} \longrightarrow \text{User Authorizes} \longrightarrow \text{System Executes} \longrightarrow \text{Audit Logged}$$
- **Consequences**:
  - Full transparency and candidate control.
  - Protects platform reputation by strictly eliminating mass unsolicited messaging or automated bot applications.
  - Every authorization writes an immutable audit record to `action_audits`.

---

### ADR-006: Asynchronous Signal Propagation & Optimistic Event Bus in UX State
- **Status**: Accepted
- **Context**: When a candidate completes an assessment, multiple downstream intelligence components must be recalculated: Skill Confidence $\to$ Skill Gap $\to$ Roadmap Milestones $\to$ Job Match Scores $\to$ Career Readiness Index. Performing these recalculations synchronously inside the assessment submission request would cause latency spikes ($> 10\text{s}$) and frozen UI states.
- **Decision**: 
  - Assessment submission immediately grades answers, updates `profile_skills` locally, and responds to the client in $\le 500\text{ms}$.
  - A background event worker asynchronously triggers downstream recalculation tasks.
  - The frontend employs **TanStack Query optimistic cache updates** to instantly reflect the new skill badge, while background polling/WebSocket notifies the client when global readiness scores finish recalibration.
- **Consequences**:
  - Instantaneous, fluid user feedback.
  - Decouples heavy AI inference from the primary web request cycle.

---

### ADR-007: Two-Stage Visual Diff Approval Pattern for Generated Artifacts
- **Status**: Accepted
- **Context**: When users view AI-optimized resumes or cover notes, traditional "rich text editors" make it difficult to identify what the AI modified, added, or removed. This leads to candidates accidentally adopting changes they did not notice.
- **Decision**: Require a **Two-Stage Visual Diff Interface**:
  - Stage 1: Side-by-side or inline color-coded diff (green for additions, strike-through red for deletions, blue for rephrasing) with granular *"Accept"* / *"Reject"* controls per section.
  - Stage 2: Final full preview of the assembled document with explicit *"Approve & Create Version"* action.
- **Consequences**:
  - Eliminates candidate blind spots.
  - Empowers candidates with line-by-line editorial control over their career presentation.

---

### ADR-008: Hybrid Progressive Profiling (Conversational + Structured Ingestion)
- **Status**: Accepted
- **Context**: Forcing early-career users through lengthy 20-field onboarding forms leads to high drop-off ($\approx 45\%$). Conversely, purely conversational chatbots struggle to capture rigorously structured database entities (precise dates, GPA, nested work experience).
- **Decision**: Adopt a **Hybrid Progressive Profiling Architecture**:
  1. *Primary Fast Path*: Resume PDF/DOCX upload parsed in under 15 seconds into a pre-filled structured confirmation screen.
  2. *Secondary Exploratory Path*: Optional AI Career Conversation for undecided users to discover target role alignment before uploading a resume.
  3. *Zero-Blocker Fallback*: Manual profile editor available at every step.
- **Consequences**:
  - Maximizes onboarding conversion ($\ge 80\%$ target).
  - Accommodates both prepared candidates (with existing resumes) and early students exploring their initial direction.
