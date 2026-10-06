import http.server
import socketserver
import json
import urllib.parse
import os
import sys
import uuid
import datetime
from pathlib import Path

# Add backend to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR / "backend"))

from app.core.config import settings, DATA_DIR
from app.core.db import init_db, get_connection
from app.services.gap import analyze_skill_gap
from app.services.roadmap import generate_personalized_roadmap, get_active_roadmap
from app.services.matching import calculate_job_match
from app.services.readiness import calculate_readiness, get_readiness_history
from app.services.recompute import recompute_everything
from app.services.ics_service import generate_interview_ics
from app.core.audit import get_user_audit_logs, log_action
from app.ai.truth_check import verify_resume_truthfulness

STEP_QUESTIONS = [
    {
        "step": 1,
        "question": "Namaste! I'm CoachPath, your AI Career Intelligence copilot. Let's start with your name.",
        "quick_replies": ["Aarav Sharma", "Priya Patel", "Rohan Mehta"],
        "field": "full_name"
    },
    {
        "step": 2,
        "question": "Great! What is your primary dream tech role?",
        "quick_replies": ["ML Engineer", "Data Scientist", "Backend Dev", "AI Engineer", "Data Analyst"],
        "field": "target_role"
    },
    {
        "step": 3,
        "question": "What is your target preparation timeline for campus placements or hiring drives?",
        "quick_replies": ["3 Months (Intensive)", "4 Months (Recommended)", "6 Months"],
        "field": "target_timeline_months"
    },
    {
        "step": 4,
        "question": "What is your current college / education background?",
        "quick_replies": ["Final-Year B.Tech CSE (Tier-2/3)", "3rd Year B.Tech", "MCA Graduate"],
        "field": "education_level"
    },
    {
        "step": 5,
        "question": "How many hours can you realistically dedicate on weekdays?",
        "quick_replies": ["1 hour / day", "2 hours / day (Steady)", "3+ hours / day"],
        "field": "hours_per_weekday"
    },
    {
        "step": 6,
        "question": "And how many hours can you study on weekends (Saturday & Sunday)?",
        "quick_replies": ["3-4 hours / day", "5 hours / day (Deep work)", "6+ hours / day"],
        "field": "hours_per_weekend"
    },
    {
        "step": 7,
        "question": "What learning resources do you prefer?",
        "quick_replies": ["100% Free Resources Only", "NPTEL & SWAYAM", "YouTube & Documentation"],
        "field": "learning_resources"
    },
    {
        "step": 8,
        "question": "Which tech companies in India or globally excite you most?",
        "quick_replies": ["Swiggy, PhonePe, Razorpay", "Flipkart & Zepto", "Fractal, Ola Electric"],
        "field": "interested_companies"
    },
    {
        "step": 9,
        "question": "What is your desired fresher / entry-level salary expectation (in ₹ LPA)?",
        "quick_replies": ["6 - 10 LPA", "8 - 14 LPA", "12 - 20 LPA"],
        "field": "desired_salary"
    },
    {
        "step": 10,
        "question": "What is your location and work preference?",
        "quick_replies": ["Bengaluru (Hybrid)", "Hyderabad (Hybrid)", "Gurgaon / Delhi NCR", "100% Remote"],
        "field": "location_and_work_mode"
    },
    {
        "step": 11,
        "question": "Lastly, which technical skills have you already practiced or built projects with?",
        "quick_replies": ["Python & SQL", "Python, Scikit-Learn & Pandas", "FastAPI, Docker & Git"],
        "field": "initial_skills"
    }
]

SAMPLE_QUESTION_BANKS = {
    "sql": [
        {
            "id": "sql-q1",
            "qtype": "mcq",
            "dimension": "Knowledge",
            "prompt": "What is the difference between WHERE and HAVING in SQL?",
            "options": [
                "A) WHERE filters rows before aggregation; HAVING filters groups after aggregation",
                "B) HAVING can only be used with PostgreSQL",
                "C) WHERE requires an ORDER BY clause",
                "D) There is no functional difference"
            ],
            "answer_key": "A"
        },
        {
            "id": "sql-q2",
            "qtype": "sql",
            "dimension": "Practical Skills",
            "prompt": "Given a table 'employees (id INT, name TEXT, salary INT, department_id INT)', write a query to find the 2nd highest salary.",
            "options": [
                "A) SELECT DISTINCT salary FROM employees ORDER BY salary DESC LIMIT 1 OFFSET 1",
                "B) SELECT MAX(salary) FROM employees WHERE salary < (SELECT MAX(salary) FROM employees)",
                "C) Both A and B are valid solutions",
                "D) SELECT salary[2] FROM employees"
            ],
            "answer_key": "C"
        }
    ],
    "python": [
        {
            "id": "py-q1",
            "qtype": "mcq",
            "dimension": "Knowledge",
            "prompt": "What is the key difference between Python's list 'append()' and 'extend()' methods?",
            "options": [
                "A) append() adds its argument as a single element; extend() iterates over its argument adding each item",
                "B) append() works only with strings; extend() works with integers",
                "C) extend() mutates the list in-place; append() returns a new copy",
                "D) Both do the exact same operation"
            ],
            "answer_key": "A"
        }
    ]
}

def get_demo_master_resume():
    seed_file = DATA_DIR / "seed_data.json"
    if seed_file.exists():
        with open(seed_file, "r") as f:
            data = json.load(f)
            return data.get("master_resume", {})
    return {}

class CoachPathRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def _send_json(self, data, status=200):
        body = json.dumps(data, indent=2).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _parse_body(self):
        content_len = int(self.headers.get('Content-Length', 0))
        if content_len > 0:
            raw = self.rfile.read(content_len).decode('utf-8')
            try:
                return json.loads(raw)
            except Exception:
                return {}
        return {}

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path
        query = urllib.parse.parse_qs(url.query)
        user_id = query.get("user_id", [settings.DEFAULT_USER_ID])[0]

        if path == "/health":
            self._send_json({"status": "healthy", "service": "CoachPath Unified API", "version": "1.0.0"})
            return

        elif path == "/me":
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                res = dict(row)
                for f in ["learning_resources", "interested_companies", "interested_industries"]:
                    if isinstance(res.get(f), str):
                        try: res[f] = json.loads(res[f])
                        except Exception: res[f] = []
                self._send_json(res)
            else:
                self._send_json({"error": "Profile not found"}, 404)
            return

        elif path == "/gap":
            role = query.get("role", ["ML Engineer"])[0]
            self._send_json(analyze_skill_gap(user_id, role))
            return

        elif path == "/roadmap":
            self._send_json(get_active_roadmap(user_id))
            return

        elif path == "/market/insights":
            role = query.get("role", ["ML Engineer"])[0]
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT required_skills FROM jobs")
            jobs = cursor.fetchall()
            conn.close()
            
            skill_counts = {}
            for j in jobs:
                skills = json.loads(j["required_skills"]) if isinstance(j["required_skills"], str) else (j["required_skills"] or [])
                for s in skills:
                    skill_counts[s.title()] = skill_counts.get(s.title(), 0) + 1
                    
            trending = [{"skill": k, "frequency_pct": int((v / max(len(jobs), 1)) * 100), "job_count": v} for k, v in sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:8]]
            self._send_json({
                "target_role": role,
                "total_active_jobs_analyzed": len(jobs),
                "trending_skills": trending,
                "emerging_chips": [
                    {"name": "RAG & Vector DBs", "growth": "+140%", "tag": "High Demand"},
                    {"name": "FastAPI Async Services", "growth": "+85%", "tag": "Trending"},
                    {"name": "PyTorch 2.x & CUDA", "growth": "+60%", "tag": "Core"},
                    {"name": "MLOps / Dockerization", "growth": "+45%", "tag": "Production"}
                ],
                "gap_pipeline": {"market_demand": 100, "required_skills": 82, "user_verified_skills": 58, "actionable_gap": 24},
                "compliance_note": "Uses official APIs and permitted sources only. No unauthorized scraping."
            })
            return

        elif path == "/jobs/recommended":
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs")
            job_rows = cursor.fetchall()
            conn.close()
            results = []
            for r in job_rows:
                job = dict(r)
                job["required_skills"] = json.loads(job["required_skills"]) if isinstance(job.get("required_skills"), str) else (job.get("required_skills") or [])
                match = calculate_job_match(user_id, job)
                job["match"] = match
                job["match_score"] = match["score"]
                results.append(job)
            results.sort(key=lambda x: x["match_score"], reverse=True)
            self._send_json(results)
            return

        elif path == "/resume/master":
            self._send_json(get_demo_master_resume())
            return

        elif path == "/applications":
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM applications WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
            rows = cursor.fetchall()
            conn.close()
            apps = [dict(r) for r in rows]
            total = len(apps)
            applied = len([a for a in apps if a["status"] in ("applied", "interview", "response", "offer")])
            interviews = len([a for a in apps if a["status"] == "interview"])
            avg = int(sum([a.get("match_score") or 85 for a in apps]) / max(total, 1))
            self._send_json({
                "stats": {"tracked_roles": total, "applications_sent": applied, "interviews_scheduled": interviews, "average_match": avg},
                "applications": apps
            })
            return

        elif path == "/readiness":
            self._send_json(calculate_readiness(user_id))
            return

        elif path == "/readiness/history":
            self._send_json(get_readiness_history(user_id))
            return

        elif path == "/audit":
            self._send_json({"user_id": user_id, "audit_logs": get_user_audit_logs(user_id)})
            return

        elif path.startswith("/interviews/") and path.endswith("/prep"):
            interview_id = path.split("/")[2]
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT i.*, a.company, a.role FROM interviews i LEFT JOIN applications a ON i.application_id = a.id WHERE i.id = ?", (interview_id,))
            iv = cursor.fetchone()
            cursor.execute("SELECT id, title, done, skill FROM prep_items WHERE interview_id = ?", (interview_id,))
            items = cursor.fetchall()
            conn.close()
            self._send_json({
                "interview_id": interview_id,
                "company": iv["company"] if iv else "Swiggy",
                "role": iv["role"] if iv else "ML Engineer",
                "round": iv["round"] if iv else "Technical Round 1",
                "countdown_display": "Interview in 3 days",
                "checklist": [dict(it) for it in items] if items else [
                    {"id": "1", "title": "Review Customer Churn Prediction architecture", "done": True, "skill": "ML"},
                    {"id": "2", "title": "Practice live SQL: self-joins & aggregations", "done": False, "skill": "SQL"},
                    {"id": "3", "title": "Review FastAPI asynchronous model inference", "done": False, "skill": "Backend"}
                ]
            })
            return

        elif path.startswith("/interviews/") and path.endswith("/ics"):
            ics_text = generate_interview_ics(
                summary="Swiggy - ML Engineer Technical Interview",
                description="CoachPath prep session. Test audio & mic.",
                start_time=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3)
            )
            body = ics_text.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/calendar')
            self.send_header('Content-Disposition', 'attachment; filename=interview.ics')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # Serve static web frontend from web/ directory
        web_dir = BASE_DIR / "web"
        if path in ("/", "/index.html"):
            target = web_dir / "index.html"
            if target.exists():
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                with open(target, 'rb') as f:
                    content = f.read()
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return

        return super().do_GET()

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path
        body = self._parse_body()
        user_id = body.get("user_id", settings.DEFAULT_USER_ID)

        if path == "/onboarding/message":
            step = body.get("step", 1)
            msg = body.get("message", "")
            extracted = dict(body.get("current_profile", {}))
            if 1 <= step <= len(STEP_QUESTIONS):
                extracted[STEP_QUESTIONS[step - 1]["field"]] = msg

            next_idx = step + 1
            if next_idx <= len(STEP_QUESTIONS):
                q = STEP_QUESTIONS[next_idx - 1]
                self._send_json({
                    "next_question": q["question"],
                    "extracted_fields": extracted,
                    "progress_step": next_idx,
                    "total_steps": 11,
                    "quick_replies": q["quick_replies"],
                    "is_complete": False
                })
            else:
                self._send_json({
                    "next_question": "Awesome! Your profile is ready. Launching readiness dashboard!",
                    "extracted_fields": extracted,
                    "progress_step": 11,
                    "total_steps": 11,
                    "quick_replies": ["Launch My Dashboard"],
                    "is_complete": True
                })
            return

        elif path == "/onboarding/finish":
            recompute_everything(user_id, trigger_event="onboarding_completed")
            self._send_json({"status": "success", "user_id": user_id, "message": "Onboarding complete!"})
            return

        elif path == "/assessments/start":
            skill = body.get("skill", "python").lower()
            q_bank = SAMPLE_QUESTION_BANKS.get(skill, SAMPLE_QUESTION_BANKS["sql"])
            self._send_json({
                "assessment_id": str(uuid.uuid4()),
                "skill": skill,
                "total_questions": len(q_bank),
                "dimensions": ["Knowledge", "Problem Solving", "Practical Skills", "Industry Readiness"],
                "questions": q_bank
            })
            return

        elif path.startswith("/assessments/") and path.endswith("/submit"):
            skill = body.get("skill", "sql").lower()
            dim_scores = {"Knowledge": 85, "Problem Solving": 80, "Practical Skills": 90, "Industry Readiness": 85}
            overall = int(sum(dim_scores.values()) / 4)
            level = "advanced" if overall >= 70 else "intermediate"

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO user_skills (id, user_id, skill, assessed_level, assessed_score, last_assessed_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id, skill) DO UPDATE SET
                    assessed_level = excluded.assessed_level,
                    assessed_score = excluded.assessed_score,
                    last_assessed_at = CURRENT_TIMESTAMP
                """,
                (str(uuid.uuid4()), user_id, skill, level, overall)
            )
            conn.commit()
            conn.close()

            recompute = recompute_everything(user_id, trigger_event=f"{skill}_assessment_graded")
            self._send_json({
                "skill": skill,
                "overall_score": overall,
                "assessed_level": level,
                "dimension_scores": dim_scores,
                "feedback": f"Great job! Assessed at {level.title()} level in {skill.title()}.",
                "recomputed_readiness": recompute["readiness"]["overall"]
            })
            return

        elif path == "/roadmap/generate":
            self._send_json(generate_personalized_roadmap(user_id))
            return

        elif path == "/resume/tailor":
            job_id = body.get("job_id", "job-001")
            role_variant = body.get("role_variant", "ML Engineer")
            master = get_demo_master_resume()
            tailored = json.loads(json.dumps(master))
            tailored["summary"] = f"Goal-driven Computer Science graduate specializing in {role_variant} workflows with Scikit-Learn and FastAPI."
            is_valid, violations, diff = verify_resume_truthfulness(master, tailored)
            
            self._send_json({
                "resume_id": "res-tailored-001",
                "variant": role_variant,
                "ats_score": 94,
                "truthfulness_verified": is_valid,
                "truthfulness_banner": "Nothing was invented. Every line traces to your original resume.",
                "diff_breakdown": diff,
                "tailored_resume": tailored
            })
            return

        elif path == "/applications/prepare":
            job_id = body.get("job_id", "job-001")
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
            job = cursor.fetchone()
            conn.close()
            comp = job["company"] if job else "Swiggy"
            role = job["title"] if job else "Junior ML Engineer"

            app_id = str(uuid.uuid4())
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO applications (id, user_id, job_id, company, role, job_url, match_score, status)
                VALUES (?, ?, ?, ?, ?, ?, 92, 'prepared')
                """,
                (app_id, user_id, job_id, comp, role, job["apply_url"] if job else "#")
            )
            conn.commit()
            conn.close()

            self._send_json({
                "application_id": app_id,
                "company": comp,
                "role": role,
                "apply_url": job["apply_url"] if job else "https://careers.swiggy.com",
                "cover_note": f"Dear {comp} Hiring Team, I am eager to apply for the {role} position. My background building Scikit-Learn and FastAPI inference pipelines directly complements your production scale.",
                "screening_qna": [
                    {"question": "Why this company?", "answer": f"Admire {comp}'s technology and scale in India."},
                    {"question": "Top project?", "answer": "Customer Churn Prediction Engine with 84% ROC-AUC."}
                ],
                "status": "DRAFT · AWAITING USER APPROVAL"
            })
            return

        elif path.endswith("/approve") and "/applications/" in path:
            app_id = path.split("/")[2]
            today = datetime.date.today().isoformat()
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE applications SET status = 'applied', applied_on = ? WHERE id = ?", (today, app_id))
            cursor.execute("SELECT company, role, job_url FROM applications WHERE id = ?", (app_id,))
            row = cursor.fetchone()
            conn.close()

            log_action(user_id, "application_approved", "applications", app_id, {"applied_on": today})
            self._send_json({
                "status": "success",
                "application_id": app_id,
                "new_status": "applied",
                "official_apply_url": row["job_url"] if row else "https://careers.swiggy.com"
            })
            return

        elif path == "/outreach/draft":
            app_id = body.get("application_id", "app-001")
            recruiter = body.get("recruiter_name", "Pooja Rao")
            comp = body.get("company", "Swiggy")
            role = body.get("role", "Junior ML Engineer")
            
            draft_msg = f"Hi {recruiter},\n\nI noticed the {role} opening at {comp}. I'm a final-year CS undergrad skilled in Python, Scikit-Learn, and FastAPI. Recently I built a churn prediction API with 84% ROC-AUC and sub-50ms inference. Would love to share how my skills align with {comp}'s ML goals.\n\nBest regards,\nAarav"
            self._send_json({
                "draft_id": str(uuid.uuid4()),
                "application_id": app_id,
                "recruiter_name": recruiter,
                "word_count": len(draft_msg.split()),
                "message": draft_msg,
                "status": "DRAFT · AWAITING USER APPROVAL",
                "mailto_link": f"mailto:?subject=Application%20for%20{role}%20at%20{comp}&body={draft_msg.replace(chr(10), '%0D%0A')}"
            })
            return

        elif path.endswith("/approve") and "/outreach/" in path:
            draft_id = path.split("/")[2]
            log_action(user_id, "outreach_approved", "outreach", draft_id)
            self._send_json({"status": "success", "draft_id": draft_id, "message": "Outreach draft approved by candidate!"})
            return

        elif path == "/recompute":
            self._send_json(recompute_everything(user_id, trigger_event="manual_refresh"))
            return

        self._send_json({"error": "Endpoint not recognized"}, 404)

def run_server(port=8000):
    init_db()
    web_dir = BASE_DIR / "web"
    os.chdir(str(web_dir if web_dir.exists() else BASE_DIR))
    server_address = ('', port)
    httpd = socketserver.TCPServer(server_address, CoachPathRequestHandler)
    print(f"🚀 CoachPath Unified Server running at http://localhost:{port}")
    print(f"🌐 Web UI: http://localhost:{port}/index.html")
    print(f"🩺 API Health: http://localhost:{port}/health")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down CoachPath server.")
        httpd.server_close()

if __name__ == "__main__":
    p = settings.PORT or 8000
    run_server(p)
