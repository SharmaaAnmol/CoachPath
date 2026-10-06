import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.services.roadmap import generate_personalized_roadmap

class TestRoadmapGeneration(unittest.TestCase):
    def test_roadmap_constrained_by_hours(self):
        res = generate_personalized_roadmap(settings.DEFAULT_USER_ID)
        self.assertIn("roadmap_id", res)
        self.assertIn("items", res)
        self.assertGreater(len(res["items"]), 0)
        
        # Verify weekly hours constraint is respected
        self.assertEqual(res["weekly_hours"], 20.0) # 5*2 + 2*5 = 20
        self.assertGreaterEqual(res["total_items"], 1)
        
        # Verify items have resources mapped
        first_item = res["items"][0]
        self.assertIn("resources", first_item)
        self.assertIn("priority", first_item)
        self.assertIn("est_hours", first_item)

if __name__ == "__main__":
    unittest.main()
