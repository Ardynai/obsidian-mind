import ast
import hashlib
import json
import unittest
from pathlib import Path

from somatic.reports.n_of_1_fabric_plan import (
    build_n_of_1_fabric_pack_plan,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


class NOf1FabricPackPlanTests(unittest.TestCase):
    def test_fixture_parse_and_preserves_planning_only_boundaries(self):
        payload = self._read_json(
            REPO_ROOT / "fixtures" / "reports" / "n-of-1-fabric-pack-plan-placeholder.json"
        )

        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["id"], "n-of-1-fabric-pack-plan-placeholder")
        self.assertEqual(payload["class"], "data")
        self.assertIn(payload["suggested_type"], ("document", "dataset"))
        self.assertTrue(payload["planning_only"])
        self.assertTrue(payload["private_only_by_default"])
        self.assertFalse(payload["publishing_enabled"])
        self.assertFalse(payload["signing_enabled"])
        self.assertFalse(payload["catalog_publication_enabled"])
        self.assertFalse(payload["transport_enabled"])
        self.assertFalse(payload["magnet_uri_created"])
        self.assertFalse(payload["webseed_created"])
        self.assertFalse(payload["contains_code"])
        self.assertFalse(payload["contains_executable_files"])
        self.assertFalse(payload["personal_health_data_exported"])
        self.assertFalse(payload["raw_real_health_data_allowed"])
        self.assertIn(
            "consent",
            " ".join(payload["future_real_packaging_requirements"]).lower(),
        )

    def test_build_plan_references_packet_and_reuses_artifact_hashes(self):
        report_packet = self._minimal_report_packet()

        plan = build_n_of_1_fabric_pack_plan(
            run_dir=Path("runs") / "run-n-of-1-test",
            report_packet=report_packet,
        ).to_dict()

        self.assertEqual(plan["id"], "n-of-1-fabric-pack-plan")
        self.assertEqual(plan["run_id"], "run-n-of-1-test")
        self.assertEqual(plan["report_packet_ref"], "artifacts/n_of_1_report_packet.json")
        self.assertEqual(plan["report_packet_id"], "n-of-1-report-packet")
        self.assertEqual(plan["report_packet_sha256"], self._payload_sha256(report_packet))
        self.assertEqual(plan["class"], "data")
        self.assertEqual(plan["suggested_type"], "document")
        self.assertFalse(plan["contains_code"])
        self.assertFalse(plan["contains_executable_files"])
        self.assertEqual(plan["executable_files"], [])
        self.assertFalse(plan["publishing_enabled"])
        self.assertFalse(plan["signing_enabled"])
        self.assertFalse(plan["catalog_publication_enabled"])
        self.assertFalse(plan["transport_enabled"])
        self.assertFalse(plan["magnet_uri_created"])
        self.assertFalse(plan["webseed_created"])
        self.assertTrue(plan["private_only_by_default"])
        self.assertFalse(plan["seedable"])
        self.assertFalse(plan["personal_health_data_exported"])
        self.assertFalse(plan["raw_real_health_data_allowed"])
        self.assertEqual(
            plan["artifact_hashes"],
            report_packet["artifact_hashes"],
        )
        generic_ref = plan["sensor_evidence_artifact_refs"]["csi_evidence_pack"]
        environment_ref = plan["sensor_evidence_artifact_refs"]["environment_evidence_pack"]
        self.assertEqual(
            plan["planned_sensor_evidence_artifact_ids"],
            ["csi_evidence_pack", "environment_evidence_pack"],
        )
        self.assertEqual(generic_ref["classification"], "compatible")
        self.assertEqual(generic_ref["artifact_ref"], "artifacts/csi_evidence_pack.json")
        self.assertEqual(
            generic_ref["sha256"], report_packet["artifact_hashes"]["csi_evidence_pack"]
        )
        self.assertFalse(generic_ref["raw_signal_values_exported"])
        self.assertEqual(environment_ref["classification"], "compatible")
        self.assertEqual(
            environment_ref["artifact_ref"],
            "artifacts/environment_evidence_pack.json",
        )
        self.assertEqual(
            environment_ref["sha256"],
            report_packet["artifact_hashes"]["environment_evidence_pack"],
        )

        file_plans = {item["id"]: item for item in plan["file_plans"]}
        self.assertEqual(tuple(file_plans), tuple(plan["planned_file_ids"]))
        self.assertIn("n_of_1_report_packet", file_plans)
        self.assertIn("sensor_stream_plan", file_plans)
        self.assertEqual(
            file_plans["n_of_1_report_packet"]["path"],
            "artifacts/n_of_1_report_packet.json",
        )
        self.assertEqual(
            file_plans["sensor_stream_plan"]["sha256"],
            report_packet["artifact_hashes"]["sensor_stream_plan"],
        )
        self.assertEqual(
            file_plans["sensor_stream_plan"]["source"],
            "report_packet.artifact_refs",
        )
        self._assert_no_plan_leaks(plan)

    def test_build_plan_is_deterministic_for_reordered_packet_refs(self):
        left_packet = self._minimal_report_packet()
        right_packet = self._minimal_report_packet()
        right_packet["artifact_refs"] = dict(reversed(list(right_packet["artifact_refs"].items())))
        right_packet["artifact_hashes"] = dict(
            reversed(list(right_packet["artifact_hashes"].items()))
        )

        left = build_n_of_1_fabric_pack_plan(
            run_dir=Path("runs") / "run-left",
            report_packet=left_packet,
        ).to_dict()
        right = build_n_of_1_fabric_pack_plan(
            run_dir=Path("runs") / "run-right",
            report_packet=right_packet,
        ).to_dict()

        for payload in (left, right):
            payload.pop("run_id", None)
            payload.pop("source_run_dir", None)
        self.assertEqual(left, right)

    def test_build_plan_fails_closed_for_unsafe_packet_artifact_refs(self):
        report_packet = self._minimal_report_packet()
        report_packet["artifact_refs"]["sensor_stream_plan"]["relative_path"] = str(
            REPO_ROOT / "private.json"
        )
        report_packet["artifact_refs"]["sensor_stream_plan"]["path_or_uri"] = (
            "fixture://sensors/private.json"
        )

        plan = build_n_of_1_fabric_pack_plan(
            run_dir=Path("runs") / "run-n-of-1-test",
            report_packet=report_packet,
        ).to_dict()

        file_plans = {item["id"]: item for item in plan["file_plans"]}
        unsafe_ref = file_plans["sensor_stream_plan"]
        self.assertEqual(unsafe_ref["path"], "")
        self.assertIsNone(unsafe_ref["sha256"])
        self.assertFalse(unsafe_ref["present"])
        self._assert_no_plan_leaks(plan)

    def test_fabric_plan_module_adds_no_network_hardware_database_publish_or_transport_surfaces(
        self,
    ):
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
            "supabase",
            "psycopg2",
            "asyncpg",
            "sqlite3",
            "sqlalchemy",
            "pymongo",
            "firebase_admin",
            "boto3",
            "azure",
            "google",
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
            "cv2",
            "mediapipe",
            "pyaudio",
            "sounddevice",
            "librosa",
            "numpy",
            "scipy",
            "pandas",
            "neurokit2",
            "apscheduler",
            "schedule",
            "celery",
            "rq",
            "redis",
            "twilio",
            "smtplib",
            "torrent",
            "libtorrent",
            "bencode",
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
            "run",
            "VideoCapture",
            "InputStream",
            "Microphone",
            "connect_db",
            "cursor",
            "schedule",
            "add_job",
            "send_notification",
            "notify",
            "remind",
            "start_monitoring",
            "prescribe",
        }
        path = REPO_ROOT / "somatic" / "reports" / "n_of_1_fabric_plan.py"
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

    @staticmethod
    def _minimal_report_packet():
        return {
            "schema_version": 1,
            "id": "n-of-1-report-packet",
            "run_id": "run-n-of-1-test",
            "workflow_mode": "n-of-1",
            "report_packet_ref": "artifacts/n_of_1_report_packet.json",
            "artifact_refs": {
                "sensor_stream_plan": {
                    "name": "sensor_stream_plan",
                    "relative_path": "artifacts/sensor_stream_plan.json",
                    "path_or_uri": "artifacts/sensor_stream_plan.json",
                    "sha256": "a" * 64,
                    "present": True,
                    "retention": "run",
                    "kind": "sensor-stream-plan",
                },
                "n_of_1_summary": {
                    "name": "n_of_1_summary",
                    "relative_path": "artifacts/n_of_1_summary.json",
                    "path_or_uri": "artifacts/n_of_1_summary.json",
                    "sha256": "b" * 64,
                    "present": True,
                    "retention": "run",
                    "kind": "report-packet-summary",
                },
                "csi_evidence_pack": {
                    "name": "csi_evidence_pack",
                    "relative_path": "artifacts/csi_evidence_pack.json",
                    "path_or_uri": "artifacts/csi_evidence_pack.json",
                    "sha256": "c" * 64,
                    "present": True,
                    "retention": "run",
                    "kind": "csi-evidence-pack",
                },
                "environment_evidence_pack": {
                    "name": "environment_evidence_pack",
                    "relative_path": "artifacts/environment_evidence_pack.json",
                    "path_or_uri": "artifacts/environment_evidence_pack.json",
                    "sha256": "d" * 64,
                    "present": True,
                    "retention": "run",
                    "kind": "environment-tabular-evidence-pack",
                },
            },
            "artifact_hashes": {
                "sensor_stream_plan": "a" * 64,
                "n_of_1_summary": "b" * 64,
                "csi_evidence_pack": "c" * 64,
                "environment_evidence_pack": "d" * 64,
            },
            "artifact_count": 4,
            "packet_complete": True,
        }

    @staticmethod
    def _payload_sha256(payload):
        encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def _read_json(path):
        return json.loads(Path(path).read_text(encoding="utf-8"))

    def _assert_no_plan_leaks(self, payload):
        encoded = (
            json.dumps(payload, sort_keys=True)
            .lower()
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
        for forbidden in (
            "fixture_refs",
            "sample-esp32-csi",
            "sample-amplitude-phase",
            "sample-csi-jsonl",
            "environment-parsed.csv",
            "environment-mixed.csv",
            "source_id",
            "source_ids",
            "private_ref",
            "private_refs",
            "unsafe_ref",
            "unsafe_refs",
            "source_path",
            "local_path",
            "staging_root",
            "provider_payload_body",
            "parser_report_body",
            "parser_summary_body",
            "api_key",
            "access_token",
            "refresh_token",
            "secret_value",
            "authorization",
            "bearer",
        ):
            with self.subTest(plan_leak=forbidden):
                self.assertNotIn(forbidden, encoded)


if __name__ == "__main__":
    unittest.main()
