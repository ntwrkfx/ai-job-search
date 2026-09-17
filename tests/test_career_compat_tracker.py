import tempfile
import unittest
from pathlib import Path

from tools.career_compat.tracker import (
    TrackerConflict, TrackerRowError, TrackerSchemaError, UnknownTrackerStatus, parse_tracker,
)


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


    def _write_tracker(self, rows, header=None):
        header = header or "date,company,sector,role,role_type,channel,status,contact_person,fit_rating,notes,cv_file,cover_letter_file,source,deadline"
        tmp = tempfile.TemporaryDirectory()
        path = Path(tmp.name) / "tracker.csv"
        path.write_text(header + "\n" + "\n".join(rows) + "\n", encoding="utf-8")
        self.addCleanup(tmp.cleanup)
        return path

    def test_wrong_header_fails_closed(self):
        path = self._write_tracker([], header="date,company,role,status")
        with self.assertRaises(TrackerSchemaError):
            parse_tracker(path)

    def test_unknown_status_fails_closed(self):
        path = self._write_tracker([
            "2026-09-05,Acme,Tech,Engineer,technical,portal,future_state,,,,,,https://example.test/acme,"
        ])
        with self.assertRaises(UnknownTrackerStatus):
            parse_tracker(path)

    def test_missing_company_or_role_fails_closed(self):
        path = self._write_tracker([
            "2026-09-05,,Tech,Engineer,technical,portal,applied,,,,,,https://example.test/acme,"
        ])
        with self.assertRaises(TrackerRowError):
            parse_tracker(path)

    def test_conflicting_open_states_fail_closed(self):
        path = self._write_tracker([
            "2026-09-05,Acme,Tech,Engineer,technical,portal,applied,,,,,,https://example.test/acme,",
            "2026-09-06, ACME ,Tech, engineer ,technical,portal,interview,,,,,,https://example.test/acme,",
        ])
        with self.assertRaises(TrackerConflict):
            parse_tracker(path)

    def test_exact_duplicate_rows_collapse_by_digest(self):
        row = "2026-09-05,Acme,Tech,Engineer,technical,portal,applied,,,,,,https://example.test/acme,"
        path = self._write_tracker([row, row])
        self.assertEqual(len(parse_tracker(path)), 1)

    def test_final_history_can_coexist_with_later_open_state(self):
        path = self._write_tracker([
            "2026-08-01,Acme,Tech,Engineer,technical,portal,rejected,,,,,,https://example.test/old,",
            "2026-09-05,Acme,Tech,Engineer,technical,portal,applied,,,,,,https://example.test/new,",
        ])
        observations = parse_tracker(path)
        self.assertEqual([item["observed_status"] for item in observations], ["rejected", "applied"])

    def test_parse_tracker_does_not_modify_source_file(self):
        before = FIXTURE.read_bytes()
        parse_tracker(FIXTURE)
        self.assertEqual(FIXTURE.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
