import json
import uuid
from typing import Dict, Any, List
from app.core.db import get_connection

WEIGHTS = {
    "technical": 0.25,
    "dsa": 0.15,
    "projects": 0.15,
    "resume": 0.10,
    "interview": 0.15,
    "industry": 0.10,
    "job_readiness": 0.10
}

def calculate_readiness(user_id: str) -> Dict[str, Any]:
    """
    Computes candidate career readiness score across the 7 verified components (Slide 14):
    - Technical Skills (25%)
    - DSA (15%)
    - Projects (15%)
    - Resume (10%)
    - Interview Skills (15%)
    - Industry Skills (10%)
    - Job Readiness (10%)
    
    Includes 'Biggest Lever' sensitivity calculation (highest weight * gap)
    reproducing the 78% -> 82% insight card.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Technical Skills: Average assessed/known scores
    cursor.execute("SELECT assessed_score, self_level FROM user_skills WHERE user_id = ?", (user_id,))
    skills = cursor.fetchall()
    if skills:
        scores = [s["assessed_score"] if s["assessed_score"] is not None else (70 if s["self_level"] == "intermediate" else 45) for s in skills]
        technical_score = int(sum(scores) / len(scores))
    else:
        technical_score = 60

    # 2. DSA Score
    cursor.execute("SELECT assessed_score FROM user_skills WHERE user_id = ? AND lower(skill) in ('data structures', 'dsa')", (user_id,))
    dsa_row = cursor.fetchone()
    dsa_score = dsa_row["assessed_score"] if (dsa_row and dsa_row["assessed_score"] is not None) else 65

    # 3. Projects Score
    cursor.execute("SELECT count(*) as count FROM user_projects WHERE user_id = ?", (user_id,))
    proj_count = cursor.fetchone()["count"]
    projects_score = min(95, 50 + (proj_count * 20)) # e.g. 2 projects = 90

    # 4. Resume Score (latest ATS score)
    cursor.execute("SELECT ats_score FROM resumes WHERE user_id = ? ORDER BY created_at DESC LIMIT 1", (user_id,))
    resume_row = cursor.fetchone()
    resume_score = resume_row["ats_score"] if (resume_row and resume_row["ats_score"]) else 82

    # 5. Interview Skills (prep items done + mock score)
    cursor.execute("SELECT count(*) as total, sum(done) as completed FROM prep_items p JOIN interviews i ON p.interview_id = i.id WHERE i.user_id = ?", (user_id,))
    prep_stats = cursor.fetchone()
    total_prep = prep_stats["total"] or 0
    done_prep = prep_stats["completed"] or 0
    if total_prep > 0:
        interview_score = int((done_prep / total_prep) * 50) + 40
    else:
        interview_score = 65

    # 6. Industry Skills
    industry_score = 75

    # 7. Job Readiness (Applications activity & top match)
    cursor.execute("SELECT count(*) as app_count FROM applications WHERE user_id = ?", (user_id,))
    app_count = cursor.fetchone()["app_count"]
    job_readiness_score = min(95, 60 + (app_count * 10))
    
    conn.close()

    components = {
        "technical": technical_score,
        "dsa": dsa_score,
        "projects": projects_score,
        "resume": resume_score,
        "interview": interview_score,
        "industry": industry_score,
        "job_readiness": job_readiness_score
    }

    # Overall weighted score
    overall = int(round(sum(components[k] * WEIGHTS[k] for k in components)))

    # Compute 'Biggest Lever' (highest weight * (100 - current_score))
    levers = []
    for comp, score in components.items():
        gap = 100 - score
        impact = WEIGHTS[comp] * gap
        levers.append((comp, impact, score, gap))
    
    levers.sort(key=lambda x: x[1], reverse=True)
    top_lever = levers[0]
    lever_name = top_lever[0]
    lever_current = top_lever[2]
    
    # Calculate projected overall if top lever improved by 20 points
    simulated_components = dict(components)
    simulated_components[lever_name] = min(100, lever_current + 20)
    projected_overall = int(round(sum(simulated_components[k] * WEIGHTS[k] for k in simulated_components)))

    lever_friendly_names = {
        "technical": "Core Technical Skills",
        "dsa": "Data Structures & Algorithms",
        "projects": "Production Portfolio Projects",
        "resume": "Resume ATS Keyword Alignment",
        "interview": "Interview Preparation & System Design",
        "industry": "High-Demand Industry Skills",
        "job_readiness": "Active Applications & Interview Funnel"
    }

    biggest_lever = {
        "component": lever_name,
        "label": lever_friendly_names.get(lever_name, lever_name.title()),
        "current_score": lever_current,
        "projected_overall": projected_overall,
        "overall_delta": projected_overall - overall,
        "recommendation": f"Focusing on {lever_friendly_names.get(lever_name, lever_name)} can boost your career readiness from {overall}% to {projected_overall}%!"
    }

    # Save snapshot to database
    save_readiness_snapshot(user_id, overall, components)

    return {
        "overall": overall,
        "components": components,
        "weights": WEIGHTS,
        "biggest_lever": biggest_lever
    }

def save_readiness_snapshot(user_id: str, overall: int, components: Dict[str, int]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO readiness_snapshots (id, user_id, overall, technical, dsa, projects, resume, interview, industry, job_readiness)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(uuid.uuid4()),
            user_id,
            overall,
            components["technical"],
            components["dsa"],
            components["projects"],
            components["resume"],
            components["interview"],
            components["industry"],
            components["job_readiness"]
        )
    )
    conn.commit()
    conn.close()

def get_readiness_history(user_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT overall, technical, dsa, projects, resume, interview, industry, job_readiness, created_at
        FROM readiness_snapshots
        WHERE user_id = ?
        ORDER BY created_at ASC
        LIMIT 20
        """,
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
