# Document Evidence Validation

> 33 nodes · cohesion 0.12

## Key Concepts

- **DocumentFixtureEvidenceProvider** (28 connections) — `somatic/evidence/document_fixture.py`
- **DocumentEvidencePackTests** (24 connections) — `tests/test_document_evidence_pack.py`
- **document_evidence_pack_artifact_metadata()** (12 connections) — `somatic/evidence/document_evidence_pack.py`
- **validate_document_evidence_pack_v1()** (11 connections) — `somatic/evidence/document_evidence_pack.py`
- **._assert_doc_pack_sanitized()** (8 connections) — `tests/test_document_evidence_pack.py`
- **.test_document_evidence_pack_is_deterministic_and_compatible()** (6 connections) — `tests/test_document_evidence_pack.py`
- **classify_document_evidence_pack_compatibility()** (5 connections) — `somatic/evidence/document_evidence_pack.py`
- **.test_document_contract_rejects_malformed_unsupported_and_private()** (5 connections) — `tests/test_document_evidence_pack.py`
- **._mask_phase11l_safe_terms()** (4 connections) — `tests/test_document_evidence_pack.py`
- **.test_document_evidence_artifact_metadata_uses_run_relative_refs()** (4 connections) — `tests/test_document_evidence_pack.py`
- **.test_document_evidence_pack_fails_closed_on_missing_unsafe_refs()** (4 connections) — `tests/test_document_evidence_pack.py`
- **.test_document_evidence_pack_partial_status_without_ranking()** (4 connections) — `tests/test_document_evidence_pack.py`
- **._refresh()** (3 connections) — `tests/test_document_evidence_pack.py`
- **.test_document_artifact_metadata_sanitizes_phase11b_review_status()** (3 connections) — `tests/test_document_evidence_pack.py`
- **.test_document_artifact_metadata_sanitizes_phase11c_preflight_status()** (3 connections) — `tests/test_document_evidence_pack.py`
- **.test_document_artifact_metadata_sanitizes_phase11d_lifecycle_status()** (3 connections) — `tests/test_document_evidence_pack.py`
- **.test_document_artifact_metadata_sanitizes_phase11e_audit_index_status()** (3 connections) — `tests/test_document_evidence_pack.py`
- **.test_document_artifact_metadata_sanitizes_phase11f_audit_handoff_status()** (3 connections) — `tests/test_document_evidence_pack.py`
- **.test_document_evidence_pack_forbids_all_privacy_violations()** (3 connections) — `tests/test_document_evidence_pack.py`
- **.test_document_example_run_writes_generic_refs_without_ranking_changes()** (3 connections) — `tests/test_document_evidence_pack.py`
- **.status()** (2 connections) — `somatic/evidence/document_fixture.py`
- **._assert_no_absolute_paths()** (2 connections) — `tests/test_document_evidence_pack.py`
- **._assert_no_forbidden_doc_keys()** (2 connections) — `tests/test_document_evidence_pack.py`
- **._read_json()** (2 connections) — `tests/test_document_evidence_pack.py`
- **.test_document_provider_status_metadata_boundary()** (2 connections) — `tests/test_document_evidence_pack.py`
- *... and 8 more nodes in this community*

## Relationships

- [Document Evidence Pack Construction](Document_Evidence_Pack_Construction.md) (7 shared connections)
- [Cross-Domain Evidence Contracts](Cross-Domain_Evidence_Contracts.md) (4 shared connections)
- [Document Adapter Contract Validation](Document_Adapter_Contract_Validation.md) (4 shared connections)
- [Benchmarking and Scoring](Benchmarking_and_Scoring.md) (3 shared connections)
- [Workflow Evidence Analysis](Workflow_Evidence_Analysis.md) (2 shared connections)
- [Document Evidence Fixtures](Document_Evidence_Fixtures.md) (2 shared connections)
- [Adapter Readiness Evaluation](Adapter_Readiness_Evaluation.md) (2 shared connections)
- [Toy Counter Evidence Validation](Toy_Counter_Evidence_Validation.md) (2 shared connections)
- [Sensor Evidence Framework](Sensor_Evidence_Framework.md) (2 shared connections)
- [Phase 12 Closeout Summary](Phase_12_Closeout_Summary.md) (1 shared connections)
- [Phase 11 Audit Status](Phase_11_Audit_Status.md) (1 shared connections)

## Source Files

- `somatic/evidence/document_evidence_pack.py`
- `somatic/evidence/document_fixture.py`
- `tests/test_document_evidence_pack.py`

## Audit Trail

- EXTRACTED: 93 (59%)
- INFERRED: 65 (41%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*