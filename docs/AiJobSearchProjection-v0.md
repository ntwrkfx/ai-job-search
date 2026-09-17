# ai-job-search Compatibility Projection/v0

Status: FROZEN_V0_FOR_IMPLEMENTATION  
Authority effect: NONE  
Canonical contract: `CareerDomainContract/v0` + `v0.1 Amendment`  
Qualified target: `MadsLorentzen/ai-job-search@09435eb1a572eddbd0180e8ea9c3acf84f90604a`

## 1. Purpose

Define a deterministic compatibility boundary between canonical Career Domain state and the upstream `ai-job-search` workflow without making upstream profile/tracker files an independent authority.

Direction A: Career Domain -> disposable upstream-compatible profile projection.  
Direction B: upstream workflow artifacts -> source-bound observations/events imported back into Career Domain.

## 2. Projection envelope

Every generated projection MUST record:

```yaml
projection_type: ai-job-search-profile
projection_version: v0
compiler_version: string
contract_version: v0+v0.1
source_generation: string|null
source_digests: [string]
target_upstream_commit: 09435eb1a572eddbd0180e8ea9c3acf84f90604a
created_at: timestamp
```

Rebuilding from the same canonical inputs and compiler version MUST produce semantically identical output.

## 3. `01-candidate-profile.md` mapping

| Upstream section | Canonical source | Rule |
|---|---|---|
| Identity/name | `Candidate` | render canonical identity |
| Location | `Candidate` + `Preference` | separate current location from location constraints |
| Phone/email/LinkedIn/GitHub | verified/user-stated `Claim` | omit unsupported values |
| Employment status | `Claim` | user-stated/verified only |
| Constraints | `Preference` | never infer |
| Languages | `Skill` | require declared proficiency/status |
| Education | `Education` | retain dates/institution/field and evidence boundary |
| Professional Experience | `Experience` + supported `Claim` | bullets may only restate admitted claims |
| Independent Projects | `Project` + supported `Claim` | authorship/ownership must be evidenced |
| Technical Skills | `Skill` | render VERIFIED or USER_STATED; omit unsupported inferred skills |
| Domain Expertise | `Skill`/`Claim` | same trust rule |
| Software & Tools | `Skill` | same trust rule |
| Publications | `Publication` | authorship must be evidenced/user-stated |
| Awards | `Recognition` | evidence/user statement required |
| References | `Contact` relationship binding | never create a person from generated text |

The current upstream profile template contains all of these categories; missing canonical support must fail as an explicit coverage error rather than silently dropping data.

## 4. `02-behavioral-profile.md` mapping

Source precedence:

1. explicit `BehavioralAssessment` with source/method binding;
2. user-authored `Preference` describing work style;
3. omit/leave unpopulated.

Prohibited:
- inferring PI/DISC/MBTI/etc. labels from ordinary career history;
- promoting workflow-generated behavioral prose into candidate truth;
- converting a fit interpretation into a stable personality claim.

`Growth Areas` are derived framing unless explicitly user-authored. They are projection content, not canonical claims.

## 5. `03-writing-style.md` mapping

Writing style is procedural/presentation state, not candidate factual history.

Sources:
- user-authored writing preferences;
- bounded style profile derived from user-provided writing samples;
- target workflow defaults.

A compiler may add target-required safety/writing rules, but MUST keep them distinguishable from user preferences so upstream changes can replace defaults without rewriting personal state.

## 6. `07-interview-prep.md` mapping

STAR examples are projections over canonical `Story` + supported `Claim` references.

Required behavior:
- Situation/Task/Action/Result wording may be generated;
- factual payload must trace to admitted claims/evidence;
- quantified results require verified/user-stated support;
- generated STAR prose remains a derived artifact;
- editing generated STAR prose must not silently mutate Career Knowledge.

## 7. Other upstream inputs

`04-job-evaluation.md` and workflow scoring rules remain upstream workflow logic. Their scores/results import as versioned `FitAssessment`/`GapAssessment` artifacts, never candidate facts.

Custom templates and portal skills remain workflow/provider configuration, not Career Knowledge.

## 8. Upstream tracker contract

Current canonical tracker header:

```text
date,company,sector,role,role_type,channel,status,contact_person,fit_rating,notes,cv_file,cover_letter_file,source,deadline
```

Importer field map:

| Tracker field | Canonical destination |
|---|---|
| `date` | application event time / submitted-at observation |
| `company` | employer identity candidate + source-bound observation |
| `sector` | opportunity/employer observation |
| `role` | opportunity role title |
| `role_type` | opportunity classification observation |
| `channel` | application source/channel |
| `status` | application transition candidate, mapped below |
| `contact_person` | contact observation/binding; never silently merge by name alone |
| `fit_rating` | derived `FitAssessment` result attributed to ai-job-search |
| `notes` | operational annotation; not candidate truth |
| `cv_file` | generated/submitted Artifact binding |
| `cover_letter_file` | generated/submitted Artifact binding |
| `source` | opportunity source provenance |
| `deadline` | opportunity observation |

## 9. Status map

Upstream -> canonical:

```text
ranked          -> Application.SHORTLISTED
drafted         -> Application.PREPARING
applied         -> Application.SUBMITTED
interview       -> Application.INTERVIEWING
offer           -> Application.OFFER
hired           -> Application.CLOSED + Outcome.HIRED
rejected        -> Application.REJECTED + Outcome.REJECTED
no_response     -> Application.CLOSED + Outcome.NO_RESPONSE
offer_declined  -> Application.CLOSED + Outcome.OFFER_DECLINED
withdrawn       -> Application.WITHDRAWN + Outcome.WITHDRAWN
expired         -> Opportunity.CLOSED; if a local Application exists, reconcile to CLOSED with Outcome.OPPORTUNITY_EXPIRED
```

Unknown tracker spellings MUST map to `UNKNOWN/RECONCILIATION_REQUIRED`, never to a guessed terminal state.

## 10. Identity reconciliation

Tracker rows currently identify applications operationally by company + role with workflow-specific handling for repeated/final rows.

The importer MUST NOT adopt company+role as the canonical ID.

Resolution sequence:

1. exact stored provider/source binding if present;
2. canonical posting URL/source identity if available;
3. normalized employer + role + application date/channel with uniqueness proof;
4. otherwise `RECONCILIATION_REQUIRED`.

Once resolved, persist a source binding so subsequent imports are idempotent.

## 11. Application archives

`documents/applications/<company>_<role>/` is an upstream workflow archive, not canonical authority.

Eligible imports:
- exact posting text/source as `OpportunityObservation`;
- submitted CV/cover-letter references as `Artifact` bindings;
- outcome events as `ApplicationEvent`/`Outcome` candidates;
- interview-stage events;
- workflow-generated fit/gap assessments as derived artifacts.

Ineligible automatic imports:
- generated resume bullets as new candidate claims;
- generated interview answers as source truth;
- generated company research as employer truth without source provenance;
- inferred skills as verified skills.

## 12. Import idempotency

Each imported row/artifact/event MUST have a deterministic source key, for example:

```text
sha256(target_upstream_commit | source_path | source_record_identity | source_content_digest)
```

A second import of the same source key produces no new authoritative mutation.

Changed source content produces a new observation/event or explicit correction; it does not rewrite history invisibly.

## 13. Conflict semantics

If canonical Application state and imported upstream state cannot be ordered safely:

```text
verification = UNKNOWN
reconciliation = REQUIRED
mutation = BLOCKED
```

Examples:
- canonical WITHDRAWN but tracker says interview;
- canonical OFFER from a verified provider event but tracker regressed to applied;
- duplicate company+role rows with no stable source binding.

## 14. Projection isolation

Projected upstream files MUST be treated as disposable.

Acceptance proof:

1. generate projection;
2. run upstream workflow/read contract tests;
3. delete projected files;
4. regenerate from canonical inputs;
5. verify semantic equivalence and unchanged canonical state.

## 15. First implementation slice

Implement only:

1. schema fixtures for Candidate, Claims/Evidence, Education, Experience, Project, Skill, Publication/Recognition, Preferences, Stories;
2. deterministic renderer for the four upstream profile files qualified above;
3. manifest containing projection envelope and file digests;
4. read-only tracker parser using the exact 14-column header;
5. status-map transformer that emits proposed canonical events without mutating canonical state;
6. idempotency/conflict tests.

No Gmail mutation, job submission, provider write, or canonical-state mutation is authorized by this slice.
