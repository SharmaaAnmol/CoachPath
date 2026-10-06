from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import uuid
from app.core.config import settings
from app.core.db import get_connection
from app.core.audit import log_action

router = APIRouter(prefix="/outreach", tags=["Recruiter Outreach"])

@router.post("/draft")
def generate_recruiter_outreach(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Drafts a concise <=90 word personalized outreach message.
    Enforces 'no spam' rate limits (max 3 drafts per application).
    Holds in 'DRAFT · AWAITING USER APPROVAL' status.
    """
    user_id = payload.get("user_id", settings.DEFAULT_USER_ID)
    app_id = payload.get("application_id")
    recruiter_name = payload.get("recruiter_name", "Technical Recruiter")
    recruiter_role = payload.get("recruiter_role", "Talent Acquisition Lead")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Rate limit check (Slide 11)
    cursor.execute("SELECT count(*) as count FROM outreach WHERE application_id = ?", (app_id,))
    existing_drafts = cursor.fetchone()["count"]
    if existing_drafts >= 3:
        conn.close()
        raise HTTPException(status_code=429, detail="Anti-spam rate limit: Maximum 3 drafts allowed per application.")

    cursor.execute("SELECT company, role FROM applications WHERE id = ?", (app_id,))
    app = cursor.fetchone()
    conn.close()

    company = app["company"] if app else "your engineering team"
    role = app["role"] if app else "Machine Learning Engineer"

    # Craft tight <= 90 word message
    draft_text = (
        f"Hi {recruiter_name},\n\n"
        f"I saw the {role} opening at {company} and wanted to reach out. "
        f"I'm a final-year CS undergrad experienced with Python, Scikit-Learn, and FastAPI. "
        f"Recently, I engineered a high-scale customer churn predictor achieving 84% ROC-AUC with sub-50ms inference. "
        f"I'd love to connect and share how my background aligns with {company}'s goals.\n\n"
        f"Best,\nAarav"
    )
    
    word_count = len(draft_text.split())
    draft_id = str(uuid.uuid4())

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO outreach (id, user_id, application_id, recruiter_name, recruiter_role, draft, status)
        VALUES (?, ?, ?, ?, ?, ?, 'draft')
        """,
        (draft_id, user_id, app_id, recruiter_name, recruiter_role, draft_text)
    )
    conn.commit()
    conn.close()

    return {
        "draft_id": draft_id,
        "application_id": app_id,
        "recruiter_name": recruiter_name,
        "recruiter_role": recruiter_role,
        "word_count": word_count,
        "message": draft_text,
        "status": "DRAFT · AWAITING USER APPROVAL",
        "mailto_link": f"mailto:?subject=Application%20for%20{role}%20at%20{company}&body={draft_text.replace(chr(10), '%0D%0A')}"
    }

@router.post("/{draft_id}/approve")
def approve_outreach(draft_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Human approval gate for recruiter outreach."""
    user_id = payload.get("user_id", settings.DEFAULT_USER_ID)
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE outreach SET status = 'approved', approved_at = CURRENT_TIMESTAMP WHERE id = ?", (draft_id,))
    cursor.execute("SELECT recruiter_name, recruiter_role, application_id FROM outreach WHERE id = ?", (draft_id,))
    row = cursor.fetchone()
    conn.close()

    log_action(
        user_id=user_id,
        action="recruiter_outreach_approved",
        entity="outreach",
        entity_id=draft_id,
        payload={"recruiter": row["recruiter_name"] if row else "", "role": row["recruiter_role"] if row else ""},
        approved_by_user=True
    )

    return {
        "status": "success",
        "draft_id": draft_id,
        "message": "Outreach message approved by user and logged in audit log."
    }
