import json
import unittest
from pathlib import Path

from somatic.evidence.document_adapter import document_fixture_adapter_status
from somatic.safety.phase11_contracts import (
    PHASE11_DOCUMENT_DOMAIN,
    PHASE11_REVIEW_RECORD_STATUS_INCOMPLETE,
    PHASE11_REVIEW_RECORD_STATUS_REJECTED,
    PHASE11_REVIEW_RECORD_STATUS_REVIEWED,
    PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    phase11_document_ingestion_contract_spec,
    phase11_review_record_fixture_bundle,
    phase11_review_record_status_summary,
    phase11_wifi_csi_rf_booth_contract_spec,
    validate_phase11_contract_spec,
    validate_phase11_review_record,
)
from somatic.sensors.csi_adapter import wifi_csi_source_adapter_status

REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_RECORD_FIXTURE = REPO_ROOT / "fixtures" / "reviews" / "phase-11b-review-records-v1.json"
FORBIDDEN_REVIEW_TERMS = (
    "document-parsed.json",
    "document-mixed.json",
    "sample-esp32-csi",
    "sample-amplitude-phase",
    "sample-csi-jsonl",
    "fixture://",
    "fixtures/",
    "https://",
    "http://",
    "example.invalid",
    "c:/",
    "source_id",
    "source_ids",
    "device_id",
    "device_ids",
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
    "model weights",
    "parser_body",
    "provider_body",
    "diagnosis",
    "treatment",
    "medical",
    "clinical",
)


class Phase11BReviewRecordFixtureTests(unittest.TestCase):
    def test_fixture_bundle_matches_deterministic_helper(self):
        fixture = json.loads(REVIEW_RECORD_FIXTURE.read_text(encoding="utf-8"))
        generated = phase11_review_record_fixture_bundle()

        self.assertEqual(fixture, generated)
        self.assertEqual(fixture["fixture_contract_version"], 1)
        self.assertEqual(fixture["fixture_kind"], "phase-11b-review-record-fixtures")
        self.assertTrue(fixture["planning_only"])
        self.assertTrue(fixture["metadata_only"])
        self.assertFalse(fixture["execution_permitted"])
        self.assertFalse(fixture["real_mode_runtime_enabled"])
        self.assertEqual(
            set(fixture["records"]),
            {
                "document_ingestion_reviewed",
                "wifi_csi_rf_booth_reviewed",
                "incomplete_review_record",
                "rejected_review_record",
                "all_gates_reviewed_runtime_disabled",
            },
        )
        self._assert_no_private_values(fixture)

    def test_completed_review_records_are_compatible_but_do_not_enable_runtime(self):
        records = phase11_review_record_fixture_bundle()["records"]
        for name in (
            "document_ingestion_reviewed",
            "wifi_csi_rf_booth_reviewed",
            "all_gates_reviewed_runtime_disabled",
        ):
            with self.subTest(record=name):
                record = records[name]
                result = validate_phase11_review_record(record)

                self.assertTrue(result.compatible, result.errors)
                self.assertEqual(result.record_status, PHASE11_REVIEW_RECORD_STATUS_REVIEWED)
                self.assertEqual(result.reviewed_gate_count, 7)
                self.assertEqual(result.missing_gate_count, 0)
                self.assertEqual(result.rejected_gate_count, 0)
                self.assertFalse(result.to_dict()["execution_permitted"])
                self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])
                self.assertEqual(record["runtime_stage"], "not-implemented")
                self.assertFalse(record["execution_permitted"])
                self.assertFalse(record["real_mode_runtime_enabled"])
                self._assert_no_private_values(record)

    def test_incomplete_and_rejected_records_fail_closed(self):
        records = phase11_review_record_fixture_bundle()["records"]
        incomplete = validate_phase11_review_record(records["incomplete_review_record"])
        rejected = validate_phase11_review_record(records["rejected_review_record"])

        self.assertFalse(incomplete.compatible)
        self.assertEqual(incomplete.classification, "incomplete")
        self.assertEqual(incomplete.record_status, PHASE11_REVIEW_RECORD_STATUS_INCOMPLETE)
        self.assertEqual(incomplete.missing_gate_count, 3)
        self.assertIn("phase11_review_record_required_review_missing", incomplete.errors)
        self.assertFalse(incomplete.to_dict()["execution_permitted"])
        self.assertFalse(incomplete.to_dict()["real_mode_runtime_enabled"])

        self.assertFalse(rejected.compatible)
        self.assertEqual(rejected.classification, "rejected")
        self.assertEqual(rejected.record_status, PHASE11_REVIEW_RECORD_STATUS_REJECTED)
        self.assertEqual(rejected.rejected_gate_count, 1)
        self.assertIn("phase11_review_record_rejected", rejected.errors)
        self.assertFalse(rejected.to_dict()["execution_permitted"])
        self.assertFalse(rejected.to_dict()["real_mode_runtime_enabled"])

    def test_review_records_connect_to_specs_without_runtime_enablement(self):
        records = phase11_review_record_fixture_bundle()["records"]
        document_spec = phase11_document_ingestion_contract_spec(
            records["document_ingestion_reviewed"]
        )
        rf_spec = phase11_wifi_csi_rf_booth_contract_spec(records["wifi_csi_rf_booth_reviewed"])

        for spec in (document_spec, rf_spec):
            with self.subTest(domain=spec["domain"]):
                self.assertTrue(validate_phase11_contract_spec(spec).compatible)
                self.assertEqual(spec["readiness_gate"]["missing_gate_count"], 0)
                self.assertTrue(spec["readiness_gate"]["ready"])
                self.assertEqual(
                    spec["p11b_review_record_status"]["review_record_status"],
                    PHASE11_REVIEW_RECORD_STATUS_REVIEWED,
                )
                self.assertFalse(spec["readiness_gate"]["execution_permitted"])
                self.assertFalse(spec["readiness_gate"]["real_mode_runtime_enabled"])
                self.assertFalse(spec["execution_permitted"])
                self.assertFalse(spec["real_mode_runtime_enabled"])
                self.assertEqual(spec["runtime_stage"], "not-implemented")
                self._assert_no_private_values(spec)

    def test_default_review_status_surfaces_are_planning_only(self):
        document_summary = phase11_review_record_status_summary(
            domain=PHASE11_DOCUMENT_DOMAIN,
        )
        rf_summary = phase11_review_record_status_summary(
            domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
        )

        for summary in (document_summary, rf_summary):
            with self.subTest(domain=summary["domain"]):
                self.assertEqual(
                    summary["review_record_status"],
                    PHASE11_REVIEW_RECORD_STATUS_INCOMPLETE,
                )
                self.assertEqual(summary["reviewed_gate_count"], 0)
                self.assertEqual(summary["missing_gate_count"], 7)
                self.assertEqual(summary["runtime_stage"], "not-implemented")
                self.assertFalse(summary["execution_permitted"])
                self.assertFalse(summary["real_mode_runtime_enabled"])
                self._assert_no_private_values(summary)

        for status in (
            document_fixture_adapter_status(),
            wifi_csi_source_adapter_status(),
        ):
            with self.subTest(adapter=status["adapter_kind"]):
                p11b = status["p11b_review_record_status"]
                self.assertEqual(
                    p11b["review_record_status"],
                    PHASE11_REVIEW_RECORD_STATUS_INCOMPLETE,
                )
                self.assertIn("p11b-review-record-fixture", status["capability_labels"])
                self.assertIn("review-evidence-only", status["capability_labels"])
                self.assertIn(
                    "runtime-disabled-after-review",
                    status["capability_labels"],
                )
                self.assertFalse(p11b["execution_permitted"])
                self.assertFalse(p11b["real_mode_runtime_enabled"])
                self.assertFalse(status["real_mode_execution_permitted"])
                self._assert_no_private_values(p11b)

    def _assert_no_private_values(self, payload):
        encoded = json.dumps(payload, sort_keys=True).lower().replace("\\", "/")
        self.assertNotRegex(encoded, r"[a-z]:/")
        for forbidden in FORBIDDEN_REVIEW_TERMS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)


if __name__ == "__main__":
    unittest.main()
