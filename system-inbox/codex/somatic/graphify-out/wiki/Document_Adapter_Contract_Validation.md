# Document Adapter Contract Validation

> 12 nodes · cohesion 0.35

## Key Concepts

- **validate_document_adapter_output()** (12 connections) — `somatic/evidence/document_adapter.py`
- **DocumentAdapterContractTests** (10 connections) — `tests/test_document_adapter_contract.py`
- **._assert_no_adapter_leak()** (7 connections) — `tests/test_document_adapter_contract.py`
- **.test_unsafe_adapter_output_is_rejected_before_pack_build()** (6 connections) — `tests/test_document_adapter_contract.py`
- **.test_provider_preserves_first_adapter_validation_result()** (5 connections) — `tests/test_document_adapter_contract.py`
- **.test_fixture_evaluation_validates_before_pack_build()** (4 connections) — `tests/test_document_adapter_contract.py`
- **.test_unknown_safe_adapter_fields_still_fail_closed()** (4 connections) — `tests/test_document_adapter_contract.py`
- **._valid_adapter_output()** (4 connections) — `tests/test_document_adapter_contract.py`
- **.test_fixture_adapter_status_is_metadata_only()** (3 connections) — `tests/test_document_adapter_contract.py`
- **.test_malformed_adapter_output_fails_closed_without_echo()** (3 connections) — `tests/test_document_adapter_contract.py`
- **Validate and sanitize metadata-only document adapter output.** (1 connections) — `somatic/evidence/document_adapter.py`
- **test_document_adapter_contract.py** (1 connections) — `tests/test_document_adapter_contract.py`

## Relationships

- [Document Adapter Readiness](Document_Adapter_Readiness.md) (5 shared connections)
- [Document Evidence Validation](Document_Evidence_Validation.md) (4 shared connections)
- [Document Evidence Pack Construction](Document_Evidence_Pack_Construction.md) (3 shared connections)
- [Phase 11 Audit Status](Phase_11_Audit_Status.md) (1 shared connections)
- [Document Evidence Fixtures](Document_Evidence_Fixtures.md) (1 shared connections)

## Source Files

- `somatic/evidence/document_adapter.py`
- `tests/test_document_adapter_contract.py`

## Audit Trail

- EXTRACTED: 44 (73%)
- INFERRED: 16 (27%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*