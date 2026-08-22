import ast
import hashlib
import tempfile
import unittest
from pathlib import Path

from somatic.sensors.evidence import (
    SENSOR_EVIDENCE_ARTIFACT_REF_CLASSIFICATIONS,
    SENSOR_EVIDENCE_COMPATIBILITY_CLASSIFICATIONS,
    SENSOR_EVIDENCE_FINGERPRINT_ALGORITHM,
    SENSOR_EVIDENCE_FINGERPRINT_SCOPE,
    SENSOR_EVIDENCE_READINESS_VOCABULARY,
    SENSOR_EVIDENCE_REQUIRED_FALSE_FLAGS,
    SENSOR_EVIDENCE_REQUIRED_TRUE_FLAGS,
    SENSOR_EVIDENCE_SCHEMA_VERSION,
    SENSOR_EVIDENCE_STATUS_VOCABULARY,
    SensorEvidenceContract,
    SensorEvidenceContractIdentity,
    build_sensor_evidence_artifact_ref,
    classify_sensor_evidence_artifact_ref,
    classify_sensor_evidence_contract,
    compute_sensor_evidence_fingerprint,
    safe_sensor_artifact_hashes,
    safe_sensor_artifact_ref,
    safe_sensor_artifact_refs,
    sensor_evidence_privacy_violation_count,
    sensor_evidence_readiness_status,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


class SensorEvidenceContractTests(unittest.TestCase):
    def test_generic_vocabulary_matches_csi_v1_foundation(self):
        self.assertEqual(SENSOR_EVIDENCE_SCHEMA_VERSION, 1)
        self.assertEqual(
            SENSOR_EVIDENCE_ARTIFACT_REF_CLASSIFICATIONS,
            ("compatible", "missing", "malformed", "hash_mismatch", "unsafe_ref"),
        )
        self.assertEqual(SENSOR_EVIDENCE_STATUS_VOCABULARY, ("parsed", "partial", "rejected"))
        self.assertEqual(
            SENSOR_EVIDENCE_READINESS_VOCABULARY,
            (
                "ready-with-sanitized-metadata",
                "partial-sanitized-metadata",
                "rejected-fail-closed",
            ),
        )
        self.assertEqual(
            SENSOR_EVIDENCE_COMPATIBILITY_CLASSIFICATIONS,
            ("compatible", "incompatible", "unsupported_version", "malformed"),
        )
        self.assertEqual(
            sensor_evidence_readiness_status("parsed", evidence_quality=100),
            "ready-with-sanitized-metadata",
        )
        self.assertEqual(
            sensor_evidence_readiness_status("partial", evidence_quality=100),
            "partial-sanitized-metadata",
        )
        self.assertEqual(
            sensor_evidence_readiness_status("parsed", evidence_quality=0),
            "rejected-fail-closed",
        )

    def test_artifact_refs_and_hashes_are_run_relative_and_sanitized(self):
        self.assertEqual(
            safe_sensor_artifact_ref("artifacts/sensor_evidence_pack.json"),
            "artifacts/sensor_evidence_pack.json",
        )
        for ref in (
            "",
            "../private.json",
            "artifacts/../private.json",
            str(REPO_ROOT / "private.json"),
            "/home/runner/work/somatic/private.json",
            "https://example.invalid/private.json",
            "fixture://sensors/private.json",
        ):
            with self.subTest(ref=ref):
                self.assertEqual(safe_sensor_artifact_ref(ref), "")

        self.assertEqual(
            safe_sensor_artifact_refs(
                {
                    "good": "artifacts/sensor_evidence_pack.json",
                    "bad": str(REPO_ROOT / "private.json"),
                }
            ),
            {"good": "artifacts/sensor_evidence_pack.json"},
        )
        self.assertEqual(
            safe_sensor_artifact_hashes({"good": "a" * 64, "bad": "not-a-hash"}),
            {"bad": None, "good": "a" * 64},
        )

    def test_generic_artifact_ref_builds_and_verifies_run_relative_sha256(self):
        pack = self._pack()
        with tempfile.TemporaryDirectory() as tmp:
            artifact_path = Path(tmp) / "artifacts" / "generic_sensor_evidence.json"
            artifact_path.parent.mkdir(parents=True)
            artifact_path.write_text("{}", encoding="utf-8")
            artifact_sha256 = self._sha256(artifact_path)

            ref = build_sensor_evidence_artifact_ref(
                "generic_sensor_evidence",
                "artifacts/generic_sensor_evidence.json",
                artifact_sha256=artifact_sha256,
                evidence_pack=pack,
                provider_kind="generic-sensor",
                evidence_kind="sanitized-run-artifact",
            )
            result = classify_sensor_evidence_artifact_ref(
                ref,
                run_dir=tmp,
                require_present=True,
                verify_hash=True,
            )

        self.assertEqual(ref["classification"], "compatible")
        self.assertEqual(ref["artifact_ref"], "artifacts/generic_sensor_evidence.json")
        self.assertEqual(ref["relative_path"], "artifacts/generic_sensor_evidence.json")
        self.assertEqual(ref["sha256"], artifact_sha256)
        self.assertEqual(ref["artifact_sha256"], artifact_sha256)
        self.assertEqual(ref["pack_fingerprint"], pack["pack_fingerprint"])
        self.assertTrue(result.present)
        self.assertEqual(result.classification, "compatible")
        self.assertEqual(result.sha256, artifact_sha256)
        self._assert_sanitized(ref)
        self._assert_sanitized(result.to_dict())

    def test_generic_artifact_ref_fails_closed_for_missing_and_malformed_refs(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = build_sensor_evidence_artifact_ref(
                "missing",
                "artifacts/missing.json",
                artifact_sha256="a" * 64,
            )
            result = classify_sensor_evidence_artifact_ref(
                missing,
                run_dir=tmp,
                require_present=True,
            )

        self.assertEqual(result.classification, "missing")
        self.assertFalse(result.present)
        self.assertEqual(result.errors, ("missing_artifact",))
        self._assert_sanitized(result.to_dict())

        for ref in (
            "../private.json",
            "artifacts/../private.json",
            str(REPO_ROOT / "private.json"),
            "https://example.invalid/private.json",
            "fixture://sensors/private.json",
            "",
        ):
            with self.subTest(ref=ref):
                result = classify_sensor_evidence_artifact_ref(
                    {
                        "name": "bad",
                        "artifact_ref": ref,
                        "artifact_sha256": "b" * 64,
                    }
                )
                self.assertEqual(result.classification, "unsafe_ref")
                self.assertFalse(result.present)
                self.assertIn("invalid_artifact_ref", result.errors)
                self._assert_sanitized(result.to_dict())

        malformed_hash = classify_sensor_evidence_artifact_ref(
            {
                "name": "bad_hash",
                "artifact_ref": "artifacts/csi_evidence_pack.json",
                "artifact_sha256": "not-a-hash",
            }
        )
        self.assertEqual(malformed_hash.classification, "malformed")
        self.assertEqual(malformed_hash.errors, ("invalid_artifact_sha256",))
        self._assert_sanitized(malformed_hash.to_dict())

    def test_generic_artifact_ref_fails_closed_for_hash_mismatch_and_private_refs(self):
        with tempfile.TemporaryDirectory() as tmp:
            artifact_path = Path(tmp) / "artifacts" / "csi_evidence_pack.json"
            artifact_path.parent.mkdir(parents=True)
            artifact_path.write_text("{}", encoding="utf-8")

            mismatch = classify_sensor_evidence_artifact_ref(
                {
                    "name": "csi_evidence_pack",
                    "artifact_ref": "artifacts/csi_evidence_pack.json",
                    "artifact_sha256": "c" * 64,
                },
                run_dir=tmp,
                require_present=True,
                verify_hash=True,
            )

        self.assertEqual(mismatch.classification, "hash_mismatch")
        self.assertEqual(mismatch.errors, ("artifact_hash_mismatch",))
        self._assert_sanitized(mismatch.to_dict())

        private_ref = classify_sensor_evidence_artifact_ref(
            {
                "name": "csi_evidence_pack",
                "artifact_ref": "artifacts/csi_evidence_pack.json",
                "artifact_sha256": "d" * 64,
                "private_ref": "fixture://sensors/private.json",
            }
        )
        self.assertEqual(private_ref.classification, "malformed")
        self.assertIn("privacy_boundary_violation", private_ref.errors)
        self._assert_sanitized(private_ref.to_dict())

        non_object = classify_sensor_evidence_artifact_ref(["not", "a", "ref"])
        self.assertEqual(non_object.classification, "malformed")
        self.assertEqual(non_object.errors, ("artifact_ref_not_object",))

    def test_generic_contract_accepts_sanitized_pack(self):
        pack = self._pack()
        result = classify_sensor_evidence_contract(pack, contract=self._contract())

        self.assertTrue(result.valid)
        self.assertEqual(result.classification, "compatible")
        self.assertTrue(result.fingerprint_verified)
        self.assertEqual(
            compute_sensor_evidence_fingerprint(pack),
            pack["pack_fingerprint"],
        )
        self._assert_sanitized(result.to_dict())

    def test_generic_contract_rejects_malformed_and_unsupported_packs(self):
        contract = self._contract()

        non_object = classify_sensor_evidence_contract(["not-a-pack"], contract=contract)
        self.assertEqual(non_object.classification, "malformed")
        self.assertEqual(non_object.errors, ("payload_not_object",))

        malformed = self._pack()
        del malformed["evidence_contract_version"]
        result = classify_sensor_evidence_contract(malformed, contract=contract)
        self.assertEqual(result.classification, "malformed")
        self.assertEqual(result.errors, ("missing_or_invalid_version_fields",))

        unsupported = self._pack()
        unsupported["contract_version"] = 2
        unsupported["evidence_contract_version"] = 2
        unsupported["schema_version"] = 2
        self._refresh(unsupported)
        result = classify_sensor_evidence_contract(unsupported, contract=contract)
        self.assertEqual(result.classification, "unsupported_version")
        self.assertEqual(result.errors, ("unsupported_contract_version",))
        self._assert_sanitized(result.to_dict())

    def test_generic_contract_rejects_incompatible_privacy_and_identity_drift(self):
        contract = self._contract()

        private_payload = self._pack()
        private_payload["provider_payload_body"] = {
            "samples": [1, 2, 3],
            "source_id": "private-source",
        }
        self._refresh(private_payload)
        result = classify_sensor_evidence_contract(private_payload, contract=contract)
        self.assertEqual(result.classification, "incompatible")
        self.assertIn("privacy_boundary_violation", result.errors)
        self.assertGreater(result.privacy_violation_count, 0)
        self._assert_sanitized(result.to_dict())

        unsafe_ref = self._pack()
        unsafe_ref["artifact_refs"] = {"pack": str(REPO_ROOT / "private.json")}
        self._refresh(unsafe_ref)
        result = classify_sensor_evidence_contract(unsafe_ref, contract=contract)
        self.assertEqual(result.classification, "incompatible")
        self.assertIn("invalid_artifact_refs", result.errors)
        self.assertGreater(result.privacy_violation_count, 0)

        posix_absolute_ref = self._pack()
        posix_absolute_ref["artifact_refs"] = {
            "pack": "/home/runner/work/somatic/private.json",
        }
        self._refresh(posix_absolute_ref)
        result = classify_sensor_evidence_contract(posix_absolute_ref, contract=contract)
        self.assertEqual(result.classification, "incompatible")
        self.assertIn("invalid_artifact_refs", result.errors)
        self.assertGreater(result.privacy_violation_count, 0)

        privacy_flag_drift = self._pack()
        privacy_flag_drift["personal_data_exported"] = True
        self._refresh(privacy_flag_drift)
        result = classify_sensor_evidence_contract(privacy_flag_drift, contract=contract)
        self.assertEqual(result.classification, "incompatible")
        self.assertIn("closed_boundary_flags_not_preserved", result.errors)
        self.assertGreater(result.privacy_violation_count, 0)

        identity_drift = self._pack()
        identity_drift["exporter_id"] = "generic-exporter-v1-copy"
        self._refresh(identity_drift)
        result = classify_sensor_evidence_contract(identity_drift, contract=contract)
        self.assertEqual(result.classification, "incompatible")
        self.assertIn("invalid_contract_identity", result.errors)

    def test_generic_contract_rejects_unsafe_unknown_payloads(self):
        safe_unknown = self._pack()
        safe_unknown["producer_build"] = "generic-v1"
        self._refresh(safe_unknown)
        result = classify_sensor_evidence_contract(safe_unknown, contract=self._contract())

        self.assertEqual(result.classification, "compatible")
        self.assertEqual(result.unknown_field_count, 1)
        self.assertEqual(result.warnings, ("additive_unknown_fields_ignored",))

        unsafe_unknown = self._pack()
        unsafe_unknown["future_measurement_blob"] = {"numeric_payload": [1, 2, 3]}
        self._refresh(unsafe_unknown)
        result = classify_sensor_evidence_contract(unsafe_unknown, contract=self._contract())

        self.assertEqual(result.classification, "incompatible")
        self.assertIn("unsafe_unknown_field_payload", result.errors)
        self.assertGreater(result.privacy_violation_count, 0)
        self._assert_sanitized(result.to_dict())

    def test_generic_contract_rejects_raw_like_nested_known_objects(self):
        contract = self._contract()

        unsafe_counts = self._pack()
        unsafe_counts["counts"]["measurement_values"] = [1, 2, 3]
        self._refresh(unsafe_counts)
        result = classify_sensor_evidence_contract(unsafe_counts, contract=contract)
        self.assertEqual(result.classification, "incompatible")
        self.assertIn("invalid_count_payload", result.errors)

        unsafe_diagnostics = self._pack()
        unsafe_diagnostics["diagnostic_counts"]["parser_report_body"] = {"rows": [1, 2]}
        self._refresh(unsafe_diagnostics)
        result = classify_sensor_evidence_contract(unsafe_diagnostics, contract=contract)
        self.assertEqual(result.classification, "incompatible")
        self.assertIn("invalid_diagnostic_counts", result.errors)
        self.assertIn("privacy_boundary_violation", result.errors)

        unsafe_scores = self._pack()
        unsafe_scores["scores"]["raw_score_values"] = [0.1, 0.2]
        self._refresh(unsafe_scores)
        result = classify_sensor_evidence_contract(unsafe_scores, contract=contract)
        self.assertEqual(result.classification, "incompatible")
        self.assertIn("invalid_score_payload", result.errors)

    def test_generic_privacy_scan_counts_forbidden_keys_and_strings(self):
        payload = {
            "provider_payload_body": {
                "raw_values": [1, 2],
                "source_id": "private-source",
            },
            "artifact_ref": str(REPO_ROOT / "private.json"),
        }

        self.assertGreater(sensor_evidence_privacy_violation_count(payload), 0)

    def test_generic_evidence_module_adds_no_network_hardware_or_capture_imports(self):
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
        path = REPO_ROOT / "somatic" / "sensors" / "evidence.py"
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

    def _pack(self):
        payload = {
            "schema_version": SENSOR_EVIDENCE_SCHEMA_VERSION,
            "contract_version": 1,
            "evidence_contract_version": 1,
            "id": "generic-sanitized-evidence-pack",
            "pack_id": None,
            "pack_fingerprint": None,
            "fingerprint_algorithm": SENSOR_EVIDENCE_FINGERPRINT_ALGORITHM,
            "fingerprint_scope": SENSOR_EVIDENCE_FINGERPRINT_SCOPE,
            "exporter_id": "generic-sensor-evidence-exporter-v1",
            "provider_kind": "generic-sensor",
            "evidence_kind": "sanitized-run-artifact",
            "status": "parsed",
            "readiness_status": "ready-with-sanitized-metadata",
            "metadata_only": True,
            "portable_json": True,
            "deterministic": True,
            "bounded": True,
            "explainable": True,
            "non_diagnostic": True,
            "artifact_refs": {"pack": "artifacts/generic_sensor_evidence.json"},
            "artifact_hashes": {"pack": "a" * 64},
            "diagnostic_counts": {
                "error_count": 0,
                "parse_error_count": 0,
                "warning_count": 0,
            },
            "counts": {
                "fixture_count": 1,
                "frame_count": 0,
                "sample_count": 0,
            },
            "scores": {"evidence_quality": 100},
        }
        for field in SENSOR_EVIDENCE_REQUIRED_TRUE_FLAGS:
            payload[field] = True
        for field in SENSOR_EVIDENCE_REQUIRED_FALSE_FLAGS:
            payload[field] = False
        self._refresh(payload)
        return payload

    def _contract(self):
        required_fields = (
            "schema_version",
            "contract_version",
            "evidence_contract_version",
            "id",
            "pack_id",
            "pack_fingerprint",
            "fingerprint_algorithm",
            "fingerprint_scope",
            "exporter_id",
            "provider_kind",
            "evidence_kind",
            "status",
            "readiness_status",
            "metadata_only",
            "portable_json",
            "deterministic",
            "bounded",
            "explainable",
            "non_diagnostic",
            "artifact_refs",
            "artifact_hashes",
            "diagnostic_counts",
            "counts",
            "scores",
        )
        known_fields = frozenset(
            set(required_fields)
            | set(SENSOR_EVIDENCE_REQUIRED_TRUE_FLAGS)
            | set(SENSOR_EVIDENCE_REQUIRED_FALSE_FLAGS)
        )
        return SensorEvidenceContract(
            identity=SensorEvidenceContractIdentity(
                provider_kind="generic-sensor",
                evidence_kind="sanitized-run-artifact",
                contract_version=1,
                exporter_id="generic-sensor-evidence-exporter-v1",
            ),
            version_fields={
                "schema_version": SENSOR_EVIDENCE_SCHEMA_VERSION,
                "contract_version": 1,
                "evidence_contract_version": 1,
            },
            required_fields=required_fields,
            required_object_fields=(
                "artifact_refs",
                "artifact_hashes",
                "diagnostic_counts",
                "counts",
                "scores",
            ),
            expected_identity_fields={
                "id": "generic-sanitized-evidence-pack",
                "exporter_id": "generic-sensor-evidence-exporter-v1",
                "provider_kind": "generic-sensor",
                "evidence_kind": "sanitized-run-artifact",
            },
            known_top_level_fields=known_fields,
            pack_id_prefix="generic-evidence-pack-",
        )

    @staticmethod
    def _refresh(payload):
        payload["pack_id"] = None
        payload["pack_fingerprint"] = None
        fingerprint = compute_sensor_evidence_fingerprint(payload)
        payload["pack_fingerprint"] = fingerprint
        payload["pack_id"] = f"generic-evidence-pack-{fingerprint[:16]}"

    def _assert_sanitized(self, payload):
        encoded = repr(payload).lower()
        for forbidden in (
            "samples",
            "raw_values",
            "amplitude",
            "phase",
            "rssi",
            "source_id",
            "provider_payload_body",
            "parser_report_body",
            "parser_summary_body",
            "example.invalid",
        ):
            self.assertNotIn(forbidden, encoded)
        self._assert_no_absolute_paths(payload)

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
    def _sha256(path):
        digest = hashlib.sha256()
        with Path(path).open("rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                digest.update(chunk)
        return digest.hexdigest()


if __name__ == "__main__":
    unittest.main()
