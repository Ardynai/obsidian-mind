import copy
import json
import unittest

from somatic.safety.phase11_contracts import (
    PHASE11_DOCUMENT_DOMAIN,
    PHASE11_LIFECYCLE_DECISION_ALL_GATES_REVIEWED_RUNTIME_DISABLED,
    PHASE11_LIFECYCLE_DECISION_BLOCKED,
    PHASE11_LIFECYCLE_DECISION_NEEDS_MORE_REVIEW,
    PHASE11_LIFECYCLE_DECISION_REJECTED,
    PHASE11_LIFECYCLE_DECISION_SAFE_FOR_PLANNING,
    PHASE11_LIFECYCLE_STAGE_ARCHIVED,
    PHASE11_LIFECYCLE_STAGE_CREATED,
    PHASE11_LIFECYCLE_STAGE_DECISION_RECORDED,
    PHASE11_LIFECYCLE_STAGE_REJECTED,
    PHASE11_LIFECYCLE_STAGE_REVIEWED,
    PHASE11_LIFECYCLE_STAGE_SUPERSEDED,
    PHASE11_SIGNOFF_VERDICT_BLOCKERS,
    PHASE11_SIGNOFF_VERDICT_NO_BLOCKERS,
    PHASE11_SIGNOFF_VERDICT_REJECTED,
    PHASE11_SIGNOFF_VERDICT_SUPERSEDED,
    PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    phase11_compare_preflight_dossiers,
    phase11_document_ingestion_preflight_dossier,
    phase11_document_ingestion_review_record,
    phase11_dossier_decision_record,
    phase11_dossier_lifecycle_record,
    phase11_dossier_lifecycle_status_summary,
    phase11_rejected_review_record,
    phase11_reviewer_signoff_metadata,
    phase11_wifi_csi_rf_booth_preflight_dossier,
    phase11_wifi_csi_rf_booth_review_record,
    validate_phase11_dossier_decision_record,
    validate_phase11_dossier_lifecycle_record,
    validate_phase11_reviewer_signoff_metadata,
)

UNSAFE_LIFECYCLE_SENTINELS = (
    "https://example.invalid",
    "c:/private",
    "source_id",
    "source-id",
    "device_id",
    "device-id",
    "router_id",
    "api_key",
    "access_token",
    "secret_value",
    "authorization",
    "password",
    "raw_document_text",
    "raw_csi",
    "raw_rf",
    "raw_values",
    "model_body",
    "parser_body",
    "provider_body",
    "clinical",
    "medical",
)


class Phase11DDossierLifecycleAuditTests(unittest.TestCase):
    def test_lifecycle_records_are_deterministic_and_non_executable(self):
        cases = (
            (
                phase11_document_ingestion_preflight_dossier(
                    phase11_document_ingestion_review_record()
                ),
                PHASE11_DOCUMENT_DOMAIN,
            ),
            (
                phase11_wifi_csi_rf_booth_preflight_dossier(
                    phase11_wifi_csi_rf_booth_review_record()
                ),
                PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
            ),
        )

        for dossier, domain in cases:
            with self.subTest(domain=domain):
                record_a = phase11_dossier_lifecycle_record(
                    dossier,
                    lifecycle_stage=PHASE11_LIFECYCLE_STAGE_REVIEWED,
                    signoff=phase11_reviewer_signoff_metadata(
                        verdict=PHASE11_SIGNOFF_VERDICT_NO_BLOCKERS,
                        review_scope="planning-audit",
                    ),
                    decision_record=phase11_dossier_decision_record(
                        dossier,
                        decision=PHASE11_LIFECYCLE_DECISION_SAFE_FOR_PLANNING,
                    ),
                )
                record_b = phase11_dossier_lifecycle_record(
                    copy.deepcopy(dossier),
                    lifecycle_stage=PHASE11_LIFECYCLE_STAGE_REVIEWED,
                    signoff=phase11_reviewer_signoff_metadata(
                        verdict=PHASE11_SIGNOFF_VERDICT_NO_BLOCKERS,
                        review_scope="planning-audit",
                    ),
                    decision_record=phase11_dossier_decision_record(
                        copy.deepcopy(dossier),
                        decision=PHASE11_LIFECYCLE_DECISION_SAFE_FOR_PLANNING,
                    ),
                )
                result = validate_phase11_dossier_lifecycle_record(
                    record_a,
                    expected_domain=domain,
                )

                self.assertEqual(record_a, record_b)
                self.assertTrue(result.compatible, result.errors)
                self.assertEqual(record_a["lifecycle_stage"], "reviewed")
                self.assertEqual(record_a["audit_decision"]["decision"], "safe-for-planning")
                self.assertEqual(record_a["reviewer_signoff"]["verdict"], "no-blockers")
                self.assertEqual(record_a["runtime_stage"], "not-implemented")
                self.assertFalse(record_a["execution_permitted"])
                self.assertFalse(record_a["real_mode_runtime_enabled"])
                self.assertNotIn("gates", record_a)
                self.assertNotIn("reviews", record_a)
                self._assert_no_private_values(record_a)

    def test_all_lifecycle_stages_validate_without_runtime_permission(self):
        reviewed = phase11_document_ingestion_preflight_dossier(
            phase11_document_ingestion_review_record()
        )
        rejected = phase11_document_ingestion_preflight_dossier(
            phase11_rejected_review_record(
                domain=PHASE11_DOCUMENT_DOMAIN,
                rejected_gate="license-review",
            )
        )
        previous = phase11_document_ingestion_preflight_dossier()
        cases = (
            (
                PHASE11_LIFECYCLE_STAGE_CREATED,
                previous,
                PHASE11_SIGNOFF_VERDICT_BLOCKERS,
                PHASE11_LIFECYCLE_DECISION_NEEDS_MORE_REVIEW,
                None,
            ),
            (
                PHASE11_LIFECYCLE_STAGE_REVIEWED,
                reviewed,
                PHASE11_SIGNOFF_VERDICT_NO_BLOCKERS,
                PHASE11_LIFECYCLE_DECISION_SAFE_FOR_PLANNING,
                None,
            ),
            (
                PHASE11_LIFECYCLE_STAGE_SUPERSEDED,
                reviewed,
                PHASE11_SIGNOFF_VERDICT_SUPERSEDED,
                PHASE11_LIFECYCLE_DECISION_BLOCKED,
                previous,
            ),
            (
                PHASE11_LIFECYCLE_STAGE_REJECTED,
                rejected,
                PHASE11_SIGNOFF_VERDICT_REJECTED,
                PHASE11_LIFECYCLE_DECISION_REJECTED,
                previous,
            ),
            (
                PHASE11_LIFECYCLE_STAGE_ARCHIVED,
                reviewed,
                PHASE11_SIGNOFF_VERDICT_SUPERSEDED,
                PHASE11_LIFECYCLE_DECISION_BLOCKED,
                previous,
            ),
            (
                PHASE11_LIFECYCLE_STAGE_DECISION_RECORDED,
                reviewed,
                PHASE11_SIGNOFF_VERDICT_NO_BLOCKERS,
                PHASE11_LIFECYCLE_DECISION_ALL_GATES_REVIEWED_RUNTIME_DISABLED,
                previous,
            ),
        )

        for stage, dossier, verdict, decision, prior in cases:
            with self.subTest(stage=stage):
                record = phase11_dossier_lifecycle_record(
                    dossier,
                    lifecycle_stage=stage,
                    previous_dossier=prior,
                    signoff=phase11_reviewer_signoff_metadata(verdict=verdict),
                    decision_record=phase11_dossier_decision_record(
                        dossier,
                        decision=decision,
                    ),
                )
                result = validate_phase11_dossier_lifecycle_record(record)

                self.assertTrue(result.compatible, result.errors)
                self.assertEqual(record["lifecycle_stage"], stage)
                self.assertEqual(record["runtime_stage"], "not-implemented")
                self.assertFalse(record["execution_permitted"])
                self.assertFalse(record["real_mode_runtime_enabled"])
                self.assertFalse(record["audit_decision"]["execution_permitted"])
                self._assert_no_private_values(record)

    def test_dossier_comparison_is_deterministic_and_sanitized(self):
        left = phase11_document_ingestion_preflight_dossier()
        right = phase11_document_ingestion_preflight_dossier(
            phase11_document_ingestion_review_record()
        )

        same = phase11_compare_preflight_dossiers(left, copy.deepcopy(left))
        changed_a = phase11_compare_preflight_dossiers(left, right)
        changed_b = phase11_compare_preflight_dossiers(copy.deepcopy(left), copy.deepcopy(right))

        self.assertTrue(same["equal"])
        self.assertEqual(same["changed_field_count"], 0)
        self.assertFalse(changed_a["equal"])
        self.assertEqual(changed_a, changed_b)
        self.assertIn("status", changed_a["changed_fields"])
        self.assertIn("gate-statuses", changed_a["changed_fields"])
        self.assertIn("record-fingerprints", changed_a["changed_fields"])
        self.assertEqual(changed_a["runtime_stage"], "not-implemented")
        self.assertFalse(changed_a["execution_permitted"])
        self._assert_no_private_values(changed_a)

    def test_signoff_and_decision_validators_fail_closed(self):
        safe_signoff = phase11_reviewer_signoff_metadata(
            reviewer_label="p11d-planning-reviewer",
            verdict=PHASE11_SIGNOFF_VERDICT_NO_BLOCKERS,
        )
        safe_decision = phase11_dossier_decision_record(
            phase11_document_ingestion_preflight_dossier(
                phase11_document_ingestion_review_record()
            ),
            decision=PHASE11_LIFECYCLE_DECISION_ALL_GATES_REVIEWED_RUNTIME_DISABLED,
        )

        self.assertTrue(validate_phase11_reviewer_signoff_metadata(safe_signoff).compatible)
        self.assertTrue(validate_phase11_dossier_decision_record(safe_decision).compatible)

        unsafe_signoff = dict(safe_signoff)
        unsafe_signoff["reviewer_label"] = "p11d-reviewer-source-id-c:/private"
        unsafe_decision = dict(safe_decision)
        unsafe_decision["decision_reason"] = "clinical medical source-id"
        unsafe_decision["execution_permitted"] = True

        for payload, validator in (
            (unsafe_signoff, validate_phase11_reviewer_signoff_metadata),
            (unsafe_decision, validate_phase11_dossier_decision_record),
        ):
            with self.subTest(payload=payload.get("schema_version")):
                result = validator(payload)
                encoded = (
                    json.dumps(
                        (result.to_dict(), result.sanitized_record),
                        sort_keys=True,
                    )
                    .lower()
                    .replace("\\", "/")
                )
                self.assertFalse(result.compatible)
                self.assertFalse(result.to_dict()["execution_permitted"])
                for sentinel in UNSAFE_LIFECYCLE_SENTINELS:
                    self.assertNotIn(sentinel, encoded)

    def test_lifecycle_validator_rejects_contradictions_and_runtime_implications(self):
        reviewed = phase11_document_ingestion_preflight_dossier(
            phase11_document_ingestion_review_record()
        )
        missing = phase11_document_ingestion_preflight_dossier()
        cases = []

        unsupported = phase11_dossier_lifecycle_record(reviewed)
        unsupported["lifecycle_contract_version"] = 999
        cases.append(("unsupported", unsupported))

        runtime = phase11_dossier_lifecycle_record(reviewed)
        runtime["execution_permitted"] = True
        cases.append(("runtime", runtime))

        contradictory_decision = phase11_dossier_lifecycle_record(
            missing,
            lifecycle_stage=PHASE11_LIFECYCLE_STAGE_REVIEWED,
            signoff=phase11_reviewer_signoff_metadata(verdict=PHASE11_SIGNOFF_VERDICT_NO_BLOCKERS),
            decision_record=phase11_dossier_decision_record(
                missing,
                decision=PHASE11_LIFECYCLE_DECISION_SAFE_FOR_PLANNING,
            ),
        )
        cases.append(("decision", contradictory_decision))

        unsafe = phase11_dossier_lifecycle_record(reviewed)
        unsafe["source_id"] = "source-id-c:/private"
        cases.append(("unsafe", unsafe))

        mixed_domain = phase11_dossier_lifecycle_record(
            phase11_wifi_csi_rf_booth_preflight_dossier(phase11_wifi_csi_rf_booth_review_record()),
            lifecycle_stage=PHASE11_LIFECYCLE_STAGE_DECISION_RECORDED,
            previous_dossier=phase11_document_ingestion_preflight_dossier(),
            signoff=phase11_reviewer_signoff_metadata(
                verdict=PHASE11_SIGNOFF_VERDICT_NO_BLOCKERS,
            ),
            decision_record=phase11_dossier_decision_record(
                phase11_wifi_csi_rf_booth_preflight_dossier(
                    phase11_wifi_csi_rf_booth_review_record()
                ),
                decision=PHASE11_LIFECYCLE_DECISION_ALL_GATES_REVIEWED_RUNTIME_DISABLED,
            ),
        )
        cases.append(("mixed-domain-comparison", mixed_domain))

        for name, record in cases:
            with self.subTest(case=name):
                result = validate_phase11_dossier_lifecycle_record(record)
                self.assertFalse(result.compatible)
                self.assertFalse(result.to_dict()["execution_permitted"])
                self.assertEqual(
                    result.sanitized_record["lifecycle_stage"],
                    PHASE11_LIFECYCLE_STAGE_REJECTED,
                )

    def test_status_summary_is_compact_and_runtime_disabled(self):
        summary = phase11_dossier_lifecycle_status_summary(domain=PHASE11_DOCUMENT_DOMAIN)

        self.assertEqual(summary["lifecycle_stage"], PHASE11_LIFECYCLE_STAGE_CREATED)
        self.assertEqual(summary["audit_decision"], PHASE11_LIFECYCLE_DECISION_NEEDS_MORE_REVIEW)
        self.assertEqual(summary["runtime_stage"], "not-implemented")
        self.assertFalse(summary["execution_permitted"])
        self.assertFalse(summary["real_mode_runtime_enabled"])
        self.assertNotIn("reviewer_signoff", summary)
        self.assertNotIn("audit_decision_record", summary)
        self._assert_no_private_values(summary)

    def _assert_no_private_values(self, payload):
        encoded = json.dumps(payload, sort_keys=True).lower().replace("\\", "/")
        encoded = encoded.replace(
            "real-mode-authorization-missing",
            "real-mode-gap-missing",
        )
        self.assertNotRegex(encoded, r"[a-z]:/")
        for forbidden in UNSAFE_LIFECYCLE_SENTINELS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)


if __name__ == "__main__":
    unittest.main()
