# Phase 11F Audit Handoff Reporting

Phase 11F adds compact audit handoff records over the Phase 11E audit-index
and change-control layer. These handoffs are communication and reporting
artifacts only. They are not authorization to run real document adapters,
capture WiFi CSI, execute models, or enable any runtime path.

## Handoff Scope

The handoff helpers live in `somatic.safety.phase11_contracts`. A handoff is
built only from sanitized Phase 11E audit-index metadata and contains:

- Handoff id and fingerprint.
- Schema and contract versions.
- Domain label for document-ingestion or RF booth / WiFi CSI planning.
- Included audit-index label and fingerprint.
- Lifecycle status counts.
- Reviewer-scope coverage counts.
- Local retention/export policy summary.
- Blocking, rejection, and unresolved review counts.
- `runtime_stage: not-implemented`.
- `execution_permitted: false`.

The handoff never exposes the underlying audit-index entries, change-control
records, lifecycle records, review records, dossier bodies, provider bodies,
parser bodies, model bodies, document contents, CSI values, radio measurement
bodies, local paths, or network locators.

## Validation

Phase 11F validators fail closed for:

- Missing required fields.
- Unsupported versions.
- Contradictory counts.
- Unsafe labels or fingerprints.
- Runtime permission flags.
- Unsafe private values or keys.

Rejected handoffs return sanitized rejected metadata and do not echo unsafe
input values.

## Public Surfaces

Doctor, provider manifest, adapter status, release summary, and document
artifact inspection expose compact handoff status only: contract version,
handoff id, fingerprint, status, included audit-index label and fingerprint,
summary counts, runtime stage, and execution false.

They do not dump audit-index bodies, lifecycle records, review records,
dossier bodies, decision bodies, provider bodies, parser bodies, model bodies,
document contents, CSI values, radio measurement bodies, local paths, or
network locators.

## Non-Goals

Phase 11F intentionally does not add real document ingestion, file crawling,
PDF parsing, RuView execution, model download or execution, ESP32 flashing,
packet capture, monitor mode, MQTT/UDP listeners, router/AP control,
smart-home bridges, provider execution, parser execution, model execution, or
care claims.

## Verification

The focused Phase 11F test is
`tests/test_phase11f_audit_handoff_reporting.py`.

It proves deterministic handoff construction, sanitized compact summaries,
fail-closed validation, and the rule that completed reviews with no blockers
still leave runtime execution disabled.
