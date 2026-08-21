# Toy Counter Evidence Validation

> 39 nodes · cohesion 0.09

## Key Concepts

- **ToyCounterEvidencePackTests** (15 connections) — `tests/test_toy_counter_evidence_pack.py`
- **ToyCounterFixtureSensorProvider** (14 connections) — `somatic/sensors/toy_counter.py`
- **toy_counter.py** (13 connections) — `somatic/sensors/toy_counter.py`
- **evaluate_toy_counter_fixture_refs()** (9 connections) — `somatic/sensors/toy_counter.py`
- **._assert_toy_pack_sanitized()** (8 connections) — `tests/test_toy_counter_evidence_pack.py`
- **validate_toy_counter_evidence_pack_v1()** (7 connections) — `somatic/sensors/toy_counter_evidence_pack.py`
- **RunWriterTests** (7 connections) — `tests/test_run_writer.py`
- **classify_toy_counter_evidence_pack_compatibility()** (6 connections) — `somatic/sensors/toy_counter_evidence_pack.py`
- **compute_toy_counter_evidence_pack_fingerprint()** (6 connections) — `somatic/sensors/toy_counter_evidence_pack.py`
- **_read_fixture_rows()** (5 connections) — `somatic/sensors/toy_counter.py`
- **.test_toy_counter_contract_rejects_malformed_unsupported_and_private_payloads()** (5 connections) — `tests/test_toy_counter_evidence_pack.py`
- **.test_toy_counter_n_of_1_report_packet_and_fabric_plan_refs()** (5 connections) — `tests/test_toy_counter_evidence_pack.py`
- **.test_toy_counter_pack_is_deterministic_and_compatible()** (5 connections) — `tests/test_toy_counter_evidence_pack.py`
- **_increment()** (4 connections) — `somatic/sensors/toy_counter.py`
- **.test_manifest_sensor_evidence_refs_include_multiple_provider_packs()** (4 connections) — `tests/test_run_writer.py`
- **.test_toy_counter_fails_closed_for_missing_and_unsafe_refs()** (4 connections) — `tests/test_toy_counter_evidence_pack.py`
- **_quality_score()** (3 connections) — `somatic/sensors/toy_counter.py`
- **.evidence_pack()** (3 connections) — `somatic/sensors/toy_counter.py`
- **._refresh()** (3 connections) — `tests/test_toy_counter_evidence_pack.py`
- **.test_toy_counter_example_run_writes_generic_refs_without_ranking_changes()** (3 connections) — `tests/test_toy_counter_evidence_pack.py`
- **.test_toy_counter_mixed_fixture_is_partial_without_ranking_effect()** (3 connections) — `tests/test_toy_counter_evidence_pack.py`
- **_aggregate_status()** (2 connections) — `somatic/sensors/toy_counter.py`
- **_fixture_ref_tuple()** (2 connections) — `somatic/sensors/toy_counter.py`
- **_safe_fixture_name()** (2 connections) — `somatic/sensors/toy_counter.py`
- **._assert_no_absolute_paths()** (2 connections) — `tests/test_toy_counter_evidence_pack.py`
- *... and 14 more nodes in this community*

## Relationships

- [Sensor Evidence Provider Validation](Sensor_Evidence_Provider_Validation.md) (6 shared connections)
- [Sensor Evidence Framework](Sensor_Evidence_Framework.md) (6 shared connections)
- [Toy Counter Evidence Pack](Toy_Counter_Evidence_Pack.md) (5 shared connections)
- [Workflow Evidence Analysis](Workflow_Evidence_Analysis.md) (2 shared connections)
- [Document Evidence Validation](Document_Evidence_Validation.md) (2 shared connections)
- [Environment Evidence Provider](Environment_Evidence_Provider.md) (2 shared connections)
- [N-of-1 Report Planning](N-of-1_Report_Planning.md) (2 shared connections)

## Source Files

- `somatic/sensors/toy_counter.py`
- `somatic/sensors/toy_counter_evidence_pack.py`
- `tests/test_run_writer.py`
- `tests/test_toy_counter_evidence_pack.py`

## Audit Trail

- EXTRACTED: 120 (76%)
- INFERRED: 37 (24%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*