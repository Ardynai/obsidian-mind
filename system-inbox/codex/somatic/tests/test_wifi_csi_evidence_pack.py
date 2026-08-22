import ast
import json
import tempfile
import unittest
from pathlib import Path

from somatic.mock_runtime import run_mock_workflow
from somatic.sensors.csi_batch import evaluate_csi_replay_batch
from somatic.sensors.csi_evidence_pack import (
    CSI_EVIDENCE_PACK_CONTRACT_VERSION,
    CSI_EVIDENCE_PACK_EXPORTER_ID,
    build_csi_evidence_pack,
    compute_csi_evidence_pack_fingerprint,
)
from somatic.sensors.csi_parser import build_csi_parser_artifacts

REPO_ROOT = Path(__file__).resolve().parents[1]
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
FORBIDDEN_EVIDENCE_PACK_KEYS = {
    "samples",
    "raw_values",
    "real",
    "imag",
    "amplitude",
    "phase",
    "rssi",
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
    "api_key",
    "access_token",
    "refresh_token",
    "secret",
    "secret_value",
    "password",
    "authorization",
    "bearer",
}
FORBIDDEN_EVIDENCE_PACK_WORDS = (
    "raw_values",
    "amplitude",
    "phase",
    "rssi",
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


class WifiCsiEvidencePackTests(unittest.TestCase):
    def test_valid_replay_evidence_pack_is_deterministic(self):
        report, parsed = build_csi_parser_artifacts(VALID_REFS, repo_root=REPO_ROOT)
        scoring = report["csi_evidence_scoring"]

        left = build_csi_evidence_pack(
            parser_report_payload=report,
            parsed_summary_payload=parsed,
            scoring_payload=scoring,
            artifact_hashes={
                "parser_metadata": "a" * 64,
                "parsed_metadata": "b" * 64,
            },
            artifact_refs={
                "parser_metadata": "artifacts/csi_parser_report.json",
                "parsed_metadata": "artifacts/csi_parsed_summary.json",
            },
        )
        right = build_csi_evidence_pack(
            parser_report_payload=report,
            parsed_summary_payload=parsed,
            scoring_payload=scoring,
            artifact_hashes={
                "parsed_metadata": "b" * 64,
                "parser_metadata": "a" * 64,
            },
            artifact_refs={
                "parsed_metadata": "artifacts/csi_parsed_summary.json",
                "parser_metadata": "artifacts/csi_parser_report.json",
            },
        )

        self.assertEqual(self._stable_json(left), self._stable_json(right))
        self.assertEqual(left["contract_version"], CSI_EVIDENCE_PACK_CONTRACT_VERSION)
        self.assertEqual(left["exporter_id"], CSI_EVIDENCE_PACK_EXPORTER_ID)
        self.assertEqual(left["status"], "parsed")
        self.assertEqual(left["readiness_status"], "ready-with-sanitized-metadata")
        self.assertEqual(left["counts"]["fixture_count"], 3)
        self.assertEqual(left["counts"]["frame_count"], 6)
        self.assertEqual(left["counts"]["sample_count"], 14)
        self.assertEqual(left["scores"]["evidence_quality"], 100)
        self.assertEqual(left["scores"]["replay_integrity"], 100)
        self.assertEqual(len(left["pack_fingerprint"]), 64)
        self.assertTrue(left["pack_id"].startswith("csi-evidence-pack-"))
        self.assertFalse(left["ranking_input"])
        self._assert_payload_is_sanitized(left)

    def test_valid_partial_and_rejected_batch_inputs_export_correctly(self):
        batch = evaluate_csi_replay_batch(MIXED_GROUPS, repo_root=REPO_ROOT)
        pack = build_csi_evidence_pack(batch_payload=batch)

        self.assertEqual(pack["status"], "partial")
        self.assertEqual(pack["readiness_status"], "partial-sanitized-metadata")
        self.assertEqual(pack["counts"]["group_count"], 3)
        self.assertEqual(pack["counts"]["evaluated_group_count"], 3)
        self.assertEqual(pack["counts"]["rejected_group_count"], 1)
        self.assertEqual(pack["status_counts"], {"parsed": 4, "partial": 1, "rejected": 1})
        self.assertEqual(pack["group_status_counts"], {"parsed": 1, "partial": 1, "rejected": 1})
        self.assertEqual(pack["scores"]["aggregate_evidence_quality"], 0)
        self.assertEqual(pack["scores"]["aggregate_replay_integrity"], 0)
        self.assertEqual(
            [group["status"] for group in pack["group_summaries"]],
            ["parsed", "partial", "rejected"],
        )
        self._assert_payload_is_sanitized(pack)

    def test_unsafe_refs_and_private_fixture_names_are_not_exported(self):
        unsafe_ref = str(REPO_ROOT / "fixtures" / "sensors" / "csi" / "sample-esp32-csi.csv")
        batch = evaluate_csi_replay_batch(
            (
                {"refs": (unsafe_ref, "https://example.invalid/csi-fixture.csv")},
                {"refs": ("invalid-utf8-csi.csv",)},
            ),
            repo_root=REPO_ROOT,
        )
        pack = build_csi_evidence_pack(batch_payload=batch)

        self.assertEqual(pack["status"], "rejected")
        self.assertEqual(pack["readiness_status"], "rejected-fail-closed")
        self.assertEqual(pack["scores"]["evidence_quality"], 0)
        self._assert_payload_is_sanitized(pack)

    def test_n_of_1_fabric_plan_references_sanitized_evidence_pack(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = run_mock_workflow(
                REPO_ROOT / "fixtures" / "workflows" / "valid-n-of-1.yaml",
                repo_root=REPO_ROOT,
                output_root=Path(tmp),
                run_id="run-csi-evidence-pack-n-of-1",
            )

            manifest = self._read_json(run_dir / "manifest.json")
            evidence_pack = self._read_json(run_dir / "artifacts" / "csi_evidence_pack.json")
            summary = self._read_json(run_dir / "artifacts" / "n_of_1_summary.json")
            report_packet = self._read_json(run_dir / "artifacts" / "n_of_1_report_packet.json")
            fabric_plan = self._read_json(run_dir / "artifacts" / "n_of_1_fabric_pack_plan.json")

        self.assertIn("csi_evidence_pack", manifest["artifacts"])
        self.assertEqual(
            manifest["artifacts"]["csi_evidence_pack"],
            "artifacts/csi_evidence_pack.json",
        )
        self.assertEqual(evidence_pack["status"], "parsed")
        self.assertEqual(evidence_pack["scores"]["evidence_quality"], 100)
        self.assertEqual(
            evidence_pack["pack_fingerprint"],
            compute_csi_evidence_pack_fingerprint(evidence_pack),
        )
        self.assertEqual(
            summary["csi_evidence_pack_metadata"]["pack_fingerprint"],
            evidence_pack["pack_fingerprint"],
        )
        for refs in (
            manifest["sensor_evidence_artifact_refs"],
            summary["sensor_evidence_artifact_refs"],
            report_packet["sensor_evidence_artifact_refs"],
            fabric_plan["sensor_evidence_artifact_refs"],
        ):
            generic_ref = refs["csi_evidence_pack"]
            self.assertEqual(generic_ref["classification"], "compatible")
            self.assertEqual(generic_ref["artifact_ref"], "artifacts/csi_evidence_pack.json")
            self.assertEqual(
                generic_ref["sha256"], report_packet["artifact_hashes"]["csi_evidence_pack"]
            )
            self.assertEqual(generic_ref["pack_fingerprint"], evidence_pack["pack_fingerprint"])
        self.assertEqual(
            report_packet["artifact_refs"]["csi_evidence_pack"]["relative_path"],
            "artifacts/csi_evidence_pack.json",
        )
        file_plans = {item["id"]: item for item in fabric_plan["file_plans"]}
        self.assertIn("csi_evidence_pack", file_plans)
        self.assertEqual(
            file_plans["csi_evidence_pack"]["path"], "artifacts/csi_evidence_pack.json"
        )
        self.assertEqual(
            file_plans["csi_evidence_pack"]["sha256"],
            report_packet["artifact_hashes"]["csi_evidence_pack"],
        )
        for payload in (evidence_pack, summary["csi_evidence_pack_metadata"]):
            self._assert_payload_is_sanitized(payload)
        for payload in (report_packet, fabric_plan):
            self._assert_no_forbidden_words(payload)
            self._assert_no_absolute_paths(payload)

    def test_tournament_evidence_pack_is_readiness_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = run_mock_workflow(
                REPO_ROOT / "fixtures" / "workflows" / "valid-hypothesis-tournament.yaml",
                repo_root=REPO_ROOT,
                output_root=Path(tmp),
                run_id="run-csi-evidence-pack-tournament",
            )

            manifest = self._read_json(run_dir / "manifest.json")
            evidence_pack = self._read_json(run_dir / "artifacts" / "csi_evidence_pack.json")
            team_summary = self._read_json(run_dir / "artifacts" / "team_orchestrator_summary.json")
            ranked = self._read_json(run_dir / "artifacts" / "ranked_hypotheses.json")

        self.assertIn("csi_evidence_pack", manifest["artifacts"])
        self.assertEqual(evidence_pack["status"], "partial")
        self.assertEqual(
            evidence_pack["pack_fingerprint"],
            "5a38fce00a36d0966bc823122160196117af8f7a6777f0a2f61662da020f567e",
        )
        self.assertFalse(evidence_pack["ranking_input"])
        self.assertFalse(evidence_pack["core_tournament_scores_modified"])
        self.assertFalse(evidence_pack["tournament_rankings_modified"])
        self.assertEqual(
            team_summary["csi_evidence_pack"]["pack_fingerprint"],
            evidence_pack["pack_fingerprint"],
        )
        generic_ref = team_summary["sensor_evidence_artifact_refs"]["csi_evidence_pack"]
        self.assertEqual(generic_ref["classification"], "compatible")
        self.assertEqual(generic_ref["artifact_ref"], "artifacts/csi_evidence_pack.json")
        self.assertEqual(generic_ref["sha256"], manifest["hashes"]["csi_evidence_pack"])
        self.assertEqual(generic_ref["pack_fingerprint"], evidence_pack["pack_fingerprint"])
        self.assertEqual(
            {item["rank"] for item in ranked},
            set(range(1, len(ranked) + 1)),
        )
        self._assert_payload_is_sanitized(evidence_pack)
        self._assert_payload_is_sanitized(team_summary["csi_evidence_pack"])

    def test_evidence_pack_module_adds_no_network_hardware_or_capture_imports(self):
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
        path = REPO_ROOT / "somatic" / "sensors" / "csi_evidence_pack.py"
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

    def _assert_payload_is_sanitized(self, payload):
        self._assert_no_forbidden_keys(payload)
        self._assert_no_forbidden_words(payload)
        self._assert_no_absolute_paths(payload)

    def _assert_no_forbidden_keys(self, payload):
        if isinstance(payload, dict):
            for key, value in payload.items():
                with self.subTest(evidence_pack_key=key):
                    self.assertNotIn(str(key).lower(), FORBIDDEN_EVIDENCE_PACK_KEYS)
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
            lowered = (
                payload.lower()
                .replace(
                    "real-mode-authorization-missing",
                    "real-mode-gap-missing",
                )
                .replace("not-authorized", "not-runtime-status")
                .replace("authorization_status", "runtime_status")
                .replace(
                    "runtime_authorization_gap_ledger_contract_version",
                    "runtime_gap_ledger_contract_version",
                )
            )
            for word in FORBIDDEN_EVIDENCE_PACK_WORDS:
                with self.subTest(evidence_pack_forbidden_word=word):
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

    @staticmethod
    def _stable_json(payload):
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))

    @staticmethod
    def _read_json(path):
        return json.loads(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
