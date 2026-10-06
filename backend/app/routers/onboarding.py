from fastapi import APIRouter
from typing import Dict, Any, List
import json
from app.core.config import settings
from app.core.db import get_connection
from app.ai.schemas import OnboardingMessageRequest, OnboardingStepResponse
from app.ai.llm_client import llm_client
from app.ai.prompts.onboarding import ONBOARDING_SYSTEM_PROMPT
from app.services.recompute import recompute_everything

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])

STEP_QUESTIONS = [
    {
        "step": 1,
        "question": "Namaste! I'm CoachPath, your AI Career Intelligence copilot. Let's start with your name.",
        "quick_replies": ["Aarav Sharma", "Priya Patel", "Rohan Mehta"],
        "field": "full_name"
    },
    {
        "step": 2,
        "question": "Great! What is your primary dream tech role?",
        "quick_replies": ["ML Engineer", "Data Scientist", "Backend Dev", "AI Engineer", "Data Analyst"],
        "field": "target_role"
    },
    {
        "step": 3,
        "question": "What is your target preparation timeline for campus placements or hiring drives?",
        "quick_replies": ["3 Months (Intensive)", "4 Months (Recommended)", "6 Months"],
        "field": "target_timeline_months"
    },
    {
        "step": 4,
        "question": "What is your current college / education background?",
        "quick_replies": ["Final-Year B.Tech CSE (Tier-2/3)", "3rd Year B.Tech", "MCA Graduate", "Working Professional (Fresher)"],
        "field": "education_level"
    },
    {
        "step": 5,
        "question": "How many hours can you realistically dedicate on weekdays?",
        "quick_replies": ["1 hour / day", "2 hours / day (Steady)", "3+ hours / day"],
        "field": "hours_per_weekday"
    },
    {
        "step": 6,
        "question": "And how many hours can you study on weekends (Saturday & Sunday)?",
        "quick_replies": ["3-4 hours / day", "5 hours / day (Deep work)", "6+ hours / day"],
        "field": "hours_per_weekend"
    },
    {
        "step": 7,
        "question": "What learning resources do you prefer?",
        "quick_replies": ["100% Free Resources Only", "NPTEL & SWAYAM", "YouTube & Documentation", "Mixed"],
        "field": "learning_resources"
    },
    {
        "step": 8,
        "question": "Which tech companies in India or globally excite you most?",
        "quick_replies": ["Swiggy, PhonePe, Razorpay", "Flipkart & Zepto", "Fractal, Ola Electric", "Global Remote Startups"],
        "field": "interested_companies"
    },
    {
        "step": 9,
        "question": "What is your desired fresher / entry-level salary expectation (in ₹ LPA)?",
        "quick_replies": ["6 - 10 LPA", "8 - 14 LPA", "12 - 20 LPA", "20+ LPA"],
        "field": "desired_salary"
    },
    {
        "step": 10,
        "question": "What is your location and work preference?",
        "quick_replies": ["Bengaluru (Hybrid)", "Hyderabad (Hybrid)", "Gurgaon / Delhi NCR", "100% Remote"],
        "field": "location_and_work_mode"
    },
    {
        "step": 11,
        "question": "Lastly, which technical skills have you already practiced or built projects with?",
        "quick_replies": ["Python & SQL", "Python, Scikit-Learn & Pandas", "FastAPI, Docker & Git", "C++ & DSA"],
        "field": "initial_skills"
    }
]

@router.post("/message")
def handle_onboarding_turn(req: OnboardingMessageRequest) -> Dict[str, Any]:
    """Processes a conversational onboarding step, extracts fields, and guides candidate."""
    current_step = req.step
    user_msg = req.message
    extracted = dict(req.current_profile)
    
    # Extract current step field
    if 1 <= current_step <= len(STEP_QUESTIONS):
        field_name = STEP_QUESTIONS[current_step - 1]["field"]
        extracted[field_name] = user_msg

    next_step_index = current_step + 1
    if next_step_index <= len(STEP_QUESTIONS):
        next_step_info = STEP_QUESTIONS[next_step_index - 1]
        return {
            "next_question": next_step_info["question"],
            "extracted_fields": extracted,
            "progress_step": next_step_index,
            "total_steps": 11,
            "quick_replies": next_step_info["quick_replies"],
            "is_complete": False
        }
    else:
        return {
            "next_question": "Awesome! Your personalized career profile is ready. Let's launch your readiness dashboard and initial skill assessment!",
            "extracted_fields": extracted,
            "progress_step": 11,
            "total_steps": 11,
            "quick_replies": ["Launch My Dashboard", "Take Skills Assessment"],
            "is_complete": True
        }

@router.post("/finish")
def finish_onboarding(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Saves structured profile into DB and computes initial roadmap."""
    user_id = payload.get("user_id", settings.DEFAULT_USER_ID)
    profile_data = payload.get("profile", {})
    
    full_name = profile_data.get("full_name", "Aarav Sharma")
    target_role = profile_data.get("target_role", "ML Engineer")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO profiles (user_id, full_name, target_role, onboarding_complete)
        VALUES (?, ?, ?, 1)
        ON CONFLICT(user_id) DO UPDATE SET
            full_name = excluded.full_name,
            target_role = excluded.target_role,
            onboarding_complete = 1
        """,
        (user_id, full_name, target_role)
    )
    conn.commit()
    conn.close()

    # Trigger central recomputation
    recompute_everything(user_id, trigger_event="onboarding_completed")
    
    return {
        "status": "success",
        "user_id": user_id,
        "message": f"Welcome aboard, {full_name}! Your profile and roadmap for {target_role} are now active."
    }
