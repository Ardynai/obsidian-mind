# CSI Evidence Pack Validation

> 28 nodes · cohesion 0.21

## Key Concepts

- **WifiCsiEvidencePackCompatibilityTests** (24 connections) — `tests/test_wifi_csi_evidence_pack_compatibility.py`
- **validate_csi_evidence_pack_v1()** (20 connections) — `somatic/sensors/csi_evidence_pack.py`
- **._assert_payload_is_sanitized()** (17 connections) — `tests/test_wifi_csi_evidence_pack_compatibility.py`
- **._read_json()** (15 connections) — `tests/test_wifi_csi_evidence_pack_compatibility.py`
- **compute_csi_evidence_pack_fingerprint()** (9 connections) — `somatic/sensors/csi_evidence_pack.py`
- **._refresh_fingerprint()** (9 connections) — `tests/test_wifi_csi_evidence_pack_compatibility.py`
- **.test_generated_v1_pack_is_compatible_with_exporter_fingerprint()** (6 connections) — `tests/test_wifi_csi_evidence_pack_compatibility.py`
- **.test_additive_unknown_future_field_can_be_compatible_when_refingerprinted()** (5 connections) — `tests/test_wifi_csi_evidence_pack_compatibility.py`
- **.test_checked_in_v1_fixtures_are_compatible_and_fingerprint_stable()** (5 connections) — `tests/test_wifi_csi_evidence_pack_compatibility.py`
- **.test_exporter_identity_drift_is_incompatible()** (5 connections) — `tests/test_wifi_csi_evidence_pack_compatibility.py`
- **.test_forbidden_unknown_future_field_fails_closed_without_echoing_private_data()** (5 connections) — `tests/test_wifi_csi_evidence_pack_compatibility.py`
- **.test_generated_from_future_version_is_unsupported()** (5 connections) — `tests/test_wifi_csi_evidence_pack_compatibility.py`
- **.test_missing_exporter_boundary_flag_is_incompatible()** (5 connections) — `tests/test_wifi_csi_evidence_pack_compatibility.py`
- **.test_nested_unknown_numeric_payload_fails_closed_when_refingerprinted()** (5 connections) — `tests/test_wifi_csi_evidence_pack_compatibility.py`
- **.test_sanitized_field_change_changes_fingerprint_and_classifies_stale_pack()** (5 connections) — `tests/test_wifi_csi_evidence_pack_compatibility.py`
- **.test_wrong_required_shapes_are_incompatible()** (5 connections) — `tests/test_wifi_csi_evidence_pack_compatibility.py`
- **.test_additive_unknown_future_field_with_stale_fingerprint_is_incompatible()** (4 connections) — `tests/test_wifi_csi_evidence_pack_compatibility.py`
- **.test_missing_required_field_is_malformed_and_fail_closed()** (4 connections) — `tests/test_wifi_csi_evidence_pack_compatibility.py`
- **.test_unsupported_future_version_is_classified_without_breaking_v1_reader()** (4 connections) — `tests/test_wifi_csi_evidence_pack_compatibility.py`
- **.test_identical_sanitized_inputs_keep_same_fingerprint()** (3 connections) — `tests/test_wifi_csi_evidence_pack_compatibility.py`
- **._assert_no_absolute_paths()** (2 connections) — `tests/test_wifi_csi_evidence_pack_compatibility.py`
- **._assert_no_forbidden_keys()** (2 connections) — `tests/test_wifi_csi_evidence_pack_compatibility.py`
- **._assert_no_forbidden_words()** (2 connections) — `tests/test_wifi_csi_evidence_pack_compatibility.py`
- **.test_non_object_payload_is_malformed()** (2 connections) — `tests/test_wifi_csi_evidence_pack_compatibility.py`
- **Compute the v1 fingerprint over a persisted CSI evidence pack payload.** (1 connections) — `somatic/sensors/csi_evidence_pack.py`
- *... and 3 more nodes in this community*

## Relationships

- [CSI Evidence Pack Construction](CSI_Evidence_Pack_Construction.md) (5 shared connections)
- [CSI Compatibility Classification](CSI_Compatibility_Classification.md) (3 shared connections)
- [Sensor Evidence Provider Validation](Sensor_Evidence_Provider_Validation.md) (2 shared connections)
- [Benchmarking and Scoring](Benchmarking_and_Scoring.md) (2 shared connections)
- [CSI Evidence Pack Tests](CSI_Evidence_Pack_Tests.md) (1 shared connections)
- [CSI Data Parsing](CSI_Data_Parsing.md) (1 shared connections)

## Source Files

- `somatic/sensors/csi_evidence_pack.py`
- `tests/test_wifi_csi_evidence_pack_compatibility.py`

## Audit Trail

- EXTRACTED: 132 (77%)
- INFERRED: 40 (23%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*