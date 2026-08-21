# Phase 11 Followup Validation

> 35 nodes · cohesion 0.10

## Key Concepts

- **validate_phase11_followup_queue_index_record()** (27 connections) — `somatic/safety/phase11_contracts.py`
- **phase11_acceptance_followup_fixture_bundle()** (14 connections) — `somatic/safety/phase11_contracts.py`
- **phase11_followup_queue_index_fixture_bundle()** (14 connections) — `somatic/safety/phase11_contracts.py`
- **Phase11IFollowupQueueIndexTests** (12 connections) — `tests/test_phase11i_followup_queue_index.py`
- **Phase11FollowupQueueValidationResult** (8 connections) — `somatic/safety/phase11_contracts.py`
- **Phase11HFollowupRemediationTests** (8 connections) — `tests/test_phase11h_followup_remediation.py`
- **._assert_no_private_values()** (8 connections) — `tests/test_phase11i_followup_queue_index.py`
- **._assert_no_private_values()** (6 connections) — `tests/test_phase11h_followup_remediation.py`
- **.test_queue_indexes_are_compact_sanitized_and_non_executable()** (6 connections) — `tests/test_phase11i_followup_queue_index.py`
- **.test_resolved_for_planning_still_does_not_enable_runtime()** (5 connections) — `tests/test_phase11h_followup_remediation.py`
- **.test_accepted_for_planning_queue_still_does_not_enable_runtime()** (5 connections) — `tests/test_phase11i_followup_queue_index.py`
- **.test_queue_builder_fails_closed_when_any_source_followup_is_invalid()** (5 connections) — `tests/test_phase11i_followup_queue_index.py`
- **.test_explicit_non_acceptance_input_fails_closed()** (4 connections) — `tests/test_phase11h_followup_remediation.py`
- **.test_followup_records_are_compact_sanitized_and_non_executable()** (4 connections) — `tests/test_phase11h_followup_remediation.py`
- **.test_acceptance_validator_binds_queue_label_to_domain_and_fingerprint()** (4 connections) — `tests/test_phase11i_followup_queue_index.py`
- **.test_acceptance_validator_fails_closed_for_contradictory_status()** (4 connections) — `tests/test_phase11i_followup_queue_index.py`
- **.test_queue_acceptance_checks_cover_allowed_statuses()** (4 connections) — `tests/test_phase11i_followup_queue_index.py`
- **.test_queue_index_enforces_declared_deterministic_ordering()** (4 connections) — `tests/test_phase11i_followup_queue_index.py`
- **_invalid_phase11i_queue_result()** (3 connections) — `somatic/safety/phase11_contracts.py`
- **.test_fixture_bundle_matches_deterministic_helper()** (3 connections) — `tests/test_phase11h_followup_remediation.py`
- **.test_status_summary_is_compact_for_public_surfaces()** (3 connections) — `tests/test_phase11h_followup_remediation.py`
- **.test_fixture_bundle_matches_deterministic_helper()** (3 connections) — `tests/test_phase11i_followup_queue_index.py`
- **.test_status_summary_is_compact_for_public_surfaces()** (3 connections) — `tests/test_phase11i_followup_queue_index.py`
- **.test_validator_fails_closed_for_unsafe_or_contradictory_queue_indexes()** (3 connections) — `tests/test_phase11i_followup_queue_index.py`
- **_phase11i_ordering_errors()** (2 connections) — `somatic/safety/phase11_contracts.py`
- *... and 10 more nodes in this community*

## Relationships

- [Phase 11 Preflight Dossiers](Phase_11_Preflight_Dossiers.md) (29 shared connections)
- [Phase 11 Decision Closeout](Phase_11_Decision_Closeout.md) (10 shared connections)
- [Phase 11 Audit Status](Phase_11_Audit_Status.md) (5 shared connections)
- [Phase 11 Audit Records](Phase_11_Audit_Records.md) (2 shared connections)
- [Phase 11 Audit Validation](Phase_11_Audit_Validation.md) (1 shared connections)
- [Phase 11 Governance Review](Phase_11_Governance_Review.md) (1 shared connections)

## Source Files

- `somatic/safety/phase11_contracts.py`
- `tests/test_phase11h_followup_remediation.py`
- `tests/test_phase11i_followup_queue_index.py`

## Audit Trail

- EXTRACTED: 118 (69%)
- INFERRED: 54 (31%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*