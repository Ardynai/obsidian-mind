import copy
import json
import unittest
from pathlib import Path

from somatic.sensors.csi_batch import evaluate_csi_replay_batch
from somatic.sensors.csi_evidence_pack import (
    CSI_EVIDENCE_PACK_COMPATIBILITY_CLASSIFICATIONS,
    build_csi_evidence_pack,
    classify_csi_evidence_pack_compatibility,
    compute_csi_evidence_pack_fingerprint,
    validate_csi_evidence_pack_v1,
)
from somatic.sensors.csi_parser import build_csi_parser_artifacts

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "fixtures" / "reports"
PARSED_FIXTURE = FIXTURE_DIR / "csi-evidence-pack-v1-parsed.json"
PARTIAL_BATCH_FIXTURE = FIXTURE_DIR / "csi-evidence-pack-v1-partial-batch.json"
VALID_REFS = (
    "sample-esp32-csi.csv",
    "sample-amplitude-phase.csv",
    "sample-csi-jsonl.jsonl",
)
MIXED_GROUPS = (
    {
        "refs": (
            "sample-esp32-csi.csv",
            "sample-amplitude-phase.csv",
            "sample-csi-jsonl.jsonl",
        ),
    },
    {
        "refs": (
            "sample-esp32-csi.csv",
            "mixed-valid-invalid-csi.csv",
        ),
    },
    {"refs": ("unsupported-csi.npz",)},
)

FORBIDDEN_COMPATIBILITY_KEYS = {
    "samples",
    "raw_values",
    "real",
    "imag",
    "amplitude",
    "phase",
    "rssi",
    "raw_csi",
    "raw_rf",
    "raw_signal",
    "csi_values",
    "signal_values",
    "subcarrier",
    "subcarriers",
    "subcarrier_values",
    "values",
    "payload",
    "source_id",
    "source_ids",
    "frame_id",
    "mac",
    "bssid",
    "ssid",
    "device_id",
    "adapter_id",
    "router_id",
    "ip_address",
    "report",
    "summary",
    "files",
    "fixtures",
    "fixture_refs",
    "parse_errors",
    "local_path",
    "source_path",
    "staging_root",
    "provider_payload",
    "provider_payload_body",
    "parser_report_payload",
    "parser_report_body",
    "parsed_summary_payload",
    "parser_summary_body",
    "api_key",
    "access_token",
    "refresh_token",
    "secret",
    "secret_value",
    "password",
    "authorization",
    "bearer",
}

FORBIDDEN_COMPATIBILITY_WORDS = (
    "raw_values",
    "samples",
    "amplitude",
    "phase",
    "rssi",
    "raw_csi",
    "raw_rf",
    "raw_signal",
    "csi_values",
    "signal_values",
    "subcarrier",
    "subcarriers",
    "subcarrier_values",
    "source_id",
    "source_ids",
    "fixture_refs",
    "sample-esp32-csi",
    "sample-amplitude-phase",
    "sample-csi-jsonl",
    "mixed-valid-invalid-csi",
    "unsupported-csi",
    "invalid-utf8-csi",
    "example.invalid",
)


class WifiCsiEvidencePackCompatibilityTests(unittest.TestCase):
    def test_compatibility_classification_vocabulary_is_stable(self):
        self.assertEqual(
            CSI_EVIDENCE_PACK_COMPATIBILITY_CLASSIFICATIONS,
            ("compatible", "incompatible", "unsupported_version", "malformed"),
        )

    def test_checked_in_v1_fixtures_are_compatible_and_fingerprint_stable(self):
        parsed = self._read_json(PARSED_FIXTURE)
        partial = self._read_json(PARTIAL_BATCH_FIXTURE)

        for payload in (parsed, partial):
            with self.subTest(status=payload["status"]):
                result = validate_csi_evidence_pack_v1(payload)

                self.assertTrue(result.valid)
                self.assertTrue(result.compatible)
                self.assertEqual(result.classification, "compatible")
                self.assertEqual(result.contract_version, 1)
                self.assertEqual(result.evidence_pack_contract_version, 1)
                self.assertTrue(result.fingerprint_verified)
                self.assertEqual(
                    compute_csi_evidence_pack_fingerprint(payload),
                    payload["pack_fingerprint"],
                )
                self.assertEqual(
                    payload["pack_id"],
                    f"csi-evidence-pack-{payload['pack_fingerprint'][:16]}",
                )
                self._assert_payload_is_sanitized(payload)
                self._assert_payload_is_sanitized(result.to_dict())

    def test_generated_v1_fixtures_match_checked_in_expected_packs(self):
        report, parsed_summary = build_csi_parser_artifacts(
            VALID_REFS,
            repo_root=REPO_ROOT,
        )
        generated_parsed = build_csi_evidence_pack(
            parser_report_payload=report,
            parsed_summary_payload=parsed_summary,
            scoring_payload=report["csi_evidence_scoring"],
            artifact_hashes={
                "parser_metadata": "a" * 64,
                "parsed_metadata": "b" * 64,
                "sensor_evidence_metadata": "c" * 64,
            },
            artifact_refs={
                "parser_metadata": "artifacts/csi_parser_report.json",
                "parsed_metadata": "artifacts/csi_parsed_summary.json",
                "sensor_evidence_metadata": "artifacts/sensor_evidence_record.json",
            },
        )
        generated_partial = build_csi_evidence_pack(
            batch_payload=evaluate_csi_replay_batch(MIXED_GROUPS, repo_root=REPO_ROOT),
        )

        expected_parsed = self._read_json(PARSED_FIXTURE)
        expected_partial = self._read_json(PARTIAL_BATCH_FIXTURE)

        self.assertEqual(generated_parsed, expected_parsed)
        self.assertEqual(generated_partial, expected_partial)
        self.assertEqual(
            generated_parsed["pack_fingerprint"],
            "49dd1783afc9199b568fcb9ce49e5d0410dbde88a1f16c11d617a0985e65c517",
        )
        self.assertEqual(
            generated_partial["pack_fingerprint"],
            "5a38fce00a36d0966bc823122160196117af8f7a6777f0a2f61662da020f567e",
        )

    def test_identical_sanitized_inputs_keep_same_fingerprint(self):
        left = self._read_json(PARSED_FIXTURE)
        right = self._read_json(PARSED_FIXTURE)

        self.assertEqual(
            compute_csi_evidence_pack_fingerprint(left),
            compute_csi_evidence_pack_fingerprint(right),
        )
        self.assertEqual(left["pack_fingerprint"], right["pack_fingerprint"])

    def test_generated_v1_pack_is_compatible_with_exporter_fingerprint(self):
        report, parsed = build_csi_parser_artifacts(VALID_REFS, repo_root=REPO_ROOT)
        pack = build_csi_evidence_pack(
            parser_report_payload=report,
            parsed_summary_payload=parsed,
            scoring_payload=report["csi_evidence_scoring"],
            artifact_hashes={
                "parser_metadata": "a" * 64,
                "parsed_metadata": "b" * 64,
            },
            artifact_refs={
                "parser_metadata": "artifacts/csi_parser_report.json",
                "parsed_metadata": "artifacts/csi_parsed_summary.json",
            },
        )

        result = validate_csi_evidence_pack_v1(pack)

        self.assertEqual(result.classification, "compatible")
        self.assertTrue(result.fingerprint_verified)
        self.assertEqual(result.unknown_field_count, 0)
        self.assertEqual(
            compute_csi_evidence_pack_fingerprint(pack),
            pack["pack_fingerprint"],
        )
        self._assert_payload_is_sanitized(pack)
        self._assert_payload_is_sanitized(result.to_dict())

    def test_sanitized_field_change_changes_fingerprint_and_classifies_stale_pack(self):
        payload = self._read_json(PARSED_FIXTURE)
        changed = copy.deepcopy(payload)
        changed["counts"]["frame_count"] += 1

        self.assertNotEqual(
            compute_csi_evidence_pack_fingerprint(changed),
            payload["pack_fingerprint"],
        )
        result = validate_csi_evidence_pack_v1(changed)

        self.assertEqual(result.classification, "incompatible")
        self.assertFalse(result.valid)
        self.assertIn("invalid_fingerprint_or_pack_id", result.errors)
        self._assert_payload_is_sanitized(result.to_dict())

    def test_additive_unknown_future_field_can_be_compatible_when_refingerprinted(self):
        payload = self._read_json(PARSED_FIXTURE)
        with_unknown = copy.deepcopy(payload)
        with_unknown["producer_build"] = "compatibility-fixture-v1"
        self._refresh_fingerprint(with_unknown)

        result = validate_csi_evidence_pack_v1(with_unknown)

        self.assertEqual(result.classification, "compatible")
        self.assertTrue(result.valid)
        self.assertTrue(result.fingerprint_verified)
        self.assertEqual(result.unknown_field_count, 1)
        self.assertEqual(result.warnings, ("additive_unknown_fields_ignored",))
        self._assert_payload_is_sanitized(result.to_dict())

    def test_additive_unknown_future_field_with_stale_fingerprint_is_incompatible(self):
        payload = self._read_json(PARSED_FIXTURE)
        payload["producer_build"] = "compatibility-fixture-v1"

        result = validate_csi_evidence_pack_v1(payload)

        self.assertEqual(result.classification, "incompatible")
        self.assertFalse(result.compatible)
        self.assertIn("invalid_fingerprint_or_pack_id", result.errors)
        self.assertEqual(result.unknown_field_count, 1)
        self._assert_payload_is_sanitized(result.to_dict())

    def test_forbidden_unknown_future_field_fails_closed_without_echoing_private_data(self):
        payload = self._read_json(PARSED_FIXTURE)
        payload["fixture_refs"] = ["sample-esp32-csi.csv"]
        self._refresh_fingerprint(payload)

        result = validate_csi_evidence_pack_v1(payload)
        result_payload = result.to_dict()

        self.assertEqual(result.classification, "incompatible")
        self.assertFalse(result.valid)
        self.assertIn("privacy_boundary_violation", result.errors)
        self.assertGreater(result.privacy_violation_count, 0)
        self._assert_payload_is_sanitized(result_payload)

    def test_nested_unknown_numeric_payload_fails_closed_when_refingerprinted(self):
        payload = self._read_json(PARSED_FIXTURE)
        payload["future_measurement_blob"] = {"numeric_payload": [1, 2, 3]}
        self._refresh_fingerprint(payload)

        result = validate_csi_evidence_pack_v1(payload)

        self.assertEqual(result.classification, "incompatible")
        self.assertIn("unsafe_unknown_field_payload", result.errors)
        self.assertGreater(result.privacy_violation_count, 0)
        self._assert_payload_is_sanitized(result.to_dict())

    def test_generated_from_future_version_is_unsupported(self):
        payload = self._read_json(PARSED_FIXTURE)
        payload["generated_from"]["parser_contract_version"] = 2
        self._refresh_fingerprint(payload)

        result = validate_csi_evidence_pack_v1(payload)

        self.assertEqual(result.classification, "unsupported_version")
        self.assertEqual(result.errors, ("unsupported_generated_from_version",))
        self._assert_payload_is_sanitized(result.to_dict())

    def test_exporter_identity_drift_is_incompatible(self):
        payload = self._read_json(PARSED_FIXTURE)
        payload["exporter_id"] = "somatic-csi-evidence-pack-exporter-v1-copy"
        self._refresh_fingerprint(payload)

        result = validate_csi_evidence_pack_v1(payload)

        self.assertEqual(result.classification, "incompatible")
        self.assertIn("invalid_contract_identity", result.errors)
        self._assert_payload_is_sanitized(result.to_dict())

    def test_missing_exporter_boundary_flag_is_incompatible(self):
        payload = self._read_json(PARSED_FIXTURE)
        del payload["sandbox_only"]
        self._refresh_fingerprint(payload)

        result = validate_csi_evidence_pack_v1(payload)

        self.assertEqual(result.classification, "incompatible")
        self.assertIn("closed_boundary_flags_not_preserved", result.errors)
        self.assertGreater(result.privacy_violation_count, 0)
        self._assert_payload_is_sanitized(result.to_dict())

    def test_missing_required_field_is_malformed_and_fail_closed(self):
        payload = self._read_json(PARSED_FIXTURE)
        del payload["counts"]

        result = validate_csi_evidence_pack_v1(payload)

        self.assertEqual(result.classification, "malformed")
        self.assertFalse(result.valid)
        self.assertEqual(result.readiness_status, "rejected-fail-closed")
        self.assertEqual(result.missing_required_field_count, 1)
        self.assertEqual(result.errors, ("missing_required_fields",))
        self._assert_payload_is_sanitized(result.to_dict())

    def test_non_object_payload_is_malformed(self):
        result = validate_csi_evidence_pack_v1(["not", "a", "pack"])

        self.assertEqual(result.classification, "malformed")
        self.assertFalse(result.valid)
        self.assertEqual(result.errors, ("payload_not_object",))
        self.assertEqual(result.readiness_status, "rejected-fail-closed")

    def test_unsupported_future_version_is_classified_without_breaking_v1_reader(self):
        payload = self._read_json(PARSED_FIXTURE)
        payload["evidence_pack_contract_version"] = 2
        payload["contract_version"] = 2
        payload["schema_version"] = 2

        result = validate_csi_evidence_pack_v1(payload)

        self.assertEqual(result.classification, "unsupported_version")
        self.assertFalse(result.valid)
        self.assertEqual(result.readiness_status, "rejected-fail-closed")
        self.assertEqual(result.errors, ("unsupported_contract_version",))
        self._assert_payload_is_sanitized(result.to_dict())

    def test_wrong_required_shapes_are_incompatible(self):
        payload = self._read_json(PARSED_FIXTURE)
        payload["artifact_refs"] = {"parser_metadata": "C:/AI/somatic/private.json"}
        self._refresh_fingerprint(payload)

        result = classify_csi_evidence_pack_compatibility(payload)

        self.assertEqual(result.classification, "incompatible")
        self.assertIn("invalid_artifact_refs", result.errors)
        self.assertGreater(result.privacy_violation_count, 0)
        self._assert_payload_is_sanitized(result.to_dict())

    @staticmethod
    def _read_json(path):
        return json.loads(Path(path).read_text(encoding="utf-8"))

    @staticmethod
    def _refresh_fingerprint(payload):
        fingerprint = compute_csi_evidence_pack_fingerprint(payload)
        payload["pack_fingerprint"] = fingerprint
        payload["pack_id"] = f"csi-evidence-pack-{fingerprint[:16]}"

    def _assert_payload_is_sanitized(self, payload):
        self._assert_no_forbidden_keys(payload)
        self._assert_no_forbidden_words(payload)
        self._assert_no_absolute_paths(payload)

    def _assert_no_forbidden_keys(self, payload):
        if isinstance(payload, dict):
            for key, value in payload.items():
                with self.subTest(compatibility_key=key):
                    self.assertNotIn(str(key).lower(), FORBIDDEN_COMPATIBILITY_KEYS)
                self._assert_no_forbidden_keys(value)
        elif isinstance(payload, list):
            for item in payload:
                self._assert_no_forbidden_keys(item)

    def _assert_no_forbidden_words(self, payload):
        if isinstance(payload, dict):
            for value in payload.values():
                self._assert_no_forbidden_words(value)
        elif isinstance(payload, list):
            for item in payload:
                self._assert_no_forbidden_words(item)
        elif isinstance(payload, str):
            lowered = payload.lower().replace(
                "real-mode-authorization-missing",
                "real-mode-gap-missing",
            )
            for word in FORBIDDEN_COMPATIBILITY_WORDS:
                with self.subTest(compatibility_word=word):
                    self.assertNotIn(word, lowered)

    def _assert_no_absolute_paths(self, payload):
        if isinstance(payload, dict):
            for value in payload.values():
                self._assert_no_absolute_paths(value)
        elif isinstance(payload, list):
            for item in payload:
                self._assert_no_absolute_paths(item)
        elif isinstance(payload, str):
            normalized = payload.replace("\\", "/")
            self.assertNotIn(str(REPO_ROOT).replace("\\", "/"), normalized)
            self.assertNotRegex(normalized, r"^[A-Za-z]:/")


if __name__ == "__main__":
    unittest.main()
