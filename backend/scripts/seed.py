import os
import sys
import json
import uuid
from pathlib import Path

# Add backend to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings, DATA_DIR
from app.core.db import init_db, get_connection
from app.services.recompute import recompute_everything

def seed_database():
    print("🌱 Initializing CoachPath Database Schema...")
    init_db()

    seed_file = DATA_DIR / "seed_data.json"
    if not seed_file.exists():
        print(f"❌ Error: seed file not found at {seed_file}")
        return

    with open(seed_file, "r") as f:
        seed_data = json.load(f)

    conn = get_connection()
    cursor = conn.cursor()

    demo_user = seed_data["demo_user"]
    user_id = demo_user["user_id"]
    print(f"👤 Seeding Demo Candidate: {demo_user['full_name']} ({demo_user['target_role']})...")

    # 1. Profile
    cursor.execute(
        """
        INSERT OR REPLACE INTO profiles (
            user_id, full_name, target_role, target_timeline_months,
            education_level, experience_level, hours_per_weekday, hours_per_weekend,
            learning_resources, interested_companies, interested_industries,
            desired_salary_min, desired_salary_max, location, work_mode, onboarding_complete
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            demo_user["full_name"],
            demo_user["target_role"],
            demo_user["target_timeline_months"],
            demo_user["education_level"],
            demo_user["experience_level"],
            demo_user["hours_per_weekday"],
            demo_user["hours_per_weekend"],
            json.dumps(demo_user["learning_resources"]),
            json.dumps(demo_user["interested_companies"]),
            json.dumps(demo_user["interested_industries"]),
            demo_user["desired_salary_min"],
            demo_user["desired_salary_max"],
            demo_user["location"],
            demo_user["work_mode"],
            1 if demo_user["onboarding_complete"] else 0
        )
    )

    # 2. User Skills
    print("⚡ Seeding skills & initial assessments...")
    cursor.execute("DELETE FROM user_skills WHERE user_id = ?", (user_id,))
    for sk in seed_data["user_skills"]:
        cursor.execute(
            """
            INSERT INTO user_skills (id, user_id, skill, self_level, assessed_level, assessed_score)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                user_id,
                sk["skill"],
                sk["self_level"],
                sk["assessed_level"],
                sk["assessed_score"]
            )
        )

    # 3. User Projects
    print("📁 Seeding portfolio projects...")
    cursor.execute("DELETE FROM user_projects WHERE user_id = ?", (user_id,))
    for pr in seed_data["user_projects"]:
        cursor.execute(
            """
            INSERT INTO user_projects (id, user_id, title, description, tech, link)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                pr.get("id", str(uuid.uuid4())),
                user_id,
                pr["title"],
                pr["description"],
                json.dumps(pr.get("tech", [])),
                pr.get("link", "")
            )
        )

    # 4. Jobs
    print("💼 Seeding curated tech jobs (Bengaluru, Hyderabad, Remote, LPA salaries)...")
    for j in seed_data["jobs"]:
        cursor.execute(
            """
            INSERT OR REPLACE INTO jobs (
                id, source, external_id, title, company, location,
                work_mode, salary_min, salary_max, description, apply_url,
                required_skills, experience_required
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                j["id"],
                j["source"],
                j["external_id"],
                j["title"],
                j["company"],
                j["location"],
                j["work_mode"],
                j["salary_min"],
                j["salary_max"],
                j["description"],
                j["apply_url"],
                json.dumps(j["required_skills"]),
                j["experience_required"]
            )
        )

    # 5. Master Resume
    print("📄 Seeding master resume...")
    cursor.execute("DELETE FROM resumes WHERE user_id = ? AND kind = 'master'", (user_id,))
    cursor.execute(
        """
        INSERT INTO resumes (id, user_id, kind, label, content, ats_score)
        VALUES (?, ?, 'master', 'Master Resume', ?, 82)
        """,
        (str(uuid.uuid4()), user_id, json.dumps(seed_data["master_resume"]))
    )

    conn.commit()
    conn.close()

    # 6. Central Recompute (Generates roadmap, scores all jobs, computes readiness & biggest lever)
    print("🔄 Running Central Profile Recomputation (recompute_everything)...")
    res = recompute_everything(user_id, trigger_event="seed_initialization")
    print(f"✅ Seeding Complete! Overall Career Readiness: {res['readiness']['overall']}%")
    print(f"🎯 Top Lever: {res['readiness']['biggest_lever']['label']} ({res['readiness']['biggest_lever']['recommendation']})")

if __name__ == "__main__":
    seed_database()
