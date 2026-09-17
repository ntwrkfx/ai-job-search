import json
import tempfile
import unittest
from pathlib import Path

from tools.career_compat.projection import TARGET_REVISION, compile_projection


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


if __name__ == "__main__":
    unittest.main()
