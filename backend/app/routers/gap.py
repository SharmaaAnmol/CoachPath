from fastapi import APIRouter
from typing import Dict, Any
from app.core.config import settings
from app.services.gap import analyze_skill_gap

router = APIRouter(tags=["Skill Gap"])

@router.get("/gap")
def get_skill_gap(user_id: str = settings.DEFAULT_USER_ID, role: str = "ML Engineer") -> Dict[str, Any]:
    """Analyzes skill gaps against role requirements, labeling: Strong / Improve / Advanced-needed / Required / Recommended."""
    return analyze_skill_gap(user_id, role)
