# CSI Booth Boundary Planning

> 23 nodes · cohesion 0.13

## Key Concepts

- **WifiCsiRuViewBoothBoundaryTests** (15 connections) — `tests/test_wifi_csi_ruview_booth_boundary.py`
- **fixture_csi_source_adapter_output()** (9 connections) — `somatic/sensors/csi_adapter.py`
- **booth_first_csi_planning_profile()** (6 connections) — `somatic/sensors/csi_adapter.py`
- **build_csi_reference_inventory()** (6 connections) — `somatic/sensors/csi.py`
- **._private_surface_forbidden_terms()** (5 connections) — `tests/test_wifi_csi_ruview_booth_boundary.py`
- **.test_direct_csi_metadata_helpers_revalidate_tainted_adapter_surfaces()** (5 connections) — `tests/test_wifi_csi_ruview_booth_boundary.py`
- **._tainted_csi_metadata()** (4 connections) — `tests/test_wifi_csi_ruview_booth_boundary.py`
- **.test_csi_source_adapter_output_validates_before_planning_metadata()** (4 connections) — `tests/test_wifi_csi_ruview_booth_boundary.py`
- **.test_sandbox_evidence_record_revalidates_tainted_csi_metadata()** (4 connections) — `tests/test_wifi_csi_ruview_booth_boundary.py`
- **.test_unsafe_adapter_outputs_fail_closed_without_echoing_private_values()** (4 connections) — `tests/test_wifi_csi_ruview_booth_boundary.py`
- **ruview_reference_metadata()** (3 connections) — `somatic/sensors/csi_adapter.py`
- **.test_adapter_rejects_altered_reference_claim_labels()** (3 connections) — `tests/test_wifi_csi_ruview_booth_boundary.py`
- **.test_booth_first_profile_is_future_metadata_only()** (3 connections) — `tests/test_wifi_csi_ruview_booth_boundary.py`
- **.test_run_summary_and_report_surface_sanitized_ruview_and_booth_metadata()** (3 connections) — `tests/test_wifi_csi_ruview_booth_boundary.py`
- **_load_csi_reference_inventory_fixture()** (2 connections) — `somatic/sensors/csi.py`
- **._read_json()** (2 connections) — `tests/test_wifi_csi_ruview_booth_boundary.py`
- **.test_csi_source_adapter_status_is_closed_and_fixture_backed()** (2 connections) — `tests/test_wifi_csi_ruview_booth_boundary.py`
- **.test_provider_manifest_surfaces_only_sanitized_csi_adapter_labels()** (2 connections) — `tests/test_wifi_csi_ruview_booth_boundary.py`
- **.test_ruview_reassessment_is_conditional_reference_only()** (2 connections) — `tests/test_wifi_csi_ruview_booth_boundary.py`
- **Return sanitized RuView reassessment metadata.** (1 connections) — `somatic/sensors/csi_adapter.py`
- **Return a future booth-first CSI architecture profile as metadata only.** (1 connections) — `somatic/sensors/csi_adapter.py`
- **Return deterministic CSI source metadata for the current fixture boundary.** (1 connections) — `somatic/sensors/csi_adapter.py`
- **test_wifi_csi_ruview_booth_boundary.py** (1 connections) — `tests/test_wifi_csi_ruview_booth_boundary.py`

## Relationships

- [CSI Capture Planning](CSI_Capture_Planning.md) (7 shared connections)
- [CSI Adapter Validation](CSI_Adapter_Validation.md) (6 shared connections)
- [CSI Scaffold Validation](CSI_Scaffold_Validation.md) (2 shared connections)
- [Sandbox Sensor Provider](Sandbox_Sensor_Provider.md) (2 shared connections)
- [Benchmarking and Scoring](Benchmarking_and_Scoring.md) (1 shared connections)
- [Phase 12 Closeout Summary](Phase_12_Closeout_Summary.md) (1 shared connections)
- [Sensor Evidence Provider Validation](Sensor_Evidence_Provider_Validation.md) (1 shared connections)
- [Phase 11 Audit Status](Phase_11_Audit_Status.md) (1 shared connections)
- [Provider Manifest Validation](Provider_Manifest_Validation.md) (1 shared connections)

## Source Files

- `somatic/sensors/csi.py`
- `somatic/sensors/csi_adapter.py`
- `tests/test_wifi_csi_ruview_booth_boundary.py`

## Audit Trail

- EXTRACTED: 63 (72%)
- INFERRED: 25 (28%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*