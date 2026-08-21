# Workflow Integration Tests

> 25 nodes · cohesion 0.13

## Key Concepts

- **NOf1WorkflowTests** (17 connections) — `tests/test_n_of_1_workflow.py`
- **InSilicoWorkflowTests** (8 connections) — `tests/test_in_silico_workflow.py`
- **.test_n_of_1_workflow_writes_sensor_artifacts_and_report_boundaries()** (8 connections) — `tests/test_n_of_1_workflow.py`
- **._read_json()** (4 connections) — `tests/test_n_of_1_workflow.py`
- **._read_json()** (3 connections) — `tests/test_in_silico_workflow.py`
- **._sha256()** (3 connections) — `tests/test_in_silico_workflow.py`
- **.test_in_silico_biomodel_artifacts_are_deterministic_across_runs()** (3 connections) — `tests/test_in_silico_workflow.py`
- **.test_in_silico_workflow_writes_biomodel_artifacts_and_report_boundaries()** (3 connections) — `tests/test_in_silico_workflow.py`
- **._assert_no_forbidden_csi_artifact_words()** (3 connections) — `tests/test_n_of_1_workflow.py`
- **._assert_no_forbidden_csi_text()** (3 connections) — `tests/test_n_of_1_workflow.py`
- **._sha256()** (3 connections) — `tests/test_n_of_1_workflow.py`
- **.test_n_of_1_artifacts_are_deterministic_across_runs()** (3 connections) — `tests/test_n_of_1_workflow.py`
- **._assert_no_absolute_paths()** (2 connections) — `tests/test_n_of_1_workflow.py`
- **._assert_no_forbidden_csi_artifact_keys()** (2 connections) — `tests/test_n_of_1_workflow.py`
- **._assert_no_report_or_fabric_plan_leaks()** (2 connections) — `tests/test_n_of_1_workflow.py`
- **.test_existing_workflows_and_fabric_check_still_pass()** (2 connections) — `tests/test_n_of_1_workflow.py`
- **.test_existing_workflows_and_fabric_check_still_pass()** (1 connections) — `tests/test_in_silico_workflow.py`
- **.test_scaffold_imports_and_runtime_add_no_network_or_download_surfaces()** (1 connections) — `tests/test_in_silico_workflow.py`
- **test_in_silico_workflow.py** (1 connections) — `tests/test_in_silico_workflow.py`
- **.test_n_of_1_csi_parser_artifacts_are_stage_declared()** (1 connections) — `tests/test_n_of_1_workflow.py`
- **.test_n_of_1_runtime_adds_no_network_or_hardware_import_surfaces()** (1 connections) — `tests/test_n_of_1_workflow.py`
- **.test_phase7a_docs_and_fixtures_contain_required_boundary_language()** (1 connections) — `tests/test_n_of_1_workflow.py`
- **.test_rejects_n_of_1_workflow_missing_required_sandbox_constraints()** (1 connections) — `tests/test_n_of_1_workflow.py`
- **.test_rejects_n_of_1_workflow_with_live_capture_enabled()** (1 connections) — `tests/test_n_of_1_workflow.py`
- **test_n_of_1_workflow.py** (1 connections) — `tests/test_n_of_1_workflow.py`

## Relationships

- [Workflow Contract Loading](Workflow_Contract_Loading.md) (2 shared connections)

## Source Files

- `tests/test_in_silico_workflow.py`
- `tests/test_n_of_1_workflow.py`

## Audit Trail

- EXTRACTED: 78 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*