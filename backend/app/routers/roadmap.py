from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.core.config import settings
from app.core.db import get_connection
from app.services.roadmap import generate_personalized_roadmap, get_active_roadmap

router = APIRouter(prefix="/roadmap", tags=["Roadmap"])

@router.post("/generate")
def create_roadmap(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Generates an hour-constrained, dependency-ordered roadmap with curated free resources."""
    user_id = payload.get("user_id", settings.DEFAULT_USER_ID)
    return generate_personalized_roadmap(user_id)

@router.get("")
def read_roadmap(user_id: str = settings.DEFAULT_USER_ID) -> Dict[str, Any]:
    """Returns the candidate's active roadmap."""
    return get_active_roadmap(user_id)

@router.patch("/items/{item_id}")
def update_roadmap_item_status(item_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Updates the status of a roadmap task item (todo / in_progress / completed)."""
    status = payload.get("status", "completed")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE roadmap_items SET status = ? WHERE id = ?", (status, item_id))
    conn.commit()
    conn.close()
    return {"status": "success", "item_id": item_id, "new_status": status}
