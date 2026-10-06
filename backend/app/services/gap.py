import json
from typing import Dict, Any, List
from pathlib import Path
from app.core.config import DATA_DIR
from app.core.db import get_connection

def load_role_requirements() -> dict:
    req_file = DATA_DIR / "role_requirements.json"
    if req_file.exists():
        with open(req_file, "r") as f:
            return json.load(f)
    return {}

LEVEL_SCORES = {
    "none": 0,
    "beginner": 35,
    "intermediate": 65,
    "advanced": 90
}

def analyze_skill_gap(user_id: str, target_role: str = "ML Engineer") -> Dict[str, Any]:
    """
    Computes exact skill gap for candidate vs target role requirements.
    Categorizes skills into: Strong, Improve, Advanced-needed, Required, Recommended.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Load user skills
    cursor.execute("SELECT skill, self_level, assessed_level, assessed_score FROM user_skills WHERE user_id = ?", (user_id,))
    user_skills_rows = cursor.fetchall()
    conn.close()
    
    user_skills_map = {}
    for row in user_skills_rows:
        skill_name = row["skill"].lower()
        level = row["assessed_level"] or row["self_level"] or "beginner"
        score = row["assessed_score"]
        if score is None:
            score = LEVEL_SCORES.get(level.lower(), 40)
        user_skills_map[skill_name] = {
            "level": level.lower(),
            "score": score,
            "is_assessed": row["assessed_score"] is not None
        }

    role_data = load_role_requirements().get(target_role, {})
    required_skills = role_data.get("required_skills", [])
    
    analyzed_skills = []
    strong_count = 0
    gaps_count = 0
    total_hours_needed = 0
    
    for req in required_skills:
        skill_name = req["skill"].lower()
        target_level = req["level"].lower()
        priority = req.get("priority", "required")
        
        user_info = user_skills_map.get(skill_name, {"level": "none", "score": 0, "is_assessed": False})
        user_level = user_info["level"]
        user_score = user_info["score"]
        
        target_score_benchmark = LEVEL_SCORES.get(target_level, 65)
        score_diff = user_score - target_score_benchmark
        
        # Categorization logic
        if score_diff >= 10:
            label = "Strong"
            status_code = "strong"
            strong_count += 1
            est_hours = 0
        elif user_level == "none":
            label = "Required" if priority == "required" else "Recommended"
            status_code = "missing"
            gaps_count += 1
            est_hours = 30
        elif target_level == "advanced" and user_level in ("intermediate", "beginner"):
            label = "Advanced-needed"
            status_code = "advanced_needed"
            gaps_count += 1
            est_hours = 35 if user_level == "beginner" else 20
        else:
            label = "Improve"
            status_code = "improve"
            gaps_count += 1
            est_hours = 15
            
        total_hours_needed += est_hours
        
        analyzed_skills.append({
            "skill": req["skill"],
            "target_level": target_level,
            "current_level": user_level,
            "current_score": user_score,
            "label": label,
            "status_code": status_code,
            "priority": priority,
            "weight": req.get("weight", 0.8),
            "est_hours_needed": est_hours,
            "is_verified": user_info["is_assessed"]
        })
        
    return {
        "target_role": target_role,
        "total_skills_evaluated": len(analyzed_skills),
        "strong_count": strong_count,
        "gaps_count": gaps_count,
        "total_hours_needed": total_hours_needed,
        "skills": analyzed_skills
    }
