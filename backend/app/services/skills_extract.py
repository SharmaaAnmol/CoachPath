import json
import re
from typing import List, Set
from pathlib import Path
from app.core.config import DATA_DIR

def load_skills_taxonomy() -> dict:
    taxonomy_file = DATA_DIR / "skills_taxonomy.json"
    if taxonomy_file.exists():
        with open(taxonomy_file, "r") as f:
            return json.load(f)
    return {}

def extract_skills_from_text(text: str) -> List[str]:
    """
    Extracts technical skills from job descriptions or resumes using taxonomy regex matching.
    Matches aliases (e.g., 'torch' -> 'pytorch', 'postgres' -> 'postgresql').
    """
    if not text:
        return []
        
    taxonomy = load_skills_taxonomy()
    found_skills: Set[str] = set()
    lowered_text = " " + text.lower() + " "
    
    for category, skills in taxonomy.items():
        for canonical_name, aliases in skills.items():
            for alias in aliases:
                # Use word boundary matching
                pattern = r'(?:^|[\s,;./()\[\]])' + re.escape(alias.lower()) + r'(?:$|[\s,;./()\[\]])'
                if re.search(pattern, lowered_text):
                    found_skills.add(canonical_name)
                    break
                    
    return sorted(list(found_skills))
