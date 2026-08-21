# Workflow Contract Loading

> 24 nodes · cohesion 0.14

## Key Concepts

- **workflow_loader.py** (14 connections) — `somatic/workflow_loader.py`
- **WorkflowValidationError** (11 connections) — `somatic/workflow_loader.py`
- **parse_simple_yaml()** (7 connections) — `somatic/workflow_loader.py`
- **load_mock_provider_metadata()** (5 connections) — `somatic/workflow_loader.py`
- **_parse_dict()** (5 connections) — `somatic/workflow_loader.py`
- **_parse_list()** (5 connections) — `somatic/workflow_loader.py`
- **WorkflowLoaderTests** (5 connections) — `tests/test_workflow_loader.py`
- **load_workflow()** (4 connections) — `somatic/workflow_loader.py`
- **_parse_block()** (4 connections) — `somatic/workflow_loader.py`
- **_split_key_value()** (4 connections) — `somatic/workflow_loader.py`
- **validate_workflow()** (4 connections) — `somatic/workflow_loader.py`
- **_parse_scalar()** (3 connections) — `somatic/workflow_loader.py`
- **_launch()** (3 connections) — `somatic/cli/main.py`
- **_looks_like_key_value()** (2 connections) — `somatic/workflow_loader.py`
- **.test_fixture_loads_with_boltz_fake_backed_provider_metadata()** (2 connections) — `tests/test_in_silico_workflow.py`
- **.test_fixture_loads_with_fake_backed_sensor_provider_metadata()** (2 connections) — `tests/test_n_of_1_workflow.py`
- **.test_workflow_loader_rejects_invalid_sensor_provider_config()** (2 connections) — `tests/test_sensor_evidence_registry.py`
- **.test_workflow_loader_rejects_unsupported_mode_without_echoing_value()** (2 connections) — `tests/test_sensor_evidence_registry.py`
- **.test_loads_mock_provider_metadata_for_referenced_classes()** (2 connections) — `tests/test_workflow_loader.py`
- **.test_rejects_workflow_missing_mode()** (2 connections) — `tests/test_workflow_loader.py`
- **contracts.py** (1 connections) — `somatic/contracts.py`
- **Raised when a workflow fixture does not match the Phase 1A contract.** (1 connections) — `somatic/workflow_loader.py`
- **test_workflow_loader.py** (1 connections) — `tests/test_workflow_loader.py`
- **.test_loads_valid_literature_workflow_with_required_fields()** (1 connections) — `tests/test_workflow_loader.py`

## Relationships

- [Benchmarking and Scoring](Benchmarking_and_Scoring.md) (4 shared connections)
- [Sensor Evidence Validation](Sensor_Evidence_Validation.md) (4 shared connections)
- [Workflow Evidence Analysis](Workflow_Evidence_Analysis.md) (3 shared connections)
- [Workflow Integration Tests](Workflow_Integration_Tests.md) (2 shared connections)
- [Sensor Evidence Provider Validation](Sensor_Evidence_Provider_Validation.md) (1 shared connections)

## Source Files

- `somatic/cli/main.py`
- `somatic/contracts.py`
- `somatic/workflow_loader.py`
- `tests/test_in_silico_workflow.py`
- `tests/test_n_of_1_workflow.py`
- `tests/test_sensor_evidence_registry.py`
- `tests/test_workflow_loader.py`

## Audit Trail

- EXTRACTED: 77 (84%)
- INFERRED: 15 (16%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*