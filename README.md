# CoachPath 🚀
### AI-Powered Career Intelligence & Job Application Assistant
*Build for Bharat Hackathon 2.0*

> **"Automate the busywork. Never the decision."**

CoachPath is an end-to-end career intelligence copilot designed specifically for Indian engineering students and job seekers (especially from Tier-2 and Tier-3 colleges). It unifies the entire career journey from onboarding to placement readiness into a reactive, truthful, and human-gated workflow.

---

## 🌟 Key Features Across All 13 Roadmap Screens

1. **Personalized Onboarding (P0)**: 11-step conversational profile builder with live sidebar extraction and quick-reply chips.
2. **Multi-Dimension Skill Assessment (P0)**: Live Python & SQL tests scored across 4 dimensions: *Knowledge, Problem Solving, Practical Skills, and Industry Readiness*.
3. **Skill Gap Analysis & Live Roadmap (P0)**: Constrained by weekly study hours (e.g. 20 hrs/week) and sequenced by dependencies, mapping high-quality free Indian resources (*NPTEL, SWAYAM, freeCodeCamp, CS50, Striver Sheet*).
4. **Market Intelligence (P1)**: Real-time skill demand frequency charts, emerging technology chips (*RAG, FastAPI, PyTorch 2.x*), and gap pipeline funnel.
5. **Transparent Job Matching (P0)**: 7-factor explainable scoring (40% Skills, 15% Semantic, 15% Experience, 10% Projects, 10% Location, 5% Salary, 5% Education) with reasons and checkmark breakdowns.
6. **Truthful Resume Studio (P0)**: Role-tailored variants (*ML Engineer, Data Scientist, AI Engineer*) with ATS scoring, side-by-side diff view (*reworded vs reordered*), and a strict **100% Truthfulness Guarantee** that prevents AI hallucinations.
7. **Application Assistance & Human Approval Gate (P1)**: Prepares tailored cover note and interview screening answers; enforces human approval before opening the official verified apply link.
8. **Recruiter Cold Outreach (P1)**: Drafts high-converting, personalized cold messages under 90 words with a 3-draft anti-spam rate limiter.
9. **Application Tracker (P0)**: Comprehensive pipeline (*Saved → Applied → Recruiter Contacted → Interview → Offer*), stat cards, 5-day follow-up alerts, and CSV export.
10. **Interview Prep & Calendar Sync (P1)**: "Interview in 3 days" countdown, personalized prep checklist, mock questions, and RFC 5545 `.ics` calendar generation with 3-day, 1-day, and 1-hour alarms.
11. **Career Readiness Dashboard (P0)**: 7-component readiness index with a mathematical **"Biggest Lever"** card calculating exact sensitivity gains (e.g. *70% → 75%*).
12. **Responsible AI & Privacy (P0)**: Real-time audit log, "Export My Data" (JSON), and user-controlled "Delete My Data" button.
13. **Bharat-Specific Edge**: INR ₹ LPA salaries, Indian tech hubs, curated Indian free educational platforms, and an **English / हिन्दी (Hindi)** UI toggle.

---

## 🏗️ System Architecture & Reactive Engine

```
Onboarding → Assessment → Skill Gap → Dynamic Roadmap
     ↓            ↓            ↓             ↓
[───────────── Central Candidate Profile ─────────────]
     ↓            ↓            ↓             ↓
Job Matching → Resume Studio → Approval Gate → Application Tracker
     ↓                                               ↓
Interview Prep (.ics) ←── Career Readiness & Biggest Lever
```

Whenever a skill assessment is taken or profile constraints change, CoachPath invokes `recompute_everything(user_id)`, reactively re-sequencing the roadmap, re-ranking all jobs, and updating career readiness in real time!

---

## ⚡ Quick Start (Instant Live Demo)

### 1. Run the Unified Server & Interactive Web UI
CoachPath comes with a zero-dependency local runner that initializes the database, seeds demo data, and serves the web interface immediately:

```bash
# 1. Seed demo data (Aarav Sharma persona + realistic jobs)
python3 backend/scripts/seed.py

# 2. Start unified server
python3 server.py
```
Open **[http://localhost:8000/index.html](http://localhost:8000/index.html)** in your browser!

### 2. Run the Automated Test Suite
Verify that the 7-factor matching math, readiness sensitivity, truthfulness checker, and roadmap scheduling pass all tests:

```bash
python3 -m unittest discover -s backend/tests
```

### 3. Production FastAPI & Next.js Stack
```bash
# Backend (FastAPI + Uvicorn)
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --port 8000

# Frontend (Next.js 14 App Router)
cd frontend
npm install
npm run dev
```

---

## 📂 Repository Layout

```
Coach_Path/
├── README.md                  # Project overview & documentation
├── server.py                  # Single-command unified server launcher
├── docker-compose.yml         # Container configuration (Postgres/pgvector + FastAPI + Next.js)
├── .env.example               # Environment variables template
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI main app & router mounts
│   │   ├── local_server.py    # Zero-dependency local runner & static server
│   │   ├── core/              # Config, SQLite/Postgres DB layer, Auth, Audit logging
│   │   ├── ai/                # LLM client (Gemini/Claude), schemas, truthfulness checker, prompts
│   │   ├── routers/           # 13 REST API feature modules
│   │   ├── services/          # Matching, gap, roadmap, readiness, ics, skills extraction
│   │   └── data/              # Taxonomy JSON, role requirements, free resources, seed dataset
│   ├── scripts/               # seed.py, prefetch_jobs.py
│   └── tests/                 # Unit tests (matching, readiness, truthfulness, roadmap)
├── frontend/                  # Next.js 14 App Router project (Tailwind, TypeScript, Recharts)
├── web/                       # Standalone zero-dependency interactive Single Page App
└── docs/
    ├── schema.sql             # Supabase PostgreSQL schema with pgvector & RLS
    ├── architecture.md        # Mermaid diagrams & system architecture
    ├── scoring.md             # Transparent mathematical formulas
    ├── demo-script.md         # 3-5 minute live hackathon pitch script
    └── pitch-deck-notes.md    # Talking points & Bharat Hackathon positioning
```

---

## 🛡️ Responsible AI & Compliance

- **No Scraping**: Uses official APIs and permitted job feeds only.
- **Human In The Loop**: Both job applications and recruiter outreach hold at strict human approval gates.
- **Truthfulness Guardrail**: Dual-pass validation ensures zero hallucination on tailored resumes.
- **Data Sovereignty**: Complete data export and instant permanent deletion.
