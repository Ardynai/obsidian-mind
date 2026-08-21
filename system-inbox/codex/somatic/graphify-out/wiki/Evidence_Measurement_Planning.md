# Evidence Measurement Planning

> 78 nodes · cohesion 0.04

## Key Concepts

- **HypothesisSpec** (24 connections) — `somatic/evidence_bus/adapter.py`
- **run_evidence_loop()** (23 connections) — `somatic/evidence_bus/loop.py`
- **EvidenceSource** (22 connections) — `somatic/evidence_bus/records.py`
- **MeasurementPlan** (21 connections) — `somatic/evidence_bus/records.py`
- **fusion.py** (15 connections) — `somatic/sensors/fusion.py`
- **fuse_rf_vision()** (15 connections) — `somatic/sensors/fusion.py`
- **SandboxModalityAdapter** (12 connections) — `somatic/evidence_bus/sandbox_adapters.py`
- **EvidenceAdapter** (11 connections) — `somatic/evidence_bus/adapter.py`
- **sandbox_adapters.py** (11 connections) — `somatic/evidence_bus/sandbox_adapters.py`
- **EvidenceCost** (10 connections) — `somatic/evidence_bus/adapter.py`
- **StructuredVerdict** (10 connections) — `somatic/evidence_bus/records.py`
- **fuse_csi_units()** (10 connections) — `somatic/sensors/fusion.py`
- **EvidenceBusLoopTests** (9 connections) — `tests/test_evidence_bus_loop.py`
- **_features_for()** (8 connections) — `somatic/evidence_bus/sandbox_adapters.py`
- **pose_model_status()** (8 connections) — `somatic/sensors/pose_model.py`
- **sandbox_adapters()** (7 connections) — `somatic/evidence_bus/sandbox_adapters.py`
- **propose_next_measurement()** (7 connections) — `somatic/science/falsifier.py`
- **records.py** (6 connections) — `somatic/evidence_bus/records.py`
- **infer_pose()** (6 connections) — `somatic/sensors/pose_model.py`
- **.test_pose_model_stays_off()** (6 connections) — `tests/test_live_csi.py`
- **.plan()** (6 connections) — `somatic/sensors/live_video.py`
- **adapter.py** (5 connections) — `somatic/evidence_bus/adapter.py`
- **.test_dataclasses_are_lightweight_contracts()** (5 connections) — `tests/test_evidence_bus.py`
- **.test_requires_analysis_insight()** (5 connections) — `tests/test_evidence_bus_loop.py`
- **test_evidence_bus_loop.py** (5 connections) — `tests/test_evidence_bus_loop.py`
- *... and 53 more nodes in this community*

## Relationships

- [Sensor Hardware Ingestion](Sensor_Hardware_Ingestion.md) (38 shared connections)
- [Consent Ledger Management](Consent_Ledger_Management.md) (21 shared connections)
- [Consent and Experiment Storage](Consent_and_Experiment_Storage.md) (15 shared connections)
- [Live CSI Adapter](Live_CSI_Adapter.md) (12 shared connections)
- [Presence and Research Rendering](Presence_and_Research_Rendering.md) (11 shared connections)
- [Evidence Bus Sandbox](Evidence_Bus_Sandbox.md) (7 shared connections)
- [Benchmarking and Scoring](Benchmarking_and_Scoring.md) (5 shared connections)
- [Workflow Evidence Analysis](Workflow_Evidence_Analysis.md) (3 shared connections)
- [Biomodel Evidence Processing](Biomodel_Evidence_Processing.md) (2 shared connections)
- [Sensor Evidence Records](Sensor_Evidence_Records.md) (2 shared connections)
- [Belief Ledger Posteriors](Belief_Ledger_Posteriors.md) (1 shared connections)
- [Biosecurity Screening Harness](Biosecurity_Screening_Harness.md) (1 shared connections)

## Source Files

- `somatic/agents/falcon.py`
- `somatic/evidence_bus/__init__.py`
- `somatic/evidence_bus/adapter.py`
- `somatic/evidence_bus/loop.py`
- `somatic/evidence_bus/records.py`
- `somatic/evidence_bus/sandbox_adapters.py`
- `somatic/science/falsifier.py`
- `somatic/sensors/fusion.py`
- `somatic/sensors/live_video.py`
- `somatic/sensors/pose_model.py`
- `tests/test_evidence_bus.py`
- `tests/test_evidence_bus_loop.py`
- `tests/test_live_csi.py`
- `tests/test_sandbox_source.py`
- `tests/test_video_pose.py`

## Audit Trail

- EXTRACTED: 269 (73%)
- INFERRED: 97 (27%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*