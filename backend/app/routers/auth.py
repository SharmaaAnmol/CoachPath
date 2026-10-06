from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from app.core.config import settings
from app.core.db import get_connection

router = APIRouter(tags=["Auth"])

@router.get("/me")
def get_current_user_profile(user_id: str = settings.DEFAULT_USER_ID) -> Dict[str, Any]:
    """Returns the central profile for the authenticated/demo candidate."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
        
    res = dict(row)
    import json
    for field in ["learning_resources", "interested_companies", "interested_industries"]:
        if isinstance(res.get(field), str):
            try:
                res[field] = json.loads(res[field])
            except Exception:
                res[field] = []
    return res
