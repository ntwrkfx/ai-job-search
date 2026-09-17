import json
import tempfile
import unittest
from pathlib import Path

from tools.career_compat.projection import ProjectionInputError, TARGET_REVISION, compile_projection


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "career_compat" / "candidate.json"


class ProjectionTests(unittest.TestCase):
    def test_compile_projection_emits_deterministic_manifest(self):
        source = json.loads(FIXTURE.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            manifest_a = compile_projection(source, Path(first))
            manifest_b = compile_projection(source, Path(second))

        self.assertEqual(manifest_a, manifest_b)
        self.assertEqual(manifest_a["schema"], "AiJobSearchProjectionManifest/v0")
        self.assertEqual(manifest_a["target_revision"], TARGET_REVISION)
        self.assertEqual(list(manifest_a["files"]), sorted(manifest_a["files"]))
        self.assertNotIn("generated_at", manifest_a)


    def test_projection_writes_exact_upstream_profile_files(self):
        source = json.loads(FIXTURE.read_text(encoding="utf-8"))
        expected = {
            ".claude/skills/job-application-assistant/01-candidate-profile.md",
            ".claude/skills/job-application-assistant/02-behavioral-profile.md",
            ".claude/skills/job-application-assistant/03-writing-style.md",
            ".claude/skills/job-application-assistant/07-interview-prep.md",
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = compile_projection(source, root)
            self.assertEqual(set(manifest["files"]), expected)
            self.assertTrue(all((root / path).is_file() for path in expected))

    def test_projection_preserves_source_bound_content(self):
        source = json.loads(FIXTURE.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            compile_projection(source, root)
            profile = (root / ".claude/skills/job-application-assistant/01-candidate-profile.md").read_text()
            behavior = (root / ".claude/skills/job-application-assistant/02-behavioral-profile.md").read_text()
            writing = (root / ".claude/skills/job-application-assistant/03-writing-style.md").read_text()
            interview = (root / ".claude/skills/job-application-assistant/07-interview-prep.md").read_text()
        for value in ["Casey Example", "Example Systems", "Example University", "Project Atlas", "Deterministic Systems", "Example Award"]:
            self.assertIn(value, profile)
        self.assertIn("user-provided assessment", behavior)
        self.assertIn("Prefer evidence-backed claims", writing)
        self.assertIn("Reliability recovery", interview)
        self.assertIn("story-1, exp-1", interview)

    def test_projection_files_are_byte_identical_for_same_input(self):
        source = json.loads(FIXTURE.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            a = Path(first)
            b = Path(second)
            manifest = compile_projection(source, a)
            compile_projection(source, b)
            for relative in manifest["files"]:
                self.assertEqual((a / relative).read_bytes(), (b / relative).read_bytes())


    def test_unknown_schema_writes_nothing(self):
        source = json.loads(FIXTURE.read_text(encoding="utf-8"))
        source["schema"] = "CareerCandidateProjectionInput/future"
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp) / "projection"
            with self.assertRaises(ProjectionInputError):
                compile_projection(source, output_root)
            self.assertFalse(output_root.exists())

    def test_missing_candidate_name_writes_nothing(self):
        source = json.loads(FIXTURE.read_text(encoding="utf-8"))
        del source["candidate"]["identity"]["name"]
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp) / "projection"
            with self.assertRaises(ProjectionInputError):
                compile_projection(source, output_root)
            self.assertFalse(output_root.exists())


if __name__ == "__main__":
    unittest.main()
