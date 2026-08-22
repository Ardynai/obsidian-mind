# Phase 11H Follow-Up And Remediation Planning

Phase 11H adds compact follow-up and remediation planning records over Phase
11G handoff acceptance records. These records are planning queues only. They do
not authorize document ingestion, file crawling, PDF parsing, RuView execution,
model execution, ESP32 flashing, packet capture, monitor mode, MQTT/UDP, router
or AP control, smart-home bridges, or any runtime adapter behavior.

The follow-up layer consumes sanitized Phase 11G acceptance metadata only. A
record includes:

- follow-up id
- schema and contract versions
- domain label
- source acceptance label and hash
- follow-up type and status
- blocker disposition, reviewer queue, and stale renewal summaries
- unresolved review, blocking, and rejection counts
- `runtime_stage: not-implemented`
- `execution_permitted: false`

Follow-up types are `stale-renewal`, `blocker-disposition`,
`reviewer-queue`, `needs-more-review`, and `archived-no-action`.

Follow-up statuses are `open`, `blocked`, `resolved-for-planning`, `rejected`,
and `archived`. `resolved-for-planning` means only that planning blockers were
summarized as dispositioned. It does not enable runtime.

The validators fail closed for missing fields, unsupported versions,
contradictory status/type/count combinations, runtime-authorizing wording,
unsafe values, URLs, absolute paths, source identifiers, credentials,
device/router identifiers, model/parser/provider bodies, raw document text, raw
CSI/RF, and medical or clinical claims.

The deterministic fixture is
`fixtures/reviews/phase-11h-followup-remediation-v1.json`. It contains
sanitized follow-up records for document-ingestion and RF booth / WiFi CSI
planning, including blocker disposition, reviewer queue, stale renewal,
resolved-for-planning, archived-no-action, and rejected examples.

The focused Phase 11H test is
`tests/test_phase11h_followup_remediation.py`.

## Phase 11I Continuation

Phase 11I consumes these sanitized follow-up records to build reviewer queue
indexes and queue acceptance checks. Queue acceptance labels such as
`accepted-for-planning-queue` remain navigation metadata only; they do not
authorize any runtime adapter behavior.
