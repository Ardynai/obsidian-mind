# CSI Replay Evaluation

> 17 nodes · cohesion 0.25

## Key Concepts

- **evaluate_csi_replay_batch()** (20 connections) — `somatic/sensors/csi_batch.py`
- **WifiCsiBatchReplayTests** (13 connections) — `tests/test_wifi_csi_batch_replay.py`
- **._assert_batch_payload_is_sanitized()** (11 connections) — `tests/test_wifi_csi_batch_replay.py`
- **.test_batch_readiness_is_metadata_only_and_not_ranking_input()** (4 connections) — `tests/test_wifi_csi_batch_replay.py`
- **.test_multiple_fixture_groups_evaluate_deterministically()** (4 connections) — `tests/test_wifi_csi_batch_replay.py`
- **.test_unsafe_refs_and_invalid_utf8_fail_closed_with_redacted_metadata()** (4 connections) — `tests/test_wifi_csi_batch_replay.py`
- **._stable_json()** (3 connections) — `tests/test_wifi_csi_batch_replay.py`
- **.test_empty_batch_rejects_without_provider_group_output()** (3 connections) — `tests/test_wifi_csi_batch_replay.py`
- **.test_over_limit_group_refs_fail_closed_without_ref_export()** (3 connections) — `tests/test_wifi_csi_batch_replay.py`
- **.test_over_limit_groups_fail_closed_without_group_expansion()** (3 connections) — `tests/test_wifi_csi_batch_replay.py`
- **.test_valid_partial_and_rejected_groups_aggregate_fail_closed()** (3 connections) — `tests/test_wifi_csi_batch_replay.py`
- **_ref_limit_group_summary()** (2 connections) — `somatic/sensors/csi_batch.py`
- **._assert_no_absolute_paths()** (2 connections) — `tests/test_wifi_csi_batch_replay.py`
- **._assert_no_forbidden_batch_keys()** (2 connections) — `tests/test_wifi_csi_batch_replay.py`
- **._assert_no_forbidden_batch_words()** (2 connections) — `tests/test_wifi_csi_batch_replay.py`
- **Evaluate CSI fixture groups through sanitized provider replay metadata only.** (1 connections) — `somatic/sensors/csi_batch.py`
- **test_wifi_csi_batch_replay.py** (1 connections) — `tests/test_wifi_csi_batch_replay.py`

## Relationships

- [CSI Batch Readiness](CSI_Batch_Readiness.md) (7 shared connections)
- [CSI Evidence Pack Tests](CSI_Evidence_Pack_Tests.md) (2 shared connections)
- [Workflow Evidence Analysis](Workflow_Evidence_Analysis.md) (1 shared connections)
- [Sensor Evidence Provider Validation](Sensor_Evidence_Provider_Validation.md) (1 shared connections)
- [Sandbox Sensor Provider](Sandbox_Sensor_Provider.md) (1 shared connections)
- [CSI Evidence Pack Construction](CSI_Evidence_Pack_Construction.md) (1 shared connections)

## Source Files

- `somatic/sensors/csi_batch.py`
- `tests/test_wifi_csi_batch_replay.py`

## Audit Trail

- EXTRACTED: 62 (77%)
- INFERRED: 19 (23%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*