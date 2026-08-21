# Document Adapter Readiness

> 20 nodes · cohesion 0.13

## Key Concepts

- **document_adapter.py** (13 connections) — `somatic/evidence/document_adapter.py`
- **DocumentAdapterOutputValidationResult** (10 connections) — `somatic/evidence/document_adapter.py`
- **document_adapter_real_mode_readiness_gate()** (6 connections) — `somatic/evidence/document_adapter.py`
- **_adapter_privacy_violation_count()** (4 connections) — `somatic/evidence/document_adapter.py`
- **_invalid_result()** (4 connections) — `somatic/evidence/document_adapter.py`
- **sanitize_document_adapter_output()** (4 connections) — `somatic/evidence/document_adapter.py`
- **rejected_document_adapter_output()** (3 connections) — `somatic/evidence/document_adapter.py`
- **.test_adapter_specific_gate_helpers_keep_modes_distinct()** (3 connections) — `tests/test_real_mode_readiness_gate.py`
- **_adapter_string_privacy_violation_count()** (2 connections) — `somatic/evidence/document_adapter.py`
- **.to_dict()** (2 connections) — `somatic/evidence/document_adapter.py`
- **_unsafe_adapter_key()** (2 connections) — `somatic/evidence/document_adapter.py`
- **.compatible()** (1 connections) — `somatic/evidence/document_adapter.py`
- **.error_count()** (1 connections) — `somatic/evidence/document_adapter.py`
- **.readiness_status()** (1 connections) — `somatic/evidence/document_adapter.py`
- **.status()** (1 connections) — `somatic/evidence/document_adapter.py`
- **Metadata-only document adapter boundary.  The adapter contract is intentionall** (1 connections) — `somatic/evidence/document_adapter.py`
- **Sanitized fail-closed validation result for adapter output.** (1 connections) — `somatic/evidence/document_adapter.py`
- **Return the shared real-mode gate for the document adapter boundary.** (1 connections) — `somatic/evidence/document_adapter.py`
- **Return safe adapter metadata, rejecting unsafe output fail-closed.** (1 connections) — `somatic/evidence/document_adapter.py`
- **Return a deterministic rejected metadata-only adapter output.** (1 connections) — `somatic/evidence/document_adapter.py`

## Relationships

- [Document Adapter Contract Validation](Document_Adapter_Contract_Validation.md) (5 shared connections)
- [Phase 11 Audit Status](Phase_11_Audit_Status.md) (2 shared connections)
- [Adapter Readiness Evaluation](Adapter_Readiness_Evaluation.md) (2 shared connections)
- [Document Evidence Pack Construction](Document_Evidence_Pack_Construction.md) (2 shared connections)
- [Metadata Document Adapter](Metadata_Document_Adapter.md) (1 shared connections)
- [Document Evidence Fixtures](Document_Evidence_Fixtures.md) (1 shared connections)
- [CSI Adapter Validation](CSI_Adapter_Validation.md) (1 shared connections)

## Source Files

- `somatic/evidence/document_adapter.py`
- `tests/test_real_mode_readiness_gate.py`

## Audit Trail

- EXTRACTED: 57 (92%)
- INFERRED: 5 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*