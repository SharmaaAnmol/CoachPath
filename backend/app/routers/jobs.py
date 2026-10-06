from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import json
from app.core.config import settings
from app.core.db import get_connection
from app.services.matching import calculate_job_match

router = APIRouter(prefix="/jobs", tags=["Jobs & Matching"])

@router.get("/recommended")
def get_recommended_jobs(user_id: str = settings.DEFAULT_USER_ID) -> List[Dict[str, Any]]:
    """Returns jobs scored and ranked for candidate with transparent match score rings and breakdowns."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs")
    job_rows = cursor.fetchall()
    
    results = []
    for row in job_rows:
        job = dict(row)
        job["required_skills"] = json.loads(job["required_skills"]) if isinstance(job.get("required_skills"), str) else (job.get("required_skills") or [])
        
        # Calculate transparent match score
        match_info = calculate_job_match(user_id, job)
        job["match"] = match_info
        job["match_score"] = match_info["score"]
        results.append(job)
        
    conn.close()
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results

@router.get("/{job_id}/match")
def get_job_match_breakdown(job_id: str, user_id: str = settings.DEFAULT_USER_ID) -> Dict[str, Any]:
    """Returns deep explainable breakdown and rationale for a specific job."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
        
    job = dict(row)
    job["required_skills"] = json.loads(job["required_skills"]) if isinstance(job.get("required_skills"), str) else (job.get("required_skills") or [])
    
    return calculate_job_match(user_id, job)

@router.post("/{job_id}/save")
def save_job_to_tracker(job_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Saves a job directly to the candidate's application tracker."""
    user_id = payload.get("user_id", settings.DEFAULT_USER_ID)
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    job = cursor.fetchone()
    if not job:
        conn.close()
        raise HTTPException(status_code=404, detail="Job not found")
        
    import uuid
    app_id = str(uuid.uuid4())
    cursor.execute(
        """
        INSERT INTO applications (id, user_id, job_id, company, role, job_url, status)
        VALUES (?, ?, ?, ?, ?, ?, 'saved')
        """,
        (app_id, user_id, job_id, job["company"], job["title"], job["apply_url"])
    )
    conn.commit()
    conn.close()
    
    return {"status": "success", "application_id": app_id, "message": f"Saved {job['title']} at {job['company']} to Application Tracker"}
