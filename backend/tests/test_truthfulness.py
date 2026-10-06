import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ai.truth_check import verify_resume_truthfulness

class TestTruthfulnessChecker(unittest.TestCase):
    def setUp(self):
        self.master_resume = {
            "summary": "Computer Science student proficient in Python and Scikit-Learn.",
            "skills": ["Python", "SQL", "Scikit-Learn", "FastAPI"],
            "experience": [
                {
                    "company": "Kubernetix Tech Labs",
                    "role": "Machine Learning Intern",
                    "bullets": ["Trained baseline models reducing ingestion errors by 32%."]
                }
            ],
            "projects": [
                {
                    "title": "Customer Churn Prediction Engine",
                    "bullets": ["Reached 84% ROC-AUC with SMOTE balancing."]
                }
            ],
            "education": [{"institution": "Visvesvaraya Technological University", "degree": "B.Tech CSE"}]
        }

    def test_truthful_tailored_resume_passes(self):
        tailored = {
            "summary": "Computer Science student proficient in Python and Scikit-Learn.",
            "skills": ["Python", "FastAPI", "SQL", "Scikit-Learn"],
            "experience": [
                {
                    "company": "Kubernetix Tech Labs",
                    "role": "Machine Learning Intern",
                    "bullets": ["Trained baseline models reducing ingestion errors by 32%."]
                }
            ],
            "projects": [
                {
                    "title": "Customer Churn Prediction Engine",
                    "bullets": ["Reached 84% ROC-AUC with SMOTE balancing."]
                }
            ]
        }
        is_valid, violations, diff = verify_resume_truthfulness(self.master_resume, tailored)
        self.assertTrue(is_valid)
        self.assertEqual(len([v for v in violations if "Unverified" in v]), 0)

    def test_hallucinated_skill_or_employer_fails(self):
        hallucinated = {
            "skills": ["Python", "Kubernetes", "Quantum Computing", "Google Brain Intern"],
            "experience": [
                {
                    "company": "Google",
                    "role": "Senior Staff Architect",
                    "bullets": ["Built TPU infrastructure from scratch."]
                }
            ],
            "projects": []
        }
        is_valid, violations, diff = verify_resume_truthfulness(self.master_resume, hallucinated)
        self.assertFalse(is_valid)
        self.assertGreater(len(violations), 0)
        # Check that unverified skills and unverified employer are caught
        violations_text = " ".join(violations)
        self.assertIn("Google", violations_text)
        self.assertIn("Kubernetes", violations_text)

if __name__ == "__main__":
    unittest.main()
