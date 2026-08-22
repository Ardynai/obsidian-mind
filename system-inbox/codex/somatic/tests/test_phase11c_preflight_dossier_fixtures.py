import json
import unittest
from pathlib import Path

from somatic.evidence.document_adapter import document_fixture_adapter_status
from somatic.safety.phase11_contracts import (
    PHASE11_DOCUMENT_DOMAIN,
    PHASE11_PREFLIGHT_STATUS_MISSING,
    PHASE11_PREFLIGHT_STATUS_REJECTED,
    PHASE11_PREFLIGHT_STATUS_REVIEWED,
    PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    phase11_preflight_dossier_fixture_bundle,
    phase11_preflight_status_summary,
    validate_phase11_preflight_dossier,
)
from somatic.sensors.csi_adapter import wifi_csi_source_adapter_status
from somatic.sensors.registry import sensor_evidence_provider_manifest

REPO_ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT_DOSSIER_FIXTURE = (
    REPO_ROOT / "fixtures" / "reviews" / "phase-11c-preflight-dossiers-v1.json"
)
FORBIDDEN_PREFLIGHT_TERMS = (
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


class Phase11CPreflightDossierFixtureTests(unittest.TestCase):
    def test_fixture_bundle_matches_deterministic_helper(self):
        fixture = json.loads(PREFLIGHT_DOSSIER_FIXTURE.read_text(encoding="utf-8"))
        generated = phase11_preflight_dossier_fixture_bundle()

        self.assertEqual(fixture, generated)
        self.assertEqual(fixture["fixture_contract_version"], 1)
        self.assertEqual(fixture["fixture_kind"], "phase-11c-preflight-dossiers")
        self.assertTrue(fixture["planning_only"])
        self.assertTrue(fixture["metadata_only"])
        self.assertFalse(fixture["execution_permitted"])
        self.assertFalse(fixture["real_mode_runtime_enabled"])
        self.assertEqual(
            set(fixture["dossiers"]),
            {
                "document_ingestion_reviewed",
                "wifi_csi_rf_booth_reviewed",
                "incomplete_review_record",
                "rejected_review_record",
                "missing_review_record",
            },
        )
        self._assert_no_private_values(fixture)

    def test_fixture_dossiers_validate_with_runtime_disabled(self):
        dossiers = phase11_preflight_dossier_fixture_bundle()["dossiers"]
        expected = {
            "document_ingestion_reviewed": PHASE11_PREFLIGHT_STATUS_REVIEWED,
            "wifi_csi_rf_booth_reviewed": PHASE11_PREFLIGHT_STATUS_REVIEWED,
            "incomplete_review_record": PHASE11_PREFLIGHT_STATUS_MISSING,
            "rejected_review_record": PHASE11_PREFLIGHT_STATUS_REJECTED,
            "missing_review_record": PHASE11_PREFLIGHT_STATUS_MISSING,
        }

        for name, dossier in dossiers.items():
            with self.subTest(dossier=name):
                result = validate_phase11_preflight_dossier(dossier)
                self.assertEqual(dossier["status"], expected[name])
                self.assertEqual(result.status, expected[name])
                self.assertEqual(dossier["runtime_stage"], "not-implemented")
                self.assertFalse(dossier["execution_permitted"])
                self.assertFalse(dossier["real_mode_runtime_enabled"])
                self.assertTrue(dossier["packet_id"].startswith("p11c-preflight-"))
                self.assertEqual(len(dossier["packet_fingerprint"]), 64)
                self._assert_no_private_values(dossier)

    def test_default_preflight_status_surfaces_are_planning_only(self):
        for domain in (PHASE11_DOCUMENT_DOMAIN, PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN):
            with self.subTest(domain=domain):
                status = phase11_preflight_status_summary(domain=domain)
                self.assertEqual(
                    status["preflight_status"],
                    PHASE11_PREFLIGHT_STATUS_MISSING,
                )
                self.assertEqual(status["missing_gate_count"], 7)
                self.assertEqual(status["runtime_stage"], "not-implemented")
                self.assertFalse(status["execution_permitted"])
                self.assertFalse(status["real_mode_runtime_enabled"])
                self.assertNotIn("preflight_dossier_kind", status)
                self._assert_no_private_values(status)

    def test_adapter_statuses_expose_compact_preflight_status(self):
        for status in (
            document_fixture_adapter_status(),
            wifi_csi_source_adapter_status(),
        ):
            with self.subTest(adapter=status["adapter_kind"]):
                p11c = status["p11c_preflight_status"]
                self.assertIn("p11c-preflight-dossier", status["capability_labels"])
                self.assertIn("preflight-evidence-only", status["capability_labels"])
                self.assertEqual(
                    p11c["preflight_status"],
                    PHASE11_PREFLIGHT_STATUS_MISSING,
                )
                self.assertEqual(p11c["missing_gate_count"], 7)
                self.assertFalse(p11c["execution_permitted"])
                self.assertFalse(p11c["real_mode_runtime_enabled"])
                self.assertFalse(status["real_mode_execution_permitted"])
                self._assert_no_private_values(p11c)

    def test_provider_manifest_exposes_compact_preflight_status(self):
        manifest = sensor_evidence_provider_manifest()
        providers = {provider["provider_id"]: provider for provider in manifest["providers"]}

        for provider_id in ("document-fixture", "wifi-csi"):
            with self.subTest(provider=provider_id):
                provider = providers[provider_id]
                self.assertEqual(
                    provider["preflight_packet_status"],
                    PHASE11_PREFLIGHT_STATUS_MISSING,
                )
                self.assertEqual(provider["preflight_packet_missing_gate_count"], 7)
                self.assertTrue(provider["preflight_packet_id"].startswith("p11c-preflight-"))
                self.assertEqual(len(provider["preflight_packet_fingerprint"]), 64)
                self.assertFalse(provider["preflight_packet_execution_permitted"])
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
        for forbidden in FORBIDDEN_PREFLIGHT_TERMS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)


if __name__ == "__main__":
    unittest.main()
