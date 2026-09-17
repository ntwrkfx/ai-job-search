# CareerDomainContract/v0

Status: FROZEN_V0_FOR_COMPATIBILITY_EXPERIMENTS  
Authority effect: NONE  
Production adoption: NOT AUTHORIZED BY THIS DOCUMENT  
Branch context: `research/career-domain-contract-v0`  
Purpose: establish stable semantic boundaries for interoperability among career knowledge, job-search workflows, career operations, reference frameworks, and external providers.

## 1. Core invariants

1. Candidate fact != generated wording.
2. Observation != durable truth.
3. Derived assessment != source fact.
4. External provider state != local authoritative state.
5. Reference framework != candidate classification.
6. Generated artifact != evidence source unless explicitly ingested and verified.
7. UNKNOWN != VERIFIED.
8. Missing evidence must not be converted into a positive claim by repetition or model confidence.
9. Every mutation must have one authoritative owner per collision domain.
10. Compatibility projections are disposable and reproducible from authoritative state.

## 2. Domain planes

### 2.1 Career Knowledge

Authoritative for durable candidate-owned facts and preferences.

Entities:
- `Candidate`
- `Claim`
- `Evidence`
- `Experience`
- `Project`
- `Skill`
- `Story`
- `Goal`
- `Preference`

### 2.2 Career Market

Authoritative for normalized, source-bound observations about external opportunities and employers.

Entities:
- `Employer`
- `OpportunityObservation`
- `Opportunity`
- `RequirementObservation`
- `CompensationObservation`

Market observations remain time-bound and source-bound. Normalization does not erase provenance.

### 2.3 Career Analysis

Derived, versioned, non-factual conclusions.

Entities:
- `FitAssessment`
- `ReadinessAssessment`
- `GapAssessment`
- `EconomicAssessment`
- `OpportunityPriority`

Every assessment MUST bind its inputs, method, method version, creation time, and evidence references.

### 2.4 Career Operations

Authoritative for user-owned workflow state.

Entities:
- `Application`
- `ApplicationEvent`
- `Contact`
- `Interaction`
- `Outreach`
- `Interview`
- `Outcome`

Operational state must use explicit transitions. Append-only event history is preferred where chronology matters.

### 2.5 Career Reference

Read-only procedural or competency knowledge with `authority_effect = NONE`.

Entities:
- `Framework`
- `FrameworkVersion`
- `Level`
- `CompetencyDimension`
- `Expectation`
- `AntiPattern`

A framework may support a `ReadinessAssessment`; it must not mutate candidate truth.

## 3. Minimum provenance envelope

Every cross-system object MUST support:

```yaml
source_system: string
source_id: string|null
observed_at: timestamp|null
source_digest: string|null
provenance_status: VERIFIED|USER_STATED|SOURCE_OBSERVED|DERIVED|UNVERIFIED|USER_CANNOT_CONFIRM
```

Derived objects additionally MUST support:

```yaml
method: string
method_version: string
input_refs: [stable-ref]
created_at: timestamp
```

External observations SHOULD also carry:

```yaml
source_url: string|null
source_host: string|null
observed_payload_digest: string|null
```

## 4. Candidate claims

`Claim` is the atomic candidate-truth unit.

Minimum fields:

```yaml
claim_id: stable-id
candidate_id: stable-id
claim_type: string
value: scalar|object
status: VERIFIED|USER_STATED|UNVERIFIED|USER_CANNOT_CONFIRM|SUPERSEDED
valid_from: timestamp|null
valid_to: timestamp|null
evidence_refs: [evidence-id]
created_at: timestamp
updated_at: timestamp
```

Rules:
- A claim is not verified merely because it exists in a resume, generated document, interview-prep artifact, or prior model output.
- Quantified claims require an evidence reference or explicit user statement.
- `USER_CANNOT_CONFIRM` must never decay into VERIFIED through reuse.
- Supersession preserves lineage.

## 5. Evidence

Minimum fields:

```yaml
evidence_id: stable-id
evidence_type: USER_STATEMENT|DOCUMENT|REPOSITORY|PORTFOLIO|CERTIFICATE|EMPLOYMENT_RECORD|EXTERNAL_SOURCE|OTHER
source_ref: string
source_digest: string|null
captured_at: timestamp
scope: string|null
```

Evidence ingestion never implies that every statement in the source becomes candidate truth.

## 6. Opportunity model

`OpportunityObservation` preserves what a source said at a point in time.

`Opportunity` is the normalized identity used across observations and operations.

Minimum normalized fields:

```yaml
opportunity_id: stable-id
employer_id: stable-id
role_title: string
location: object|null
employment_type: string|null
canonical_url: string|null
first_observed_at: timestamp
last_observed_at: timestamp
status: OPEN|CLOSED|UNKNOWN
observation_refs: [observation-id]
```

Requirement extraction is DERIVED from one or more observations and must remain traceable to them.

## 7. Assessment contract

Assessments never mutate candidate facts or opportunity observations.

Minimum assessment envelope:

```yaml
assessment_id: stable-id
assessment_type: FIT|READINESS|GAP|ECONOMIC|PRIORITY
candidate_id: stable-id
opportunity_id: stable-id|null
framework_ref: stable-ref|null
method: string
method_version: string
input_refs: [stable-ref]
result: object
created_at: timestamp
```

Re-running an assessment creates a new version or result; it does not rewrite historical results in place unless explicitly declared as a correction.

## 8. Application lifecycle

`Application` is authoritative local operational state.

Minimum fields:

```yaml
application_id: stable-id
candidate_id: stable-id
opportunity_id: stable-id
state: DISCOVERED|SHORTLISTED|PREPARING|READY|SUBMITTED|SCREENING|INTERVIEWING|OFFER|REJECTED|WITHDRAWN|CLOSED|UNKNOWN
state_generation: integer
created_at: timestamp
updated_at: timestamp
```

Every real transition SHOULD emit an `ApplicationEvent` containing previous state, next state, source, observed time, and note/reference.

External provider status is first captured as provider state or observation. It becomes local application state only through an explicit reconciliation rule.

## 9. Contacts and interactions

`Contact` describes a person. `Interaction` describes an observed or user-recorded event involving that person.

Job-specific roles must be modeled separately from standing relationship roles.

No external email, message, or profile observation may silently overwrite user-confirmed contact data.

## 10. Generated artifacts

Artifacts include resumes, cover letters, interview-prep packs, outreach drafts, reports, and exports.

Minimum metadata:

```yaml
artifact_id: stable-id
artifact_type: string
input_refs: [stable-ref]
producer: string
producer_version: string|null
created_at: timestamp
content_digest: string
verification_status: PASS|FAIL|UNKNOWN|NOT_APPLICABLE
```

Artifacts are outputs, not source truth. If an artifact reveals a new candidate fact, that fact must enter through normal claim/evidence ingestion.

## 11. Provider bindings

External systems such as JobGPT or WorkorAI are provider surfaces, not semantic authorities.

Minimum binding:

```yaml
provider: string
local_object_type: string
local_object_id: stable-id
external_object_type: string
external_object_id: string
observed_at: timestamp
provider_payload_digest: string|null
```

Writes to providers require explicit effect semantics. Reads are observations until reconciled.

## 12. Reference frameworks

Career ladders and competency models are immutable/versioned inputs to analysis.

A readiness result MUST bind the exact framework/version used. Example:

```yaml
framework_ref: ladder/danscratch@594fef1
level_ref: L4
```

`candidate.level = L4` is prohibited as a canonical fact unless a separate authoritative source explicitly establishes it.

## 13. Compatibility projection: ai-job-search

`ai-job-search` is treated as a replaceable workflow engine.

Authoritative Career Knowledge may be compiled into its expected profile files, including:
- candidate profile
- behavioral profile
- writing style
- interview/story context

Projection rules:
- projection is deterministic from bounded source inputs;
- projection records input digests and compiler version;
- projected files are not independently authoritative;
- upstream workflow updates must not become a migration of candidate truth.

## 14. Reverse import: ai-job-search

Outputs eligible for import include:
- newly observed opportunities;
- application lifecycle events;
- submitted artifact references;
- interview events;
- outcomes;
- gap observations.

Import rules:
- generated text never becomes a candidate claim automatically;
- tracker rows require stable identity reconciliation;
- conflicting application state fails closed for manual reconciliation;
- duplicate imports are idempotent by source identity/digest.

## 15. JobSync integration posture

JobSync is qualified as a relational schema and UX donor, not an initial writable authority.

Useful donor concepts:
- normalized employer/contact/job relationships;
- job-specific contact roles;
- automation discovery metadata;
- tasks/activity and interview records;
- local-first self-hosted UI patterns.

Running JobSync as a second application-state writer is explicitly out of scope for v0.

## 16. career-ops integration posture

Qualified donor concepts:
- user-layer vs system-layer separation;
- primary vs derived trust tiers;
- append-only chronology where appropriate;
- `derived-unverified` / `user-cannot-confirm` semantics;
- external content as data, never instructions;
- candidate facts isolated from updateable workflow logic.

## 17. jobContextMCP integration posture

Qualified donor concepts:
- consolidated domain facades;
- persistent session context;
- materials/story/contact domains;
- generation provenance gate;
- durable work rows and execution attribution;
- multi-client MCP/HTTP/CLI surface.

Its complete data model is not adopted by this contract; only bounded concepts are qualified.

## 18. Anti-drift rules

The following are contract violations:
- two mutable local systems claiming authoritative application state;
- an external provider overwriting local truth without reconciliation;
- a generated artifact introducing a durable candidate fact automatically;
- a fit/readiness score stored as candidate fact;
- an opportunity update erasing its prior observation provenance;
- compatibility-projection files becoming an independent source of truth;
- framework updates rewriting historical assessments without version change.

## 19. V0 acceptance checks

A compatibility implementation is conformant only if it demonstrates:

1. Candidate claim round-trip preserves evidence and status.
2. Projection to `ai-job-search` is reproducible from identical inputs.
3. Generated artifacts cannot mutate Career Knowledge implicitly.
4. Importing the same workflow outcome twice is idempotent.
5. Conflicting external application status yields UNKNOWN/RECONCILIATION_REQUIRED rather than blind overwrite.
6. Historical assessments retain method/framework versions.
7. Provider identifiers remain bindings, not canonical IDs.
8. Deleting and rebuilding a compatibility projection loses no authoritative state.
9. Unknown evidence remains unknown.
10. Source observations retain time and digest provenance.

## 20. Explicit non-goals for v0

- Choosing a production database.
- Choosing a user interface.
- Replacing upstream `ai-job-search` workflow logic.
- Adopting JobSync as a runtime.
- Adopting jobContextMCP as the canonical store.
- Defining autonomous submission policy.
- Defining commercial product packaging.
- Migrating historical `engagement-os` state.

## 21. Next implementation slice

The first conforming experiment should contain only:

1. minimal Career Knowledge fixtures;
2. deterministic compiler into upstream `ai-job-search` profile inputs;
3. contract tests over the generated projection;
4. read-only parser/importer for application outcome artifacts;
5. idempotency and provenance tests.

No external application submission, email sending, or provider mutation is required for this slice.
