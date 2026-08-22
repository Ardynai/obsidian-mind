# Phase 11B Review-Record Fixtures

Phase 11B adds deterministic review-record fixtures and fail-closed validators
around the Phase 11A real-mode contract specs. It is pre-runtime planning only.
It does not permit document ingestion, RF capture, hardware access, model
execution, network behavior, dependency installation, or provider execution.

## Review Record Scope

The review-record contract lives in `somatic.safety.phase11_contracts`. It
defines structured review entries for:

- Consent review.
- License/source review.
- Privacy review.
- Hardware review.
- Model artifact review.
- Dependency review.
- Network policy review.

Each review entry is metadata-only, sanitized, and carries
`runtime_permission: false`. The top-level record also keeps
`execution_permitted: false`, `real_mode_runtime_enabled: false`, and
`runtime_stage: not-implemented`.

## Fixtures

The deterministic fixture bundle is
`fixtures/reviews/phase-11b-review-records-v1.json`. It includes:

- A document-ingestion reviewed record.
- A WiFi CSI / RF booth reviewed record.
- An incomplete record.
- A rejected fail-closed record.
- An all-gates-reviewed-but-runtime-disabled record.

These records are review evidence only. A completed record can satisfy the
planning readiness gate, but it still cannot enable runtime execution.

## Validators

`validate_phase11_review_record` fails closed for:

- Missing required review fields.
- Unsupported review-record contract versions.
- Unknown fields.
- Contradictory status, count, or gate summaries.
- Any runtime permission or execution flag.
- Unsafe private values or keys.

Rejected or invalid records return sanitized rejected metadata and do not echo
unsafe input values.

## Public Surfaces

Public adapter, provider, release, and doctor surfaces expose only compact
review-record status: contract version, status, reviewed/missing/rejected gate
counts, runtime stage, and execution-permitted false. They do not dump review
record bodies into portable evidence packs or reports.

## Phase 11C Continuation

Phase 11C consumes these review records with the Phase 11A specs to build
sanitized preflight dossiers. A dossier can summarize packet id, fingerprint,
per-gate status, and rejection reasons for planning review only, but it still
cannot enable runtime execution.

## Phase 11D Continuation

Phase 11D consumes Phase 11C dossiers to build lifecycle audit records,
reviewer signoff metadata, dossier comparisons, and explicit audit decisions.
Those records remain evidence of planning review only and cannot enable real
adapter execution.

## Non-Goals

Phase 11B intentionally does not add real document ingestion, file crawling,
PDF parsing, RuView execution, model download or execution, ESP32 flashing,
packet capture, monitor mode, MQTT/UDP listeners, router/AP control,
smart-home bridges, raw document text, raw CSI/RF values, provider bodies,
parser bodies, model bodies, credentials, local paths, URLs, or care claims.

## Verification

The focused Phase 11B tests are:

- `tests/test_phase11b_review_record_fixtures.py`
- `tests/test_phase11b_review_record_validator.py`

They prove deterministic fixture generation, fail-closed validation, sanitized
rejection, and the rule that completed review records still leave runtime
execution disabled.
