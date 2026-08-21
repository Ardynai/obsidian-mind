# Workflow Evidence Analysis

> 68 nodes · cohesion 0.06

## Key Concepts

- **mock_runtime.py** (83 connections) — `somatic/mock_runtime.py`
- **run_mock_workflow()** (33 connections) — `somatic/mock_runtime.py`
- **_run_n_of_1()** (24 connections) — `somatic/mock_runtime.py`
- **_n_of_1_summary()** (16 connections) — `somatic/mock_runtime.py`
- **_configured_fixture_evidence_pack_specs()** (13 connections) — `somatic/mock_runtime.py`
- **_run_in_silico_screening()** (13 connections) — `somatic/mock_runtime.py`
- **_run_robin_loop()** (10 connections) — `somatic/mock_runtime.py`
- **_sensor_evidence_artifact_refs_for_packs()** (6 connections) — `somatic/mock_runtime.py`
- **csi_evidence_pack_artifact_metadata()** (6 connections) — `somatic/sensors/csi_evidence_pack.py`
- **environment_evidence_pack_artifact_metadata()** (6 connections) — `somatic/sensors/environment_evidence_pack.py`
- **sensor_evidence_provider_by_artifact_name()** (6 connections) — `somatic/sensors/registry.py`
- **_artifact_payload_sha256()** (5 connections) — `somatic/mock_runtime.py`
- **falcon.py** (4 connections) — `somatic/agents/falcon.py`
- **finch.py** (4 connections) — `somatic/agents/finch.py`
- **_add_sensor_evidence_pack_artifacts()** (4 connections) — `somatic/mock_runtime.py`
- **_attach_configured_sensor_evidence_packs()** (4 connections) — `somatic/mock_runtime.py`
- **_configured_evidence_pack_spec()** (4 connections) — `somatic/mock_runtime.py`
- **_csi_sensor_evidence_artifact_refs()** (4 connections) — `somatic/mock_runtime.py`
- **_evaluate_workflow_csi_replay_batch()** (4 connections) — `somatic/mock_runtime.py`
- **_in_silico_biomodel_request()** (4 connections) — `somatic/mock_runtime.py`
- **analyze_raw_evidence()** (3 connections) — `somatic/agents/finch.py`
- **_assert_in_silico_workflow_gates()** (3 connections) — `somatic/mock_runtime.py`
- **_configured_evidence_pack_metadata()** (3 connections) — `somatic/mock_runtime.py`
- **_configured_evidence_pack_payload()** (3 connections) — `somatic/mock_runtime.py`
- **_configured_evidence_pack_readiness()** (3 connections) — `somatic/mock_runtime.py`
- *... and 43 more nodes in this community*

## Relationships

- [Sensor Evidence Provider Validation](Sensor_Evidence_Provider_Validation.md) (13 shared connections)
- [Biomodel Evidence Processing](Biomodel_Evidence_Processing.md) (9 shared connections)
- [Evidence Bus Sandbox](Evidence_Bus_Sandbox.md) (4 shared connections)
- [Environment Evidence Provider](Environment_Evidence_Provider.md) (4 shared connections)
- [N-of-1 Report Planning](N-of-1_Report_Planning.md) (4 shared connections)
- [Run Artifact Writer](Run_Artifact_Writer.md) (4 shared connections)
- [CSI Evidence Pack Construction](CSI_Evidence_Pack_Construction.md) (4 shared connections)
- [Evidence Measurement Planning](Evidence_Measurement_Planning.md) (3 shared connections)
- [Phase 11 Audit Status](Phase_11_Audit_Status.md) (3 shared connections)
- [CSI Capture Planning](CSI_Capture_Planning.md) (3 shared connections)
- [Biomodel Artifact Management](Biomodel_Artifact_Management.md) (3 shared connections)
- [Sensor Evidence Framework](Sensor_Evidence_Framework.md) (3 shared connections)

## Source Files

- `somatic/agents/crow.py`
- `somatic/agents/falcon.py`
- `somatic/agents/finch.py`
- `somatic/cli/main.py`
- `somatic/mock_runtime.py`
- `somatic/sensors/csi_evidence_pack.py`
- `somatic/sensors/environment_evidence_pack.py`
- `somatic/sensors/registry.py`

## Audit Trail

- EXTRACTED: 348 (97%)
- INFERRED: 10 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*