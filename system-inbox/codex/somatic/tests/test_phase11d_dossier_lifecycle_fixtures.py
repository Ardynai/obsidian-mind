import json
import unittest
from pathlib import Path

from somatic.evidence.document_adapter import document_fixture_adapter_status
from somatic.safety.phase11_contracts import (
    PHASE11_DOCUMENT_DOMAIN,
    PHASE11_LIFECYCLE_DECISION_NEEDS_MORE_REVIEW,
    PHASE11_LIFECYCLE_STAGE_CREATED,
    PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    phase11_dossier_lifecycle_fixture_bundle,
    phase11_dossier_lifecycle_status_summary,
    validate_phase11_dossier_lifecycle_record,
)
from somatic.sensors.csi_adapter import wifi_csi_source_adapter_status
from somatic.sensors.registry import sensor_evidence_provider_manifest

REPO_ROOT = Path(__file__).resolve().parents[1]
LIFECYCLE_FIXTURE = (
    REPO_ROOT / "fixtures" / "reviews" / "phase-11d-dossier-lifecycle-records-v1.json"
)
FORBIDDEN_LIFECYCLE_TERMS = (
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


class Phase11DDossierLifecycleFixtureTests(unittest.TestCase):
    def test_fixture_bundle_matches_deterministic_helper(self):
        fixture = json.loads(LIFECYCLE_FIXTURE.read_text(encoding="utf-8"))
        generated = phase11_dossier_lifecycle_fixture_bundle()

        self.assertEqual(fixture, generated)
        self.assertEqual(fixture["fixture_contract_version"], 1)
        self.assertEqual(
            fixture["fixture_kind"],
            "phase-11d-dossier-lifecycle-records",
        )
        self.assertTrue(fixture["planning_only"])
        self.assertTrue(fixture["metadata_only"])
        self.assertFalse(fixture["execution_permitted"])
        self.assertFalse(fixture["real_mode_runtime_enabled"])
        self.assertEqual(
            set(fixture["records"]),
            {
                "created",
                "reviewed",
                "superseded",
                "rejected",
                "archived",
                "decision_recorded",
            },
        )
        self.assertEqual(
            fixture["comparisons"]["missing_to_reviewed_document"]["domain"],
            PHASE11_DOCUMENT_DOMAIN,
        )
        self.assertTrue(
            fixture["comparisons"]["missing_to_reviewed_document"]["left_packet_id"].startswith(
                "p11c-preflight-document-ingestion-"
            )
        )
        self.assertTrue(
            fixture["comparisons"]["missing_to_reviewed_document"]["right_packet_id"].startswith(
                "p11c-preflight-document-ingestion-"
            )
        )
        self.assertEqual(
            fixture["comparisons"]["missing_to_reviewed_rf_booth"]["domain"],
            PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
        )
        self.assertTrue(
            fixture["comparisons"]["missing_to_reviewed_rf_booth"]["left_packet_id"].startswith(
                "p11c-preflight-wifi-csi-rf-booth-"
            )
        )
        self.assertTrue(
            fixture["comparisons"]["missing_to_reviewed_rf_booth"]["right_packet_id"].startswith(
                "p11c-preflight-wifi-csi-rf-booth-"
            )
        )
        self._assert_no_private_values(fixture)

    def test_fixture_lifecycle_records_validate_with_runtime_disabled(self):
        records = phase11_dossier_lifecycle_fixture_bundle()["records"]

        for name, record in records.items():
            with self.subTest(record=name):
                result = validate_phase11_dossier_lifecycle_record(record)

                self.assertTrue(result.compatible, result.errors)
                self.assertEqual(record["runtime_stage"], "not-implemented")
                self.assertFalse(record["execution_permitted"])
                self.assertFalse(record["real_mode_runtime_enabled"])
                self.assertFalse(record["audit_decision"]["execution_permitted"])
                self.assertTrue(record["lifecycle_record_id"].startswith("p11d-"))
                self.assertEqual(len(record["lifecycle_record_fingerprint"]), 64)
                self.assertNotIn("gates", record)
                self.assertNotIn("reviews", record)
                self._assert_no_private_values(record)

    def test_default_lifecycle_status_surfaces_are_audit_only(self):
        for domain in (PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN):
            with self.subTest(domain=domain):
                status = phase11_dossier_lifecycle_status_summary(domain=domain)

                self.assertEqual(status["lifecycle_stage"], PHASE11_LIFECYCLE_STAGE_CREATED)
                self.assertEqual(
                    status["audit_decision"],
                    PHASE11_LIFECYCLE_DECISION_NEEDS_MORE_REVIEW,
                )
                self.assertEqual(status["runtime_stage"], "not-implemented")
                self.assertFalse(status["execution_permitted"])
                self.assertFalse(status["real_mode_runtime_enabled"])
                self.assertNotIn("reviewer_signoff", status)
                self.assertNotIn("audit_decision_record", status)
                self._assert_no_private_values(status)

    def test_adapter_statuses_expose_compact_lifecycle_status(self):
        for status in (
            document_fixture_adapter_status(),
            wifi_csi_source_adapter_status(),
        ):
            with self.subTest(adapter=status["adapter_kind"]):
                p11d = status["p11d_lifecycle_audit_status"]
                self.assertIn("p11d-lifecycle-audit-record", status["capability_labels"])
                self.assertIn("audit-evidence-only", status["capability_labels"])
                self.assertEqual(p11d["lifecycle_stage"], PHASE11_LIFECYCLE_STAGE_CREATED)
                self.assertEqual(
                    p11d["audit_decision"],
                    PHASE11_LIFECYCLE_DECISION_NEEDS_MORE_REVIEW,
                )
                self.assertFalse(p11d["execution_permitted"])
                self.assertFalse(p11d["real_mode_runtime_enabled"])
                self.assertFalse(status["real_mode_execution_permitted"])
                self._assert_no_private_values(p11d)

    def test_provider_manifest_exposes_compact_lifecycle_status(self):
        manifest = sensor_evidence_provider_manifest()
        providers = {provider["provider_id"]: provider for provider in manifest["providers"]}

        for provider_id in ("document-fixture", "wifi-csi"):
            with self.subTest(provider=provider_id):
                provider = providers[provider_id]
                self.assertEqual(provider["lifecycle_audit_contract_version"], 1)
                self.assertEqual(provider["lifecycle_audit_stage"], "created")
                self.assertEqual(
                    provider["lifecycle_audit_decision"],
                    PHASE11_LIFECYCLE_DECISION_NEEDS_MORE_REVIEW,
                )
                self.assertTrue(provider["lifecycle_audit_record_id"].startswith("p11d-lifecycle-"))
                self.assertEqual(
                    len(provider["lifecycle_audit_record_fingerprint"]),
                    64,
                )
                self.assertFalse(provider["lifecycle_audit_execution_permitted"])
                self._assert_no_private_values(provider)

    def _assert_no_private_values(self, payload):
        encoded = json.dumps(payload, sort_keys=True).lower().replace("\\", "/")
        encoded = encoded.replace(
            "real-mode-authorization-missing",
            "real-mode-gap-missing",
        )
        encoded = encoded.replace("not-authorized", "not-runtime-status")
        encoded = encoded.replace("authorization_status", "runtime_status")
        encoded = encoded.replace(
            "runtime_authorization_gap_ledger_contract_version",
            "runtime_gap_ledger_contract_version",
        )
        self.assertNotRegex(encoded, r"[a-z]:/")
        for forbidden in FORBIDDEN_LIFECYCLE_TERMS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)


if __name__ == "__main__":
    unittest.main()
