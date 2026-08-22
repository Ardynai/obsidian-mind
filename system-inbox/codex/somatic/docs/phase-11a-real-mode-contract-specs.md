# Phase 11A Real-Mode Contract Specs

Phase 11A defines future real-mode adapter contracts for document ingestion and
RF booth / WiFi CSI work. It is contract/spec planning only. It does not add a
runtime, provider body, parser body, model body, dependency, network behavior,
document ingestion, RF capture, or hardware control.

## Shared Contract Layer

The shared contract layer lives in `somatic.safety.phase11_contracts` and extends
the existing `somatic.safety.adapter_readiness` gate. It keeps the same review
gates: consent, license review, privacy review, hardware review, model artifact
review, dependency review, and network policy review.

Every Phase 11A contract spec reports:

- `planning_only: true`
- `metadata_only: true`
- `runtime_stage: not-implemented`
- `execution_permitted: false`
- `real_mode_runtime_enabled: false`

Even when every review gate is recorded as complete, runtime execution remains
disabled until a later explicit opt-in runtime phase exists.

## Document Ingestion Contracts

The document contract spec covers only future requirements:

- Metadata-only staging contract: count/status metadata only.
- Parser boundary contract: parser execution remains disabled in this phase.
- Artifact privacy contract: no body text, origin identifiers, local names,
  paths, URLs, provider details, or parser details may cross the public boundary.
- License/source review contract: required before any future real adapter work.

Phase 11A does not crawl files, parse PDFs, ingest documents, call networks, or
export document bodies.

## RF Booth / WiFi CSI Contracts

The RF booth contract spec covers only future review metadata:

- Booth hardware topology metadata contract: small controlled booth,
  single-intended-subject assumption, fixed AP role, receiver role count range,
  and empty-booth baseline concept.
- Consent/privacy contract: required before any future real-mode work.
- Hardware review contract: required before hardware access.
- Model artifact review contract: required before any model download or
  execution.
- Network policy contract: required before any network behavior.

Phase 11A does not execute RuView, download or run models, flash ESP32 devices,
capture packets, enter monitor mode, start MQTT/UDP listeners, control routers
or APs, bridge smart-home systems, or export RF signal data.

## Status Surfaces

The compact public status appears as `p11a_contract_status` on the existing
document and WiFi CSI adapter status surfaces. Provider manifests expose only
safe labels such as `p11a-contract-spec-only`, `real-mode-planning-only`, and
`no-runtime-enable`.

Doctor output names the Phase 11A contract specs for humans, but machine-readable
evidence artifacts keep public-safe `p11a` status fields to preserve existing
CSI and document privacy scanners.

## Phase 11B Continuation

Phase 11B adds deterministic review-record fixtures and fail-closed validators
around these Phase 11A specs. Review records can document consent,
license/source, privacy, hardware, model artifact, dependency, and network
policy review state, but completed review records still keep
`execution_permitted: false`, `real_mode_runtime_enabled: false`, and
`runtime_stage: not-implemented`.

## Phase 11C Continuation

Phase 11C assembles these specs and Phase 11B review records into sanitized
preflight dossiers. The dossiers can report packet ids, fingerprints, per-gate
status, and rejection reasons for planning review only; they still keep
`execution_permitted: false`, `real_mode_runtime_enabled: false`, and
`runtime_stage: not-implemented`.

## Phase 11D Continuation

Phase 11D wraps Phase 11C dossiers with lifecycle audit records,
deterministic dossier comparisons, reviewer signoff metadata, and explicit
audit decisions. Those records remain planning evidence only and still keep
`execution_permitted: false`, `real_mode_runtime_enabled: false`, and
`runtime_stage: not-implemented`.

## Non-Goals

Phase 11A intentionally does not add:

- Real document ingestion, crawling, PDF parsing, or parser execution.
- Live RF capture, packet capture, monitor mode, device probing, or hardware
  access.
- Model download, model execution, RuView execution, or provider execution.
- Network calls, MQTT/UDP listeners, router/AP control, or smart-home bridges.
- Raw document text, raw CSI/RF data, origin identifiers, fixture names,
  absolute paths, URLs, credentials, provider bodies, parser bodies, model
  bodies, device/router identifiers, or care claims in sanitized artifacts.

## Verification

The focused Phase 11A tests are in
`tests/test_phase11a_contract_spec_planning_surfaces.py`. They validate both
domain specs, prove all-gates-reviewed still leaves runtime disabled, reject
unknown or private fields fail-closed, and verify compact adapter status remains
safe for public surfaces.
