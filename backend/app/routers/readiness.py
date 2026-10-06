from fastapi import APIRouter
from typing import Dict, Any, List
from app.core.config import settings
from app.services.readiness import calculate_readiness, get_readiness_history

router = APIRouter(prefix="/readiness", tags=["Readiness Dashboard"])

@router.get("")
def get_readiness_dashboard(user_id: str = settings.DEFAULT_USER_ID) -> Dict[str, Any]:
    """Calculates 7-component career readiness score and biggest lever improvement opportunity."""
    return calculate_readiness(user_id)

@router.get("/history")
def get_readiness_timeline(user_id: str = settings.DEFAULT_USER_ID) -> List[Dict[str, Any]]:
    """Returns chronological readiness history snapshots for progress charts."""
    return get_readiness_history(user_id)
