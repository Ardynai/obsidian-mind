# Dossier Lifecycle Management

> 92 nodes · cohesion 0.05

## Key Concepts

- **phase11_dossier_lifecycle_record()** (27 connections) — `somatic/safety/phase11_contracts.py`
- **phase11_dossier_lifecycle_status_summary()** (25 connections) — `somatic/safety/phase11_contracts.py`
- **phase11_document_ingestion_preflight_dossier()** (21 connections) — `somatic/safety/phase11_contracts.py`
- **phase11_document_ingestion_review_record()** (21 connections) — `somatic/safety/phase11_contracts.py`
- **phase11_dossier_decision_record()** (21 connections) — `somatic/safety/phase11_contracts.py`
- **validate_phase11_preflight_dossier()** (21 connections) — `somatic/safety/phase11_contracts.py`
- **phase11_preflight_status_summary()** (19 connections) — `somatic/safety/phase11_contracts.py`
- **phase11_reviewer_signoff_metadata()** (17 connections) — `somatic/safety/phase11_contracts.py`
- **phase11_dossier_lifecycle_fixture_bundle()** (14 connections) — `somatic/safety/phase11_contracts.py`
- **phase11_wifi_csi_rf_booth_preflight_dossier()** (14 connections) — `somatic/safety/phase11_contracts.py`
- **_phase11_preflight_comparison_ref()** (13 connections) — `somatic/safety/phase11_contracts.py`
- **phase11_review_record()** (13 connections) — `somatic/safety/phase11_contracts.py`
- **phase11_wifi_csi_rf_booth_review_record()** (13 connections) — `somatic/safety/phase11_contracts.py`
- **phase11_review_record_fixture_bundle()** (12 connections) — `somatic/safety/phase11_contracts.py`
- **.test_completed_reviews_still_do_not_enable_runtime()** (12 connections) — `tests/test_phase11f_audit_handoff_reporting.py`
- **_safe_preflight_status()** (11 connections) — `somatic/safety/phase11_contracts.py`
- **.test_all_reviewed_records_still_do_not_enable_runtime()** (11 connections) — `tests/test_phase11e_audit_index_change_control.py`
- **Phase11CReviewPacketBuilderTests** (10 connections) — `tests/test_phase11c_review_packet_builder.py`
- **.test_lifecycle_records_are_deterministic_and_non_executable()** (10 connections) — `tests/test_phase11d_dossier_lifecycle_audit.py`
- **_default_preflight_dossier_for_domain()** (9 connections) — `somatic/safety/phase11_contracts.py`
- **.test_all_lifecycle_stages_validate_without_runtime_permission()** (9 connections) — `tests/test_phase11d_dossier_lifecycle_audit.py`
- **.test_lifecycle_validator_rejects_contradictions_and_runtime_implications()** (9 connections) — `tests/test_phase11d_dossier_lifecycle_audit.py`
- **phase11_rejected_review_record()** (8 connections) — `somatic/safety/phase11_contracts.py`
- **Phase11DDossierLifecycleAuditTests** (8 connections) — `tests/test_phase11d_dossier_lifecycle_audit.py`
- **test_status_summary_snapshot.py** (8 connections) — `tests/test_status_summary_snapshot.py`
- *... and 67 more nodes in this community*

## Relationships

- [Phase 11 Preflight Dossiers](Phase_11_Preflight_Dossiers.md) (40 shared connections)
- [Phase 11 Audit Records](Phase_11_Audit_Records.md) (32 shared connections)
- [Phase 11 Audit Status](Phase_11_Audit_Status.md) (30 shared connections)
- [Phase 11 Contract Review](Phase_11_Contract_Review.md) (21 shared connections)
- [Preflight Dossier Validation](Preflight_Dossier_Validation.md) (5 shared connections)
- [Phase 11 Audit Validation](Phase_11_Audit_Validation.md) (4 shared connections)
- [Dossier Lifecycle Fixtures](Dossier_Lifecycle_Fixtures.md) (3 shared connections)
- [Benchmarking and Scoring](Benchmarking_and_Scoring.md) (2 shared connections)
- [Phase 12 Closeout Summary](Phase_12_Closeout_Summary.md) (2 shared connections)
- [Sensor Evidence Provider Validation](Sensor_Evidence_Provider_Validation.md) (2 shared connections)
- [Provider Manifest Validation](Provider_Manifest_Validation.md) (1 shared connections)

## Source Files

- `somatic/safety/phase11_contracts.py`
- `tests/test_phase11c_preflight_dossier_fixtures.py`
- `tests/test_phase11c_review_packet_builder.py`
- `tests/test_phase11d_dossier_lifecycle_audit.py`
- `tests/test_phase11e_audit_index_change_control.py`
- `tests/test_phase11f_audit_handoff_reporting.py`
- `tests/test_status_summary_snapshot.py`

## Audit Trail

- EXTRACTED: 367 (67%)
- INFERRED: 183 (33%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*