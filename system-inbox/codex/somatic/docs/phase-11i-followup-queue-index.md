# Phase 11I Follow-Up Queue Indexes

Phase 11I adds compact queue/index records over the sanitized Phase 11H
follow-up/remediation records. These records are reviewer-navigation artifacts
only. They do not authorize document ingestion, file crawling, PDF parsing,
RuView execution, model execution, ESP32 flashing, packet capture, monitor
mode, MQTT/UDP, router or AP control, smart-home bridges, or any runtime
adapter behavior.

The queue index layer consumes validated Phase 11H records only. A queue index
record includes:

- queue id and fingerprint
- schema and queue contract versions
- domain label
- included follow-up labels and hashes
- queue status counts
- blocker disposition, reviewer queue, and stale renewal counts
- unresolved review, blocking, open, blocked, stale, archived, rejected, and
  resolved-for-planning counts
- `runtime_stage: not-implemented`
- `execution_permitted: false`

Queue acceptance checks use these statuses: `accepted-for-planning-queue`,
`blocked-queue`, `stale-queue`, `rejected-queue`, `archived-no-action`, and
`needs-more-review`. These labels classify the review queue only. They are not
permission to run adapters, enable real mode, ingest documents, capture RF/CSI,
or execute models.

The validators fail closed for missing fields, unsupported versions,
contradictory queue counts, contradictory queue acceptance status,
runtime-authorizing wording, unsafe values, URLs, absolute paths, source
identifiers, credentials, device/router identifiers, model/parser/provider
bodies, raw document text, raw CSI/RF, and medical or clinical claims.

The deterministic fixture is
`fixtures/reviews/phase-11i-followup-queue-index-v1.json`. It contains
document-ingestion and RF booth / WiFi CSI queue indexes plus acceptance-check
examples for every queue status, all built from existing sanitized Phase 11H
follow-up records.

The focused Phase 11I test is `tests/test_phase11i_followup_queue_index.py`.
