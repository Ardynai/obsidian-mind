# Sensor Evidence Validation

> 17 nodes · cohesion 0.25

## Key Concepts

- **validate_sensor_evidence_workflow_config()** (20 connections) — `somatic/sensors/registry.py`
- **SensorEvidenceRegistryTests** (19 connections) — `tests/test_sensor_evidence_registry.py`
- **.test_private_scalar_fields_fail_closed_and_sanitize_from_workflow_artifact()** (5 connections) — `tests/test_sensor_evidence_registry.py`
- **.test_unsafe_refs_and_excessive_counts_fail_with_sanitized_errors()** (5 connections) — `tests/test_sensor_evidence_registry.py`
- **._assert_sanitized_validation_text()** (4 connections) — `tests/test_sensor_evidence_registry.py`
- **.test_live_device_network_and_credential_fields_fail_closed()** (4 connections) — `tests/test_sensor_evidence_registry.py`
- **.test_sanitizer_removes_csi_and_environment_fixture_refs()** (4 connections) — `tests/test_sensor_evidence_registry.py`
- **.test_valid_workflows_pass_sensor_evidence_config_validation()** (4 connections) — `tests/test_sensor_evidence_registry.py`
- **._toy_input()** (4 connections) — `tests/test_sensor_evidence_registry.py`
- **._csi_parser_input()** (3 connections) — `tests/test_sensor_evidence_registry.py`
- **._environment_input()** (3 connections) — `tests/test_sensor_evidence_registry.py`
- **.test_unknown_provider_fails_closed_without_echoing_identifier()** (3 connections) — `tests/test_sensor_evidence_registry.py`
- **.test_unsafe_toy_config_fails_closed_with_sanitized_errors()** (3 connections) — `tests/test_sensor_evidence_registry.py`
- **.test_unsupported_fixture_mode_fails_closed_without_echoing_value()** (3 connections) — `tests/test_sensor_evidence_registry.py`
- **._csi_group_input()** (2 connections) — `tests/test_sensor_evidence_registry.py`
- **._document_input()** (2 connections) — `tests/test_sensor_evidence_registry.py`
- **test_sensor_evidence_registry.py** (1 connections) — `tests/test_sensor_evidence_registry.py`

## Relationships

- [Sensor Evidence Provider Validation](Sensor_Evidence_Provider_Validation.md) (15 shared connections)
- [Workflow Contract Loading](Workflow_Contract_Loading.md) (4 shared connections)
- [Benchmarking and Scoring](Benchmarking_and_Scoring.md) (2 shared connections)

## Source Files

- `somatic/sensors/registry.py`
- `tests/test_sensor_evidence_registry.py`

## Audit Trail

- EXTRACTED: 70 (79%)
- INFERRED: 19 (21%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*