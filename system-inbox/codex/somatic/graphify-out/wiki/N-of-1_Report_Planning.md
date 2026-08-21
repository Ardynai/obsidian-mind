# N-of-1 Report Planning

> 51 nodes · cohesion 0.08

## Key Concepts

- **n_of_1_packet.py** (16 connections) — `somatic/reports/n_of_1_packet.py`
- **build_n_of_1_fabric_pack_plan()** (13 connections) — `somatic/reports/n_of_1_fabric_plan.py`
- **n_of_1_fabric_plan.py** (13 connections) — `somatic/reports/n_of_1_fabric_plan.py`
- **build_n_of_1_report_packet()** (12 connections) — `somatic/reports/n_of_1_packet.py`
- **NOf1FabricPackPlanTests** (10 connections) — `tests/test_n_of_1_fabric_pack_plan.py`
- **NOf1ReportPacketTests** (8 connections) — `tests/test_n_of_1_report_packet.py`
- **collect_n_of_1_artifact_refs()** (7 connections) — `somatic/reports/n_of_1_packet.py`
- **collect_n_of_1_sensor_evidence_artifact_refs()** (7 connections) — `somatic/reports/n_of_1_packet.py`
- **collect_n_of_1_optional_artifact_refs()** (6 connections) — `somatic/reports/n_of_1_packet.py`
- **_file_plans()** (5 connections) — `somatic/reports/n_of_1_fabric_plan.py`
- **_sensor_evidence_artifact_refs()** (5 connections) — `somatic/reports/n_of_1_fabric_plan.py`
- **.test_build_plan_references_packet_and_reuses_artifact_hashes()** (5 connections) — `tests/test_n_of_1_fabric_pack_plan.py`
- **.to_dict()** (4 connections) — `somatic/reports/n_of_1_fabric_plan.py`
- **artifact_payload_sha256()** (4 connections) — `somatic/reports/n_of_1_packet.py`
- **NOf1ArtifactRef** (4 connections) — `somatic/reports/n_of_1_packet.py`
- **.to_dict()** (4 connections) — `somatic/reports/n_of_1_packet.py`
- **._minimal_report_packet()** (4 connections) — `tests/test_n_of_1_fabric_pack_plan.py`
- **.test_build_plan_fails_closed_for_unsafe_packet_artifact_refs()** (4 connections) — `tests/test_n_of_1_fabric_pack_plan.py`
- **__init__.py** (3 connections) — `somatic/reports/__init__.py`
- **_artifact_ref_names()** (3 connections) — `somatic/reports/n_of_1_fabric_plan.py`
- **_json_ready()** (3 connections) — `somatic/reports/n_of_1_fabric_plan.py`
- **NOf1FabricFilePlan** (3 connections) — `somatic/reports/n_of_1_fabric_plan.py`
- **NOf1FabricPackPlan** (3 connections) — `somatic/reports/n_of_1_fabric_plan.py`
- **_ordered_artifact_hashes()** (3 connections) — `somatic/reports/n_of_1_fabric_plan.py`
- **_json_ready()** (3 connections) — `somatic/reports/n_of_1_packet.py`
- *... and 26 more nodes in this community*

## Relationships

- [Workflow Evidence Analysis](Workflow_Evidence_Analysis.md) (4 shared connections)
- [Sensor Evidence Framework](Sensor_Evidence_Framework.md) (4 shared connections)
- [Toy Counter Evidence Validation](Toy_Counter_Evidence_Validation.md) (2 shared connections)
- [Sensor Evidence Provider Validation](Sensor_Evidence_Provider_Validation.md) (1 shared connections)

## Source Files

- `somatic/reports/__init__.py`
- `somatic/reports/n_of_1_fabric_plan.py`
- `somatic/reports/n_of_1_packet.py`
- `tests/test_n_of_1_fabric_pack_plan.py`
- `tests/test_n_of_1_report_packet.py`

## Audit Trail

- EXTRACTED: 184 (90%)
- INFERRED: 21 (10%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*