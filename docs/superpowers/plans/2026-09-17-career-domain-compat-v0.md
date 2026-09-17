# Career Domain Compatibility v0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic compatibility compiler and read-only tracker importer between canonical career-domain data and upstream `ai-job-search`.

**Architecture:** Keep upstream workflow files unmodified. A stdlib-only Python package under `tools/career_compat/` renders disposable profile projections into a caller-supplied root and emits a deterministic SHA-256 manifest. A separate tracker module validates the exact upstream CSV schema and returns observation proposals without mutating source or canonical state.

**Tech Stack:** Python 3.10+ standard library, `unittest`, `pathlib`, `json`, `csv`, `hashlib`, `tempfile`.

**Spec:** `docs/superpowers/specs/2026-09-17-career-domain-compat-design.md`

## Global Constraints

- Authority effect: NONE.
- Production adoption is not authorized by this slice.
- Target upstream revision is `09435eb1a572eddbd0180e8ea9c3acf84f90604a`.
- Use Python standard library only; add no dependencies.
- No network, provider, model, email, job-board, or application-submission calls.
- No production code may be written before its failing test is observed.
- Unknown or conflicting tracker evidence fails closed.
- Projection output must be deterministic and disposable.

---

### Task 1: Canonical hashing and deterministic projection manifest

**Files:**
- Create: `tools/career_compat/__init__.py`
- Create: `tools/career_compat/common.py`
- Create: `tools/career_compat/projection.py`
- Create: `tests/test_career_compat_projection.py`
- Create: `tests/fixtures/career_compat/candidate.json`

**Interfaces:**
- Produces: `canonical_json_bytes(value: object) -> bytes`
- Produces: `sha256_hex(data: bytes) -> str`
- Produces: `compile_projection(source: dict, output_root: pathlib.Path) -> dict`
- Manifest schema: `AiJobSearchProjectionManifest/v0`

- [ ] **Step 1: Add synthetic canonical fixture and failing manifest test**

Create a fixture with schema `CareerCandidateProjectionInput/v0`, one language, one education record, one experience, one project, grouped skills, one publication, one recognition, one reference, one behavioral assessment, writing preferences, and one STAR story. Use synthetic names such as `Casey Example` and `Example Systems`; no real personal data.

Add this test:

```python
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
```

- [ ] **Step 2: Run the test and verify RED**

Run:

```bash
python -m unittest tests.test_career_compat_projection.ProjectionTests.test_compile_projection_emits_deterministic_manifest -v
```

Expected: failure because `tools.career_compat.projection` or `compile_projection` does not exist.

- [ ] **Step 3: Implement canonical serialization, SHA-256 helpers, and minimal manifest generation**

`canonical_json_bytes` must call `json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")`.

`compile_projection` must validate only the top-level schema at this step, calculate `source_digest`, create an empty sorted file map, write `.career-compat/manifest.json` using canonical JSON plus trailing newline, and return the parsed manifest.

- [ ] **Step 4: Run the focused test and verify GREEN**

Run the same command. Expected: PASS.

- [ ] **Step 5: Commit Task 1**

```bash
git add tools/career_compat tests/test_career_compat_projection.py tests/fixtures/career_compat/candidate.json
git commit -m "feat: add deterministic career projection manifest"
```

### Task 2: Render the four upstream profile projections atomically

**Files:**
- Modify: `tools/career_compat/projection.py`
- Modify: `tests/test_career_compat_projection.py`

**Interfaces:**
- `compile_projection(source, output_root)` writes exactly four upstream Markdown projections plus `.career-compat/manifest.json`.
- Relative paths are fixed by the design spec.

- [ ] **Step 1: Add failing tests for rendered files, evidence discipline, and deterministic bytes**

Add tests that assert:

```python
expected = {
    ".claude/skills/job-application-assistant/01-candidate-profile.md",
    ".claude/skills/job-application-assistant/02-behavioral-profile.md",
    ".claude/skills/job-application-assistant/03-writing-style.md",
    ".claude/skills/job-application-assistant/07-interview-prep.md",
}
self.assertEqual(set(manifest["files"]), expected)
```

Also assert the candidate profile contains `Casey Example`, `Example Systems`, education, project, publication and recognition fixture values; behavioral output names its assessment source; writing output contains only fixture-provided preferences; interview output contains the fixture STAR story and its evidence IDs.

Compile into two temporary roots and assert the bytes of every projected file are identical.

- [ ] **Step 2: Run the projection test module and verify RED**

```bash
python -m unittest tests.test_career_compat_projection -v
```

Expected: tests fail because the four Markdown files are absent.

- [ ] **Step 3: Implement focused renderers**

Implement private functions:

```python
def _render_candidate_profile(source: dict) -> str: ...
def _render_behavioral_profile(source: dict) -> str: ...
def _render_writing_style(source: dict) -> str: ...
def _render_interview_prep(source: dict) -> str: ...
```

Rendering rules:
- Stable section order exactly follows the canonical schema order in the spec.
- List order follows source order; never sort user chronology.
- Optional absent sections render as `None recorded.` rather than fabricated content.
- `evidence_ids` render as an explicit `Evidence:` annotation when present.
- Behavioral assessments render their `source` and `observed_at` fields.
- Writing preferences render only explicit preference values from `writing_preferences`.
- STAR stories render Situation/Task/Action/Result and evidence annotations.
- End every Markdown file with exactly one newline.

Write all rendered content first into an in-memory mapping, validate it, then create parent directories and write files. Calculate file digests from the exact UTF-8 bytes written. Write the manifest last.

- [ ] **Step 4: Run projection tests and verify GREEN**

```bash
python -m unittest tests.test_career_compat_projection -v
```

Expected: all projection tests PASS.

- [ ] **Step 5: Commit Task 2**

```bash
git add tools/career_compat/projection.py tests/test_career_compat_projection.py
git commit -m "feat: render career profile compatibility projection"
```

### Task 3: Fail closed before writing incomplete canonical input

**Files:**
- Modify: `tools/career_compat/projection.py`
- Modify: `tests/test_career_compat_projection.py`

**Interfaces:**
- Produces: `ProjectionInputError(ValueError)`.
- Validation happens before any output path is created.

- [ ] **Step 1: Add failing tests for schema and required identity fields**

Add tests for an unknown schema and for missing `candidate.identity.name`. For each case, use a nonexistent temporary child output path and assert:

```python
with self.assertRaises(ProjectionInputError):
    compile_projection(source, output_root)
self.assertFalse(output_root.exists())
```

- [ ] **Step 2: Run focused validation tests and verify RED**

```bash
python -m unittest tests.test_career_compat_projection.ProjectionTests.test_unknown_schema_writes_nothing tests.test_career_compat_projection.ProjectionTests.test_missing_candidate_name_writes_nothing -v
```

Expected: failure because validation is insufficient and/or files are created.

- [ ] **Step 3: Implement minimal pre-write validation**

Validate:
- source is a dict;
- exact schema;
- `candidate` is a dict;
- `candidate.identity` is a dict;
- `candidate.identity.name` is a non-empty string;
- top-level optional collections, when present, have the expected container type.

Do not add semantic validation beyond fields exercised by the fixture and spec.

- [ ] **Step 4: Run all projection tests and verify GREEN**

```bash
python -m unittest tests.test_career_compat_projection -v
```

- [ ] **Step 5: Commit Task 3**

```bash
git add tools/career_compat/projection.py tests/test_career_compat_projection.py
git commit -m "test: fail closed on invalid career projection input"
```

### Task 4: Parse tracker rows into read-only workflow observations

**Files:**
- Create: `tools/career_compat/tracker.py`
- Create: `tests/test_career_compat_tracker.py`
- Create: `tests/fixtures/career_compat/tracker.csv`
- Modify: `tools/career_compat/__init__.py`

**Interfaces:**
- Produces: `parse_tracker(path: pathlib.Path) -> list[dict]`
- Produces: `TrackerSchemaError(ValueError)`, `TrackerRowError(ValueError)`, `UnknownTrackerStatus(ValueError)`, `TrackerConflict(ValueError)`.
- Observation schema: `CareerWorkflowObservation/v0`.

- [ ] **Step 1: Add synthetic tracker fixture and failing happy-path test**

Fixture header must be exactly:

```text
date,company,sector,role,role_type,channel,status,contact_person,fit_rating,notes,cv_file,cover_letter_file,source,deadline
```

Include rows covering `ranked`, `applied`, `interview`, and `rejected` with distinct company/role pairs.

Assert every result contains:

```python
{
    "schema": "CareerWorkflowObservation/v0",
    "source_system": "ai-job-search",
    "application_key": "<normalized-company>::<normalized-role>",
    "observed_status": "...",
    "terminal": False,
    "source_row_digest": "<sha256>",
}
```

and `rejected` has `terminal is True`.

- [ ] **Step 2: Run tracker test and verify RED**

```bash
python -m unittest tests.test_career_compat_tracker.TrackerTests.test_parse_tracker_returns_observations -v
```

Expected: failure because `tracker.py` does not exist.

- [ ] **Step 3: Implement exact-schema CSV parsing and observation transformation**

Use `csv.DictReader(newline="")`. Require fieldnames to exactly equal the 14-column tuple. Normalize application keys with `strip().casefold()` and collapse internal whitespace to one space. Compute `source_row_digest` from canonical JSON serialization of the raw row dictionary, not from reconstructed CSV text.

Final statuses are exactly:

```python
FINAL_STATUSES = {"hired", "rejected", "no_response", "offer_declined", "withdrawn", "expired"}
```

Recognized non-final statuses are `ranked`, `drafted`, `applied`, `interview`, `offer`.

- [ ] **Step 4: Run focused tracker test and verify GREEN**

Run the same test. Expected: PASS.

- [ ] **Step 5: Commit Task 4**

```bash
git add tools/career_compat/tracker.py tools/career_compat/__init__.py tests/test_career_compat_tracker.py tests/fixtures/career_compat/tracker.csv
git commit -m "feat: import ai job tracker as observations"
```

### Task 5: Fail closed on unknown and conflicting tracker evidence

**Files:**
- Modify: `tools/career_compat/tracker.py`
- Modify: `tests/test_career_compat_tracker.py`

**Interfaces:**
- `parse_tracker` remains read-only and raises typed errors before returning ambiguous results.

- [ ] **Step 1: Add failing tests for malformed evidence**

Add four tests:

1. Wrong header raises `TrackerSchemaError`.
2. Unknown `status=future_state` raises `UnknownTrackerStatus`.
3. Missing company or role raises `TrackerRowError`.
4. Two non-final rows with the same normalized company+role but `applied` and `interview` raise `TrackerConflict`.

Also add a test that two byte-identical duplicate rows collapse to one observation and a test that a final historical row plus a later open row are both retained.

- [ ] **Step 2: Run tracker module and verify RED**

```bash
python -m unittest tests.test_career_compat_tracker -v
```

Expected: one or more new tests fail because conflict/error behavior is not implemented.

- [ ] **Step 3: Implement typed fail-closed behavior and duplicate collapse**

Process all rows into observations first. Reject invalid rows immediately. Deduplicate by `source_row_digest`. Group remaining observations by `application_key`; if two or more non-final observations in a group have different statuses, raise `TrackerConflict`. Do not treat final history plus an open observation as a conflict.

- [ ] **Step 4: Verify source file immutability and GREEN**

In the test, capture `fixture.read_bytes()` before and after `parse_tracker`; assert equality. Then run:

```bash
python -m unittest tests.test_career_compat_tracker -v
```

Expected: all tracker tests PASS.

- [ ] **Step 5: Commit Task 5**

```bash
git add tools/career_compat/tracker.py tests/test_career_compat_tracker.py
git commit -m "test: fail closed on ambiguous career tracker evidence"
```

### Task 6: Whole-repository verification

**Files:**
- Modify only if a compatibility-specific defect is discovered by verification.

**Interfaces:**
- No new interface; this task proves compatibility with the upstream repository.

- [ ] **Step 1: Run the complete Python suite**

```bash
python -m unittest discover -s tests -t . -v
```

Expected: PASS, zero failures/errors.

- [ ] **Step 2: Run repository security guards**

```bash
python tools/security_guards.py
```

Expected: exit 0.

- [ ] **Step 3: Run skill lint if PyYAML is already available**

```bash
python tools/lint_skills.py
```

If PyYAML is unavailable, record `SKIPPED_DEPENDENCY_MISSING`; do not install packages solely for this slice.

- [ ] **Step 4: Verify branch diff is bounded**

```bash
git status --short
git diff --stat master...HEAD
git log --oneline --decorate master..HEAD
```

Expected: only the design/plan, `tools/career_compat/**`, and `tests/test_career_compat_*` / `tests/fixtures/career_compat/**` are changed; working tree clean.

- [ ] **Step 5: Record final verification commit only if verification required a code fix**

If no fix was required, do not create an empty commit. If a fix was required, rerun the focused RED/GREEN cycle for that defect first and commit the verified change with a specific message.