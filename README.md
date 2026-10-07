# CoachPath 🧭

> **Production-Grade AI-Powered Career Intelligence Platform**

CoachPath is an AI-powered personal career intelligence platform that systematically guides university students, recent graduates, and early-career technology professionals from their baseline skills to verifiable job readiness and employment.

---

## 💡 Product Overview

Early-career job seekers face an opaque and disjointed landscape: generic course syllabi fail to match employer hiring criteria, job portals produce endless noisy listings with no gap feedback, resume tools encourage superficial keyword stuffing or untruthful hallucinations, and application tracking is scattered across spreadsheets.

**CoachPath solves this by introducing a single, continuously updated career profile connected to an end-to-end intelligence loop:**
- **Evidence-Based Skills**: Rather than relying on self-reported claims, candidate skills are calibrated through objective, practical scenario assessments.
- **Transparent Skill-Gap Analysis**: Benchmarks candidate capabilities against empirical market requirements for target roles, categorizing skills into Met, Developing, and Missing.
- **Dynamic Personalized Roadmaps**: Generates custom milestone learning plans targeted solely at verified gaps, automatically updating as new competencies are achieved.
- **Semantic Job Matching**: Multi-dimensional matching (skills, experience, and semantic vector similarity) accompanied by human-readable explanations of match fit.
- **Truthful Resume Optimization**: Contextually highlights genuine candidate experience against target roles with an automated anti-hallucination verification engine and visual diff review.
- **Application Tracking & Readiness**: Integrated Kanban tracker tied directly to a composite Career Readiness Index (0–100%) providing clear next actions.

---

## 🔁 Core Product Loop

```mermaid
flowchart TD
    User([User]) --> Profile[Central Career Profile]
    Profile --> Assessment[Objective Skill Assessment]
    Assessment --> Gap[Transparent Skill-Gap Analysis]
    Gap --> Roadmap[Dynamic Personalized Roadmap]
    Roadmap --> Market[Market Intelligence & Jobs]
    Market --> Matching[Semantic Job Matching + Explanations]
    Matching --> Resume[Truthful Resume Optimization]
    Resume --> Approval{Human-in-the-Loop Review}
    Approval --> Tracker[Application Pipeline Tracker]
    Tracker --> Readiness[Career Readiness Score]
    Readiness --> Profile
```

---

## 🏛️ Technology Stack

| Layer | Technology | Key Capabilities |
| :--- | :--- | :--- |
| **Frontend** | **Next.js, React, TypeScript, Tailwind CSS** | Server-side rendering, responsive interface, modern UX, type safety |
| **Backend** | **Python, FastAPI** | Asynchronous execution, high throughput, native AI ecosystem integration |
| **Relational Data** | **PostgreSQL** | ACID transactions, strict relational schemas, user career graph |
| **Vector Storage** | **pgvector** | Relational vector similarity search, unified backup/transactions |
| **Cache & Queue** | **Redis** | Fast token validation, rate-limiting, asynchronous task brokering |
| **AI & LLM Services** | **LLMs, Embeddings, RAG, Pydantic/Instructor** | Structured outputs, semantic search, explainable recommendation scoring |
| **Deployment** | **Docker, Docker Compose** | Reproducible multi-service development and containerized production deployment |

---

## 🎯 Target Initial Roles

For early iterations, CoachPath prioritizes university students and early-career tech professionals across 7 primary paths:

- Software Engineer (Generalist)
- Backend Developer
- Frontend Developer
- Data Analyst
- Data Scientist
- Machine Learning Engineer
- AI Engineer

---

## 🛡️ Responsible AI & Guiding Principles

1. **One Central Career Profile**: All intelligence derives from and feeds back into a single persistent profile.
2. **Evidence-Based Skills**: Skills are calibrated via assessments, projects, and verifiable experience—never self-reported hype.
3. **Transparent Skill-Gap Analysis**: Explains exactly *why* a gap exists and how to close it.
4. **Personalized Roadmaps**: Actionable step-by-step milestones tailored to the user's actual background, not generic lists.
5. **Explainable Job Matching**: Provides clear rationale and missing skill callouts for every matched role.
6. **Truthful Resume Optimization**:
   - 🚫 **Never** fabricate qualifications, education, work experience, projects, or achievements.
   - 🚫 **Never** invent unproven skills.
   - ✅ Restructures, polishes, and highlights existing authentic experience to align with job descriptions.
7. **Human-in-the-Loop Approval Model**:
   - For any consequential action (application submission, outreach, major profile edits):
     $$\text{CoachPath Prepares} \longrightarrow \text{User Reviews} \longrightarrow \text{User Approves} \longrightarrow \text{Action Executes} \longrightarrow \text{Audit Logged}$$
   - Zero spam or blind automated bulk applications.
8. **Privacy & Security First**: End-to-end data protection, PII anonymization, and user data sovereignty.

---

## 📦 Project Structure & Documentation

```
.
├── docs/                             # Architecture & Product Documentation
│   ├── product-requirements.md       # Complete PRD: vision, personas, epics, NFRs, acceptance criteria
│   ├── user-flows.md                 # Detailed step-by-step user journeys (Phase 0)
│   ├── system-architecture.md        # Technical component topology & design (Phase 0)
│   ├── database-schema.md            # PostgreSQL, pgvector & Redis data models (Phase 0)
│   ├── api-specification.md          # REST API contracts & schemas (Phase 0)
│   ├── ai-architecture.md            # LLM pipelines, RAG, guardrails, and scoring (Phase 0)
│   ├── security-and-privacy.md       # Auth, PII handling, and anti-abuse safeguards (Phase 0)
│   ├── testing-strategy.md           # Unit, integration, E2E, and AI evaluation (Phase 0)
│   ├── development-roadmap.md        # Engineering phase breakdown & milestones (Phase 0)
│   └── architecture-decisions.md     # Architecture Decision Records (ADRs) (Phase 0)
├── .env.example                      # Configuration template for local & production
├── .gitignore                        # Global ignore rules for Node, Python, and env
└── README.md                         # Project overview and guidance
```

---

## 🚀 Development Phasing

CoachPath is engineered under a phased methodology:

- [x] **Phase 0.0: Project Inception & Scaffolding** *(Completed)*
- [x] **Phase 0.1: Product Requirements Document (PRD)** *(Completed in [`/docs/product-requirements.md`](docs/product-requirements.md))*
- [ ] **Phase 0.2: Technical Design & Architecture Specifications** *(Next in `/docs`)*
- [ ] **Phase 1: Foundation & Infrastructure Setup**
- [ ] **Phase 2: Career Profile & Skill Ingestion Engine**
- [ ] **Phase 3: Evidence-Based Assessment & Skill Gap Engine**
- [ ] **Phase 4: Dynamic Career Roadmap Engine**
- [ ] **Phase 5: Job Ingestion & Semantic Matching**
- [ ] **Phase 6: Truthful Resume Tailoring & Export**
- [ ] **Phase 7: Application Tracking, Readiness Dashboard & Approval Gateway**
- [ ] **Phase 8: Security Hardening, E2E Testing & Release**

---

## 📄 License

Proprietary — All rights reserved.
