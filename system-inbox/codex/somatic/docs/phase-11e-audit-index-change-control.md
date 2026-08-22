# Phase 11E Audit Index And Change Control

Phase 11E adds a deterministic audit-index and change-control layer around
the Phase 11D lifecycle audit records. It is still pre-runtime planning only.
Audit indexes, supersession chains, reviewer-scope summaries, and retention
policies do not permit runtime execution.

## Audit Index Scope

The audit-index helpers live in `somatic.safety.phase11_contracts`. An index
records sanitized metadata only:

- Index id and contract versions.
- Included dossier packet labels.
- Included lifecycle record labels.
- Included decision record labels.
- Deterministic fingerprints for included sanitized records.
- Created, reviewed, superseded, rejected, archived, and decision-recorded
  lifecycle counts.
- Blocking and rejection counts.
- `runtime_stage: not-implemented`.
- `execution_permitted: false`.

The index never exposes underlying review records, dossier bodies, lifecycle
record bodies, decision bodies, provider bodies, parser bodies, model bodies,
local paths, network locators, document text, CSI values, or radio measurement
bodies.

## Deterministic Ordering

Audit-index entries are ordered by sanitized labels and deterministic hashes.
Ordering does not depend on local filesystem traversal order, platform path
sorting, or timestamps. The public index reports only compact labels, counts,
fingerprints, and status fields.

## Supersession Chains

Supersession chains prove that a sanitized lifecycle record supersedes a prior
sanitized record label and hash. Validators fail closed when a chain has a
cycle, points across domains without explicit safe metadata, omits a prior
link, omits a future link, contradicts the indexed records, or implies
runtime permission.

## Reviewer-Scope Coverage

Reviewer-scope summaries cover document-ingestion planning and RF booth /
WiFi CSI planning. They report scope labels for consent, license/source,
privacy, hardware, model artifact, dependency, and network policy gates.

Coverage summaries do not include reviewer identity secrets. A complete
coverage summary is planning evidence only and still leaves execution disabled.

## Export And Retention Policy

Export and retention policy records are local-only metadata:

- Metadata-only fixture export is allowed for deterministic checked-in review
  fixtures.
- Source content and signal-value export are prohibited.
- Retention is a label only, with no local path.
- External upload and network transfer are disabled.
- Runtime stage remains `not-implemented`.
- Execution remains false.

## Fixtures

The deterministic fixture bundle is
`fixtures/reviews/phase-11e-audit-index-v1.json`. It contains sanitized audit
index metadata, change-control records, supersession chains, reviewer-scope
coverage summaries, and export/retention policy examples for document
ingestion and RF booth / WiFi CSI planning.

## Validators

The Phase 11E validators fail closed for:

- Missing required fields.
- Unsupported versions.
- Contradictory counts.
- Invalid ordering.
- Invalid supersession chains.
- Cross-domain drift.
- Decisions implying execution permission.
- Unsafe private values or keys.

Rejected records return sanitized rejected metadata and do not echo unsafe
input values.

## Public Surfaces

Doctor, provider manifest, adapter status, release summary, and document
artifact inspection expose compact audit-index status only: contract version,
index id, fingerprint, status, entry count, blocking count, rejection count,
supersession count, retention-policy count, runtime stage, and execution
false.

They do not dump audit-index bodies, lifecycle records, review records,
dossier bodies, decision bodies, provider bodies, parser bodies, model bodies,
document contents, CSI values, radio measurement bodies, local paths, or
network locators.

## Non-Goals

Phase 11E intentionally does not add real document ingestion, file crawling,
PDF parsing, RuView execution, model download or execution, ESP32 flashing,
packet capture, monitor mode, MQTT/UDP listeners, router/AP control,
smart-home bridges, provider execution, parser execution, model execution, or
care claims.

## Verification

The focused Phase 11E test is
`tests/test_phase11e_audit_index_change_control.py`.

It proves deterministic audit-index construction, sanitized ordering,
supersession-chain validation, export/retention policy validation, compact
public status, and the rule that completed audit indexes still leave runtime
execution disabled.

## Phase 11F Continuation

Phase 11F consumes these audit-index records to build compact handoff and
reporting summaries. Those handoffs remain metadata-only planning artifacts
and still cannot permit runtime execution.
