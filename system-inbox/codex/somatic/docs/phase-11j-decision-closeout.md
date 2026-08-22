# Phase 11J Decision Closeouts

Phase 11J adds compact reviewer decision-closeout records over sanitized Phase
11I follow-up queue indexes and queue acceptance checks. These records are
planning-decision metadata only. They do not authorize document ingestion, file
crawling, PDF parsing, RuView execution, model execution, ESP32 flashing,
packet capture, monitor mode, MQTT/UDP, router or AP control, smart-home
bridges, or any runtime adapter behavior.

The closeout layer consumes validated Phase 11I queue records only. A closeout
record includes:

- closeout id
- schema and closeout contract versions
- domain label
- source queue label and hash
- closeout decision
- closeout status
- reviewer disposition summary
- unresolved review, blocker, stale, archived, rejected, and deferred counts
- `runtime_stage: not-implemented`
- `execution_permitted: false`

Closeout decisions are `closed-for-planning`, `deferred`, `rejected`,
`archived`, `needs-new-review`, and `blocked`. Closeout statuses are
`complete`, `incomplete`, `blocked`, `rejected`, and `archived`. A
`closed-for-planning` closeout means the planning queue can be closed; it is
not authorization to run adapters, enable real mode, ingest documents, capture
RF/CSI, or execute models.

The validators fail closed for missing fields, unsupported versions,
contradictory closeout status, decisions or wording that imply runtime
authorization, unsafe values, URLs, absolute paths, source identifiers,
credentials, device/router identifiers, model/parser/provider bodies, raw
document text, raw CSI/RF, and medical or clinical claims.

The deterministic fixture is
`fixtures/reviews/phase-11j-decision-closeout-v1.json`. It contains
document-ingestion and RF booth / WiFi CSI closeout records built from existing
sanitized Phase 11I queue indexes and acceptance checks.

The focused Phase 11J test is `tests/test_phase11j_decision_closeout.py`.
