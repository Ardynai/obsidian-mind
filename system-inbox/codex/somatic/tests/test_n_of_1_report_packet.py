import ast
import hashlib
import json
import unittest
from pathlib import Path

from somatic.reports.n_of_1_packet import (
    EXPECTED_N_OF_1_PACKET_ARTIFACTS,
    build_n_of_1_report_packet,
    collect_n_of_1_artifact_refs,
    collect_n_of_1_sensor_evidence_artifact_refs,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


class NOf1ReportPacketTests(unittest.TestCase):
    def test_packet_fixture_parse_and_preserves_closed_safety_boundaries(self):
        payload = self._read_json(
            REPO_ROOT / "fixtures" / "reports" / "n-of-1-report-packet-placeholder.json"
        )

        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["id"], "n-of-1-report-packet-placeholder")
        self.assertTrue(payload["mock"])
        self.assertTrue(payload["offline"])
        self.assertTrue(payload["research_only"])
        self.assertTrue(payload["sandbox_only"])
        self.assertTrue(payload["fake_backed"])
        self.assertFalse(payload["medical_record"])
        self.assertFalse(payload["advice_generated"])
        self.assertFalse(payload["effectiveness_claim"])
        self.assertFalse(payload["real_monitoring"])
        self.assertFalse(payload["real_scheduling"])

        flags = payload["safety_boundary_flags"]
        for flag in (
            "fake_backed",
            "no_hardware",
            "no_real_health_data",
            "no_diagnosis",
            "no_treatment",
            "no_recommendation",
            "no_prescription",
            "no_emergency_triage",
            "no_effectiveness_claim",
            "no_monitoring",
            "no_scheduling",
        ):
            with self.subTest(flag=flag):
                self.assertTrue(flags[flag])

    def test_collect_artifact_refs_is_deterministic_and_hashes_payloads(self):
        payloads = {
            "sensor_stream_plan": {"schema_version": 1, "id": "plan"},
            "sensor_observations": {"schema_version": 1, "id": "observations"},
            "sensor_feature_set": {"schema_version": 1, "id": "feature-set"},
        }

        left = collect_n_of_1_artifact_refs(payloads)
        right = collect_n_of_1_artifact_refs(dict(reversed(list(payloads.items()))))

        self.assertEqual(left, right)
        refs = {ref.name: ref.to_dict() for ref in left}
        self.assertEqual(tuple(refs), EXPECTED_N_OF_1_PACKET_ARTIFACTS)
        self.assertTrue(refs["sensor_stream_plan"]["present"])
        self.assertEqual(
            refs["sensor_stream_plan"]["relative_path"],
            "artifacts/sensor_stream_plan.json",
        )
        self.assertEqual(
            refs["sensor_stream_plan"]["sha256"],
            self._payload_sha256(payloads["sensor_stream_plan"]),
        )

        missing_ref = refs["baseline_graph"]
        self.assertFalse(missing_ref["present"])
        self.assertIsNone(missing_ref["sha256"])
        self.assertEqual(
            missing_ref["missing_reason"],
            "missing-required-n-of-1-artifact",
        )

    def test_build_packet_summarizes_loop_and_fails_closed_for_missing_artifacts(self):
        workflow = {"id": "valid-n-of-1", "mode": "n-of-1"}
        payloads = {
            "sensor_stream_plan": {"schema_version": 1, "id": "plan"},
            "sensor_observations": {
                "schema_version": 1,
                "id": "observations",
                "observations": [{}, {}, {}],
            },
            "sensor_feature_set": {"schema_version": 1, "id": "feature-set"},
            "n_of_1_summary": {
                "schema_version": 1,
                "id": "summary",
                "baseline_comparison_summary": {"status_counts": {}},
                "intervention_summary": {"category": "rest_placeholder"},
                "response_trend_summary": {
                    "trend_counts": {
                        "toward_baseline": 1,
                        "away_from_baseline": 0,
                        "unchanged": 5,
                        "insufficient_data": 1,
                    }
                },
            },
        }

        packet = build_n_of_1_report_packet(
            run_id="run-packet-test",
            workflow=workflow,
            artifact_payloads=payloads,
            generated_at="run-packet-test",
        ).to_dict()

        self.assertEqual(packet["id"], "n-of-1-report-packet")
        self.assertEqual(packet["run_id"], "run-packet-test")
        self.assertEqual(packet["workflow_mode"], "n-of-1")
        self.assertEqual(packet["generated_at"], "run-packet-test")
        self.assertEqual(packet["artifact_count"], len(EXPECTED_N_OF_1_PACKET_ARTIFACTS))
        self.assertFalse(packet["packet_complete"])
        self.assertEqual(packet["packet_status"], "missing-required-artifacts")
        self.assertIn("baseline_graph", packet["missing_artifacts"])
        self.assertEqual(packet["artifact_hashes"]["baseline_graph"], None)
        self.assertEqual(
            packet["artifact_hashes"]["sensor_stream_plan"],
            self._payload_sha256(payloads["sensor_stream_plan"]),
        )
        self.assertEqual(
            [stage["stage"] for stage in packet["loop_stages"]],
            [
                "observation",
                "baseline",
                "intervention_tag",
                "follow_up",
                "response_comparison",
            ],
        )
        self.assertTrue(packet["safety_boundary_flags"]["no_effectiveness_claim"])
        self.assertFalse(packet["medical_record"])
        self.assertIn("not a medical record", " ".join(packet["limitations"]).lower())

    def test_build_packet_adds_optional_environment_evidence_ref_without_completeness_change(self):
        workflow = {"id": "valid-n-of-1", "mode": "n-of-1"}
        payloads = {
            "sensor_stream_plan": {"schema_version": 1, "id": "plan"},
            "environment_evidence_pack": {
                "schema_version": 1,
                "id": "environment-sanitized-evidence-pack",
                "provider_kind": "environment-fixture",
                "evidence_kind": "environment-tabular-evidence-pack",
                "pack_id": "environment-evidence-pack-" + "a" * 16,
                "pack_fingerprint": "a" * 64,
                "status": "parsed",
                "readiness_status": "ready-with-sanitized-metadata",
            },
        }

        packet = build_n_of_1_report_packet(
            run_id="run-packet-test",
            workflow=workflow,
            artifact_payloads=payloads,
            generated_at="run-packet-test",
        ).to_dict()

        self.assertFalse(packet["packet_complete"])
        self.assertIn("baseline_graph", packet["missing_artifacts"])
        self.assertIn("environment_evidence_pack", packet["artifact_refs"])
        self.assertIn("environment_evidence_pack", packet["artifact_hashes"])
        self.assertEqual(
            packet["artifact_refs"]["environment_evidence_pack"]["relative_path"],
            "artifacts/environment_evidence_pack.json",
        )
        generic_ref = packet["sensor_evidence_artifact_refs"]["environment_evidence_pack"]
        self.assertEqual(generic_ref["classification"], "compatible")
        self.assertEqual(generic_ref["provider_kind"], "environment-fixture")
        self.assertEqual(
            generic_ref["artifact_ref"],
            "artifacts/environment_evidence_pack.json",
        )

        direct_refs = collect_n_of_1_sensor_evidence_artifact_refs(payloads)
        self.assertEqual(
            direct_refs["environment_evidence_pack"]["classification"],
            "compatible",
        )
        self.assertEqual(
            direct_refs["environment_evidence_pack"]["sha256"],
            packet["artifact_hashes"]["environment_evidence_pack"],
        )

    def test_report_packet_module_adds_no_network_hardware_database_or_scheduling_imports(self):
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
            "VideoCapture",
            "InputStream",
            "Microphone",
            "connect_db",
            "execute",
            "cursor",
            "schedule",
            "add_job",
            "send_notification",
            "notify",
            "remind",
            "start_monitoring",
            "prescribe",
        }
        path = REPO_ROOT / "somatic" / "reports" / "n_of_1_packet.py"
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
    def _payload_sha256(payload):
        encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def _read_json(path):
        return json.loads(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
