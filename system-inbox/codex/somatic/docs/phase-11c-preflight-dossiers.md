# Phase 11C Preflight Dossiers

Phase 11C assembles Phase 11A contract specs and Phase 11B review records into
deterministic preflight dossiers for future document ingestion and RF booth /
WiFi CSI planning. The dossiers are local metadata packets only. They do not
permit runtime execution.

## Dossier Scope

The dossier helpers live in `somatic.safety.phase11_contracts`. Each dossier
records:

- A deterministic packet id.
- Contract, review-record, and preflight packet versions.
- Sanitized review labels for included records.
- Per-gate reviewed, missing, or rejected status.
- SHA-256 fingerprints over included sanitized records and packet metadata.
- Blocking or rejection reasons.
- `runtime_stage: not-implemented`.
- `execution_permitted: false`.

Document ingestion dossiers use the Phase 11A document contracts for
metadata-only staging, parser boundary, artifact privacy, and license/source
review. RF booth / WiFi CSI dossiers use the Phase 11A booth topology,
consent/privacy, hardware, model artifact, dependency, and network policy
planning contracts.

## Fixtures

The deterministic fixture bundle is
`fixtures/reviews/phase-11c-preflight-dossiers-v1.json`. It includes document
and RF booth / WiFi CSI dossiers for missing, rejected, and reviewed planning
states. Reviewed dossiers can show that every gate has planning evidence, but
they still keep runtime disabled.

## Validators

`validate_phase11_preflight_dossier` fails closed for:

- Missing required records or gate entries.
- Unsupported contract, review-record, or packet versions.
- Contradictory status, count, or gate summaries.
- Any runtime permission or execution flag.
- Unsafe private values or keys.

Invalid dossiers return sanitized rejected metadata and do not echo unsafe
input values.

## Public Surfaces

Doctor, provider manifest, adapter status, release summary, and document
artifact-inspection surfaces expose compact preflight status only: packet
contract version, packet id, fingerprint, status, gate counts, runtime stage,
and execution false. They do not dump review records, parser/provider bodies,
model bodies, raw document text, raw CSI/RF values, local paths, or network
addresses.

## Phase 11D Continuation

Phase 11D wraps these dossiers in lifecycle audit records. It adds sanitized
dossier comparison helpers, reviewer signoff metadata, and explicit audit
decision records. A `no-blockers` signoff or all-gates-reviewed decision still
keeps runtime execution disabled.

## Non-Goals

Phase 11C intentionally does not add real document ingestion, file crawling,
PDF parsing, RuView execution, model download or execution, ESP32 flashing,
packet capture, monitor mode, MQTT/UDP listeners, router/AP control,
smart-home bridges, provider execution, parser execution, model execution, or
care claims.

## Verification

The focused Phase 11C tests are:

- `tests/test_phase11c_review_packet_builder.py`
- `tests/test_phase11c_preflight_dossier_fixtures.py`

They prove deterministic packet construction, fail-closed validation, sanitized
rejection, compact public status, and the rule that completed dossiers still
leave runtime execution disabled.
