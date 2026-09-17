import unittest
from pathlib import Path

from tools.career_compat.tracker import parse_tracker


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "career_compat" / "tracker.csv"


class TrackerTests(unittest.TestCase):
    def test_parse_tracker_returns_observations(self):
        observations = parse_tracker(FIXTURE)
        self.assertEqual(len(observations), 4)
        by_status = {item["observed_status"]: item for item in observations}
        self.assertEqual(set(by_status), {"ranked", "applied", "interview", "rejected"})
        for item in observations:
            self.assertEqual(item["schema"], "CareerWorkflowObservation/v0")
            self.assertEqual(item["source_system"], "ai-job-search")
            self.assertIn("::", item["application_key"])
            self.assertEqual(len(item["source_row_digest"]), 64)
        self.assertFalse(by_status["ranked"]["terminal"])
        self.assertFalse(by_status["applied"]["terminal"])
        self.assertFalse(by_status["interview"]["terminal"])
        self.assertTrue(by_status["rejected"]["terminal"])


if __name__ == "__main__":
    unittest.main()
