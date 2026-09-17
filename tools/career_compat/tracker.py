"""Read-only import of ai-job-search tracker state as observations."""

import csv
from pathlib import Path

from .common import canonical_json_bytes, sha256_hex

OBSERVATION_SCHEMA = "CareerWorkflowObservation/v0"
FINAL_STATUSES = {"hired", "rejected", "no_response", "offer_declined", "withdrawn", "expired"}


def _normalize_key_part(value: str) -> str:
    return " ".join(value.strip().casefold().split())


def parse_tracker(path: Path) -> list[dict[str, object]]:
    observations: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            status = row["status"].strip()
            observations.append({
                "schema": OBSERVATION_SCHEMA,
                "source_system": "ai-job-search",
                "application_key": f"{_normalize_key_part(row['company'])}::{_normalize_key_part(row['role'])}",
                "observed_status": status,
                "terminal": status in FINAL_STATUSES,
                "source_row_digest": sha256_hex(canonical_json_bytes(row)),
                "row": dict(row),
            })
    return observations
