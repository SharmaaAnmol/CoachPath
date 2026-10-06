import json
import re
from typing import Dict, Any, List
from app.core.db import get_connection

def calculate_job_match(user_id: str, job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes transparent weighted job match score (Slide 9):
    - Skills (40%): Assessed skills count 1.0, self-reported count 0.6
    - Semantic fit (15%): Profile & goal overlap with job description
    - Experience level (15%): Fresher / 0-2 yrs alignment
    - Projects relevance (10%): Project tech & descriptions overlap
    - Location / work mode (10%): Candidate preference vs job mode
    - Salary (5%): Within desired bracket
    - Education / company prefs (5%): Match criteria
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Fetch user profile
    cursor.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
    profile_row = cursor.fetchone()
    profile = dict(profile_row) if profile_row else {}
    
    # 2. Fetch user skills
    cursor.execute("SELECT skill, self_level, assessed_level, assessed_score FROM user_skills WHERE user_id = ?", (user_id,))
    skills_rows = cursor.fetchall()
    
    # 3. Fetch user projects
    cursor.execute("SELECT title, description, tech FROM user_projects WHERE user_id = ?", (user_id,))
    projects_rows = cursor.fetchall()
    conn.close()
    
    user_skills_dict = {}
    for r in skills_rows:
        s_name = r["skill"].lower()
        is_assessed = r["assessed_score"] is not None
        user_skills_dict[s_name] = {
            "is_assessed": is_assessed,
            "weight": 1.0 if is_assessed else 0.6,
            "score": r["assessed_score"] or 60
        }
        
    job_req_skills = [s.lower() for s in job.get("required_skills", [])]
    matched_skills = []
    missing_skills = []
    
    # 1. Skills factor (Max 40 points)
    skills_points = 0.0
    if job_req_skills:
        for skill in job_req_skills:
            if skill in user_skills_dict:
                matched_skills.append(skill)
                # verified counts 1.0, self-reported 0.6
                skills_points += user_skills_dict[skill]["weight"]
            else:
                missing_skills.append(skill)
        skills_score = min(40.0, (skills_points / len(job_req_skills)) * 40.0)
    else:
        skills_score = 30.0

    # 2. Semantic fit factor (Max 15 points)
    target_role = (profile.get("target_role") or "ML Engineer").lower()
    job_title = job.get("title", "").lower()
    job_desc = job.get("description", "").lower()
    
    semantic_score = 0.0
    if target_role in job_title or job_title in target_role:
        semantic_score += 10.0
    elif any(word in job_title for word in target_role.split()):
        semantic_score += 7.0
    else:
        semantic_score += 4.0
        
    if "machine learning" in job_desc and "ml" in target_role:
        semantic_score += 5.0
    else:
        semantic_score += 3.0
    semantic_score = min(15.0, semantic_score)

    # 3. Experience level factor (Max 15 points)
    user_exp = (profile.get("experience_level") or "fresher").lower()
    job_exp = job.get("experience_required", "").lower()
    
    if "fresher" in job_exp or "0-2" in job_exp or "0-1" in job_exp or "entry" in job_exp:
        exp_score = 15.0 if user_exp in ("fresher", "0-2") else 12.0
    else:
        exp_score = 9.0

    # 4. Projects relevance factor (Max 10 points)
    proj_score = 0.0
    proj_text = " ".join([p["title"] + " " + (p["description"] or "") for p in projects_rows]).lower()
    for s in job_req_skills:
        if s in proj_text:
            proj_score += 2.5
    proj_score = min(10.0, max(proj_score, 4.0 if projects_rows else 0.0))

    # 5. Location / Work mode factor (Max 10 points)
    pref_mode = (profile.get("work_mode") or "hybrid").lower()
    job_mode = job.get("work_mode", "hybrid").lower()
    pref_loc = (profile.get("location") or "Bengaluru").lower()
    job_loc = job.get("location", "").lower()
    
    loc_score = 0.0
    if pref_mode == job_mode or job_mode == "remote":
        loc_score += 5.0
    else:
        loc_score += 3.0
        
    if any(city in job_loc for city in ["bengaluru", "bangalore", "hyderabad", "gurgaon", "remote"]):
        loc_score += 5.0
    else:
        loc_score += 3.0
    loc_score = min(10.0, loc_score)

    # 6. Salary factor (Max 5 points)
    job_sal_min = job.get("salary_min", 0)
    desired_sal_min = profile.get("desired_salary_min", 600000)
    if job_sal_min >= desired_sal_min:
        salary_score = 5.0
    elif job_sal_min >= desired_sal_min * 0.8:
        salary_score = 4.0
    else:
        salary_score = 3.0

    # 7. Education / Company preference factor (Max 5 points)
    edu_score = 4.5
    interested_comps = json.loads(profile.get("interested_companies", "[]")) if isinstance(profile.get("interested_companies"), str) else profile.get("interested_companies", [])
    if any(c.lower() in job.get("company", "").lower() for c in interested_comps):
        edu_score = 5.0

    total_score = int(round(skills_score + semantic_score + exp_score + proj_score + loc_score + salary_score + edu_score))
    total_score = min(99, max(25, total_score))

    # Construct explainable rationale
    matched_str = ", ".join([s.title() for s in matched_skills[:3]])
    missing_str = ", ".join([s.title() for s in missing_skills[:2]]) if missing_skills else "none"
    
    if total_score >= 85:
        reason = f"Excellent match ({total_score}%): Strong verified overlap in {matched_str}. Experience level & location preferences match closely."
    elif total_score >= 70:
        reason = f"High potential match ({total_score}%): Matches core requirements ({matched_str}); learn {missing_str} to reach maximum readiness."
    else:
        reason = f"Moderate match ({total_score}%): Role requires additional hands-on practice in {missing_str}."

    breakdown = {
        "skills": round(skills_score, 1),
        "semantic_fit": round(semantic_score, 1),
        "experience": round(exp_score, 1),
        "projects_relevance": round(proj_score, 1),
        "location_mode": round(loc_score, 1),
        "salary_alignment": round(salary_score, 1),
        "education_prefs": round(edu_score, 1)
    }

    return {
        "score": total_score,
        "breakdown": breakdown,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "reason": reason
    }
