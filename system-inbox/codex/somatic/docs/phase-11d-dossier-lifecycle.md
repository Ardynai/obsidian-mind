# Phase 11D Dossier Lifecycle Audit

Phase 11D adds lifecycle and audit decision metadata around the Phase 11C
preflight dossiers. It is still pre-runtime planning only. Lifecycle records,
reviewer signoff metadata, dossier comparisons, and decision records do not
permit runtime execution.

## Audit Scope

The lifecycle helpers live in `somatic.safety.phase11_contracts`. They can
record these lifecycle stages:

- `created`
- `reviewed`
- `superseded`
- `rejected`
- `archived`
- `decision-recorded`

Each lifecycle record includes sanitized dossier packet identifiers,
fingerprints, compact gate counts, one reviewer signoff metadata object, one
decision record, and a sanitized comparison against a prior dossier version.
It never includes the full underlying review records, contract bodies,
provider bodies, parser bodies, model bodies, local paths, network addresses,
document contents, CSI values, or RF values.

## Reviewer Signoff Metadata

Reviewer signoff metadata is intentionally narrow:

- Reviewer label only, with no identity secrets.
- Deterministic fixture timestamp.
- Review scope label.
- Verdict: `no-blockers`, `blockers`, `rejected`, or `superseded`.
- `runtime_stage: not-implemented`.
- `execution_permitted: false`.

The verdict is evidence for planning review only. A `no-blockers` verdict does
not enable real document ingestion, capture, model execution, networking, or
hardware access.

## Decision Records

Decision records use explicit non-runtime decisions:

- `safe-for-planning`
- `blocked`
- `rejected`
- `needs-more-review`
- `all-gates-reviewed-runtime-disabled`

Even the all-gates-reviewed decision keeps `execution_permitted: false` and
`real_mode_runtime_enabled: false`.

## Fixtures

The deterministic fixture bundle is
`fixtures/reviews/phase-11d-dossier-lifecycle-records-v1.json`. It includes
created, reviewed, superseded, rejected, archived, and decision-recorded
examples over document ingestion and RF booth / WiFi CSI planning packets.

## Validators

The Phase 11D validators fail closed for:

- Missing required fields.
- Unsupported lifecycle, signoff, decision, or comparison versions.
- Contradictory lifecycle stage, verdict, decision, dossier status, or gate
  counts.
- Any implied runtime execution.
- Unsafe private values or keys.

Invalid records return sanitized rejected audit metadata and do not echo unsafe
input values.

## Public Surfaces

Doctor, provider manifest, adapter status, release summary, and document
artifact inspection expose compact lifecycle status only: lifecycle contract
version, record id, fingerprint, lifecycle stage, audit decision, signoff
verdict, counts, runtime stage, and execution false.

They do not dump signoff bodies, decision bodies, dossier gate bodies, review
records, parser/provider bodies, model bodies, document contents, CSI values,
RF values, local paths, or network addresses.

## Phase 11E Continuation

Phase 11E consumes these lifecycle audit records to build deterministic
audit-index/change-control metadata. It adds sanitized ordering,
supersession-chain summaries, reviewer-scope coverage, and local
export/retention policy records. Those records are planning evidence only and
still cannot permit runtime execution.

## Non-Goals

Phase 11D intentionally does not add real document ingestion, file crawling,
PDF parsing, RuView execution, model download or execution, ESP32 flashing,
packet capture, monitor mode, MQTT/UDP listeners, router/AP control,
smart-home bridges, provider execution, parser execution, model execution, or
care claims.

## Verification

The focused Phase 11D tests are:

- `tests/test_phase11d_dossier_lifecycle_audit.py`
- `tests/test_phase11d_dossier_lifecycle_fixtures.py`

They prove deterministic lifecycle construction, sanitized dossier comparison,
fail-closed validation, compact public status, and the rule that lifecycle
signoff or all-gates-reviewed decisions still leave runtime execution disabled.
