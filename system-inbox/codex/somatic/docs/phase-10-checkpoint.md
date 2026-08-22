# Phase 10 Checkpoint

Phase 10J records the current evidence and adapter baseline after Phases 10A
through 10I. It is a documentation checkpoint only. It does not add document
ingestion, file crawling, PDF parsing, WiFi CSI capture, hardware control,
model execution, network behavior, Fabric transport, or any new dependency.

## Phase 10 History

| Phase | Checkpoint Result |
| --- | --- |
| 10A | Added `document-fixture` as the first non-sensor evidence-pack domain, with metadata-only count/status artifacts. |
| 10B | Cleaned real baseline drift first: unsafe artifact refs count as privacy violations, and deterministic CSI fixture refs/hashes were made portable. |
| 10C | Kept Fabric signed-pack tests clean in a basic environment by reporting optional verification as unavailable while preserving fail-closed behavior. |
| 10D | Surfaced document evidence refs, compatibility, counts, readiness, provider status, and workflow/report summaries. |
| 10E | Shared identical evidence helpers across CSI and document packs while preserving domain-specific pack shapes and fail-closed privacy checks. |
| 10F | Added the strict metadata-only document adapter boundary and pre-pack adapter-output validation. |
| 10G | Reclassified RuView as conditional reference-only and added a booth-first WiFi CSI planning boundary for future controlled single-subject work. |
| 10H | Added the shared real-mode readiness gate for document and WiFi CSI adapter status surfaces. |
| 10I | Added shared invariant tests across provider manifest, doctor, workflow reports, inspect output, and release-summary fixture surfaces. |
| 10J | Consolidates the checkpoint and next safe lanes without changing runtime behavior. |

## Current-State Matrix

| Surface | Current Mode | Public Artifact Or Status | Real-Mode State | Safety Boundary |
| --- | --- | --- | --- | --- |
| Generic sensor evidence | Fixture-only metadata framework | Provider registry, manifest, run-relative artifact refs, deterministic fingerprints | Not a live adapter | Sanitized counts/status/fingerprint data only; no runtime execution or private payload export. |
| WiFi CSI evidence | Fixture-backed metadata evidence pack | `csi_evidence_pack` and inspect/doctor/provider status | Blocked | No capture, monitor mode, packet capture, hardware access, model execution, network listener, or care claim. |
| Document evidence | Fixture-only metadata evidence pack | `document_evidence_pack` and inspect/workflow report status | Blocked | No raw document text, filenames, origin identifiers, absolute paths, URL export, provider body, or parser body. |
| Document adapter | Metadata-only adapter boundary | `metadata-document-adapter` status with capability labels and output validation | Blocked by shared gate | No ingestion, file crawling, PDF parsing, network access, raw body export, origin identifier export, or path export. |
| WiFi CSI source adapter | Metadata-only reference boundary | `metadata-wifi-csi-source-adapter` status, RuView posture, booth-first profile | Blocked by shared gate | Reference-only, offline, fixture-backed; no RuView execution, hardware control, packet capture, model use, or bridge integration. |
| Real-mode readiness gate | Shared descriptive gate | `real-mode-readiness-gate-v1` with missing gate count and disabled execution | Blocked by default | Consent, license review, privacy review, hardware review, model artifact review, dependency review, and network policy review are all required before future real-mode work can proceed. |

## Implemented Versus Blocked

Implemented:

- Metadata-only evidence packs for generic sensor, WiFi CSI, environment, toy,
  and document fixture surfaces.
- Sanitized artifacts with run-relative refs, SHA-256 hashes, compatibility
  status, readiness status, counts, and deterministic fingerprints.
- Provider registry, provider manifest, CLI inspect, CLI doctor, workflow
  report, and release-summary status surfaces.
- Document and WiFi CSI adapter readiness status with shared real-mode gate
  reporting.
- Invariant tests that keep document and CSI public surfaces metadata-only,
  fixture/reference-only, real-mode blocked, runtime disabled, and network
  disabled.

Intentionally blocked:

- Real document ingestion, file crawling, PDF parsing, raw document text
  exposure, external document parsing, and provider/parser body export.
- RuView execution, source adoption, model download, model execution,
  WiFi CSI hardware access, ESP32 flashing, packet capture, monitor mode, MQTT/UDP
  listeners, router/AP control, smart-home bridges, and live sensing.
- Medical inference, treatment guidance, emergency triage, continuous
  monitoring, production deployment claims, and any clinical validation claim.
- Any runtime path that bypasses the shared readiness gate or treats config
  alone as permission to run.

## Next Safe Lanes

Phase 11A should stay contract-spec-only:

- Write real-mode adapter contract specs without enabling real runtime.
- Plan future document ingestion interfaces without crawling files or parsing
  documents.
- Plan future RF booth hardware specs without probing devices, flashing radios,
  or capturing packets.
- Keep all future live work blocked until consent, license review, privacy
  review, hardware review, model artifact review, dependency review, and
  network policy review are explicitly satisfied and a later opt-in runtime is
  implemented.

## Verification Baseline

The current checkpoint is guarded by:

- `tests/test_sensor_evidence_release_summary.py`
- `tests/test_phase10i_shared_safety_invariants.py`
- `tests/test_sensor_evidence_provider_manifest.py`
- `tests/test_cli_commands.py`
- `tests/test_real_mode_readiness_gate.py`
- `tests/test_document_adapter_contract.py`
- `tests/test_document_evidence_pack.py`
- `tests/test_cross_domain_evidence_framework.py`
- `tests/test_wifi_csi_ruview_booth_boundary.py`
- `tests/test_wifi_csi_evidence_pack.py`
