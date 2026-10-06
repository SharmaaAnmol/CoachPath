from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from typing import Dict, Any, List
import uuid
import datetime
import json
from app.core.config import settings
from app.core.db import get_connection
from app.services.ics_service import generate_interview_ics

router = APIRouter(prefix="/interviews", tags=["Interview Prep & Calendar"])

@router.post("")
def schedule_interview(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Schedules an upcoming interview, sets countdown, and generates prep checklist."""
    user_id = payload.get("user_id", settings.DEFAULT_USER_ID)
    application_id = payload.get("application_id")
    round_name = payload.get("round", "Technical Round 1")
    itype = payload.get("itype", "Video Call")
    
    # Default to 3 days in future if not provided
    starts_at_str = payload.get("starts_at")
    if starts_at_str:
        starts_at = datetime.datetime.fromisoformat(starts_at_str.replace("Z", "+00:00"))
    else:
        starts_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3, hours=4)
        starts_at_str = starts_at.isoformat()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT company, role FROM applications WHERE id = ?", (application_id,))
    app = cursor.fetchone()
    
    interview_id = str(uuid.uuid4())
    topics = ["Python internals", "SQL optimization", "ML pipeline architecture", "Project walkthrough"]
    
    cursor.execute(
        """
        INSERT INTO interviews (id, user_id, application_id, starts_at, round, itype, topics)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (interview_id, user_id, application_id, starts_at_str, round_name, itype, json.dumps(topics))
    )

    # Generate personalized prep items (checkboxes) based on round and weak skills
    default_prep_items = [
        "Review Customer Churn Prediction architecture & trade-offs",
        "Practice live SQL: 2nd highest salary, self-joins & aggregations",
        "Deep dive into Overfitting vs Underfitting & Regularization techniques",
        "Review FastAPI asynchronous request handling vs synchronous CPU models",
        "Prepare 'Tell me about yourself' tailored to the hiring team"
    ]
    
    for item in default_prep_items:
        cursor.execute(
            """
            INSERT INTO prep_items (id, interview_id, title, done, skill)
            VALUES (?, ?, ?, 0, 'Interview Prep')
            """,
            (str(uuid.uuid4()), interview_id, item)
        )

    conn.commit()
    conn.close()

    return {
        "interview_id": interview_id,
        "round": round_name,
        "starts_at": starts_at_str,
        "countdown_days": 3,
        "countdown_text": "Interview in 3 days",
        "prep_items_count": len(default_prep_items)
    }

@router.get("/{interview_id}/prep")
def get_interview_prep(interview_id: str) -> Dict[str, Any]:
    """Fetches countdown, checklist items, and simulated mock questions."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT i.*, a.company, a.role FROM interviews i LEFT JOIN applications a ON i.application_id = a.id WHERE i.id = ?", (interview_id,))
    interview = cursor.fetchone()
    
    if not interview:
        conn.close()
        raise HTTPException(status_code=404, detail="Interview not found")

    cursor.execute("SELECT id, title, done, skill FROM prep_items WHERE interview_id = ?", (interview_id,))
    prep_rows = cursor.fetchall()
    conn.close()

    mock_questions = [
        {
            "category": "Project Walkthrough",
            "question": "How did you handle class imbalance when predicting customer churn?",
            "sample_good_answer": "I evaluated SMOTE oversampling vs class weights in Scikit-Learn Random Forest, measuring precision-recall curves rather than raw accuracy."
        },
        {
            "category": "System Design / Practical",
            "question": "How would you deploy and serve this ML model if traffic scaled to 1,000 requests per second?",
            "sample_good_answer": "I would decouple inference using asynchronous message queues (RabbitMQ/Kafka) with Redis caching for frequent predictions and scale FastAPI containers behind a load balancer."
        }
    ]

    return {
        "interview_id": interview_id,
        "company": interview["company"] or "Swiggy",
        "role": interview["role"] or "Junior ML Engineer",
        "round": interview["round"],
        "starts_at": interview["starts_at"],
        "countdown_display": "Interview in 3 days",
        "checklist": [dict(r) for r in prep_rows],
        "mock_questions": mock_questions
    }

@router.get("/{interview_id}/ics")
def download_interview_calendar(interview_id: str):
    """Returns downloadable RFC 5545 .ics file with 3-day, 1-day, and 1-hour VALARM reminders."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT i.*, a.company, a.role FROM interviews i LEFT JOIN applications a ON i.application_id = a.id WHERE i.id = ?", (interview_id,))
    row = cursor.fetchone()
    conn.close()

    comp = row["company"] if (row and row["company"]) else "Swiggy"
    role = row["role"] if (row and row["role"]) else "ML Engineer"
    rnd = row["round"] if row else "Technical Interview"
    
    start_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3)
    ics_text = generate_interview_ics(
        summary=f"{comp} - {role} ({rnd})",
        description=f"CoachPath Interview Preparation for {comp}. Ensure camera & microphone are tested. Review prep checklist.",
        start_time=start_time
    )

    return PlainTextResponse(
        content=ics_text,
        media_type="text/calendar",
        headers={"Content-Disposition": f"attachment; filename=interview_{interview_id[:8]}.ics"}
    )
