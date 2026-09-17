"""Deterministic projection of canonical career data into ai-job-search files."""

import json
from pathlib import Path
from typing import Any

from .common import canonical_json_bytes, sha256_hex

TARGET_REVISION = "09435eb1a572eddbd0180e8ea9c3acf84f90604a"
SOURCE_SCHEMA = "CareerCandidateProjectionInput/v0"
MANIFEST_SCHEMA = "AiJobSearchProjectionManifest/v0"

PROFILE_BASE = ".claude/skills/job-application-assistant"
PROFILE_PATHS = {
    "candidate": f"{PROFILE_BASE}/01-candidate-profile.md",
    "behavior": f"{PROFILE_BASE}/02-behavioral-profile.md",
    "writing": f"{PROFILE_BASE}/03-writing-style.md",
    "interview": f"{PROFILE_BASE}/07-interview-prep.md",
}


def _evidence(item: dict[str, Any]) -> str | None:
    values = item.get("evidence_ids") or []
    return ", ".join(str(value) for value in values) if values else None


def _append_evidence(lines: list[str], item: dict[str, Any]) -> None:
    evidence = _evidence(item)
    if evidence:
        lines.append(f"Evidence: {evidence}")


def _render_candidate_profile(source: dict[str, Any]) -> str:
    candidate = source.get("candidate", {})
    identity = candidate.get("identity", {})
    lines = ["# Candidate Profile", "", "## Identity"]
    for label, key in [
        ("Name", "name"), ("Location", "location"), ("Phone", "phone"),
        ("Email", "email"), ("LinkedIn", "linkedin"), ("GitHub", "github"),
        ("Status", "status"), ("Constraints", "constraints"),
    ]:
        lines.append(f"- **{label}:** {identity.get(key) or 'None recorded.'}")

    lines.extend(["", "### Languages"])
    languages = candidate.get("languages") or []
    if languages:
        lines.extend(["| Language | Level | Notes |", "|---|---|---|"])
        for item in languages:
            lines.append(f"| {item.get('language', '')} | {item.get('level', '')} | {item.get('notes', '')} |")
    else:
        lines.append("None recorded.")

    lines.extend(["", "## Education"])
    education = candidate.get("education") or []
    if not education:
        lines.append("None recorded.")
    for item in education:
        topics = ", ".join(item.get("topics") or [])
        lines.append(f"- **{item.get('degree', '')}**, {item.get('institution', '')} ({item.get('period', '')}) — {topics}")
        _append_evidence(lines, item)

    lines.extend(["", "## Professional Experience"])
    experiences = candidate.get("experiences") or []
    if not experiences:
        lines.append("None recorded.")
    for item in experiences:
        lines.extend([
            f"### {item.get('title', '')} - {item.get('company', '')} ({item.get('period', '')})",
            item.get("location") or "",
        ])
        for achievement in item.get("achievements") or []:
            lines.append(f"- {achievement}")
        _append_evidence(lines, item)

    lines.extend(["", "## Independent Projects"])
    projects = candidate.get("projects") or []
    if not projects:
        lines.append("None recorded.")
    for item in projects:
        lines.append(f"- **{item.get('name', '')}:** {item.get('description', '')}")
        _append_evidence(lines, item)

    lines.extend(["", "## Technical Skills"])
    skills = candidate.get("skills") or {}
    for heading, key in [
        ("Programming & ML", "programming_and_ml"),
        ("Domain Expertise", "domain_expertise"),
        ("Software & Tools", "software_and_tools"),
    ]:
        lines.extend(["", f"### {heading}"])
        values = skills.get(key) or []
        lines.append(", ".join(values) if values else "None recorded.")

    lines.extend(["", "## Publications"])
    publications = candidate.get("publications") or []
    if not publications:
        lines.append("None recorded.")
    for item in publications:
        lines.append(
            f"- {item.get('authors', '')} ({item.get('year', '')}). {item.get('title', '')}. "
            f"{item.get('venue', '')}. {item.get('url', '')}".rstrip()
        )
        _append_evidence(lines, item)

    lines.extend(["", "## Awards & Recognition"])
    recognitions = candidate.get("recognitions") or []
    if not recognitions:
        lines.append("None recorded.")
    for item in recognitions:
        lines.append(f"- {item.get('title', '')} - {item.get('organization', '')} ({item.get('year', '')})")
        _append_evidence(lines, item)

    lines.extend(["", "## References"])
    references = candidate.get("references") or []
    if not references:
        lines.append("None recorded.")
    for item in references:
        lines.append(
            f"- {item.get('name', '')}, {item.get('title', '')}, {item.get('company', '')} "
            f"({item.get('email', '')}, {item.get('phone', '')})"
        )
    return "\n".join(lines).rstrip() + "\n"


def _render_behavioral_profile(source: dict[str, Any]) -> str:
    assessments = source.get("behavioral_assessments") or []
    lines = ["# Behavioral Profile", ""]
    if not assessments:
        lines.append("None recorded.")
        return "\n".join(lines).rstrip() + "\n"
    for index, item in enumerate(assessments, start=1):
        lines.extend([
            f"## Assessment {index}: {item.get('type', 'Unspecified')}",
            f"- **Profile:** {item.get('profile') or 'None recorded.'}",
            f"- **Source:** {item.get('source') or 'None recorded.'}",
            f"- **Observed:** {item.get('observed_at') or 'None recorded.'}",
            f"- **Summary:** {item.get('summary') or 'None recorded.'}",
            "",
            "### Drives",
        ])
        drives = item.get("drives") or []
        lines.append("None recorded." if not drives else "")
        for drive in drives:
            lines.append(f"- **{drive.get('name', '')} ({drive.get('level', '')}):** {drive.get('meaning', '')}")
        for heading, key in [("Strengths", "strengths"), ("How You Work Best", "work_preferences"), ("Growth Areas", "growth_areas")]:
            lines.extend(["", f"### {heading}"])
            values = item.get(key) or []
            lines.extend([f"- {value}" for value in values] or ["None recorded."])
    return "\n".join(lines).rstrip() + "\n"


def _render_writing_style(source: dict[str, Any]) -> str:
    prefs = source.get("writing_preferences") or {}
    lines = ["# Writing Style Guide"]
    for heading, key in [("Tone", "tone"), ("Avoid", "avoid"), ("Rules", "rules")]:
        lines.extend(["", f"## {heading}"])
        values = prefs.get(key) or []
        lines.extend([f"- {value}" for value in values] or ["None recorded."])
    return "\n".join(lines).rstrip() + "\n"


def _render_interview_prep(source: dict[str, Any]) -> str:
    stories = source.get("stories") or []
    lines = ["# Interview Preparation Guide", "", "## Evidence-backed STAR Stories"]
    if not stories:
        lines.append("None recorded.")
        return "\n".join(lines).rstrip() + "\n"
    for index, item in enumerate(stories, start=1):
        lines.extend([
            "",
            f"### {index}. {item.get('title', '')} ({item.get('skill', '')})",
            f"**S:** {item.get('situation', '')}",
            f"**T:** {item.get('task', '')}",
            f"**A:** {item.get('action', '')}",
            f"**R:** {item.get('result', '')}",
            f"**Use for:** {', '.join(item.get('use_for') or [])}",
        ])
        _append_evidence(lines, item)
    return "\n".join(lines).rstrip() + "\n"


def compile_projection(source: dict[str, Any], output_root: Path) -> dict[str, Any]:
    if source.get("schema") != SOURCE_SCHEMA:
        raise ValueError(f"unsupported source schema: {source.get('schema')!r}")

    rendered = {
        PROFILE_PATHS["candidate"]: _render_candidate_profile(source),
        PROFILE_PATHS["behavior"]: _render_behavioral_profile(source),
        PROFILE_PATHS["writing"]: _render_writing_style(source),
        PROFILE_PATHS["interview"]: _render_interview_prep(source),
    }
    files = {
        relative: sha256_hex(content.encode("utf-8"))
        for relative, content in sorted(rendered.items())
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "source_schema": SOURCE_SCHEMA,
        "source_digest": sha256_hex(canonical_json_bytes(source)),
        "target_revision": TARGET_REVISION,
        "files": files,
    }

    for relative, content in rendered.items():
        path = output_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    manifest_path = output_root / ".career-compat" / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_bytes(canonical_json_bytes(manifest) + b"\n")
    return json.loads(manifest_path.read_text(encoding="utf-8"))
