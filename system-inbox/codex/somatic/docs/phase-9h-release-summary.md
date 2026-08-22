# Phase 9H / 11M Release Summary

Phase 9H closes the Phase 8C through Phase 9G sensor-evidence subsystem as a
documented, fixture-only, metadata-only surface. Phase 10D extends the Phase 8C
through Phase 10D release surface through document evidence operationalization
without changing runtime evidence generation, scoring, ranking, Fabric
transport, or ingestion behavior. Phase 10E extends the range through a shared
cross-domain evidence framework and CSI/document contract hardening without
changing pack shapes, artifact names, runtime generation, scoring, ranking,
Fabric transport, or ingestion behavior. Phase 10F adds a strict metadata-only
document adapter boundary before document evidence-pack construction without
adding ingestion, file crawling, parsing, network access, dependencies, or
transport/install behavior. Phase 10G adds a strict metadata-only WiFi CSI
source adapter boundary, reclassifies RuView as conditional reference-only, and
records a booth-first future planning profile without changing CSI pack shapes,
fingerprints, parser behavior, runtime generation, scoring, ranking, Fabric
transport, or ingestion behavior. Phase 10H adds a shared real-mode readiness
gate across document and WiFi CSI adapter surfaces without enabling ingestion,
hardware access, model execution, network access, or live runtime behavior.
Phase 10I locks those boundaries with shared invariant tests across provider
manifest, doctor, workflow report, artifact inspection, and release-summary
fixture surfaces. Phase 10J records the checkpoint and next safe lanes without
changing runtime behavior. Phase 11A adds `somatic.safety.phase11_contracts`
as the contract/spec-only planning layer for future document ingestion and RF
booth / WiFi CSI real-mode review requirements without enabling runtime
behavior. Phase 11B adds deterministic review-record fixtures and fail-closed
validators for the Phase 11A review gates while keeping runtime execution
disabled. Phase 11C assembles those contract specs and review records into
deterministic sanitized preflight dossiers with packet fingerprints, per-gate
status, and rejection reasons while keeping runtime execution disabled. Phase
11D adds lifecycle audit records, deterministic dossier comparisons, reviewer
signoff metadata, and explicit audit decisions while keeping runtime execution
disabled.
Phase 11E adds deterministic audit indexes, change-control records,
supersession chains, reviewer-scope coverage summaries, and local
export/retention policies around those lifecycle audit records while keeping
runtime execution disabled.
Phase 11F adds compact audit handoff records over those sanitized audit-index
records for provider, doctor, release, and inspection reporting while keeping
runtime execution disabled.
Phase 11G adds compact handoff acceptance/check records over those sanitized
Phase 11F handoff reports so downstream reviewers can distinguish accepted,
blocked, stale, and rejected planning handoffs while keeping runtime execution
disabled.
Phase 11H adds compact follow-up/remediation planning queues over those
sanitized Phase 11G acceptance records so reviewers can distinguish stale
renewal, blocker disposition, reviewer queue, needs-more-review, and archived
no-action follow-ups while keeping runtime execution disabled.
Phase 11I adds compact follow-up queue indexes and queue acceptance checks over
those sanitized Phase 11H follow-up records so reviewers can see open, blocked,
stale, archived, rejected, resolved-for-planning, and needs-more-review queues
without enabling runtime execution.
Phase 11J adds compact reviewer decision-closeout records over those sanitized
Phase 11I queue indexes so reviewers can close, defer, reject, archive, or
block planning queues without enabling runtime execution.
Phase 11K adds a compact review-trail export over the Phase 11A through 11J
planning metadata so future reviewers can navigate the trail without enabling
runtime execution.
Phase 11L adds a compact runtime-authorization gap ledger over the Phase 11A
through 11K planning metadata so reviewers can see the remaining future
authorization prerequisites without enabling runtime execution.
Phase 11M adds the final Phase 11 planning/governance closeout index over the
Phase 11A through 11L metadata trail and declares Phase 11 complete as a
pre-runtime planning/governance phase without enabling runtime execution.

The current documented range is Phase 8C through Phase 11M.

## Completed Scope

| Phase | Public Result |
| --- | --- |
| 8C | Stable local CSI parser contract and sanitized parser CLI output. |
| 8D | Fixture replay through the sandbox provider, without capture paths. |
| 8E | CSI evidence scoring over sanitized replay status and counts. |
| 8F | CSI batch readiness metadata for tournament reports. |
| 8G | Deterministic CSI evidence-pack export at `artifacts/csi_evidence_pack.json`. |
| 8H | Public CSI parser, n-of-1, and tournament example docs. |
| 8I | CSI v1 compatibility and fingerprint hardening. |
| 9A | Generic sensor-evidence contract primitives. |
| 9B | Generic run and Fabric planning refs by run-relative path plus SHA-256. |
| 9C | `environment-fixture` provider and `artifacts/environment_evidence_pack.json`. |
| 9D | Provider registry and workflow config validation. |
| 9E | Toy provider extension template and `toy-counter-fixture` example. |
| 9F | Provider discovery and workflow validation CLI. |
| 9G | Provider manifest snapshot contract and drift tests. |
| 10A | `document-fixture` as the first non-sensor evidence-pack domain. |
| 10D | Document evidence artifact inspection, readiness counts, workflow summary, and release-summary surfacing. |
| 10E | Cross-domain evidence framework surface plus shared CSI/document compatibility and privacy hardening. |
| 10F | Metadata-only document adapter boundary with fail-closed output validation. |
| 10G | Metadata-only WiFi CSI source boundary, conditional RuView reference status, and booth-first planning profile. |
| 10H | Shared real-mode readiness gate for document and WiFi CSI adapter status surfaces. |
| 10I | Shared safety invariants across provider manifest, doctor, workflow, inspect, and release-summary fixture surfaces. |
| 10J | Phase 10 checkpoint and roadmap consolidation for future real-mode planning. |
| 11A | Contract/spec-only future real-mode requirements for document ingestion and RF booth / WiFi CSI review surfaces. |
| 11B | Review-record fixtures and fail-closed conformance validators for Phase 11A planning gates, with runtime still disabled. |
| 11C | Sanitized preflight dossier packets over Phase 11A specs and Phase 11B review records, with runtime still disabled. |
| 11D | Lifecycle audit records, dossier comparison helpers, reviewer signoff metadata, and explicit audit decisions, with runtime still disabled. |
| 11E | Audit-index records, change-control helpers, supersession chains, reviewer-scope summaries, and local export/retention policy metadata, with runtime still disabled. |
| 11F | Compact audit handoff/reporting records over Phase 11E audit-index metadata, with runtime still disabled. |
| 11G | Handoff acceptance/check records over Phase 11F handoff reports, with accepted-for-planning still runtime disabled. |
| 11H | Follow-up/remediation planning queues over Phase 11G acceptance records, with resolved-for-planning still runtime disabled. |
| 11I | Follow-up queue indexes and acceptance checks over Phase 11H records, with runtime still disabled. |
| 11J | Reviewer decision closeouts over Phase 11I queue records, with runtime still disabled. |
| 11K | Review-trail export over Phase 11A through 11J planning metadata, with runtime still disabled. |
| 11L | Runtime-authorization gap ledger over Phase 11A through 11K planning metadata, with runtime still disabled. |
| 11M | Final Phase 11 planning/governance closeout index over Phase 11A through 11L metadata, with runtime still disabled. |

## Public Commands

```powershell
python -m somatic csi-parse <fixture-name> --repo-root .
python -m somatic sensor-evidence providers
python -m somatic sensor-evidence providers --format json
python -m somatic sensor-evidence validate --workflow <workflow.yaml>
python -m somatic sensor-evidence validate --workflow <workflow.yaml> --format json
python -m somatic sensor-evidence inspect --artifact <artifact.json>
python -m somatic sensor-evidence inspect --artifact <artifact.json> --format json
```

`sensor-evidence providers --format json` is the machine-readable provider
manifest contract. Its current manifest contract version is 1. The current
provider count is 4. `sensor-evidence inspect` validates persisted sanitized
document and CSI evidence-pack artifacts and reports compatibility, readiness,
counts, fingerprint, and run-relative artifact reference metadata only. Phase
10E adds no new public CLI command. Phase 10F keeps the same commands and adds
sanitized document adapter status where `document-fixture` is already listed or inspected.
Phase 10G keeps the same commands and adds sanitized CSI source-adapter status
where `wifi-csi` is already listed by provider discovery and doctor output.
Phase 10H keeps the same commands and adds shared real-mode readiness gate
status where adapter-backed providers already appear. Phase 10I keeps the same
commands and proves the public surfaces preserve shared safety invariants.
Phase 10J adds only checkpoint documentation and machine-summary alignment.
Phase 11A keeps the same commands and adds compact p11a planning status where
adapter-backed providers already appear. It does not add an execution command.
Phase 11B keeps the same commands and adds compact review-record status where
adapter-backed providers already appear. It does not add an execution command.
Phase 11C keeps the same commands and adds compact preflight dossier status
where adapter-backed providers already appear. It does not add an execution
command.
Phase 11D keeps the same commands and adds compact lifecycle audit status where
adapter-backed providers already appear. It does not add an execution command.
Phase 11E keeps the same commands and adds compact audit-index/change-control
status where adapter-backed providers already appear. It does not add an
execution command.
Phase 11F keeps the same commands and adds compact audit handoff status where
adapter-backed providers already appear. It does not add an execution command.
Phase 11G keeps the same commands and adds compact handoff acceptance status
where adapter-backed providers already appear. It does not add an execution
command.
Phase 11H keeps the same commands and adds compact follow-up/remediation queue
status where adapter-backed providers already appear. It does not add an
execution command.
Phase 11I keeps the same commands and adds compact follow-up queue index status
where adapter-backed providers already appear. It does not add an execution
command.
Phase 11J keeps the same commands and adds compact decision-closeout status
where adapter-backed providers already appear. It does not add an execution
command.
Phase 11K keeps the same commands and adds compact review-trail export status
where adapter-backed providers already appear. It does not add an execution
command.
Phase 11L keeps the same commands and adds compact runtime gap ledger status
where adapter-backed providers already appear. It does not add an execution
command.
Phase 11M keeps the same commands and adds compact planning/governance closeout
status where adapter-backed providers already appear. It does not add an
execution command.

## Registered Providers

| Provider ID | Evidence Kind | Artifact Name | Run-Relative Artifact |
| --- | --- | --- | --- |
| `wifi-csi` | `csi-evidence-pack` | `csi_evidence_pack` | `artifacts/csi_evidence_pack.json` |
| `environment-fixture` | `environment-tabular-evidence-pack` | `environment_evidence_pack` | `artifacts/environment_evidence_pack.json` |
| `toy-counter-fixture` | `toy-counter-evidence-pack` | `toy_counter_evidence_pack` | `artifacts/toy_counter_evidence_pack.json` |
| `document-fixture` | `document-evidence-pack` | `document_evidence_pack` | `artifacts/document_evidence_pack.json` |

## Compatibility Contracts

Evidence-pack readers and the provider manifest use the stable compatibility
classifications `compatible`, `incompatible`, `unsupported_version`, and
`malformed`.

CSI v1 evidence packs preserve the existing artifact name, public shape,
compatibility classifications, pack ID prefix, and deterministic fingerprint scope
while using the shared evidence-pack contract validator underneath.
Environment, toy, and document evidence packs follow the generic contract and
keep their artifact names and deterministic fingerprints stable. The provider manifest is
checked in as `fixtures/providers/sensor-evidence-provider-manifest-v1.json`.

## Run And Fabric Reference Behavior

Run manifests, n-of-1 packets, tournament summaries, and planning-only Fabric
surfaces reference evidence packs by run-relative artifact path plus SHA-256.
When a pack supplies a fingerprint, the compact ref carries it as metadata.
Portable refs do not inline local fixture contents or detailed local parser
diagnostics.

Phase 10D operationalizes `document-fixture` by surfacing
`document_evidence_pack` refs, compatibility status, document count/status
readiness metadata, and sanitized report summaries wherever the document pack is
emitted. This remains metadata-only and does not add document ingestion or
source parsing.

Phase 10E introduces `somatic.evidence.framework` as the neutral import surface
for deterministic fingerprints, run-relative artifact refs, compatibility
classification, status-count helpers, and privacy scanning. CSI and document
evidence keep their domain-specific count fields, status behavior, artifact
names, and fingerprints, but share the same fail-closed validator path.

Phase 10F adds `somatic.evidence.document_adapter` as the strict boundary for
future document providers. The current `document-fixture` provider is the first
implementation. Its public capability labels are `metadata-only`,
`fixture-only`, `offline`, `no-network`, `no-file-crawling`, `no-pdf-parsing`,
`no-real-ingestion`, `no-raw-body-export`, `no-source-id-export`,
`no-absolute-path-export`, and `no-url-export`. Adapter outputs are validated
before evidence-pack construction; invalid output becomes a rejected sanitized
metadata result.

Phase 10G adds `somatic.sensors.csi_adapter` as the strict metadata-only
boundary for future WiFi CSI source/provider work. The current surface is
fixture-backed, offline, reference-only, and fail-closed. RuView is no longer a
blanket rejection; it is tracked as conditional reference-only while preserving
earlier overclaim, model-loading, and unverified deployment warnings. The booth
profile records a future single-subject controlled-booth direction with fixed AP
plus receiver-node planning metadata. Somatic still does not run RuView, flash
devices, download or execute models, bridge home automation systems, or perform
care inference.

Phase 10H adds `somatic.safety.adapter_readiness` as the shared real-mode
readiness gate for future adapter work. The default document and WiFi CSI gates
are `blocked-fixture-reference-only` with missing consent, license review,
privacy review, hardware review, model artifact review, dependency review, and
network policy review. Even a fully reviewed gate remains runtime-disabled until
a later phase adds an explicit opt-in runtime.

Phase 10I adds shared invariant coverage across public provider, doctor,
workflow report, artifact inspection, and release-summary fixture surfaces. It
proves that document and WiFi CSI surfaces consistently remain metadata-only,
fixture or reference-only, real-mode blocked, runtime disabled, and network
disabled without changing runtime behavior.

Phase 10J adds `docs/phase-10-checkpoint.md` as the auditable baseline for
future real-mode planning. It records the Phase 10A through Phase 10I state,
the current evidence-domain matrix, implemented versus intentionally blocked
surfaces, and the next safe lanes for Phase 11A contract specs.

Phase 11A adds `somatic.safety.phase11_contracts` and
`docs/phase-11a-real-mode-contract-specs.md`. The new contract specs describe
metadata-only document staging, parser boundary, artifact privacy,
license/source review, RF booth topology metadata, consent/privacy review,
hardware review, model artifact review, and network policy review. They remain
planning-only with runtime stage `not-implemented`, execution false, and the
existing real-mode readiness gate still controlling review state.

Phase 11B extends `somatic.safety.phase11_contracts` with review-record
fixtures and validators documented in
`docs/phase-11b-review-record-fixtures.md`. The fixture bundle records consent,
license/source, privacy, hardware, model artifact, dependency, and network
policy review examples for document ingestion and RF booth / WiFi CSI planning.
Public surfaces expose only compact review-record status and counts. Completed
review records can satisfy planning readiness counts, but runtime stage remains
`not-implemented`, execution remains false, and real-mode runtime remains
disabled.

Phase 11C extends `somatic.safety.phase11_contracts` with preflight dossier
builders and validators documented in `docs/phase-11c-preflight-dossiers.md`.
The dossier bundle assembles Phase 11A specs and Phase 11B review records into
sanitized packet metadata for document ingestion and RF booth / WiFi CSI
planning. Each packet includes deterministic status, gate counts, packet id,
fingerprint, and blocking reasons. Public surfaces expose only compact dossier
status. Even a reviewed dossier keeps runtime stage `not-implemented`,
execution false, and real-mode runtime disabled.

Phase 11D extends `somatic.safety.phase11_contracts` with lifecycle audit
builders and validators documented in `docs/phase-11d-dossier-lifecycle.md`.
The lifecycle bundle records created, reviewed, superseded, rejected, archived,
and decision-recorded audit states for document ingestion and RF booth / WiFi
CSI planning. Public surfaces expose only compact lifecycle status, signoff
verdict, audit decision, counts, and fingerprints. A no-blockers signoff or
all-gates-reviewed decision still keeps runtime stage `not-implemented`,
execution false, and real-mode runtime disabled.

Phase 11E extends `somatic.safety.phase11_contracts` with audit-index and
change-control builders and validators documented in
`docs/phase-11e-audit-index-change-control.md`. The audit-index bundle records
sanitized dossier packet labels, lifecycle record labels, decision record
labels, deterministic fingerprints, lifecycle counts, blocking counts,
supersession chains, reviewer-scope coverage summaries, and local
export/retention policy metadata. Public surfaces expose only compact
audit-index status and counts. Even a fully reviewed index keeps runtime stage
`not-implemented`, execution false, and real-mode runtime disabled.

Phase 11F extends `somatic.safety.phase11_contracts` with compact audit
handoff builders and validators documented in
`docs/phase-11f-audit-handoff-reporting.md`. The handoff bundle summarizes
sanitized Phase 11E audit-index labels, fingerprints, lifecycle counts,
reviewer-scope coverage, retention/export policy status, blocking counts,
rejection counts, and unresolved review counts for document ingestion and RF
booth / WiFi CSI planning. Public surfaces expose only compact handoff status
and counts. Even when all reviews are complete and no blockers remain,
runtime stage remains `not-implemented`, execution remains false, and
real-mode runtime remains disabled.

Phase 11G extends `somatic.safety.phase11_contracts` with handoff acceptance
builders and validators documented in `docs/phase-11g-handoff-acceptance.md`.
The acceptance bundle consumes only sanitized Phase 11F handoff records and
records whether a handoff is accepted for planning, blocked, stale, or
rejected. Public surfaces expose only compact acceptance status, hashes,
booleans, and counts. Accepted for planning is not runtime permission:
runtime stage remains `not-implemented`, execution remains false, and
real-mode runtime remains disabled.

Phase 11H extends `somatic.safety.phase11_contracts` with follow-up and
remediation builders and validators documented in
`docs/phase-11h-followup-remediation.md`. The follow-up bundle consumes only
sanitized Phase 11G acceptance records and records stale renewal, blocker
disposition, reviewer queue, needs-more-review, and archived-no-action planning
queues. Public surfaces expose only compact follow-up status, source acceptance
label/hash, summary labels, and counts. Resolved for planning is not runtime
permission: runtime stage remains `not-implemented`, execution remains false,
and real-mode runtime remains disabled.

Phase 11I extends `somatic.safety.phase11_contracts` with follow-up queue index
builders and validators documented in
`docs/phase-11i-followup-queue-index.md`. The queue bundle consumes only
sanitized Phase 11H follow-up records and records queue status counts, blocker
disposition counts, reviewer queue counts, stale renewal counts, unresolved
review counts, and queue acceptance checks. Accepted for planning queue status
is not runtime permission: runtime stage remains `not-implemented`, execution
remains false, and real-mode runtime remains disabled.

Phase 11J extends `somatic.safety.phase11_contracts` with reviewer
decision-closeout builders and validators documented in
`docs/phase-11j-decision-closeout.md`. The closeout bundle consumes only
sanitized Phase 11I queue index and queue acceptance metadata and records
close, defer, reject, archive, needs-new-review, and blocked planning
decisions. Closed for planning is not runtime permission: runtime stage remains
`not-implemented`, execution remains false, and real-mode runtime remains
disabled.

Phase 11K extends `somatic.safety.phase11_contracts` with review-trail export
builders and validators documented in
`docs/phase-11k-review-trail-export.md`. The export consumes only existing
sanitized Phase 11A through 11J status and closeout summaries and records the
phase range, covered phase count, domain labels, final closeout
decision/status, unresolved review counts, blocker counts, stale counts, and
the `real-mode-authorization-missing` readiness gap. Exported review trails are
not runtime permission: runtime stage remains `not-implemented`, execution
remains false, and real-mode runtime remains disabled.

Phase 11L extends `somatic.safety.phase11_contracts` with runtime-authorization
gap ledger builders and validators documented in
`docs/phase-11l-runtime-authorization-gap-ledger.md`. The ledger consumes only
existing sanitized Phase 11A through 11K status, closeout, and export summaries
and records the source phase range, covered phase count, domain labels,
`not-authorized` authorization status, the `real-mode-authorization-missing`
readiness gap, missing future gate counts, unresolved review counts, blocker
counts, and stale counts. Ledgered gaps are not runtime permission: runtime
stage remains `not-implemented`, execution remains false, and real-mode runtime
remains disabled.

Phase 11M extends `somatic.safety.phase11_contracts` with planning/governance
closeout builders and validators documented in
`docs/phase-11m-planning-governance-closeout.md`. The closeout consumes only
existing sanitized Phase 11A through 11L status, closeout, review-trail export,
and runtime gap ledger summaries and records the final status
`phase-11-planning-governance-complete`, `not-authorized` runtime authorization
status, the `real-mode-authorization-missing` readiness gap, compact counts,
and the requirement that a future phase be explicit before runtime work.
Governance complete is not runtime permission: runtime stage remains
`not-implemented`, execution remains false, and real-mode runtime remains
disabled.

## Privacy Boundary And Non-Goals

The subsystem is standard-library only, offline, fixture-only, and sanitized
metadata only. It does not add new providers, live capture, hardware access,
network listeners, provider secrets, package dependencies, runtime scoring
changes, tournament ranking changes, Fabric publishing, Fabric transport, or
Fabric install behavior. It also does not add RuView execution, device flashing,
model download/execution, packet capture, monitor mode, WiFi device probing, or
home-automation bridging. Phase 11B review records, Phase 11C preflight
dossiers, Phase 11D lifecycle audit records, Phase 11E audit indexes,
Phase 11F audit handoffs, Phase 11G handoff acceptance checks, Phase 11H
follow-up/remediation queues, Phase 11I follow-up queue indexes, Phase 11J
decision closeouts, Phase 11K review-trail exports, Phase 11L runtime gap
ledgers, and Phase 11M planning/governance closeout indexes are
planning evidence only;
they are not permission to run real adapters.

Portable artifacts and public summaries must avoid fixture filenames, private
paths, source identifiers, unsafe refs, local parser detail documents, provider
internals, secret-like fields, and provider measurement contents.

## Phase 10A — First Non-Sensor Evidence Domain

Phase 10A adds the `document-fixture` provider as the first non-sensor evidence
domain. It lives in `somatic/evidence/` rather than `somatic/sensors/` and
reuses the same generic evidence contract primitives, artifact-ref pattern, and
sanitization guarantees. The provider reads small checked-in JSON fixtures from
`fixtures/evidence/document/` and emits sanitized count/status metadata only —
no raw document bodies, absolute paths, or credentials leak into artifacts.

Source map:
- `somatic/evidence/document_evidence_pack.py` — contract, builder, fingerprint
- `somatic/evidence/document_fixture.py` — fixture-only provider
- `fixtures/evidence/document/` — checked-in document fixtures
- `examples/document-evidence-demo/` — example workflow
- `tests/test_document_evidence_pack.py` — deterministic, privacy, and ref tests

## Phase 10E — Cross-Domain Evidence Framework

Phase 10E adds a shared framework facade and moves CSI evidence-pack
compatibility onto the generic contract engine with CSI-specific contract data.
The change is intentionally structural: CSI parser/scoring/batch metadata,
document count/status metadata, provider registry entries, workflow summaries,
and report behavior remain domain-owned.

Source map:
- `somatic/evidence/framework.py` — neutral facade over shared evidence helpers
- `somatic/sensors/evidence.py` — shared contract validation, ref, fingerprint, status-count, and privacy helpers
- `somatic/sensors/csi_evidence_pack.py` — CSI domain contract using the shared validator
- `somatic/evidence/document_evidence_pack.py` — document domain contract using the framework facade
- `tests/test_cross_domain_evidence_framework.py` — CSI/document privacy and compatibility regressions

## Phase 10F — Document Adapter Boundary

Phase 10F adds a metadata-only adapter contract ahead of document evidence-pack
construction. `document-fixture` now implements that boundary and routes fixture
count/status metadata through fail-closed adapter validation before the pack
builder sees it. Unsafe or unknown adapter output becomes a rejected sanitized
metadata result instead of reaching portable artifacts.

Source map:
- `somatic/evidence/document_adapter.py` — metadata-only adapter contract and output validator
- `somatic/evidence/document_fixture.py` — first adapter implementation
- `somatic/evidence/document_evidence_pack.py` — defensive pack-builder validation and status metadata
- `tests/test_document_adapter_contract.py` — adapter output validation and privacy regressions

## Phase 10G — WiFi CSI Source Boundary

Phase 10G adds a metadata-only CSI source boundary ahead of future booth-first
work. The boundary validates RuView reassessment and booth-planning metadata
before CSI planning summaries consume it. Unsafe output becomes a rejected
sanitized metadata result and never reaches portable CSI evidence packs.

Source map:
- `somatic/sensors/csi_adapter.py` — metadata-only CSI source adapter contract and output validator
- `somatic/sensors/csi.py` — CSI planning metadata surface
- `fixtures/sensors/csi/csi-reference-inventory.json` — RuView reassessment and booth profile metadata
- `tests/test_wifi_csi_ruview_booth_boundary.py` — RuView, booth, adapter, and privacy regressions

## Phase 10H — Shared Real-Mode Readiness Gate

Phase 10H adds one shared readiness contract for future real-mode document and
WiFi CSI adapters. It distinguishes fixture mode, reference-only mode,
metadata-only adapter mode, and future real mode. The current providers remain
fixture or reference-only, and execution remains disabled.

Source map:
- `somatic/safety/adapter_readiness.py` — shared real-mode readiness gate contract
- `somatic/evidence/document_adapter.py` — document adapter gate surface
- `somatic/sensors/csi_adapter.py` — WiFi CSI adapter gate surface
- `tests/test_real_mode_readiness_gate.py` — shared gate and missing-gate regressions

## Phase 10I — Shared Safety Invariant Audit

Phase 10I adds regression coverage for document and WiFi CSI public surfaces.
The audit scans provider manifest, doctor, workflow reports, artifact
inspection, and the machine release-summary fixture for shared adapter/evidence
safety invariants. It does not add runtime behavior.

Source map:
- `tests/test_phase10i_shared_safety_invariants.py` — cross-surface invariant audit
- `somatic/cli/main.py` — CSI and document artifact inspection summaries
- `fixtures/reports/sensor-evidence-subsystem-summary-v1.json` — machine-readable invariant status surface

## Phase 10J — Checkpoint And Roadmap Consolidation

Phase 10J records the auditable Phase 10 checkpoint for future real-mode work.
It documents the completed Phase 10A through Phase 10I sequence, the current
evidence-domain matrix, implemented versus intentionally blocked surfaces, and
Phase 11A contract-spec-only lanes.

Source map:
- `docs/phase-10-checkpoint.md` — consolidated checkpoint, matrix, and next safe lanes
- `docs/source-map.md` — repository map through the checkpoint
- `tests/test_sensor_evidence_release_summary.py` — release-summary and checkpoint doc assertions

## Extension Path

Future sanitized fixture-only providers should follow
`docs/sensor-evidence-extension-template.md`: add a provider module, an
evidence-pack module, a sanitized registry entry, bounded workflow config
validation, deterministic evidence-pack tests, provider-manifest snapshot
updates, and privacy tests.
