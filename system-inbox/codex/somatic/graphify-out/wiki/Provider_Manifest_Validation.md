# Provider Manifest Validation

> 26 nodes · cohesion 0.13

## Key Concepts

- **sensor_evidence_provider_manifest()** (23 connections) — `somatic/sensors/registry.py`
- **SensorEvidenceProviderManifestTests** (13 connections) — `tests/test_sensor_evidence_provider_manifest.py`
- **validate_sensor_evidence_provider_manifest()** (11 connections) — `somatic/sensors/registry.py`
- **classify_sensor_evidence_provider_manifest_compatibility()** (9 connections) — `somatic/sensors/registry.py`
- **SensorEvidenceProviderManifestCompatibilityResult** (7 connections) — `somatic/sensors/registry.py`
- **.test_manifest_compatibility_rejects_malformed_unsupported_and_incompatible()** (4 connections) — `tests/test_sensor_evidence_provider_manifest.py`
- **_real_mode_gate_entry_fields()** (3 connections) — `somatic/sensors/registry.py`
- **_sensor_evidence_provider_manifest_entry()** (3 connections) — `somatic/sensors/registry.py`
- **._assert_manifest_sanitized()** (3 connections) — `tests/test_sensor_evidence_provider_manifest.py`
- **.test_cli_provider_json_is_the_manifest_contract()** (3 connections) — `tests/test_sensor_evidence_provider_manifest.py`
- **.test_manifest_accepts_safe_additive_metadata()** (3 connections) — `tests/test_sensor_evidence_provider_manifest.py`
- **.test_manifest_matches_checked_in_snapshot_and_validates()** (3 connections) — `tests/test_sensor_evidence_provider_manifest.py`
- **.test_manifest_rejects_private_or_internal_metadata_without_echoing_values()** (3 connections) — `tests/test_sensor_evidence_provider_manifest.py`
- **.test_manifest_rejects_real_mode_readiness_gate_drift()** (3 connections) — `tests/test_sensor_evidence_provider_manifest.py`
- **_manifest_provider_count()** (2 connections) — `somatic/sensors/registry.py`
- **.to_dict()** (2 connections) — `somatic/sensors/registry.py`
- **.test_cli_provider_text_renders_manifest_order()** (2 connections) — `tests/test_sensor_evidence_provider_manifest.py`
- **.test_manifest_generation_does_not_change_tournament_outputs()** (2 connections) — `tests/test_sensor_evidence_provider_manifest.py`
- **.test_manifest_generation_is_deterministic()** (2 connections) — `tests/test_sensor_evidence_provider_manifest.py`
- **.test_manifest_required_field_set_is_stable()** (2 connections) — `tests/test_sensor_evidence_provider_manifest.py`
- **Sanitized compatibility result for provider registry manifests.** (1 connections) — `somatic/sensors/registry.py`
- **Return the public, deterministic provider registry manifest.** (1 connections) — `somatic/sensors/registry.py`
- **Validate a public provider manifest without echoing private values.** (1 connections) — `somatic/sensors/registry.py`
- **.compatible()** (1 connections) — `somatic/sensors/registry.py`
- **test_sensor_evidence_provider_manifest.py** (1 connections) — `tests/test_sensor_evidence_provider_manifest.py`
- *... and 1 more nodes in this community*

## Relationships

- [Sensor Evidence Provider Validation](Sensor_Evidence_Provider_Validation.md) (15 shared connections)
- [Benchmarking and Scoring](Benchmarking_and_Scoring.md) (4 shared connections)
- [Phase 12 Closeout Summary](Phase_12_Closeout_Summary.md) (2 shared connections)
- [Adapter Readiness Evaluation](Adapter_Readiness_Evaluation.md) (1 shared connections)
- [Safety Invariant Tests](Safety_Invariant_Tests.md) (1 shared connections)
- [Dossier Lifecycle Management](Dossier_Lifecycle_Management.md) (1 shared connections)
- [Dossier Lifecycle Fixtures](Dossier_Lifecycle_Fixtures.md) (1 shared connections)
- [Sensor Evidence Release Summary](Sensor_Evidence_Release_Summary.md) (1 shared connections)
- [CSI Booth Boundary Planning](CSI_Booth_Boundary_Planning.md) (1 shared connections)

## Source Files

- `somatic/sensors/registry.py`
- `tests/test_sensor_evidence_provider_manifest.py`

## Audit Trail

- EXTRACTED: 72 (66%)
- INFERRED: 37 (34%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*