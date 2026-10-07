"""
AI Career Onboarding Conversation Router (Placeholder).
Scheduled for implementation in Phase 4.
"""

from typing import Dict
from fastapi import APIRouter

router = APIRouter(prefix="/onboarding", tags=["Group 2: Onboarding"])


@router.get("", summary="Onboarding Module Status")
async def onboarding_status() -> Dict[str, str]:
    """Structural router placeholder for conversational career onboarding."""
    return {"module": "onboarding", "status": "placeholder", "phase": "Phase 4"}
