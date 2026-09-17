# Career Domain Compatibility v0 Design

Status: APPROVED FOR BOUNDED IMPLEMENTATION
Authority effect: NONE
Production adoption: NOT AUTHORIZED
Target upstream revision: `09435eb1a572eddbd0180e8ea9c3acf84f90604a`

## Goal

Add a deterministic, read-only compatibility boundary between canonical career-domain data and the upstream `ai-job-search` workflow without making this repository authoritative for career truth.

## Scope

The first slice has two directions only:

1. **Projection**: canonical candidate JSON -> upstream-compatible Markdown files plus a deterministic manifest.
2. **Observation import**: upstream `job_search_tracker.csv` -> validated observation/event proposals. The importer never mutates canonical state.

No provider calls, network access, auto-apply, external side effects, database, scheduler, or model invocation are part of v0.

## Invariants

1. Candidate fact != generated wording.
2. Observation != durable truth.
3. Derived assessment != source fact.
4. External workflow state != canonical state until reconciled.
5. Generated files are disposable projections.
6. UNKNOWN != VERIFIED.
7. Unknown tracker statuses fail closed.
8. Conflicting rows for the same open application fail closed.
9. Projection output is deterministic for identical canonical input.
10. No timestamps or random identifiers may appear in projection manifests.

## Canonical input envelope

The compiler consumes one UTF-8 JSON object with these top-level keys:

- `schema`: must equal `CareerCandidateProjectionInput/v0`.
- `candidate`: identity, languages, education, experiences, projects, skills, publications, recognitions, references.
- `behavioral_assessments`: source-bound assessment observations.
- `writing_preferences`: explicit user-authored style preferences only.
- `stories`: evidence-backed STAR source material.

Every claim-like item may carry `evidence_ids`; the compiler preserves provenance annotations where the upstream format can display them, but it does not invent missing evidence.

## Projection outputs

The compiler writes only under a caller-supplied output root:

- `.claude/skills/job-application-assistant/01-candidate-profile.md`
- `.claude/skills/job-application-assistant/02-behavioral-profile.md`
- `.claude/skills/job-application-assistant/03-writing-style.md`
- `.claude/skills/job-application-assistant/07-interview-prep.md`
- `.career-compat/manifest.json`

It never writes directly to repository root unless the caller explicitly supplies that root.

The manifest schema is `AiJobSearchProjectionManifest/v0` and contains:

- `source_schema`
- `source_digest`
- `target_revision`
- sorted `files` mapping relative path -> SHA-256 digest

The manifest contains no generated timestamp.

## Tracker import

The importer accepts the exact 14-column upstream header:

`date,company,sector,role,role_type,channel,status,contact_person,fit_rating,notes,cv_file,cover_letter_file,source,deadline`

Canonical recognized statuses are:

- `ranked`
- `drafted`
- `applied`
- `interview`
- `offer`
- `hired`
- `rejected`
- `no_response`
- `offer_declined`
- `withdrawn`
- `expired`

Each row becomes a `CareerWorkflowObservation/v0` proposal containing source-system identity, normalized company/role key, observed status, terminal flag, selected fields, and `source_row_digest`.

The importer is read-only. It never rewrites the CSV and never chooses a canonical mutation.

## Conflict semantics

- Unknown header -> `TrackerSchemaError`.
- Unknown status -> `UnknownTrackerStatus`.
- Missing company or role -> `TrackerRowError`.
- Multiple non-final rows for the same normalized company+role with different statuses -> `TrackerConflict`.
- Exact duplicate rows may coexist but collapse to one observation by row digest.
- Final historical rows may coexist with a later open row; they remain separate observations.

## Implementation shape

Use Python 3.10+ standard library only.

Create:

- `tools/career_compat/__init__.py` — public API exports.
- `tools/career_compat/common.py` — canonical JSON serialization and SHA-256 helpers.
- `tools/career_compat/projection.py` — validation, rendering, atomic projection write, manifest.
- `tools/career_compat/tracker.py` — tracker parsing and observation transformation.
- `tests/test_career_compat_projection.py` — projection contract tests.
- `tests/test_career_compat_tracker.py` — tracker/read-only/conflict tests.
- `tests/fixtures/career_compat/candidate.json` — non-personal synthetic canonical fixture.
- `tests/fixtures/career_compat/tracker.csv` — synthetic tracker fixture.

No modification to existing upstream workflow files is required for v0.

## Acceptance

v0 is complete when:

1. Projection tests demonstrate RED before implementation and GREEN afterward.
2. Identical input compiled twice yields byte-identical files and manifest.
3. Manifest digests verify every projected file.
4. Missing required canonical fields fail before any output is committed.
5. Tracker parsing accepts the exact upstream schema and all canonical statuses.
6. Unknown status and conflicting open-state rows fail closed.
7. Import leaves the source CSV byte-for-byte unchanged.
8. `python -m unittest discover -s tests -t . -v` passes from a clean branch baseline after implementation.
9. `python tools/security_guards.py` passes.
10. No network access or external provider invocation is required by tests.