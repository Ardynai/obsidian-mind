import ast
import json
import unittest
from pathlib import Path

from somatic.sensors.environment import (
    EnvironmentFixtureSensorProvider,
    evaluate_environment_fixture_refs,
)
from somatic.sensors.environment_evidence_pack import (
    ENVIRONMENT_EVIDENCE_PACK_CONTRACT_VERSION,
    ENVIRONMENT_EVIDENCE_PACK_EXPORTER_ID,
    classify_environment_evidence_pack_compatibility,
    compute_environment_evidence_pack_fingerprint,
    validate_environment_evidence_pack_v1,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_ENVIRONMENT_WORDS = (
    "fixture://",
    "fixtures/",
    "environment-parsed.csv",
    "environment-mixed.csv",
    "source_id",
    "source_ids",
    "frame_id",
    "mac",
    "bssid",
    "ssid",
    "device_id",
    "router_id",
    "ip_address",
    "provider_payload",
    "provider_payload_body",
    "parser_report_body",
    "parser_summary_body",
    "csi",
    "amplitude",
    "phase",
    "rssi",
    "subcarrier",
    "raw_rf",
    "raw_signal",
    "signal_values",
    "medical",
    "clinical",
    "patient",
    "health",
    "diagnosis",
    "treatment",
    "baseline",
    "intervention",
    "medication",
    "clinician",
    "respiratory",
    "sleep",
    "vital",
    "monitoring",
    "api_key",
    "access_token",
    "refresh_token",
    "secret_value",
    "authorization",
    "bearer",
    "credential",
)
FORBIDDEN_ENVIRONMENT_KEYS = {
    "samples",
    "raw_values",
    "values",
    "payload",
    "provider_payload",
    "provider_payload_body",
    "report",
    "summary",
    "files",
    "fixtures",
    "fixture_refs",
    "source_id",
    "source_ids",
    "private_ref",
    "private_refs",
    "unsafe_ref",
    "unsafe_refs",
    "local_path",
    "source_path",
    "staging_root",
}


class EnvironmentEvidencePackTests(unittest.TestCase):
    def test_environment_fixture_pack_is_deterministic_and_compatible(self):
        provider = EnvironmentFixtureSensorProvider()

        left = provider.evidence_pack(("environment-parsed.csv",), repo_root=REPO_ROOT)
        right = provider.evidence_pack(("environment-parsed.csv",), repo_root=REPO_ROOT)

        self.assertEqual(left, right)
        self.assertEqual(left["contract_version"], ENVIRONMENT_EVIDENCE_PACK_CONTRACT_VERSION)
        self.assertEqual(left["exporter_id"], ENVIRONMENT_EVIDENCE_PACK_EXPORTER_ID)
        self.assertEqual(left["provider_kind"], "environment-fixture")
        self.assertEqual(left["evidence_kind"], "environment-tabular-evidence-pack")
        self.assertEqual(left["status"], "parsed")
        self.assertEqual(left["readiness_status"], "ready-with-sanitized-metadata")
        self.assertEqual(left["counts"]["row_count"], 3)
        self.assertEqual(left["counts"]["parsed_row_count"], 3)
        self.assertEqual(left["scores"]["evidence_quality"], 93)
        self.assertTrue(left["pack_id"].startswith("environment-evidence-pack-"))
        self.assertEqual(
            compute_environment_evidence_pack_fingerprint(left),
            left["pack_fingerprint"],
        )
        result = validate_environment_evidence_pack_v1(left)
        self.assertEqual(result.classification, "compatible")
        self.assertTrue(result.fingerprint_verified)
        self._assert_environment_pack_sanitized(left)

    def test_environment_mixed_fixture_is_partial_without_ranking_effect(self):
        pack = EnvironmentFixtureSensorProvider().evidence_pack(
            ("environment-mixed.csv",),
            repo_root=REPO_ROOT,
        )

        self.assertEqual(pack["status"], "partial")
        self.assertEqual(pack["readiness_status"], "partial-sanitized-metadata")
        self.assertEqual(pack["counts"]["row_count"], 3)
        self.assertEqual(pack["counts"]["partial_row_count"], 1)
        self.assertEqual(pack["counts"]["rejected_row_count"], 1)
        self.assertFalse(pack["ranking_input"])
        self.assertFalse(pack["core_tournament_scores_modified"])
        self.assertFalse(pack["tournament_rankings_modified"])
        self._assert_environment_pack_sanitized(pack)

    def test_environment_pack_fails_closed_for_missing_and_unsafe_refs(self):
        for refs in (
            ("missing-environment.csv",),
            ("../private.csv",),
            (str(REPO_ROOT / "fixtures" / "sensors" / "environment" / "environment-parsed.csv"),),
            ("fixture://sensors/environment/environment-parsed.csv",),
        ):
            with self.subTest(refs=refs):
                pack = EnvironmentFixtureSensorProvider().evidence_pack(
                    refs,
                    repo_root=REPO_ROOT,
                )
                self.assertEqual(pack["status"], "rejected")
                self.assertEqual(pack["readiness_status"], "rejected-fail-closed")
                self.assertEqual(pack["scores"]["evidence_quality"], 0)
                result = validate_environment_evidence_pack_v1(pack)
                self.assertEqual(result.classification, "compatible")
                self._assert_environment_pack_sanitized(pack)

    def test_environment_contract_rejects_malformed_unsupported_and_private_payloads(self):
        good = EnvironmentFixtureSensorProvider().evidence_pack(
            ("environment-parsed.csv",),
            repo_root=REPO_ROOT,
        )

        non_object = classify_environment_evidence_pack_compatibility(["not-a-pack"])
        self.assertEqual(non_object.classification, "malformed")
        self.assertEqual(non_object.readiness_status, "rejected-fail-closed")

        unsupported = dict(good)
        unsupported["contract_version"] = 2
        unsupported["evidence_contract_version"] = 2
        self._refresh(unsupported)
        result = validate_environment_evidence_pack_v1(unsupported)
        self.assertEqual(result.classification, "unsupported_version")

        stale = dict(good)
        stale["counts"] = dict(stale["counts"], row_count=4)
        result = validate_environment_evidence_pack_v1(stale)
        self.assertEqual(result.classification, "incompatible")
        self.assertIn("invalid_fingerprint_or_pack_id", result.errors)

        private = dict(good)
        private["provider_payload_body"] = {"values": [1, 2, 3]}
        self._refresh(private)
        result = validate_environment_evidence_pack_v1(private)
        self.assertEqual(result.classification, "incompatible")
        self.assertIn("privacy_boundary_violation", result.errors)

    def test_environment_fixture_evaluation_does_not_echo_refs(self):
        evaluation = evaluate_environment_fixture_refs(
            ("environment-parsed.csv", "../private.csv"),
            repo_root=REPO_ROOT,
        )

        encoded = json.dumps(evaluation, sort_keys=True).lower()
        self.assertEqual(evaluation["status"], "partial")
        self.assertIn("unsafe-ref", evaluation["parse_error_categories"])
        self.assertNotIn("environment-parsed.csv", encoded)
        self.assertNotIn("../private.csv", encoded)

    def test_environment_modules_add_no_network_hardware_or_capture_imports(self):
        forbidden_import_roots = {
            "requests",
            "urllib",
            "http",
            "socket",
            "websocket",
            "aiohttp",
            "httpx",
            "openai",
            "anthropic",
            "scapy",
            "pyshark",
            "pcapy",
            "dpkt",
            "wifi",
            "bleak",
            "bluetooth",
            "serial",
            "usb",
            "pyusb",
            "numpy",
            "scipy",
            "pandas",
        }
        forbidden_call_names = {
            "urlopen",
            "urlretrieve",
            "request",
            "create_connection",
            "connect",
            "sniff",
            "pcap",
            "set_monitor_mode",
            "scan",
            "download",
            "upload",
            "publish",
            "seed",
            "sign",
            "install",
            "execute",
        }
        for path in (
            REPO_ROOT / "somatic" / "sensors" / "environment.py",
            REPO_ROOT / "somatic" / "sensors" / "environment_evidence_pack.py",
        ):
            with self.subTest(path=path.name):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imported = {alias.name.split(".")[0] for alias in node.names}
                        self.assertTrue(imported.isdisjoint(forbidden_import_roots))
                    if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                        module = node.module.split(".")[0]
                        self.assertNotIn(module, forbidden_import_roots)
                    if isinstance(node, ast.Call):
                        name = (
                            node.func.id
                            if isinstance(node.func, ast.Name)
                            else getattr(node.func, "attr", None)
                        )
                        self.assertNotIn(name, forbidden_call_names)

    def _assert_environment_pack_sanitized(self, payload):
        self._assert_no_forbidden_environment_keys(payload)
        encoded = (
            json.dumps(payload, sort_keys=True)
            .lower()
            .replace(
                "real-mode-authorization-missing",
                "real-mode-gap-missing",
            )
        )
        for forbidden in FORBIDDEN_ENVIRONMENT_WORDS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)
        self._assert_no_absolute_paths(payload)

    def _assert_no_forbidden_environment_keys(self, payload):
        if isinstance(payload, dict):
            for key, value in payload.items():
                with self.subTest(key=key):
                    self.assertNotIn(str(key).lower(), FORBIDDEN_ENVIRONMENT_KEYS)
                self._assert_no_forbidden_environment_keys(value)
        elif isinstance(payload, list):
            for item in payload:
                self._assert_no_forbidden_environment_keys(item)

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

    @staticmethod
    def _refresh(payload):
        payload["pack_id"] = None
        payload["pack_fingerprint"] = None
        fingerprint = compute_environment_evidence_pack_fingerprint(payload)
        payload["pack_fingerprint"] = fingerprint
        payload["pack_id"] = f"environment-evidence-pack-{fingerprint[:16]}"


if __name__ == "__main__":
    unittest.main()
