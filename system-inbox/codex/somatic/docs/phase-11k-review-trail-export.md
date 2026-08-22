# Phase 11K Review Trail Export

Phase 11K adds a compact review-trail export over the Phase 11A through 11J
planning metadata. The export is for future reviewer navigation only. It does
not authorize document ingestion, file crawling, PDF parsing, RuView execution,
model execution, WiFi CSI or RF capture, provider execution, network calls, or
real-mode adapter behavior.

The export consumes existing sanitized Phase 11 status summaries and the Phase
11J decision-closeout summaries. It records only:

- export id and contract version
- phase range `11A-11J`
- covered phase count
- domain labels
- per-domain final closeout decision and status
- unresolved review, blocker, and stale counts
- readiness gap summary `real-mode-authorization-missing`
- `runtime_stage: not-implemented`
- `execution_permitted: false`
- `real_mode_runtime_enabled: false`

`complete`, `exported`, or `closed-for-planning` language in review trail
metadata remains planning/export status only. It is not permission to run
adapters, ingest documents, capture RF/CSI, execute models, or enable real
mode.

The validator fails closed for missing fields, unsupported contract versions,
unknown fields, runtime-authorization wording, unsafe or private values, URLs,
absolute paths, source/device/router identifiers, credentials, model/parser or
provider bodies, raw document text, raw CSI/RF markers, medical or clinical
claims, and non-integer counts.

The deterministic export fixture is
`fixtures/reviews/phase-11k-review-trail-export-v1.json`.
