import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.services.readiness import calculate_readiness

class TestReadiness(unittest.TestCase):
    def test_readiness_calculation(self):
        res = calculate_readiness(settings.DEFAULT_USER_ID)
        self.assertIn("overall", res)
        self.assertGreaterEqual(res["overall"], 0)
        self.assertLessEqual(res["overall"], 100)
        
        comps = res["components"]
        for c in ["technical", "dsa", "projects", "resume", "interview", "industry", "job_readiness"]:
            self.assertIn(c, comps)
            self.assertGreaterEqual(comps[c], 0)
            self.assertLessEqual(comps[c], 100)
            
        lever = res["biggest_lever"]
        self.assertIn("component", lever)
        self.assertIn("recommendation", lever)
        self.assertGreater(lever["projected_overall"], res["overall"])

if __name__ == "__main__":
    unittest.main()
