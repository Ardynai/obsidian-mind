# Phase 11 Audit Validation

> 36 nodes · cohesion 0.08

## Key Concepts

- **validate_phase11_handoff_acceptance_record()** (23 connections) — `somatic/safety/phase11_contracts.py`
- **phase11_handoff_acceptance_fixture_bundle()** (13 connections) — `somatic/safety/phase11_contracts.py`
- **Phase11AuditHandoffValidationResult** (8 connections) — `somatic/safety/phase11_contracts.py`
- **Phase11HandoffAcceptanceValidationResult** (8 connections) — `somatic/safety/phase11_contracts.py`
- **Phase11GHandoffAcceptanceTests** (8 connections) — `tests/test_phase11g_handoff_acceptance_checks.py`
- **phase11_audit_handoff_fixture_bundle()** (7 connections) — `somatic/safety/phase11_contracts.py`
- **Phase11FAuditHandoffReportingTests** (7 connections) — `tests/test_phase11f_audit_handoff_reporting.py`
- **._assert_no_private_values()** (6 connections) — `tests/test_phase11g_handoff_acceptance_checks.py`
- **._assert_no_private_values()** (5 connections) — `tests/test_phase11f_audit_handoff_reporting.py`
- **_safe_handoff_acceptance_status()** (4 connections) — `somatic/safety/phase11_contracts.py`
- **.test_handoffs_are_compact_sanitized_and_non_executable()** (4 connections) — `tests/test_phase11f_audit_handoff_reporting.py`
- **.test_acceptance_records_are_compact_sanitized_and_non_executable()** (4 connections) — `tests/test_phase11g_handoff_acceptance_checks.py`
- **.test_accepted_for_planning_still_does_not_enable_runtime()** (4 connections) — `tests/test_phase11g_handoff_acceptance_checks.py`
- **.test_explicit_non_handoff_input_fails_closed()** (4 connections) — `tests/test_phase11g_handoff_acceptance_checks.py`
- **.test_validator_fails_closed_for_unsafe_or_contradictory_acceptance()** (4 connections) — `tests/test_phase11g_handoff_acceptance_checks.py`
- **_invalid_phase11f_result()** (3 connections) — `somatic/safety/phase11_contracts.py`
- **_invalid_phase11g_result()** (3 connections) — `somatic/safety/phase11_contracts.py`
- **_phase11g_reason_list_valid()** (3 connections) — `somatic/safety/phase11_contracts.py`
- **.test_fixture_bundle_matches_deterministic_helper()** (3 connections) — `tests/test_phase11f_audit_handoff_reporting.py`
- **.test_status_summary_is_compact_for_public_surfaces()** (3 connections) — `tests/test_phase11f_audit_handoff_reporting.py`
- **.test_fixture_bundle_matches_deterministic_helper()** (3 connections) — `tests/test_phase11g_handoff_acceptance_checks.py`
- **.test_status_summary_is_compact_for_public_surfaces()** (3 connections) — `tests/test_phase11g_handoff_acceptance_checks.py`
- **Sanitized validation result for Phase 11F audit handoff records.** (2 connections) — `somatic/safety/phase11_contracts.py`
- **.compatible()** (1 connections) — `somatic/safety/phase11_contracts.py`
- **.error_count()** (1 connections) — `somatic/safety/phase11_contracts.py`
- *... and 11 more nodes in this community*

## Relationships

- [Phase 11 Preflight Dossiers](Phase_11_Preflight_Dossiers.md) (18 shared connections)
- [Phase 11 Audit Status](Phase_11_Audit_Status.md) (18 shared connections)
- [Phase 11 Audit Records](Phase_11_Audit_Records.md) (4 shared connections)
- [Dossier Lifecycle Management](Dossier_Lifecycle_Management.md) (4 shared connections)
- [Phase 11 Followup Validation](Phase_11_Followup_Validation.md) (1 shared connections)

## Source Files

- `somatic/safety/phase11_contracts.py`
- `tests/test_phase11f_audit_handoff_reporting.py`
- `tests/test_phase11g_handoff_acceptance_checks.py`

## Audit Trail

- EXTRACTED: 121 (83%)
- INFERRED: 24 (17%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*