import json
from typing import Dict, Any
from app.core.db import get_connection
from app.services.roadmap import generate_personalized_roadmap
from app.services.matching import calculate_job_match
from app.services.readiness import calculate_readiness
from app.core.audit import log_action

def recompute_everything(user_id: str, trigger_event: str = "assessment_updated") -> Dict[str, Any]:
    """
    Central Reactive Engine (Slide 3 & 15):
    Whenever a skill level is assessed or profile changes:
    1. Re-sequences the dynamic roadmap
    2. Re-scores and re-ranks all jobs in the database
    3. Re-calculates 7-component career readiness & biggest-lever card
    4. Records an audit event
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Regenerate active roadmap
    roadmap_result = generate_personalized_roadmap(user_id)
    
    # 2. Re-score all jobs for this user
    cursor.execute("SELECT * FROM jobs")
    jobs = cursor.fetchall()
    
    matched_jobs_summary = []
    for j in jobs:
        job_dict = dict(j)
        job_dict["required_skills"] = json.loads(job_dict["required_skills"]) if isinstance(job_dict.get("required_skills"), str) else job_dict.get("required_skills", [])
        
        match_result = calculate_job_match(user_id, job_dict)
        
        # Upsert match score into job_matches
        cursor.execute(
            """
            INSERT INTO job_matches (user_id, job_id, score, breakdown, matched_skills, missing_skills, reason)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, job_id) DO UPDATE SET
                score = excluded.score,
                breakdown = excluded.breakdown,
                matched_skills = excluded.matched_skills,
                missing_skills = excluded.missing_skills,
                reason = excluded.reason
            """,
            (
                user_id,
                job_dict["id"],
                match_result["score"],
                json.dumps(match_result["breakdown"]),
                json.dumps(match_result["matched_skills"]),
                json.dumps(match_result["missing_skills"]),
                match_result["reason"]
            )
        )
        matched_jobs_summary.append({
            "job_id": job_dict["id"],
            "title": job_dict["title"],
            "company": job_dict["company"],
            "score": match_result["score"]
        })
        
    conn.commit()
    conn.close()

    # 3. Recalculate Career Readiness & Biggest Lever
    readiness_result = calculate_readiness(user_id)
    
    # 4. Audit Log
    log_action(
        user_id=user_id,
        action="recompute_everything_triggered",
        entity="central_profile",
        payload={
            "trigger": trigger_event,
            "overall_readiness": readiness_result["overall"],
            "top_match_score": max([m["score"] for m in matched_jobs_summary]) if matched_jobs_summary else 0,
            "roadmap_items_count": roadmap_result["total_items"]
        }
    )

    return {
        "status": "success",
        "trigger": trigger_event,
        "readiness": readiness_result,
        "roadmap_updated": True,
        "jobs_reranked": len(matched_jobs_summary),
        "message": "Central Profile recomputed: Skills, Roadmap, Job Match Scores & Readiness updated."
    }
