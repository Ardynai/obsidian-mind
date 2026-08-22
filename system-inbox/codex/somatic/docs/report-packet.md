# Report Packet

A report packet is a reproducible research or decision-support output. It should preserve evidence, assumptions, limitations, safety decisions, artifacts, and review state.

Phase 1A defines the packet contract only. It does not implement report rendering.

## Required Fields

Report packets should include:

- `id`
- `schema_version`
- `workflow_id`
- `run_id`
- `created_at`
- `title`
- `mode`
- `summary`
- `evidence_table`
- `hypotheses`
- `counterevidence`
- `methods`
- `artifacts`
- `safety_review`
- `limitations`
- `next_step_recommendations`
- `review_state`
- `hashes`

## Summary

The summary should state what the workflow did, what evidence was considered, what remains uncertain, and whether human review is required.

For health-related reports, summaries must stay within research and decision-support framing and must not claim diagnosis, treatment, cure, emergency triage, or clinician replacement.

## Evidence Table

Evidence table entries should reference evidence record ids and include:

- Source type.
- Citation or source label.
- Claim supported.
- Confidence.
- Limitations.
- Hash or digest when available.

## Hypotheses and Counterevidence

Hypothesis entries should include:

- `id`
- `statement`
- `supporting_evidence_refs`
- `counterevidence_refs`
- `confidence`
- `assumptions`
- `tests_or_next_steps`

Counterevidence must remain visible and should not be collapsed into summaries only.

## Methods

The methods section should include:

- Workflow manifest id and version.
- Provider refs and capability ids.
- Stage list.
- Inputs used.
- Parameters and seeds when applicable.
- Known deviations from the declared workflow.

## Artifacts

Artifact entries should include:

- `id`
- `kind`
- `path_or_uri`
- `sha256`
- `created_by_stage`
- `retention`

## Safety Review

The safety review section should include:

- Safety request id.
- Safety response id.
- Decision.
- Checks performed.
- Warnings.
- Required human review.
- Blocked actions.
- Language constraints.

## Limitations

Limitations should include evidence gaps, model assumptions, data quality issues, sensor constraints, license constraints, and unreviewed areas.

## Next-Step Recommendations

Recommendations should be framed as non-clinical planning notes, research next
steps, human-review tasks, simulation follow-ups, validation needs, or
decision-support review items. They must not be presented as automatic
real-world actions, treatment recommendations, prescriptions, medical advice,
emergency triage, medication actions, clinician actions, reminders, scheduling,
monitoring, or intervention effectiveness claims.

## Phase 7F N-of-1 Report Packet

The n-of-1 report packet is a fake-backed/local/research-only packet for the
`n-of-1` fixture. It is not medical advice, not a medical record, and not a
health record.

It references every n-of-1 run artifact and records SHA-256 hashes for
reproducibility/provenance only. Hashes must not be framed as clinical
validity, treatment guidance, monitoring evidence, diagnosis, emergency triage,
or intervention effectiveness proof.

The packet must preserve no advice, no recommendation, no prescription, no
treatment recommendation, no medical advice, no diagnosis, no emergency triage,
no effectiveness claim, no real monitoring, and no reminders, automation,
notification, or scheduling.

Future real use requires consent, privacy review, safety review, human review,
clinical review where applicable, local-first storage controls, and
retention/export controls.
