# CareerDomainContract/v0.1 Amendment

Status: FROZEN_V0_1_FOR_COMPATIBILITY_EXPERIMENTS  
Authority effect: NONE  
Base contract: `CareerDomainContract/v0` at commit `91d3a7ec73a7e6079d3f046ac5a7a67d6507ba0e`  
Reason: field-level qualification against current upstream `MadsLorentzen/ai-job-search` exposed candidate-domain concepts absent from v0.

This amendment is normative. All v0 rules remain in force except where explicitly extended below.

## A1. Career Knowledge entity coverage

Extend Career Knowledge with:

- `Education`
- `Credential`
- `Publication`
- `Recognition`

The resulting v0.1 Career Knowledge entity set is:

- `Candidate`
- `Claim`
- `Evidence`
- `Experience`
- `Education`
- `Project`
- `Skill`
- `Credential`
- `Publication`
- `Recognition`
- `Story`
- `Goal`
- `Preference`

`Reference` is not added as a second person model. Employment/professional references use the existing Career Operations `Contact` entity with an explicit relationship/role binding.

## A2. Behavioral profile semantics

Add `BehavioralAssessment` to Career Analysis.

Behavioral or personality frameworks such as PI, DISC, MBTI, StrengthsFinder, or self-assessment are not canonical candidate facts merely because a workflow stores a profile label.

A behavioral assessment MUST carry:

```yaml
assessment_id: stable-id
assessment_type: BEHAVIORAL
candidate_id: stable-id
framework: string|null
framework_version: string|null
source_refs: [stable-ref]
method: string
method_version: string
result: object
created_at: timestamp
```

Self-reported work-style preferences that do not depend on an assessment framework may be stored as `Preference` objects instead.

## A3. Education

Minimum fields:

```yaml
education_id: stable-id
candidate_id: stable-id
institution: string
degree_or_program: string
field_of_study: string|null
start_date: date|null
end_date: date|null
status: string|null
evidence_refs: [evidence-id]
```

Topics/coursework inferred from syllabi are derived observations unless explicitly supported by candidate records or user confirmation.

## A4. Credentials

`Credential` includes certifications, licenses, and comparable attestations.

Minimum fields:

```yaml
credential_id: stable-id
candidate_id: stable-id
name: string
issuer: string|null
issued_at: date|null
expires_at: date|null
credential_url: string|null
evidence_refs: [evidence-id]
```

## A5. Publications

A publication may be stored as Career Knowledge only when authorship/association is supported by evidence or explicit user statement.

Minimum fields:

```yaml
publication_id: stable-id
candidate_id: stable-id
title: string
authors: [string]
published_at: date|null
venue: string|null
canonical_url: string|null
evidence_refs: [evidence-id]
```

## A6. Recognition

Awards, honors, and similar recognition use:

```yaml
recognition_id: stable-id
candidate_id: stable-id
title: string
issuer_or_event: string|null
awarded_at: date|null
evidence_refs: [evidence-id]
```

## A7. Projection rule added

A compatibility compiler targeting `ai-job-search` MUST NOT flatten provenance distinctions while rendering its Markdown profile files.

Specifically:

- verified/user-stated career facts may render as profile content;
- unverified claims must either be omitted or visibly marked according to the target workflow's supported semantics;
- behavioral labels render only from an explicitly bound BehavioralAssessment or user-authored preference;
- inferred coursework, inferred skills, and generated STAR wording remain derived until separately admitted into Career Knowledge;
- references render from Contact bindings, never by inventing or parsing unsupported person records.

## A8. V0.1 acceptance addition

Add acceptance check 11:

11. Projection coverage tests prove that education, credentials, publications, recognition, behavioral assessments, and professional references cannot be silently dropped or promoted across trust boundaries.
