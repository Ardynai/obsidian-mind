# Adapter Readiness Evaluation

> 30 nodes · cohesion 0.12

## Key Concepts

- **evaluate_real_mode_readiness()** (19 connections) — `somatic/safety/adapter_readiness.py`
- **real_mode_readiness_gate_summary()** (13 connections) — `somatic/safety/adapter_readiness.py`
- **RealModeReadinessGateTests** (12 connections) — `tests/test_real_mode_readiness_gate.py`
- **adapter_readiness.py** (11 connections) — `somatic/safety/adapter_readiness.py`
- **RealModeReadinessReviewRecord** (9 connections) — `somatic/safety/adapter_readiness.py`
- **._assert_gate_sanitized()** (6 connections) — `tests/test_real_mode_readiness_gate.py`
- **.test_document_and_csi_adapters_surface_shared_gate()** (5 connections) — `tests/test_real_mode_readiness_gate.py`
- **RealModeReadinessReport** (4 connections) — `somatic/safety/adapter_readiness.py`
- **.from_satisfied_gates()** (3 connections) — `somatic/safety/adapter_readiness.py`
- **_safe_gate_id()** (3 connections) — `somatic/safety/adapter_readiness.py`
- **_safe_gate_list()** (3 connections) — `somatic/safety/adapter_readiness.py`
- **_safe_public_label()** (3 connections) — `somatic/safety/adapter_readiness.py`
- **__init__.py** (3 connections) — `somatic/safety/__init__.py`
- **.test_all_required_gates_can_be_recorded_without_enabling_runtime()** (3 connections) — `tests/test_real_mode_readiness_gate.py`
- **.test_default_gate_blocks_fixture_or_reference_mode()** (3 connections) — `tests/test_real_mode_readiness_gate.py`
- **.test_each_missing_required_gate_fails_closed()** (3 connections) — `tests/test_real_mode_readiness_gate.py`
- **.test_mapping_review_record_requires_explicit_true_values()** (3 connections) — `tests/test_real_mode_readiness_gate.py`
- **.to_dict()** (2 connections) — `somatic/safety/adapter_readiness.py`
- **.from_mapping()** (2 connections) — `somatic/safety/adapter_readiness.py`
- **.satisfied_gate_ids()** (2 connections) — `somatic/safety/adapter_readiness.py`
- **_safe_int()** (2 connections) — `somatic/safety/adapter_readiness.py`
- **.test_review_record_dataclass_matches_required_gate_ids()** (2 connections) — `tests/test_real_mode_readiness_gate.py`
- **Shared real-mode readiness gates for future adapter runtimes.  The gate is des** (1 connections) — `somatic/safety/adapter_readiness.py`
- **Sanitized adapter real-mode readiness report.** (1 connections) — `somatic/safety/adapter_readiness.py`
- **Evaluate shared real-mode readiness without enabling a runtime.** (1 connections) — `somatic/safety/adapter_readiness.py`
- *... and 5 more nodes in this community*

## Relationships

- [Phase 11 Contract Review](Phase_11_Contract_Review.md) (7 shared connections)
- [Phase 11 Audit Status](Phase_11_Audit_Status.md) (4 shared connections)
- [Document Adapter Readiness](Document_Adapter_Readiness.md) (2 shared connections)
- [Benchmarking and Scoring](Benchmarking_and_Scoring.md) (2 shared connections)
- [Document Evidence Validation](Document_Evidence_Validation.md) (2 shared connections)
- [CSI Adapter Validation](CSI_Adapter_Validation.md) (1 shared connections)
- [Provider Manifest Validation](Provider_Manifest_Validation.md) (1 shared connections)
- [Workflow Evidence Analysis](Workflow_Evidence_Analysis.md) (1 shared connections)
- [Document Evidence Pack Construction](Document_Evidence_Pack_Construction.md) (1 shared connections)
- [Biomodel Evidence Processing](Biomodel_Evidence_Processing.md) (1 shared connections)

## Source Files

- `somatic/safety/__init__.py`
- `somatic/safety/adapter_readiness.py`
- `tests/test_real_mode_readiness_gate.py`

## Audit Trail

- EXTRACTED: 97 (78%)
- INFERRED: 27 (22%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*