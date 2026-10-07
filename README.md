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
│   ├── architecture-decisions.md     # Architecture Decision Records (ADRs) (Phase 0)
│   ├── phase-0-final-audit.md        # Comprehensive Phase 0 audit report
│   ├── frontend-architecture.md      # Frontend architecture & design system (Phase 1)
│   └── backend-architecture.md       # Backend architecture & data access (Phase 2A)
├── backend/                          # FastAPI / Python 3.13 Backend Workspace
│   ├── app/                          # Core, API routes, DB, models, schemas, services
│   ├── alembic/                      # Async database migrations and versions
│   └── tests/                        # Pytest suite with isolated in-memory testing
├── frontend/                         # Next.js 14 App Router Frontend Workspace
│   ├── src/app/(public)/             # Marketing routes (/, /about, /features, /privacy, /login, /signup)
│   ├── src/app/(app)/                # Authenticated shells (dashboard, profile, skills, roadmap, jobs, etc.)
│   ├── src/components/               # Design system atomic components and layout shell
│   ├── src/lib/mock/                 # Typed candidate mock data store (Aarav Mehta)
│   └── src/types/                    # Strict TypeScript domain interfaces
├── docker-compose.yml                # Docker Compose setup for FastAPI & PostgreSQL with pgvector
├── .env.example                      # Configuration template for local & production
├── .gitignore                        # Global ignore rules for Node, Python, and env
└── README.md                         # Project overview and guidance
```

---

## 💻 Frontend Quickstart Guide (Phase 1)

The CoachPath frontend is built with Next.js 14 (App Router), TypeScript, and Tailwind CSS.

### 1. Prerequisites
- Node.js `v20+` or `v26+`
- npm `v10+`

### 2. Local Setup
```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

Visit [`http://localhost:3000`](http://localhost:3000) in your browser.

---

## ⚙️ Backend Quickstart Guide (Phase 2A)

The CoachPath backend is built with Python 3.13, FastAPI, SQLAlchemy 2.0 (Async), and Alembic.

### 1. Prerequisites
- Python `3.13+`
- PostgreSQL `16+` with `pgvector` extension (or Docker)

### 2. Local Setup & Virtual Environment
```bash
# Navigate to the backend directory
cd backend

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Setup
```bash
# Duplicate template from project root
cp ../.env.example .env
```

### 4. Running Migrations & Seeding
```bash
# Apply migrations to database
alembic upgrade head

# Seed initial canonical benchmark roles and skills taxonomy (development/demo data)
python scripts/seed.py
```

### 5. Running the FastAPI Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- Interactive API Docs: [`http://localhost:8000/api/v1/docs`](http://localhost:8000/api/v1/docs)
- Service Liveness: [`http://localhost:8000/api/v1/health`](http://localhost:8000/api/v1/health)
- Infrastructure Readiness: [`http://localhost:8000/api/v1/ready`](http://localhost:8000/api/v1/ready)

### 6. Running Backend Tests
```bash
pytest -v
# 33 passed in ~1.5s
```

### 7. Running with Docker Compose
```bash
docker compose up -d
```

---

## 🚀 Development Phasing

CoachPath is engineered under a phased methodology:

- [x] **Phase 0: Product Definition & System Architecture** *(Completed — All 10 architecture records finalized)*
- [x] **Phase 1: Frontend Foundation, Design System & Product Shell** *(Completed — Next.js 14, Tailwind, 12 Domain Shells)*
- [x] **Phase 2A: Backend Foundation & Infrastructure Setup** *(Completed — FastAPI, SQLAlchemy 2.0, Alembic, 22 Passing Tests)*
- [x] **Phase 2B: Master PostgreSQL Data Layer Implementation** *(Completed — 37 SQLAlchemy 2.x models, Alembic migration 973e9bef3510, seed script, 33 Passing Tests)*
- [ ] **Phase 3: Authentication & User Profile Graph**
- [ ] **Phase 4: AI Career Onboarding Conversation**
- [ ] **Phase 5: Resume Ingestion & Parsing Engine**
- [ ] **Phase 6: Diagnostic Skill Assessment Engine**
- [ ] **Phase 7: Skill-Gap Analysis Engine**
- [ ] **Phase 8: Dynamic Milestone Roadmap Engine**
- [ ] **Phase 9: Job Feed Ingestion Pipeline**
- [ ] **Phase 10: Intelligent Job Matching Engine**
- [ ] **Phase 11: Truthful Resume Optimization Engine**
- [ ] **Phase 12: Application Pipeline Tracker**
- [ ] **Phase 13: Recruiter Discovery & High-Context Networking**
- [ ] **Phase 14: Role-Specific Interview Preparation Engine**
- [ ] **Phase 15: Composite Career Readiness Engine**
- [ ] **Phase 16: Settings, Privacy Controls & Data Deletion**
- [ ] **Phase 17: Production Observability, Security Hardening & Rate Limiting**
- [ ] **Phase 18: End-to-End System Integration Testing**
- [ ] **Phase 19: Production Cloud Deployment & Launch Readiness**

---

## 📄 License

Proprietary — All rights reserved.

