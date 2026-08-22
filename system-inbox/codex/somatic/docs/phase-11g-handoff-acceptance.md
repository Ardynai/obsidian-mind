# Phase 11G Handoff Acceptance Checks

Phase 11G adds compact acceptance/check records over Phase 11F audit handoff
records. These records are for downstream planning review only. They do not
authorize document ingestion, RF capture, model execution, network access, or
real adapter runtime.

The acceptance layer consumes sanitized Phase 11F handoff metadata only. It
does not read audit-index entries, lifecycle records, review-record bodies,
preflight dossier bodies, raw document text, raw CSI/RF, parser/provider bodies,
model bodies, fixture filenames, paths, URLs, credentials, source identifiers,
device identifiers, or router identifiers.

Each acceptance record includes deterministic metadata:

- acceptance id and fingerprint
- contract versions
- domain label
- source handoff label and hash
- accepted-for-planning, blocked, and stale booleans
- missing and unresolved review counts
- rejection and blocking reason labels
- `runtime_stage: not-implemented`
- `execution_permitted: false`

`accepted_for_planning` means only that the sanitized handoff is acceptable for
planning review. It is not runtime permission. Even an accepted handoff keeps
real-mode runtime disabled and must not bypass the shared readiness gate.

Validators fail closed for missing fields, unsupported versions, contradictory
accepted/blocked/stale status, stale handoff hash mismatches, unsafe/private
values, and any implied runtime permission.

## Phase 11H Continuation

Phase 11H consumes these sanitized acceptance records to build follow-up and
remediation planning queues. Those queues remain metadata-only and do not
authorize adapter execution.
