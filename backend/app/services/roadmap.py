import json
import uuid
from typing import Dict, Any, List
from app.core.config import DATA_DIR
from app.core.db import get_connection
from app.services.gap import analyze_skill_gap

def load_resources() -> List[Dict[str, Any]]:
    res_file = DATA_DIR / "resources.json"
    if res_file.exists():
        with open(res_file, "r") as f:
            return json.load(f)
    return []

# Dependency order tiers
SKILL_DEPENDENCY_TIERS = {
    "python": 1,
    "sql": 1,
    "git": 1,
    "data structures": 2,
    "numpy": 2,
    "pandas": 2,
    "machine learning": 3,
    "scikit-learn": 3,
    "matplotlib": 3,
    "fastapi": 3,
    "docker": 4,
    "pytorch": 4,
    "mlops": 5,
    "generative ai": 5,
    "system design": 5
}

def generate_personalized_roadmap(user_id: str) -> Dict[str, Any]:
    """
    Generates a personalized, constrained, dependency-ordered roadmap.
    Maps curated free resources (NPTEL, SWAYAM, freeCodeCamp, CS50).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT target_role, target_timeline_months, hours_per_weekday, hours_per_weekend FROM profiles WHERE user_id = ?", (user_id,))
    profile = cursor.fetchone()
    
    if not profile:
        target_role = "ML Engineer"
        timeline_months = 4
        hours_weekday = 2.0
        hours_weekend = 5.0
    else:
        target_role = profile["target_role"] or "ML Engineer"
        timeline_months = profile["target_timeline_months"] or 4
        hours_weekday = profile["hours_per_weekday"] or 2.0
        hours_weekend = profile["hours_per_weekend"] or 5.0

    # Total weekly hours = 5 * weekday + 2 * weekend
    weekly_hours = (5 * hours_weekday) + (2 * hours_weekend) # e.g. 10 + 10 = 20 hrs/week
    total_weeks = timeline_months * 4 # e.g. 16 weeks
    available_total_hours = weekly_hours * total_weeks # e.g. 320 hours
    
    # Gap analysis
    gap_data = analyze_skill_gap(user_id, target_role)
    gap_skills = [s for s in gap_data["skills"] if s["status_code"] != "strong"]
    
    # Sort skills by dependency tier, then weight
    gap_skills.sort(key=lambda s: (SKILL_DEPENDENCY_TIERS.get(s["skill"].lower(), 3), -s["weight"]))
    
    all_resources = load_resources()
    
    # Generate schedule items
    roadmap_items = []
    current_week = 1
    current_month = 1
    
    for item in gap_skills:
        skill_name = item["skill"].lower()
        est_hours = item["est_hours_needed"]
        weeks_for_skill = max(1, round(est_hours / weekly_hours))
        
        # Pick relevant curated resources
        matched_res = [
            {"title": r["title"], "url": r["url"], "type": r["type"], "platform": r["platform"]}
            for r in all_resources if r["skill"].lower() == skill_name
        ]
        if not matched_res:
            matched_res = [
                {"title": f"{item['skill']} Official Quickstart & Docs", "url": "https://devdocs.io", "type": "free", "platform": "Web"},
                {"title": f"{item['skill']} Hands-on Placement Practice", "url": "https://geeksforgeeks.org", "type": "free", "platform": "GeeksforGeeks"}
            ]
            
        for w in range(weeks_for_skill):
            if current_week > total_weeks:
                break
            
            title = f"Master {item['skill'].title()} ({item['label']}) - Part {w + 1}/{weeks_for_skill}" if weeks_for_skill > 1 else f"Master {item['skill'].title()} ({item['label']})"
            
            roadmap_items.append({
                "month": ((current_week - 1) // 4) + 1,
                "week": current_week,
                "title": title,
                "skill": item["skill"],
                "priority": item["priority"],
                "resources": matched_res,
                "est_hours": int(weekly_hours),
                "status": "todo"
            })
            current_week += 1

    # Cap weeks to timeline
    while current_week <= total_weeks:
        m = ((current_week - 1) // 4) + 1
        roadmap_items.append({
            "month": m,
            "week": current_week,
            "title": f"Capstone Project Implementation & Placement Mock Interviews (Week {current_week})",
            "skill": "Placement Readiness",
            "priority": "required",
            "resources": [
                {"title": "Striver's Placement Interview Series", "url": "https://takeuforward.org", "type": "free", "platform": "Take U Forward"},
                {"title": "System Design & Project Portfolio Polish", "url": "https://github.com/donnemartin/system-design-primer", "type": "free", "platform": "GitHub"}
            ],
            "est_hours": int(weekly_hours),
            "status": "todo"
        })
        current_week += 1

    # Save roadmap into database
    roadmap_id = str(uuid.uuid4())
    cursor.execute("UPDATE roadmaps SET is_active = 0 WHERE user_id = ?", (user_id,))
    cursor.execute("INSERT INTO roadmaps (id, user_id, version, is_active) VALUES (?, ?, 1, 1)", (roadmap_id, user_id))
    
    for it in roadmap_items:
        cursor.execute(
            """
            INSERT INTO roadmap_items (id, roadmap_id, month, week, title, skill, priority, resources, est_hours, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                roadmap_id,
                it["month"],
                it["week"],
                it["title"],
                it["skill"],
                it["priority"],
                json.dumps(it["resources"]),
                it["est_hours"],
                it["status"]
            )
        )
    conn.commit()
    conn.close()
    
    return {
        "roadmap_id": roadmap_id,
        "target_role": target_role,
        "timeline_months": timeline_months,
        "weekly_hours": weekly_hours,
        "available_total_hours": available_total_hours,
        "total_items": len(roadmap_items),
        "items": roadmap_items
    }

def get_active_roadmap(user_id: str) -> Dict[str, Any]:
    """Retrieves the active roadmap for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM roadmaps WHERE user_id = ? AND is_active = 1 ORDER BY generated_at DESC LIMIT 1", (user_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return generate_personalized_roadmap(user_id)
        
    roadmap_id = row["id"]
    cursor.execute("SELECT id, month, week, title, skill, priority, resources, est_hours, status FROM roadmap_items WHERE roadmap_id = ? ORDER BY week ASC", (roadmap_id,))
    items_rows = cursor.fetchall()
    conn.close()
    
    items = []
    for r in items_rows:
        items.append({
            "id": r["id"],
            "month": r["month"],
            "week": r["week"],
            "title": r["title"],
            "skill": r["skill"],
            "priority": r["priority"],
            "resources": json.loads(r["resources"]) if r["resources"] else [],
            "est_hours": r["est_hours"],
            "status": r["status"]
        })
        
    return {
        "roadmap_id": roadmap_id,
        "total_items": len(items),
        "items": items
    }
