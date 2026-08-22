import ast
import json
import tempfile
import unittest
from pathlib import Path

from somatic.mock_runtime import run_mock_workflow
from somatic.sensors.toy_counter import (
    ToyCounterFixtureSensorProvider,
    evaluate_toy_counter_fixture_refs,
)
from somatic.sensors.toy_counter_evidence_pack import (
    TOY_COUNTER_EVIDENCE_PACK_CONTRACT_VERSION,
    TOY_COUNTER_EVIDENCE_PACK_EXPORTER_ID,
    classify_toy_counter_evidence_pack_compatibility,
    compute_toy_counter_evidence_pack_fingerprint,
    validate_toy_counter_evidence_pack_v1,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
TOY_WORKFLOW = REPO_ROOT / "examples" / "sensor-evidence-demo" / "toy-counter-fixture-workflow.yaml"
FORBIDDEN_TOY_WORDS = (
    "toy-counter-parsed.csv",
    "toy-counter-mixed.csv",
    "fixture://",
    "fixtures/",
    "raw_values",
    "samples",
    "payload",
    "source_id",
    "source_ids",
    "provider_payload",
    "provider_payload_body",
    "parser_report_body",
    "parser_summary_body",
    "api_key",
    "access_token",
    "refresh_token",
    "secret_value",
    "authorization",
    "bearer",
    "credential",
    "patient_id",
    "participant_id",
    "subject_id",
    "user_id",
    "email",
    "phone",
    "address",
    "location",
    "latitude",
    "longitude",
    "geolocation",
)
FORBIDDEN_TOY_KEYS = {
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


class ToyCounterEvidencePackTests(unittest.TestCase):
    def test_toy_counter_pack_is_deterministic_and_compatible(self):
        provider = ToyCounterFixtureSensorProvider()

        left = provider.evidence_pack(("toy-counter-parsed.csv",), repo_root=REPO_ROOT)
        right = provider.evidence_pack(("toy-counter-parsed.csv",), repo_root=REPO_ROOT)

        self.assertEqual(left, right)
        self.assertEqual(left["contract_version"], TOY_COUNTER_EVIDENCE_PACK_CONTRACT_VERSION)
        self.assertEqual(left["exporter_id"], TOY_COUNTER_EVIDENCE_PACK_EXPORTER_ID)
        self.assertEqual(left["provider_kind"], "toy-counter-fixture")
        self.assertEqual(left["evidence_kind"], "toy-counter-evidence-pack")
        self.assertEqual(left["status"], "parsed")
        self.assertEqual(left["readiness_status"], "ready-with-sanitized-metadata")
        self.assertEqual(left["counts"]["row_count"], 3)
        self.assertEqual(left["counts"]["parsed_row_count"], 3)
        self.assertEqual(left["scores"]["evidence_quality"], 93)
        self.assertFalse(left["raw_signal_values_exported"])
        self.assertFalse(left["personal_health_data_exported"])
        self.assertFalse(left["medical_or_clinical_claim"])
        self.assertFalse(left["diagnosis"])
        self.assertFalse(left["treatment_recommendation"])
        self.assertTrue(left["pack_id"].startswith("toy-counter-evidence-pack-"))
        self.assertEqual(
            compute_toy_counter_evidence_pack_fingerprint(left),
            left["pack_fingerprint"],
        )
        result = validate_toy_counter_evidence_pack_v1(left)
        self.assertEqual(result.classification, "compatible")
        self.assertTrue(result.fingerprint_verified)
        self._assert_toy_pack_sanitized(left)

    def test_toy_counter_mixed_fixture_is_partial_without_ranking_effect(self):
        pack = ToyCounterFixtureSensorProvider().evidence_pack(
            ("toy-counter-mixed.csv",),
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
        self._assert_toy_pack_sanitized(pack)

    def test_toy_counter_fails_closed_for_missing_and_unsafe_refs(self):
        for refs in (
            ("missing-toy-counter.csv",),
            ("../private.csv",),
            (str(REPO_ROOT / "fixtures" / "sensors" / "toy-counter" / "toy-counter-parsed.csv"),),
            ("fixture://sensors/toy-counter/toy-counter-parsed.csv",),
        ):
            with self.subTest(refs=refs):
                pack = ToyCounterFixtureSensorProvider().evidence_pack(
                    refs,
                    repo_root=REPO_ROOT,
                )
                self.assertEqual(pack["status"], "rejected")
                self.assertEqual(pack["readiness_status"], "rejected-fail-closed")
                self.assertEqual(pack["scores"]["evidence_quality"], 0)
                result = validate_toy_counter_evidence_pack_v1(pack)
                self.assertEqual(result.classification, "compatible")
                self._assert_toy_pack_sanitized(pack)

    def test_toy_counter_contract_rejects_malformed_unsupported_and_private_payloads(self):
        good = ToyCounterFixtureSensorProvider().evidence_pack(
            ("toy-counter-parsed.csv",),
            repo_root=REPO_ROOT,
        )

        non_object = classify_toy_counter_evidence_pack_compatibility(["not-a-pack"])
        self.assertEqual(non_object.classification, "malformed")
        self.assertEqual(non_object.readiness_status, "rejected-fail-closed")

        unsupported = dict(good)
        unsupported["contract_version"] = 2
        unsupported["evidence_contract_version"] = 2
        self._refresh(unsupported)
        self.assertEqual(
            validate_toy_counter_evidence_pack_v1(unsupported).classification,
            "unsupported_version",
        )

        stale = dict(good)
        stale["counts"] = dict(stale["counts"], row_count=4)
        result = validate_toy_counter_evidence_pack_v1(stale)
        self.assertEqual(result.classification, "incompatible")
        self.assertIn("invalid_fingerprint_or_pack_id", result.errors)

        private = dict(good)
        private["provider_payload_body"] = {"values": [1, 2, 3]}
        self._refresh(private)
        result = validate_toy_counter_evidence_pack_v1(private)
        self.assertEqual(result.classification, "incompatible")
        self.assertIn("privacy_boundary_violation", result.errors)

    def test_toy_counter_evaluation_does_not_echo_refs(self):
        evaluation = evaluate_toy_counter_fixture_refs(
            ("toy-counter-parsed.csv", "../private.csv"),
            repo_root=REPO_ROOT,
        )

        encoded = json.dumps(evaluation, sort_keys=True).lower()
        self.assertEqual(evaluation["status"], "partial")
        self.assertIn("unsafe-ref", evaluation["parse_error_categories"])
        self.assertNotIn("toy-counter-parsed.csv", encoded)
        self.assertNotIn("../private.csv", encoded)

    def test_toy_counter_example_run_writes_generic_refs_without_ranking_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = run_mock_workflow(
                TOY_WORKFLOW,
                repo_root=REPO_ROOT,
                output_root=Path(tmp),
                run_id="run-toy-counter-test",
            )

            manifest = self._read_json(run_dir / "manifest.json")
            team_summary = self._read_json(run_dir / "artifacts" / "team_orchestrator_summary.json")
            toy_pack = self._read_json(run_dir / "artifacts" / "toy_counter_evidence_pack.json")
            ranked = self._read_json(run_dir / "artifacts" / "ranked_hypotheses.json")
            elo = self._read_json(run_dir / "artifacts" / "elo_ratings.json")
            bracket = self._read_json(run_dir / "artifacts" / "tournament_bracket.json")

        self.assertEqual(toy_pack["status"], "parsed")
        self.assertFalse(toy_pack["ranking_input"])
        self.assertFalse(toy_pack["core_tournament_scores_modified"])
        self.assertFalse(toy_pack["tournament_rankings_modified"])
        self.assertIn("toy_counter_evidence_pack", manifest["artifacts"])
        self.assertEqual(
            manifest["artifacts"]["toy_counter_evidence_pack"],
            "artifacts/toy_counter_evidence_pack.json",
        )
        manifest_ref = manifest["sensor_evidence_artifact_refs"]["toy_counter_evidence_pack"]
        summary_ref = team_summary["sensor_evidence_artifact_refs"]["toy_counter_evidence_pack"]
        for ref in (manifest_ref, summary_ref):
            self.assertEqual(ref["classification"], "compatible")
            self.assertEqual(
                ref["artifact_ref"],
                "artifacts/toy_counter_evidence_pack.json",
            )
            self.assertEqual(ref["sha256"], manifest["hashes"]["toy_counter_evidence_pack"])
            self.assertEqual(ref["pack_fingerprint"], toy_pack["pack_fingerprint"])
        self.assertEqual(
            team_summary["toy_counter_evidence_pack"]["pack_fingerprint"],
            toy_pack["pack_fingerprint"],
        )
        self.assertEqual(
            team_summary["toy_counter_readiness_metadata"]["row_count"],
            3,
        )
        self.assertEqual(
            [item["rank"] for item in ranked],
            list(range(1, len(ranked) + 1)),
        )
        self.assertEqual(
            [item["final_score"] for item in ranked],
            sorted([item["final_score"] for item in ranked], reverse=True),
        )
        self.assertGreaterEqual(len(bracket["rounds"]), 1)
        self.assertEqual(
            [item["rating"] for item in elo["ratings"]],
            sorted([item["rating"] for item in elo["ratings"]], reverse=True),
        )
        self._assert_toy_pack_sanitized(toy_pack)
        self._assert_toy_pack_sanitized(team_summary["toy_counter_evidence_pack"])
        self._assert_toy_pack_sanitized(team_summary["toy_counter_readiness_metadata"])
        self._assert_toy_pack_sanitized(manifest_ref)

    def test_toy_counter_n_of_1_report_packet_and_fabric_plan_refs(self):
        from somatic.reports.n_of_1_fabric_plan import build_n_of_1_fabric_pack_plan
        from somatic.reports.n_of_1_packet import build_n_of_1_report_packet

        toy_pack = ToyCounterFixtureSensorProvider().evidence_pack(
            ("toy-counter-parsed.csv",),
            repo_root=REPO_ROOT,
        )
        artifact_payloads = {
            "sensor_stream_plan": {"schema_version": 1, "id": "sensor_stream_plan"},
            "sensor_observations": {"schema_version": 1, "id": "sensor_observations"},
            "sensor_feature_set": {"schema_version": 1, "id": "sensor_feature_set"},
            "csi_parser_report": {"schema_version": 1, "id": "csi_parser_report"},
            "csi_parsed_summary": {"schema_version": 1, "id": "csi_parsed_summary"},
            "csi_evidence_pack": {
                "schema_version": 1,
                "pack_id": "csi-evidence-pack-" + "a" * 16,
                "pack_fingerprint": "a" * 64,
                "status": "parsed",
                "readiness_status": "ready-with-sanitized-metadata",
            },
            "sensor_evidence_record": {"schema_version": 1, "id": "sensor_evidence_record"},
            "n_of_1_baseline_placeholder": {"schema_version": 1, "id": "baseline"},
            "personal_profile": {"schema_version": 1, "id": "personal_profile"},
            "baseline_graph": {"schema_version": 1, "id": "baseline_graph"},
            "baseline_comparison": {"schema_version": 1, "id": "baseline_comparison"},
            "intervention_tag": {"schema_version": 1, "id": "intervention_tag"},
            "intervention_context": {"schema_version": 1, "id": "intervention_context"},
            "response_evaluation_plan": {"schema_version": 1, "id": "response_plan"},
            "mock_intervention_ledger": {"schema_version": 1, "id": "ledger"},
            "follow_up_observation_window": {"schema_version": 1, "id": "follow_up_window"},
            "follow_up_sensor_snapshot": {"schema_version": 1, "id": "follow_up_snapshot"},
            "response_comparison": {"schema_version": 1, "id": "response_comparison"},
            "response_evaluation_summary": {"schema_version": 1, "id": "response_summary"},
            "n_of_1_summary": {"schema_version": 1, "id": "n_of_1_summary"},
            "toy_counter_evidence_pack": toy_pack,
        }
        packet = build_n_of_1_report_packet(
            run_id="run-toy-counter-nof1",
            workflow={"id": "toy-nof1", "mode": "n-of-1"},
            artifact_payloads=artifact_payloads,
            generated_at="run-toy-counter-nof1",
        ).to_dict()
        plan = build_n_of_1_fabric_pack_plan(
            run_dir=Path("runs") / "run-toy-counter-nof1",
            report_packet=packet,
            generated_at="run-toy-counter-nof1",
        ).to_dict()

        packet_ref = packet["sensor_evidence_artifact_refs"]["toy_counter_evidence_pack"]
        plan_ref = plan["sensor_evidence_artifact_refs"]["toy_counter_evidence_pack"]
        self.assertEqual(packet_ref["classification"], "compatible")
        self.assertEqual(plan_ref["classification"], "compatible")
        self.assertEqual(
            packet_ref["artifact_ref"],
            "artifacts/toy_counter_evidence_pack.json",
        )
        self.assertEqual(
            plan_ref["artifact_ref"],
            "artifacts/toy_counter_evidence_pack.json",
        )
        self.assertEqual(
            plan_ref["sha256"],
            packet["artifact_hashes"]["toy_counter_evidence_pack"],
        )
        self.assertIn(
            "toy_counter_evidence_pack",
            plan["planned_sensor_evidence_artifact_ids"],
        )
        file_plan = {item["id"]: item for item in plan["file_plans"]}["toy_counter_evidence_pack"]
        self.assertEqual(
            file_plan["path"],
            "artifacts/toy_counter_evidence_pack.json",
        )
        self._assert_toy_pack_sanitized(packet_ref)
        self._assert_toy_pack_sanitized(plan_ref)
        self._assert_toy_pack_sanitized(file_plan)

    def test_toy_counter_modules_add_no_network_hardware_or_capture_imports(self):
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
            REPO_ROOT / "somatic" / "sensors" / "toy_counter.py",
            REPO_ROOT / "somatic" / "sensors" / "toy_counter_evidence_pack.py",
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

    def _assert_toy_pack_sanitized(self, payload):
        self._assert_no_forbidden_toy_keys(payload)
        encoded = (
            json.dumps(payload, sort_keys=True)
            .lower()
            .replace(
                "real-mode-authorization-missing",
                "real-mode-gap-missing",
            )
        )
        for forbidden in FORBIDDEN_TOY_WORDS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)
        self._assert_no_absolute_paths(payload)

    def _assert_no_forbidden_toy_keys(self, payload):
        if isinstance(payload, dict):
            for key, value in payload.items():
                with self.subTest(key=key):
                    self.assertNotIn(str(key).lower(), FORBIDDEN_TOY_KEYS)
                self._assert_no_forbidden_toy_keys(value)
        elif isinstance(payload, list):
            for item in payload:
                self._assert_no_forbidden_toy_keys(item)

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
        fingerprint = compute_toy_counter_evidence_pack_fingerprint(payload)
        payload["pack_fingerprint"] = fingerprint
        payload["pack_id"] = f"toy-counter-evidence-pack-{fingerprint[:16]}"

    @staticmethod
    def _read_json(path):
        return json.loads(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
