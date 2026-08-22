import ast
import json
import unittest
from pathlib import Path

from somatic.providers.sensors import (
    SENSOR_MODALITIES,
    SensorFeatureSet,
    SensorObservation,
    SensorPrivacyPolicy,
    SensorStreamPlan,
)
from somatic.sensors import SandboxSensorProvider
from somatic.sensors.csi import (
    CSI_FAKE_FEATURES,
    build_csi_capture_plan,
    build_csi_feature_plan,
    build_csi_feature_set,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CSI_REPLAY_FIXTURE_REFS = (
    "sample-esp32-csi.csv",
    "sample-amplitude-phase.csv",
    "sample-csi-jsonl.jsonl",
)
FORBIDDEN_CSI_REPLAY_KEYS = {
    "samples",
    "raw_values",
    "real",
    "imag",
    "amplitude",
    "phase",
    "rssi",
    "source_id",
    "source_ids",
}
FORBIDDEN_CSI_REPLAY_WORDS = (
    "raw_values",
    "samples",
    "imag",
    "amplitude",
    "rssi",
    "source_id",
    "source_ids",
)


class SensorProviderScaffoldTests(unittest.TestCase):
    def test_sensor_provider_modules_import_without_optional_dependencies(self):
        for module_name in (
            "somatic.providers.sensors",
            "somatic.sensors",
            "somatic.sensors.common",
            "somatic.sensors.csi",
            "somatic.sensors.csi_batch",
            "somatic.sensors.sandbox",
            "somatic.sensors.video_processor",
            "somatic.sensors.live_consent",
        ):
            with self.subTest(module_name=module_name):
                __import__(module_name)

        self.assertEqual(
            SENSOR_MODALITIES,
            {
                "csi",
                "video",
                "video3d",
                "thermal",
                "audio",
                "wearable",
                "environmental",
            },
        )

    def test_dataclasses_preserve_privacy_and_modality_boundaries(self):
        policy = SensorPrivacyPolicy(id="policy-test")
        plan = SensorStreamPlan(
            id="plan-test",
            provider_id="sandbox-sensor-provider",
            workflow_id="workflow-test",
            mode="n-of-1",
            modalities=("csi", "audio", "environmental"),
            requested_features=("respiratory_rate",),
            observation_window="placeholder",
            baseline_ref="artifacts/n_of_1_baseline_placeholder.json",
            privacy_policy=policy,
        )
        observation = SensorObservation(
            id="observation-test",
            stream_plan_id=plan.id,
            modality="audio",
            observed_at="placeholder",
            feature_name="audio_event_placeholder",
            value="none-observed-placeholder",
        )
        feature_set = SensorFeatureSet(
            id="feature-set-test",
            stream_plan_id=plan.id,
            provider_id="sandbox-sensor-provider",
            features={"audio_event_placeholder": "none-observed-placeholder"},
            source_observation_ids=(observation.id,),
        )

        self.assertTrue(policy.local_first)
        self.assertFalse(policy.raw_data_leaves_machine)
        self.assertFalse(plan.hardware_access)
        self.assertFalse(plan.network_calls)
        self.assertFalse(observation.hardware_access)
        self.assertFalse(feature_set.real_monitoring)
        self.assertIn("no emergency triage", feature_set.limitations)

    def test_rejects_unknown_sensor_modality(self):
        policy = SensorPrivacyPolicy(id="policy-test")
        with self.assertRaises(ValueError):
            SensorStreamPlan(
                id="plan-test",
                provider_id="sandbox-sensor-provider",
                workflow_id="workflow-test",
                mode="n-of-1",
                modalities=("unsupported",),
                requested_features=("respiratory_rate",),
                observation_window="placeholder",
                baseline_ref="artifacts/n_of_1_baseline_placeholder.json",
                privacy_policy=policy,
            )

        with self.assertRaises(ValueError):
            SensorObservation(
                id="observation-test",
                stream_plan_id="plan-test",
                modality="unsupported",
                observed_at="placeholder",
                feature_name="bad",
                value="bad",
            )

    def test_sandbox_provider_observations_are_deterministic_and_fake_backed(self):
        provider = SandboxSensorProvider()
        workflow = {"id": "valid-n-of-1", "mode": "n-of-1"}
        left_plan = provider.plan_stream(workflow)
        right_plan = provider.plan_stream(workflow)
        left_observations = provider.observations(left_plan)
        right_observations = provider.observations(right_plan)
        left_features = provider.features(left_plan, left_observations)
        right_features = provider.features(right_plan, right_observations)

        self.assertEqual(left_plan.to_dict(), right_plan.to_dict())
        self.assertEqual(
            [observation.to_dict() for observation in left_observations],
            [observation.to_dict() for observation in right_observations],
        )
        self.assertEqual(left_features.to_dict(), right_features.to_dict())
        self.assertEqual(left_features.features["respiratory_rate"], 14)
        self.assertEqual(left_features.features["movement_score"], 0.18)
        self.assertEqual(left_features.features["posture_state"], "upright-placeholder")
        self.assertEqual(left_features.features["sleep_state_estimate"], "awake-placeholder")
        self.assertEqual(
            left_features.features["audio_event_placeholder"],
            "none-observed-placeholder",
        )
        self.assertEqual(
            left_features.features["environmental_context_placeholder"],
            "room-context-placeholder",
        )
        self.assertIn("csi", left_features.metadata)
        self.assertTrue(left_features.metadata["csi"]["planning_only"])
        self.assertFalse(left_features.metadata["csi"]["feature_set"]["hardware_access"])
        self.assertEqual(
            left_features.metadata["csi"]["feature_set"]["features"]["motion_score"],
            0.18,
        )
        for observation in left_observations:
            self.assertTrue(observation.simulated)
            self.assertTrue(observation.offline)
            self.assertFalse(observation.hardware_access)
            self.assertFalse(observation.clinical_interpretation)
            self.assertFalse(observation.emergency_triage)

    def test_sensor_fixtures_are_fake_backed_offline_and_local_only(self):
        fixture_paths = (
            REPO_ROOT / "fixtures" / "sensors" / "sandbox-sensor-provider-placeholder.json",
            REPO_ROOT / "fixtures" / "sensors" / "sensor-privacy-policy-placeholder.json",
            REPO_ROOT / "fixtures" / "sensors" / "n-of-1-baseline-placeholder.json",
            REPO_ROOT / "fixtures" / "sensors" / "sensor-feature-set-placeholder.json",
        )
        for path in fixture_paths:
            with self.subTest(path=path.name):
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(payload["schema_version"], 1)
                self.assertTrue(payload["mock"])
                self.assertTrue(payload["offline"])
                self.assertTrue(payload["research_only"])

        provider = json.loads(
            (
                REPO_ROOT / "fixtures" / "sensors" / "sandbox-sensor-provider-placeholder.json"
            ).read_text(encoding="utf-8")
        )
        self.assertTrue(provider["fake_backed"])
        self.assertFalse(provider["limits"]["live_sensor_access_allowed"])
        self.assertFalse(provider["limits"]["hardware_access_allowed"])
        self.assertFalse(provider["limits"]["network_calls_allowed"])
        self.assertFalse(provider["limits"]["packet_capture_allowed"])
        self.assertFalse(provider["limits"]["wifi_network_probing_allowed"])
        self.assertFalse(provider["limits"]["monitor_mode_allowed"])
        self.assertFalse(provider["limits"]["driver_access_allowed"])
        self.assertFalse(provider["limits"]["real_monitoring_allowed"])
        self.assertFalse(provider["limits"]["diagnosis_treatment_allowed"])

    def test_csi_helpers_are_deterministic_and_planning_only(self):
        workflow = {"id": "valid-n-of-1", "mode": "n-of-1"}
        left_capture_plan = build_csi_capture_plan(workflow)
        right_capture_plan = build_csi_capture_plan(workflow)
        left_feature_plan = build_csi_feature_plan(left_capture_plan)
        right_feature_plan = build_csi_feature_plan(right_capture_plan)
        left_feature_set = build_csi_feature_set(left_capture_plan, left_feature_plan)
        right_feature_set = build_csi_feature_set(right_capture_plan, right_feature_plan)

        self.assertEqual(left_capture_plan.to_dict(), right_capture_plan.to_dict())
        self.assertEqual(left_feature_plan.to_dict(), right_feature_plan.to_dict())
        self.assertEqual(left_feature_set.to_dict(), right_feature_set.to_dict())
        self.assertEqual(left_feature_set.features, CSI_FAKE_FEATURES)
        self.assertEqual(left_feature_set.features["respiratory_rate"], 14)
        self.assertFalse(left_capture_plan.hardware_access)
        self.assertFalse(left_capture_plan.packet_capture)
        self.assertFalse(left_capture_plan.wifi_network_probing)
        self.assertFalse(left_capture_plan.monitor_mode)
        self.assertFalse(left_capture_plan.network_calls)
        self.assertFalse(left_capture_plan.raw_rf_data_collected)
        self.assertFalse(left_capture_plan.raw_csi_data_collected)
        self.assertTrue(left_feature_set.fake_backed)
        self.assertFalse(left_feature_set.clinical_interpretation)

    def test_csi_fixture_replay_provider_is_deterministic_and_sanitized(self):
        provider = SandboxSensorProvider()

        left = provider.replay_csi_fixtures(CSI_REPLAY_FIXTURE_REFS, repo_root=REPO_ROOT)
        right = provider.replay_csi_fixtures(CSI_REPLAY_FIXTURE_REFS, repo_root=REPO_ROOT)

        self.assertEqual(left, right)
        self.assertEqual(left["schema_version"], 1)
        self.assertEqual(left["id"], "csi-fixture-replay-provider-output")
        self.assertEqual(left["provider_id"], "sandbox-sensor-provider")
        self.assertEqual(left["mode"], "fixture-replay")
        self.assertEqual(left["status"], "parsed")
        self.assertEqual(left["fixture_count"], 3)
        self.assertEqual(left["frame_count"], 6)
        self.assertEqual(left["sample_count"], 14)
        self.assertEqual(left["csi_evidence_scoring"]["status"], "parsed")
        self.assertEqual(left["csi_evidence_scoring"]["score"], 100)
        self.assertEqual(left["csi_evidence_scoring"]["evidence_quality"], 100)
        self.assertEqual(left["report"]["csi_evidence_scoring"], left["csi_evidence_scoring"])
        self.assertEqual(left["summary"]["csi_evidence_scoring"], left["csi_evidence_scoring"])
        self.assertTrue(left["fixture_only"])
        self.assertTrue(left["summary_output_only"])
        self.assertFalse(left["hardware_access"])
        self.assertFalse(left["network_calls"])
        self.assertFalse(left["raw_signal_values_exported"])
        self.assertEqual(left["report"]["status"], "parsed")
        self.assertEqual(left["summary"]["status"], "parsed")
        self.assertEqual(
            left["report"]["replay_provider"]["mode"],
            "fixture-replay",
        )
        self._assert_csi_replay_payload_is_sanitized(left)

    def test_csi_fixture_replay_provider_keeps_mixed_fixture_partial(self):
        provider = SandboxSensorProvider()

        replay = provider.replay_csi_fixtures(
            ("sample-esp32-csi.csv", "mixed-valid-invalid-csi.csv"),
            repo_root=REPO_ROOT,
        )

        self.assertEqual(replay["status"], "partial")
        self.assertEqual(replay["report"]["status"], "partial")
        self.assertEqual(replay["summary"]["status"], "partial")
        self.assertGreater(replay["frame_count"], 0)
        self.assertGreater(replay["malformed_rows"], 0)
        self.assertEqual(replay["csi_evidence_scoring"]["status"], "partial")
        self.assertGreater(replay["csi_evidence_scoring"]["score"], 0)
        self.assertLess(replay["csi_evidence_scoring"]["score"], 100)
        self._assert_csi_replay_payload_is_sanitized(replay)

    def test_csi_fixture_replay_provider_rejects_unsupported_fixtures_safely(self):
        provider = SandboxSensorProvider()

        replay = provider.replay_csi_fixtures(("unsupported-csi.npz",), repo_root=REPO_ROOT)

        self.assertEqual(replay["status"], "rejected")
        self.assertEqual(replay["frame_count"], 0)
        self.assertEqual(replay["sample_count"], 0)
        self.assertEqual(
            replay["report"]["parse_errors"][0]["code"],
            "unsupported_extension",
        )
        self.assertEqual(replay["csi_evidence_scoring"]["status"], "rejected")
        self.assertEqual(replay["csi_evidence_scoring"]["score"], 0)
        self._assert_csi_replay_payload_is_sanitized(replay)

    def test_csi_fixture_replay_provider_sanitizes_missing_fixture_errors(self):
        provider = SandboxSensorProvider()

        replay = provider.replay_csi_fixtures(
            ("missing-csi-fixture.csv",),
            repo_root=REPO_ROOT,
        )

        self.assertEqual(replay["status"], "rejected")
        self.assertEqual(replay["report"]["parse_errors"][0]["code"], "fixture_missing")
        self.assertEqual(
            replay["report"]["fixtures"][0]["path"],
            "fixtures/sensors/csi/missing-csi-fixture.csv",
        )
        self._assert_csi_replay_payload_is_sanitized(replay)

    def test_csi_fixture_replay_provider_sanitizes_unsafe_rejected_refs(self):
        provider = SandboxSensorProvider()
        refs = (
            str(REPO_ROOT / "fixtures" / "sensors" / "csi" / "sample-esp32-csi.csv"),
            "https://example.invalid/csi-fixture.csv",
        )

        replay = provider.replay_csi_fixtures(refs, repo_root=REPO_ROOT)

        self.assertEqual(replay["status"], "rejected")
        self.assertEqual(replay["fixture_refs"], ["csi-fixture-001.csv", "csi-fixture-002.csv"])
        self.assertEqual(
            [error["code"] for error in replay["report"]["parse_errors"]],
            ["unsafe_fixture_ref", "unsafe_fixture_ref"],
        )
        self._assert_csi_replay_payload_is_sanitized(replay)

    def test_csi_fixture_replay_provider_rejects_unreadable_text_safely(self):
        provider = SandboxSensorProvider()

        replay = provider.replay_csi_fixtures(("invalid-utf8-csi.csv",), repo_root=REPO_ROOT)

        self.assertEqual(replay["status"], "rejected")
        self.assertEqual(replay["report"]["parse_errors"][0]["code"], "fixture_read_failed")
        self.assertIn("could not be read", replay["report"]["errors"][0])
        self.assertEqual(replay["csi_evidence_scoring"]["status"], "rejected")
        self.assertEqual(replay["csi_evidence_scoring"]["score"], 0)
        self._assert_csi_replay_payload_is_sanitized(replay)

    def test_sensor_scaffold_adds_no_network_or_hardware_import_surfaces(self):
        forbidden_import_roots = {
            "requests",
            "urllib",
            "http",
            "socket",
            "scapy",
            "pyshark",
            "pcapy",
            "dpkt",
            "wifi",
            "cv2",
            "mediapipe",
            "pyaudio",
            "sounddevice",
            "librosa",
            "bleak",
            "bluetooth",
            "serial",
            "usb",
            "pyusb",
            "numpy",
            "scipy",
            "neurokit2",
        }
        forbidden_call_names = {
            "urlopen",
            "urlretrieve",
            "request",
            "create_connection",
            "sniff",
            "pcap",
            "set_monitor_mode",
            "VideoCapture",
            "InputStream",
            "Microphone",
            "open",
            "scan",
            "connect",
            "download",
        }
        for path in (
            REPO_ROOT / "somatic" / "providers" / "sensors.py",
            REPO_ROOT / "somatic" / "sensors" / "common.py",
            REPO_ROOT / "somatic" / "sensors" / "csi.py",
            REPO_ROOT / "somatic" / "sensors" / "csi_batch.py",
            REPO_ROOT / "somatic" / "sensors" / "csi_scoring.py",
            REPO_ROOT / "somatic" / "sensors" / "sandbox.py",
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

    def _assert_csi_replay_payload_is_sanitized(self, payload):
        self._assert_no_forbidden_csi_replay_keys(payload)
        self._assert_no_forbidden_csi_replay_words(payload)
        self._assert_no_absolute_paths(payload)

    def _assert_no_forbidden_csi_replay_keys(self, payload):
        if isinstance(payload, dict):
            for key, value in payload.items():
                with self.subTest(csi_replay_key=key):
                    self.assertNotIn(str(key).lower(), FORBIDDEN_CSI_REPLAY_KEYS)
                self._assert_no_forbidden_csi_replay_keys(value)
        elif isinstance(payload, list):
            for item in payload:
                self._assert_no_forbidden_csi_replay_keys(item)

    def _assert_no_forbidden_csi_replay_words(self, payload):
        if isinstance(payload, dict):
            for value in payload.values():
                self._assert_no_forbidden_csi_replay_words(value)
        elif isinstance(payload, list):
            for item in payload:
                self._assert_no_forbidden_csi_replay_words(item)
        elif isinstance(payload, str):
            lowered = payload.lower()
            for word in FORBIDDEN_CSI_REPLAY_WORDS:
                with self.subTest(csi_replay_forbidden_word=word):
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
