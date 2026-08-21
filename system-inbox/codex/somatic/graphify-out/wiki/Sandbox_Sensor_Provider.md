# Sandbox Sensor Provider

> 21 nodes · cohesion 0.18

## Key Concepts

- **SandboxSensorProvider** (29 connections) — `somatic/sensors/sandbox.py`
- **SensorProviderScaffoldTests** (22 connections) — `tests/test_sensor_provider_scaffold.py`
- **._assert_csi_replay_payload_is_sanitized()** (10 connections) — `tests/test_sensor_provider_scaffold.py`
- **.plan_stream()** (4 connections) — `somatic/sensors/sandbox.py`
- **.privacy_policy()** (3 connections) — `somatic/sensors/sandbox.py`
- **.replay_csi_fixtures()** (3 connections) — `somatic/sensors/sandbox.py`
- **.test_csi_fixture_replay_provider_is_deterministic_and_sanitized()** (3 connections) — `tests/test_sensor_provider_scaffold.py`
- **.test_csi_fixture_replay_provider_keeps_mixed_fixture_partial()** (3 connections) — `tests/test_sensor_provider_scaffold.py`
- **.test_csi_fixture_replay_provider_rejects_unreadable_text_safely()** (3 connections) — `tests/test_sensor_provider_scaffold.py`
- **.test_csi_fixture_replay_provider_rejects_unsupported_fixtures_safely()** (3 connections) — `tests/test_sensor_provider_scaffold.py`
- **.test_csi_fixture_replay_provider_sanitizes_missing_fixture_errors()** (3 connections) — `tests/test_sensor_provider_scaffold.py`
- **.test_csi_fixture_replay_provider_sanitizes_unsafe_rejected_refs()** (3 connections) — `tests/test_sensor_provider_scaffold.py`
- **._csi_replay_provider_metadata()** (2 connections) — `somatic/sensors/sandbox.py`
- **._assert_no_absolute_paths()** (2 connections) — `tests/test_sensor_provider_scaffold.py`
- **._assert_no_forbidden_csi_replay_keys()** (2 connections) — `tests/test_sensor_provider_scaffold.py`
- **._assert_no_forbidden_csi_replay_words()** (2 connections) — `tests/test_sensor_provider_scaffold.py`
- **.test_sandbox_provider_observations_are_deterministic_and_fake_backed()** (2 connections) — `tests/test_sensor_provider_scaffold.py`
- **.status()** (1 connections) — `somatic/sensors/sandbox.py`
- **.test_sensor_fixtures_are_fake_backed_offline_and_local_only()** (1 connections) — `tests/test_sensor_provider_scaffold.py`
- **.test_sensor_provider_modules_import_without_optional_dependencies()** (1 connections) — `tests/test_sensor_provider_scaffold.py`
- **.test_sensor_scaffold_adds_no_network_or_hardware_import_surfaces()** (1 connections) — `tests/test_sensor_provider_scaffold.py`

## Relationships

- [Sensor Evidence Records](Sensor_Evidence_Records.md) (17 shared connections)
- [CSI Capture Planning](CSI_Capture_Planning.md) (4 shared connections)
- [CSI Booth Boundary Planning](CSI_Booth_Boundary_Planning.md) (2 shared connections)
- [Benchmarking and Scoring](Benchmarking_and_Scoring.md) (1 shared connections)
- [Phase 12 Closeout Summary](Phase_12_Closeout_Summary.md) (1 shared connections)
- [Workflow Evidence Analysis](Workflow_Evidence_Analysis.md) (1 shared connections)
- [Sensor Evidence Provider Validation](Sensor_Evidence_Provider_Validation.md) (1 shared connections)
- [CSI Replay Evaluation](CSI_Replay_Evaluation.md) (1 shared connections)
- [CSI Data Parsing](CSI_Data_Parsing.md) (1 shared connections)

## Source Files

- `somatic/sensors/sandbox.py`
- `tests/test_sensor_provider_scaffold.py`

## Audit Trail

- EXTRACTED: 89 (86%)
- INFERRED: 14 (14%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*