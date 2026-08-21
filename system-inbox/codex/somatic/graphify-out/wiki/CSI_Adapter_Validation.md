# CSI Adapter Validation

> 25 nodes · cohesion 0.13

## Key Concepts

- **csi_adapter.py** (22 connections) — `somatic/sensors/csi_adapter.py`
- **validate_csi_source_adapter_output()** (13 connections) — `somatic/sensors/csi_adapter.py`
- **CsiSourceAdapterOutputValidationResult** (8 connections) — `somatic/sensors/csi_adapter.py`
- **wifi_csi_real_mode_readiness_gate()** (6 connections) — `somatic/sensors/csi_adapter.py`
- **sanitize_csi_source_adapter_output()** (5 connections) — `somatic/sensors/csi_adapter.py`
- **_adapter_privacy_violation_count()** (4 connections) — `somatic/sensors/csi_adapter.py`
- **_invalid_result()** (4 connections) — `somatic/sensors/csi_adapter.py`
- **rejected_csi_source_adapter_output()** (3 connections) — `somatic/sensors/csi_adapter.py`
- **_ruview_reference_contract_errors()** (3 connections) — `somatic/sensors/csi_adapter.py`
- **_adapter_string_privacy_violation_count()** (2 connections) — `somatic/sensors/csi_adapter.py`
- **_booth_profile_contract_errors()** (2 connections) — `somatic/sensors/csi_adapter.py`
- **.to_dict()** (2 connections) — `somatic/sensors/csi_adapter.py`
- **_safe_adapter_category()** (2 connections) — `somatic/sensors/csi_adapter.py`
- **_sanitize_booth_profile()** (2 connections) — `somatic/sensors/csi_adapter.py`
- **_sanitize_ruview_reference()** (2 connections) — `somatic/sensors/csi_adapter.py`
- **_status_label()** (2 connections) — `somatic/sensors/csi_adapter.py`
- **_unsafe_adapter_key()** (2 connections) — `somatic/sensors/csi_adapter.py`
- **.compatible()** (1 connections) — `somatic/sensors/csi_adapter.py`
- **.error_count()** (1 connections) — `somatic/sensors/csi_adapter.py`
- **.status()** (1 connections) — `somatic/sensors/csi_adapter.py`
- **Metadata-only WiFi CSI source adapter boundary.  The boundary is for future CS** (1 connections) — `somatic/sensors/csi_adapter.py`
- **Sanitized fail-closed validation result for CSI source metadata.** (1 connections) — `somatic/sensors/csi_adapter.py`
- **Return the shared real-mode gate for the WiFi CSI source boundary.** (1 connections) — `somatic/sensors/csi_adapter.py`
- **Validate and sanitize metadata-only CSI source adapter output.** (1 connections) — `somatic/sensors/csi_adapter.py`
- **Return safe CSI source metadata, rejecting unsafe output fail-closed.** (1 connections) — `somatic/sensors/csi_adapter.py`

## Relationships

- [CSI Booth Boundary Planning](CSI_Booth_Boundary_Planning.md) (6 shared connections)
- [CSI Capture Planning](CSI_Capture_Planning.md) (2 shared connections)
- [Phase 11 Audit Status](Phase_11_Audit_Status.md) (2 shared connections)
- [Sensor Evidence Provider Validation](Sensor_Evidence_Provider_Validation.md) (1 shared connections)
- [CSI Scaffold Validation](CSI_Scaffold_Validation.md) (1 shared connections)
- [Adapter Readiness Evaluation](Adapter_Readiness_Evaluation.md) (1 shared connections)
- [Document Adapter Readiness](Document_Adapter_Readiness.md) (1 shared connections)

## Source Files

- `somatic/sensors/csi_adapter.py`

## Audit Trail

- EXTRACTED: 86 (93%)
- INFERRED: 6 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*