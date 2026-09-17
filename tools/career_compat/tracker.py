"""Read-only import of ai-job-search tracker state as observations."""

import csv
from pathlib import Path

from .common import canonical_json_bytes, sha256_hex

OBSERVATION_SCHEMA = "CareerWorkflowObservation/v0"
TRACKER_HEADER = (
    "date", "company", "sector", "role", "role_type", "channel", "status",
    "contact_person", "fit_rating", "notes", "cv_file", "cover_letter_file",
    "source", "deadline",
)
FINAL_STATUSES = {"hired", "rejected", "no_response", "offer_declined", "withdrawn", "expired"}
OPEN_STATUSES = {"ranked", "drafted", "applied", "interview", "offer"}
RECOGNIZED_STATUSES = FINAL_STATUSES | OPEN_STATUSES


class TrackerSchemaError(ValueError):
    """Tracker columns do not match the pinned upstream contract."""


class TrackerRowError(ValueError):
    """A tracker row lacks required identity fields."""


class UnknownTrackerStatus(ValueError):
    """A tracker row contains a status outside the pinned vocabulary."""


class TrackerConflict(ValueError):
    """Open workflow evidence conflicts for the same normalized application."""


def _normalize_key_part(value: str) -> str:
    return " ".join(value.strip().casefold().split())


def _observation_from_row(row: dict[str, str]) -> dict[str, object]:
    company = (row.get("company") or "").strip()
    role = (row.get("role") or "").strip()
    if not company or not role:
        raise TrackerRowError("tracker rows require non-empty company and role")

    status = (row.get("status") or "").strip()
    if status not in RECOGNIZED_STATUSES:
        raise UnknownTrackerStatus(f"unknown tracker status: {status!r}")

    return {
        "schema": OBSERVATION_SCHEMA,
        "source_system": "ai-job-search",
        "application_key": f"{_normalize_key_part(company)}::{_normalize_key_part(role)}",
        "observed_status": status,
        "terminal": status in FINAL_STATUSES,
        "source_row_digest": sha256_hex(canonical_json_bytes(row)),
        "row": dict(row),
    }


def _check_open_conflicts(observations: list[dict[str, object]]) -> None:
    open_by_key: dict[str, set[str]] = {}
    for item in observations:
        if item["terminal"]:
            continue
        key = str(item["application_key"])
        open_by_key.setdefault(key, set()).add(str(item["observed_status"]))
    conflicts = {key: statuses for key, statuses in open_by_key.items() if len(statuses) > 1}
    if conflicts:
        key = sorted(conflicts)[0]
        statuses = ", ".join(sorted(conflicts[key]))
        raise TrackerConflict(f"conflicting open statuses for {key}: {statuses}")


def parse_tracker(path: Path) -> list[dict[str, object]]:
    observations: list[dict[str, object]] = []
    seen_digests: set[str] = set()
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != TRACKER_HEADER:
            raise TrackerSchemaError(
                f"tracker header must equal {','.join(TRACKER_HEADER)}"
            )
        for row in reader:
            if None in row:
                raise TrackerRowError("tracker row has extra columns")
            observation = _observation_from_row(row)
            digest = str(observation["source_row_digest"])
            if digest in seen_digests:
                continue
            seen_digests.add(digest)
            observations.append(observation)

    _check_open_conflicts(observations)
    return observations
