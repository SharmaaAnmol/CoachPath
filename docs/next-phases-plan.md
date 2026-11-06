# CoachPath: plan for the remaining phases

Written 6 Nov 2026, after the Look D redesign shipped (PR #6).

## Where we are

| Area | Backend | Frontend |
|---|---|---|
| Auth, profile, onboarding, resume parse | Done | Done |
| Assessments, skill gaps, roadmap | Done | Done |
| Jobs, matching, resume tailoring | Done | Done |
| Application packages and recruiter outreach (11A) | **Done**: 11 + 10 endpoints | **Mock**: `/applications`, `/recruiters` show demo data |
| Pipeline tracker (12) | Tables exist (`applications`, `application_status_history`) | Mock kanban |
| Interview prep (14) | Tables exist, route is a placeholder | Mock |
| Readiness and dashboard API (15) | Placeholders | Mock readiness page; dashboard builds its own view |
| Settings, export, delete (16) | Placeholder | Partial UI |

Live risks:
- Uploaded resumes sit on local disk on Render (`STORAGE_PROVIDER=local`), so every redeploy wipes them.
- AI endpoints have no per-user rate limit, which is a cost risk on the Groq key.

## The path, in order

### Step 0: Make the live app safe (small, do first)
- Switch file storage to the existing R2/S3 adapter so resumes survive redeploys.
- Add a per-user limit on the AI endpoints (onboarding, parse, tailor, prep, outreach).
- Correct the README and landing claims (Redis and pgvector are not used) and the phase numbering.

**Done when:** a resume uploaded before a redeploy still opens after it, and the 11th AI call in a minute gets a clear "slow down" message.

### Phase 11B: Application packages and recruiter outreach, frontend
- Backend is finished, so this is UI only, wired to the real endpoints.
- From a job match: "Prepare application" → AI package (answers, cover note) → edit → approve → hand off → "I submitted it".
- `/recruiters`: real outreach drafts per company → edit (word counter) → approve → copy → "I sent it". Nothing is sent automatically.
- Remove the demo banners and mock data from both pages.

**Done when:** a user goes from a job match to a copied, approved outreach message using only real data.

### Phase 12: Application pipeline tracker
- Backend:
  - stage changes: Saved → Applied → Screening → Interviewing → Offer, plus Rejected and Withdrawn;
  - a history row for every move;
  - "Save job" from the jobs page.
- Frontend: a kanban on `/applications` with drag and drop, a keyboard and button alternative, optimistic moves that revert on error, and a detail panel with the history timeline.

**Done when:** a saved job shows up in Saved, moving it is recorded, and a reload keeps it.

### Phase 14: Interview prep
- Backend:
  - interviews CRUD, linked to an application;
  - a seeded question bank per role and skill;
  - 5 questions per interview, picked from the user's open gaps;
  - AI STAR talking points that only use the user's verified projects;
  - a practice log.
- Frontend: `/interviews` lists upcoming interviews, with a split practice view: question on the left, STAR notes on the right, and "mark practised".

**Done when:** adding an interview gives 5 targeted questions with talking points grounded in the user's own work.

### Phase 15: Readiness and command center
- Backend: one readiness service with the composite score:
  - profile 20%;
  - skills 35%;
  - roadmap 25%;
  - activity 20% (applications, practice).

  It also keeps snapshots for history, serves `GET /readiness`, `/readiness/history` and `/dashboard/summary`, and returns the top 3 next actions.
- Frontend:
  - `/career-readiness` on real data, with a 30-day trend;
  - the dashboard switches to the single summary call, which makes it faster and gives one source of truth.

**Done when:** the readiness number is the same on every page and moves when the user does something.

### Phase 16: Settings, privacy and hardening
- Edit account, change password, download all my data (JSON), delete my account (with confirmation and a cascade).
- Remove PII from logs and finish the AI limits from step 0.

**Done when:** export returns everything about the user, and delete leaves nothing behind.

### Phase 17: QA and AI checks
- One end-to-end test of the whole journey as a new user.
- Checks that tailoring, packages and outreach never invent facts.
- An accessibility pass on the new flows.

### Phase 18: Release
- Keep the backend warm (a paid instance or a ping), add error monitoring, and write a demo script with a seeded demo account.

## Suggested batches
1. Step 0 + Phase 11B: biggest visible win, because the backend is already done.
2. Phase 12.
3. Phase 14.
4. Phase 15.
5. Phases 16 → 18.

Each batch is one branch and one PR, tested before merge.
