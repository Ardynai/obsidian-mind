import copy
import json
import unittest

from somatic.safety.phase11_contracts import (
    PHASE11_DOCUMENT_DOMAIN,
    PHASE11_REVIEW_RECORD_STATUS_INCOMPLETE,
    PHASE11_REVIEW_RECORD_STATUS_REJECTED,
    PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    phase11_document_ingestion_contract_spec,
    phase11_document_ingestion_review_record,
    phase11_rejected_review_record,
    phase11_review_record_schema,
    phase11_review_record_status_summary,
    phase11_wifi_csi_rf_booth_contract_spec,
    phase11_wifi_csi_rf_booth_review_record,
    validate_phase11_review_record,
)

UNSAFE_SENTINELS = (
    "https://example.invalid",
    "c:/private",
    "source_id",
    "api_key",
    "access_token",
    "device_id",
    "router_id",
    "model_body",
    "parser_body",
    "provider_body",
    "raw_document_text",
    "raw_csi",
    "raw_values",
    "clinical",
    "medical",
    "password",
)


class Phase11BReviewRecordValidatorTests(unittest.TestCase):
    def test_schema_helper_describes_all_required_review_types(self):
        schema = phase11_review_record_schema()
        review_types = {entry["review_type"] for entry in schema["review_types"]}

        self.assertEqual(schema["review_record_contract_version"], 1)
        self.assertTrue(schema["planning_only"])
        self.assertTrue(schema["metadata_only"])
        self.assertFalse(schema["execution_permitted"])
        self.assertFalse(schema["real_mode_runtime_enabled"])
        for review_type in (
            "consent-review",
            "license-source-review",
            "privacy-review",
            "hardware-review",
            "model-artifact-review",
            "dependency-review",
            "network-policy-review",
        ):
            with self.subTest(review_type=review_type):
                self.assertIn(review_type, review_types)

    def test_non_object_missing_fields_and_unsupported_versions_fail_closed(self):
        malformed = validate_phase11_review_record("not-a-record")
        self.assertEqual(malformed.classification, "malformed")
        self.assertFalse(malformed.compatible)

        missing = phase11_document_ingestion_review_record()
        missing.pop("reviews")
        missing_result = validate_phase11_review_record(missing)
        self.assertEqual(missing_result.classification, "incompatible")
        self.assertIn(
            "phase11_review_record_required_field_missing",
            missing_result.errors,
        )

        unsupported = phase11_document_ingestion_review_record()
        unsupported["review_record_contract_version"] = 999
        unsupported_result = validate_phase11_review_record(unsupported)
        self.assertEqual(unsupported_result.classification, "unsupported_version")
        self.assertFalse(unsupported_result.compatible)
        self.assertEqual(
            unsupported_result.sanitized_record["record_status"],
            PHASE11_REVIEW_RECORD_STATUS_REJECTED,
        )

    def test_unsafe_fields_and_values_fail_closed_without_echo(self):
        cases = {
            "url": {"url": "https://example.invalid/private"},
            "absolute_path": {"absolute_path": "C:/private/document.pdf"},
            "source_ids": {"source_ids": ["source_id:secret"]},
            "credential": {"api_key": "sk-private"},
            "device": {"device_id": "device_id-private"},
            "router": {"router_id": "router_id-private"},
            "model_body": {"model_body": {"raw_values": [1, 2]}},
            "parser_body": {"parser_body": "raw_document_text"},
            "provider_body": {"provider_body": "raw_csi"},
            "clinical_claim": {"claim": "clinical medical diagnosis"},
        }

        for name, update in cases.items():
            with self.subTest(case=name):
                record = phase11_document_ingestion_review_record()
                record.update(update)
                result = validate_phase11_review_record(record)
                encoded = (
                    json.dumps(
                        (result.to_dict(), result.sanitized_record),
                        sort_keys=True,
                    )
                    .lower()
                    .replace("\\", "/")
                )

                self.assertFalse(result.compatible)
                self.assertEqual(result.classification, "incompatible")
                self.assertIn("phase11_review_record_privacy_boundary", result.errors)
                self.assertGreater(result.privacy_violation_count, 0)
                self.assertEqual(
                    result.sanitized_record["record_status"],
                    PHASE11_REVIEW_RECORD_STATUS_REJECTED,
                )
                for sentinel in UNSAFE_SENTINELS:
                    with self.subTest(case=name, sentinel=sentinel):
                        self.assertNotIn(sentinel, encoded)

    def test_contradictory_review_statuses_fail_closed(self):
        cases = []

        status_contradiction = phase11_document_ingestion_review_record(complete=False)
        status_contradiction["record_status"] = "reviewed-runtime-disabled"
        cases.append(status_contradiction)

        gate_summary_contradiction = phase11_document_ingestion_review_record()
        gate_summary_contradiction["missing_gates"] = ["network-policy-review"]
        gate_summary_contradiction["missing_gate_count"] = 1
        cases.append(gate_summary_contradiction)

        safe_contradiction = phase11_document_ingestion_review_record(complete=False)
        safe_contradiction["reviews"]["dependency_review"]["safe_to_proceed"] = True
        cases.append(safe_contradiction)

        reviewed_not_safe = phase11_document_ingestion_review_record()
        reviewed_not_safe["reviews"]["privacy_review"]["safe_to_proceed"] = False
        cases.append(reviewed_not_safe)

        for index, record in enumerate(cases):
            with self.subTest(case=index):
                result = validate_phase11_review_record(record)
                self.assertFalse(result.compatible)
                self.assertEqual(result.classification, "incompatible")
                self.assertTrue(
                    {
                        "phase11_review_record_status_contradiction",
                        "phase11_review_record_gate_summary_contradiction",
                        "phase11_review_record_gate_count_contradiction",
                    }.intersection(result.errors),
                    result.errors,
                )
                self.assertFalse(result.to_dict()["execution_permitted"])
                self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])

    def test_runtime_permission_or_authority_is_rejected(self):
        top_level = phase11_document_ingestion_review_record()
        top_level["execution_permitted"] = True
        top_level_result = validate_phase11_review_record(top_level)
        self.assertFalse(top_level_result.compatible)
        self.assertIn("phase11_review_record_runtime_implied", top_level_result.errors)

        entry_level = phase11_document_ingestion_review_record()
        entry_level["reviews"]["consent"]["runtime_permission"] = True
        entry_level_result = validate_phase11_review_record(entry_level)
        self.assertFalse(entry_level_result.compatible)
        self.assertIn("phase11_review_record_runtime_implied", entry_level_result.errors)

        authority_key = phase11_document_ingestion_review_record()
        authority_key["reviews"]["consent"]["authorization"] = "runtime allowed"
        authority_result = validate_phase11_review_record(authority_key)
        self.assertFalse(authority_result.compatible)
        self.assertIn("phase11_review_record_privacy_boundary", authority_result.errors)
        encoded = json.dumps(authority_result.sanitized_record, sort_keys=True).lower()
        self.assertNotIn("runtime allowed", encoded)
        self.assertNotIn("authorization", encoded)

    def test_rejected_records_do_not_satisfy_contract_gate(self):
        rejected = phase11_rejected_review_record(
            domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
            rejected_gate="hardware-review",
        )
        result = validate_phase11_review_record(
            rejected,
            expected_domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
        )
        spec = phase11_wifi_csi_rf_booth_contract_spec(rejected)

        self.assertEqual(result.classification, "rejected")
        self.assertFalse(result.compatible)
        self.assertFalse(spec["readiness_gate"]["ready"])
        self.assertEqual(spec["readiness_gate"]["missing_gate_count"], 7)
        self.assertFalse(spec["readiness_gate"]["execution_permitted"])
        self.assertFalse(spec["readiness_gate"]["real_mode_runtime_enabled"])

    def test_legacy_boolean_gate_maps_are_not_review_record_evidence(self):
        legacy_gate_map = {
            "consent": True,
            "license_review": True,
            "privacy_review": True,
            "hardware_review": True,
            "model_artifact_review": True,
            "dependency_review": True,
            "network_policy_review": True,
        }

        summary = phase11_review_record_status_summary(
            legacy_gate_map,
            domain=PHASE11_DOCUMENT_DOMAIN,
        )

        self.assertEqual(
            summary["review_record_status"],
            PHASE11_REVIEW_RECORD_STATUS_INCOMPLETE,
        )
        self.assertEqual(summary["reviewed_gate_count"], 0)
        self.assertEqual(summary["missing_gate_count"], 7)
        self.assertFalse(summary["execution_permitted"])
        self.assertFalse(summary["real_mode_runtime_enabled"])

    def test_domain_specific_records_are_required_when_requested(self):
        record = phase11_wifi_csi_rf_booth_review_record()
        result = validate_phase11_review_record(
            record,
            expected_domain=PHASE11_DOCUMENT_DOMAIN,
        )

        self.assertFalse(result.compatible)
        self.assertIn("phase11_review_record_domain_mismatch", result.errors)

    def test_reviewed_records_for_both_domains_still_disable_runtime(self):
        for record, spec in (
            (
                phase11_document_ingestion_review_record(),
                phase11_document_ingestion_contract_spec,
            ),
            (
                phase11_wifi_csi_rf_booth_review_record(),
                phase11_wifi_csi_rf_booth_contract_spec,
            ),
        ):
            with self.subTest(domain=record["domain"]):
                validation = validate_phase11_review_record(record)
                contract = spec(copy.deepcopy(record))

                self.assertTrue(validation.compatible, validation.errors)
                self.assertTrue(contract["readiness_gate"]["ready"])
                self.assertEqual(contract["readiness_gate"]["missing_gate_count"], 0)
                self.assertFalse(contract["readiness_gate"]["execution_permitted"])
                self.assertFalse(contract["readiness_gate"]["real_mode_runtime_enabled"])
                self.assertFalse(contract["execution_permitted"])
                self.assertFalse(contract["real_mode_runtime_enabled"])
                self.assertEqual(contract["runtime_stage"], "not-implemented")


if __name__ == "__main__":
    unittest.main()
