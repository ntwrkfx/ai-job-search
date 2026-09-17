"""Deterministic projection of canonical career data into ai-job-search files."""

import json
from pathlib import Path
from typing import Any

from .common import canonical_json_bytes, sha256_hex

TARGET_REVISION = "09435eb1a572eddbd0180e8ea9c3acf84f90604a"
SOURCE_SCHEMA = "CareerCandidateProjectionInput/v0"
MANIFEST_SCHEMA = "AiJobSearchProjectionManifest/v0"


def compile_projection(source: dict[str, Any], output_root: Path) -> dict[str, Any]:
    if source.get("schema") != SOURCE_SCHEMA:
        raise ValueError(f"unsupported source schema: {source.get('schema')!r}")

    manifest = {
        "schema": MANIFEST_SCHEMA,
        "source_schema": SOURCE_SCHEMA,
        "source_digest": sha256_hex(canonical_json_bytes(source)),
        "target_revision": TARGET_REVISION,
        "files": {},
    }
    manifest_path = output_root / ".career-compat" / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_bytes(canonical_json_bytes(manifest) + b"\n")
    return json.loads(manifest_path.read_text(encoding="utf-8"))
