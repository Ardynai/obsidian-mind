import copy
import json
import unittest

from somatic.safety.phase11_contracts import (
    PHASE11_DOCUMENT_DOMAIN,
    PHASE11_PREFLIGHT_STATUS_MISSING,
    PHASE11_PREFLIGHT_STATUS_REJECTED,
    PHASE11_PREFLIGHT_STATUS_REVIEWED,
    PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    phase11_document_ingestion_preflight_dossier,
    phase11_document_ingestion_review_record,
    phase11_preflight_status_summary,
    phase11_rejected_review_record,
    phase11_review_record_fixture_bundle,
    phase11_wifi_csi_rf_booth_preflight_dossier,
    phase11_wifi_csi_rf_booth_review_record,
    validate_phase11_preflight_dossier,
)

UNSAFE_PREFLIGHT_SENTINELS = (
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


class Phase11CReviewPacketBuilderTests(unittest.TestCase):
    def test_reviewed_dossiers_are_deterministic_and_non_executable(self):
        cases = (
            (
                phase11_document_ingestion_review_record(),
                phase11_document_ingestion_preflight_dossier,
                PHASE11_DOCUMENT_DOMAIN,
            ),
            (
                phase11_wifi_csi_rf_booth_review_record(),
                phase11_wifi_csi_rf_booth_preflight_dossier,
                PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
            ),
        )

        for record, builder, domain in cases:
            with self.subTest(domain=domain):
                dossier_a = builder(copy.deepcopy(record))
                dossier_b = builder(copy.deepcopy(record))
                result = validate_phase11_preflight_dossier(
                    dossier_a,
                    expected_domain=domain,
                )

                self.assertEqual(dossier_a, dossier_b)
                self.assertTrue(result.compatible, result.errors)
                self.assertEqual(result.status, PHASE11_PREFLIGHT_STATUS_REVIEWED)
                self.assertEqual(dossier_a["reviewed_gate_count"], 7)
                self.assertEqual(dossier_a["missing_gate_count"], 0)
                self.assertEqual(dossier_a["rejected_gate_count"], 0)
                self.assertEqual(dossier_a["runtime_stage"], "not-implemented")
                self.assertFalse(dossier_a["execution_permitted"])
                self.assertFalse(dossier_a["real_mode_runtime_enabled"])
                self.assertTrue(dossier_a["packet_id"].startswith("p11c-preflight-"))
                self.assertEqual(len(dossier_a["packet_fingerprint"]), 64)
                self._assert_no_private_values(dossier_a)

    def test_missing_and_rejected_dossiers_fail_closed(self):
        missing = phase11_document_ingestion_preflight_dossier()
        rejected = phase11_document_ingestion_preflight_dossier(
            phase11_rejected_review_record(
                domain=PHASE11_DOCUMENT_DOMAIN,
                rejected_gate="license-review",
            )
        )

        missing_result = validate_phase11_preflight_dossier(missing)
        rejected_result = validate_phase11_preflight_dossier(rejected)

        self.assertEqual(missing_result.classification, "incomplete")
        self.assertEqual(missing_result.status, PHASE11_PREFLIGHT_STATUS_MISSING)
        self.assertEqual(missing["missing_gate_count"], 7)
        self.assertFalse(missing["execution_permitted"])
        self.assertFalse(missing["real_mode_runtime_enabled"])

        self.assertEqual(rejected_result.classification, "rejected")
        self.assertEqual(rejected_result.status, PHASE11_PREFLIGHT_STATUS_REJECTED)
        self.assertEqual(rejected["rejected_gate_count"], 1)
        self.assertFalse(rejected["execution_permitted"])
        self.assertFalse(rejected["real_mode_runtime_enabled"])
        self._assert_no_private_values(missing)
        self._assert_no_private_values(rejected)

    def test_status_summary_is_compact_and_runtime_disabled(self):
        summary = phase11_preflight_status_summary(domain=PHASE11_DOCUMENT_DOMAIN)

        self.assertEqual(summary["preflight_status"], PHASE11_PREFLIGHT_STATUS_MISSING)
        self.assertEqual(summary["missing_gate_count"], 7)
        self.assertTrue(summary["preflight_packet_id"].startswith("p11c-preflight-"))
        self.assertEqual(len(summary["preflight_packet_fingerprint"]), 64)
        self.assertEqual(summary["runtime_stage"], "not-implemented")
        self.assertFalse(summary["execution_permitted"])
        self.assertFalse(summary["real_mode_runtime_enabled"])
        self.assertNotIn("preflight_dossier_kind", summary)
        self._assert_no_private_values(summary)

    def test_validator_rejects_unsafe_values_without_echo(self):
        base = phase11_document_ingestion_preflight_dossier(
            phase11_document_ingestion_review_record()
        )
        cases = {
            "url": {"url": "https://example.invalid/private"},
            "path": {"absolute_path": "C:/private/document.pdf"},
            "source": {"source_ids": ["source_id:private"]},
            "credential": {"api_key": "sk-private"},
            "device": {"device_id": "device_id-private"},
            "router": {"router_id": "router_id-private"},
            "model": {"model_body": {"raw_values": [1, 2]}},
            "parser": {"parser_body": "raw_document_text"},
            "provider": {"provider_body": "raw_csi"},
            "claim": {"claim": "clinical medical diagnosis"},
        }

        for name, update in cases.items():
            with self.subTest(case=name):
                dossier = dict(base)
                dossier.update(update)
                result = validate_phase11_preflight_dossier(dossier)
                encoded = (
                    json.dumps(
                        (result.to_dict(), result.sanitized_dossier),
                        sort_keys=True,
                    )
                    .lower()
                    .replace("\\", "/")
                )

                self.assertFalse(result.compatible)
                self.assertEqual(result.classification, "incompatible")
                self.assertIn("phase11_preflight_privacy_boundary", result.errors)
                self.assertEqual(
                    result.sanitized_dossier["status"],
                    PHASE11_PREFLIGHT_STATUS_REJECTED,
                )
                for sentinel in UNSAFE_PREFLIGHT_SENTINELS:
                    with self.subTest(case=name, sentinel=sentinel):
                        self.assertNotIn(sentinel, encoded)

    def test_validator_rejects_versions_runtime_flags_and_contradictions(self):
        cases = []
        unsupported = phase11_document_ingestion_preflight_dossier(
            phase11_document_ingestion_review_record()
        )
        unsupported["preflight_dossier_contract_version"] = 999
        cases.append(("unsupported_version", unsupported))

        runtime = phase11_document_ingestion_preflight_dossier(
            phase11_document_ingestion_review_record()
        )
        runtime["execution_permitted"] = True
        cases.append(("runtime", runtime))

        contradiction = phase11_document_ingestion_preflight_dossier(
            phase11_document_ingestion_review_record()
        )
        contradiction["missing_gate_count"] = 1
        contradiction["status"] = PHASE11_PREFLIGHT_STATUS_MISSING
        cases.append(("count", contradiction))

        tampered_hash = phase11_document_ingestion_preflight_dossier(
            phase11_document_ingestion_review_record()
        )
        tampered_hash["packet_fingerprint"] = "0" * 64
        cases.append(("hash", tampered_hash))

        for name, dossier in cases:
            with self.subTest(case=name):
                result = validate_phase11_preflight_dossier(dossier)
                self.assertFalse(result.compatible)
                self.assertFalse(result.to_dict()["execution_permitted"])
                self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])

    def test_validator_fails_closed_on_non_json_dossier_values(self):
        cases = {
            "blocking_reasons": {"blocking_reasons": object()},
            "gates": {"gates": [object()]},
            "fingerprints": {
                "included_record_fingerprints": {
                    "contract_spec": object(),
                    "review_record": "0" * 64,
                }
            },
            "label": {"contract_spec_label": object()},
        }

        for name, update in cases.items():
            with self.subTest(case=name):
                dossier = phase11_document_ingestion_preflight_dossier(
                    phase11_document_ingestion_review_record()
                )
                dossier.update(update)
                result = validate_phase11_preflight_dossier(dossier)
                encoded = json.dumps(
                    (result.to_dict(), result.sanitized_dossier),
                    sort_keys=True,
                ).lower()

                self.assertFalse(result.compatible)
                self.assertEqual(result.classification, "incompatible")
                self.assertIn("phase11_preflight_payload_not_json", result.errors)
                self.assertEqual(
                    result.sanitized_dossier["status"],
                    PHASE11_PREFLIGHT_STATUS_REJECTED,
                )
                self.assertNotIn("object at", encoded)

    def test_domain_specific_dossiers_are_required(self):
        dossier = phase11_wifi_csi_rf_booth_preflight_dossier(
            phase11_wifi_csi_rf_booth_review_record()
        )
        result = validate_phase11_preflight_dossier(
            dossier,
            expected_domain=PHASE11_DOCUMENT_DOMAIN,
        )

        self.assertFalse(result.compatible)
        self.assertIn("phase11_preflight_domain_mismatch", result.errors)

    def test_phase11b_fixture_records_can_feed_phase11c_packets(self):
        records = phase11_review_record_fixture_bundle()["records"]
        document = phase11_document_ingestion_preflight_dossier(
            records["document_ingestion_reviewed"]
        )
        rf_booth = phase11_wifi_csi_rf_booth_preflight_dossier(
            records["wifi_csi_rf_booth_reviewed"]
        )

        for dossier in (document, rf_booth):
            with self.subTest(domain=dossier["domain"]):
                result = validate_phase11_preflight_dossier(dossier)
                self.assertTrue(result.compatible, result.errors)
                self.assertEqual(dossier["status"], PHASE11_PREFLIGHT_STATUS_REVIEWED)
                self.assertFalse(dossier["execution_permitted"])
                self.assertFalse(dossier["real_mode_runtime_enabled"])

    def _assert_no_private_values(self, payload):
        encoded = json.dumps(payload, sort_keys=True).lower().replace("\\", "/")
        self.assertNotRegex(encoded, r"[a-z]:/")
        for forbidden in UNSAFE_PREFLIGHT_SENTINELS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)


if __name__ == "__main__":
    unittest.main()
