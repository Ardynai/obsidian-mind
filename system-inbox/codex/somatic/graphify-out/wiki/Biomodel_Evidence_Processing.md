# Biomodel Evidence Processing

> 86 nodes · cohesion 0.06

## Key Concepts

- **BoltzProvider** (33 connections) — `somatic/providers/boltz.py`
- **BiomodelRequest** (27 connections) — `somatic/providers/biomodel.py`
- **BoltzProviderConfig** (18 connections) — `somatic/providers/boltz.py`
- **BiomodelSafetyGateTests** (15 connections) — `tests/test_biomodel_safety_gates.py`
- **BoltzProviderScaffoldTests** (15 connections) — `tests/test_boltz_provider_scaffold.py`
- **BiomodelResult** (14 connections) — `somatic/providers/biomodel.py`
- **BiomodelPlan** (12 connections) — `somatic/providers/biomodel.py`
- **.plan()** (12 connections) — `somatic/providers/boltz.py`
- **BoltzRuntimeNotEnabledError** (12 connections) — `somatic/providers/boltz.py`
- **BoltzConfigurationError** (11 connections) — `somatic/providers/boltz.py`
- **BoltzReadinessGateError** (11 connections) — `somatic/providers/boltz.py`
- **BiomodelConsentRecord** (11 connections) — `somatic/safety/biomodel.py`
- **evaluate_biomodel_readiness()** (11 connections) — `somatic/safety/biomodel.py`
- **biomodel_result_to_evidence_record()** (10 connections) — `somatic/providers/biomodel.py`
- **BiomodelEvidenceRecord** (10 connections) — `somatic/providers/biomodel.py`
- **.run()** (10 connections) — `somatic/providers/boltz.py`
- **BiomodelRuntimePolicy** (10 connections) — `somatic/safety/biomodel.py`
- **biomodel.py** (9 connections) — `somatic/providers/biomodel.py`
- **BoltzOptionalDependencyError** (9 connections) — `somatic/providers/boltz.py`
- **boltz.py** (9 connections) — `somatic/providers/boltz.py`
- **biomodel.py** (9 connections) — `somatic/safety/biomodel.py`
- **.test_dangerous_enabled_policy_fixture_still_never_executes()** (9 connections) — `tests/test_biomodel_safety_gates.py`
- **._raise_for_real_mode()** (8 connections) — `somatic/providers/boltz.py`
- **._readiness_report()** (8 connections) — `somatic/providers/boltz.py`
- **.test_real_mode_fails_clearly_when_dependency_is_unavailable_after_gates()** (7 connections) — `tests/test_boltz_provider_scaffold.py`
- *... and 61 more nodes in this community*

## Relationships

- [Workflow Evidence Analysis](Workflow_Evidence_Analysis.md) (9 shared connections)
- [Evidence Measurement Planning](Evidence_Measurement_Planning.md) (2 shared connections)
- [Literature Evidence Providers](Literature_Evidence_Providers.md) (2 shared connections)
- [Benchmarking and Scoring](Benchmarking_and_Scoring.md) (2 shared connections)
- [Phase 12 Closeout Summary](Phase_12_Closeout_Summary.md) (2 shared connections)
- [Sensor Hardware Ingestion](Sensor_Hardware_Ingestion.md) (1 shared connections)
- [Evidence Bus Sandbox](Evidence_Bus_Sandbox.md) (1 shared connections)
- [Adapter Readiness Evaluation](Adapter_Readiness_Evaluation.md) (1 shared connections)

## Source Files

- `somatic/providers/biomodel.py`
- `somatic/providers/boltz.py`
- `somatic/safety/biomodel.py`
- `tests/test_biomodel_provider_boundary.py`
- `tests/test_biomodel_safety_gates.py`
- `tests/test_boltz_provider_scaffold.py`

## Audit Trail

- EXTRACTED: 303 (64%)
- INFERRED: 171 (36%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*