from fastapi import APIRouter
from typing import Dict, Any, List
from app.core.config import settings
from app.core.db import get_connection
from app.core.audit import get_user_audit_logs, log_action

router = APIRouter(tags=["Privacy & Responsible AI"])

@router.get("/audit")
def get_audit_trail(user_id: str = settings.DEFAULT_USER_ID) -> Dict[str, Any]:
    """Returns transparent audit trail of candidate actions, AI decisions, and human approvals."""
    logs = get_user_audit_logs(user_id)
    return {
        "user_id": user_id,
        "total_records": len(logs),
        "audit_logs": logs
    }

@router.get("/me/export")
def export_user_data(user_id: str = settings.DEFAULT_USER_ID) -> Dict[str, Any]:
    """Exports all stored candidate data for complete data portability (Slide 17)."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
    profile = cursor.fetchone()
    
    cursor.execute("SELECT * FROM user_skills WHERE user_id = ?", (user_id,))
    skills = cursor.fetchall()
    
    cursor.execute("SELECT * FROM user_projects WHERE user_id = ?", (user_id,))
    projects = cursor.fetchall()
    
    cursor.execute("SELECT * FROM applications WHERE user_id = ?", (user_id,))
    apps = cursor.fetchall()
    
    conn.close()

    log_action(user_id, "data_exported", "profiles", payload={"export_format": "json"})

    return {
        "export_timestamp": "now",
        "profile": dict(profile) if profile else {},
        "skills": [dict(s) for s in skills],
        "projects": [dict(p) for p in projects],
        "applications": [dict(a) for a in apps]
    }

@router.delete("/me/data")
def delete_user_data(user_id: str = settings.DEFAULT_USER_ID) -> Dict[str, Any]:
    """User-controlled complete data deletion button (Slide 17)."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Cascade delete all data for candidate
    for table in ["audit_log", "readiness_snapshots", "prep_items", "interviews", "outreach", "applications", "resumes", "job_matches", "roadmap_items", "roadmaps", "assessment_questions", "assessments", "user_projects", "user_skills", "profiles"]:
        cursor.execute(f"DELETE FROM {table} WHERE user_id = ?", (user_id,))
        
    conn.commit()
    conn.close()

    return {
        "status": "success",
        "message": "All user data, logs, assessments, and applications successfully and permanently deleted."
    }
