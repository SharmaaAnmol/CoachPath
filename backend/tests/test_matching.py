import unittest
import sys
from pathlib import Path

# Add backend to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.services.matching import calculate_job_match

class TestJobMatching(unittest.TestCase):
    def test_weighted_matching_score_range(self):
        sample_job = {
            "id": "test-job-1",
            "title": "Machine Learning Engineer",
            "company": "Swiggy",
            "location": "Bengaluru",
            "work_mode": "hybrid",
            "salary_min": 1200000,
            "salary_max": 1800000,
            "experience_required": "0-2 years",
            "required_skills": ["python", "machine learning", "fastapi", "sql", "docker"],
            "description": "Building machine learning dispatch optimization."
        }
        res = calculate_job_match(settings.DEFAULT_USER_ID, sample_job)
        
        self.assertIn("score", res)
        self.assertGreaterEqual(res["score"], 0)
        self.assertLessEqual(res["score"], 100)
        
        # Breakdown checks
        breakdown = res["breakdown"]
        self.assertIn("skills", breakdown)
        self.assertIn("semantic_fit", breakdown)
        self.assertIn("experience", breakdown)
        self.assertIn("projects_relevance", breakdown)
        self.assertIn("location_mode", breakdown)
        self.assertIn("salary_alignment", breakdown)
        self.assertIn("education_prefs", breakdown)
        
        # Verify explainable reason is returned
        self.assertTrue(len(res["reason"]) > 10)
        self.assertIn("match", res["reason"].lower())

if __name__ == "__main__":
    unittest.main()
