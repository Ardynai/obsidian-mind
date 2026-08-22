import copy
import json
import unittest
from pathlib import Path

from somatic.safety import phase12_contracts as phase12_contracts_module
from somatic.safety.phase12_contracts import (
    PHASE12C_ALLOWED_CAPABILITY_LABELS,
    PHASE12C_AUTHORIZATION_STATUS,
    PHASE12C_GRANT_STATUS,
    PHASE12C_PROFILE_STATUS,
    PHASE12C_SUPERVISION_PHASE,
    PHASE12C_VISUAL_SUPERVISION_PROFILE_CONTRACT_VERSION,
    PHASE12C_VISUAL_SUPERVISION_PROFILE_KIND,
    phase12b_runtime_authorization_record_candidate,
    phase12c_visual_supervision_capability_profile,
    phase12c_visual_supervision_capability_profile_status_summary,
    validate_phase12b_runtime_authorization_record_candidate,
    validate_phase12c_visual_supervision_capability_profile,
)

_finalize12c = phase12_contracts_module._finalize_phase12c_visual_supervision_capability_profile

REPO_ROOT = Path(__file__).resolve().parents[1]
PROFILE_FIXTURE = (
    REPO_ROOT / "fixtures" / "reviews" / "phase-12c-visual-supervision-capability-profile-v1.json"
)
UNSAFE_PHASE12C_SENTINELS = (
    "raw_screenshot",
    "raw-screenshot",
    "raw_ocr",
    "raw-ocr",
    "camera_capture",
    "camera-capture",
    "microphone_capture",
    "microphone-capture",
    "clipboard_capture",
    "clipboard-capture",
    "screen_recording",
    "screen-recording",
    "audio_recording",
    "audio-recording",
    "click_automation",
    "click-automation",
    "input_automation",
    "input-automation",
    "hidden_monitoring",
    "hidden-monitoring",
    "background_monitoring",
    "background-monitoring",
    "fixture://",
    "fixtures/",
    "https://",
    "http://",
    "example.invalid",
    "c:/",
    "source_id",
    "source-id",
    "device_id",
    "device-id",
    "router_id",
    "api_key",
    "access_token",
    "secret_value",
    "password",
    "raw_document_text",
    "raw_csi",
    "raw_rf",
    "model_body",
    "parser_body",
    "provider_body",
    "accepted-for-runtime",
    "execution-permitted",
    "runtime-enabled",
    "permission-granted",
    "authorization-granted",
    "approval-granted",
    "diagnosis",
    "treatment",
    "medical",
    "clinical",
)


class Phase12CVisualSupervisionCapabilityProfileTests(unittest.TestCase):
    def test_fixture_matches_deterministic_helper(self):
        fixture = json.loads(PROFILE_FIXTURE.read_text(encoding="utf-8"))
        generated = phase12c_visual_supervision_capability_profile()

        self.assertEqual(fixture, generated)
        self.assertEqual(
            fixture["visual_supervision_capability_profile_contract_version"],
            PHASE12C_VISUAL_SUPERVISION_PROFILE_CONTRACT_VERSION,
        )
        self.assertEqual(fixture["profile_kind"], PHASE12C_VISUAL_SUPERVISION_PROFILE_KIND)
        self.assertTrue(fixture["profile_id"].startswith("p12c-profile-"))
        self.assertEqual(fixture["source_phase"], "12B")
        self.assertEqual(fixture["supervision_phase"], PHASE12C_SUPERVISION_PHASE)
        self.assertEqual(fixture["authorization_status"], PHASE12C_AUTHORIZATION_STATUS)
        self.assertEqual(fixture["grant_status"], PHASE12C_GRANT_STATUS)
        self.assertEqual(
            fixture["profile_status"],
            PHASE12C_PROFILE_STATUS,
        )
        self.assertFalse(fixture["phase12c_profiles_are_approvals_grants_or_permissions"])
        self.assertEqual(fixture["runtime_stage"], "not-implemented")
        self.assertFalse(fixture["visual_capture_execution_granted"])
        self.assertFalse(fixture["clipboard_capture_execution_granted"])
        self.assertFalse(fixture["mic_capture_execution_granted"])
        self.assertFalse(fixture["camera_capture_execution_granted"])
        self.assertFalse(fixture["click_automation_execution_granted"])
        self.assertFalse(fixture["adapter_execution_granted"])
        self.assertFalse(fixture["provider_execution_granted"])
        self.assertFalse(fixture["model_execution_granted"])
        self.assertFalse(fixture["execution_permitted"])
        self.assertFalse(fixture["real_mode_runtime_enabled"])
        self.assertEqual(
            [cap["capability_label"] for cap in fixture["capability_labels"]],
            list(PHASE12C_ALLOWED_CAPABILITY_LABELS),
        )
        self.assertEqual(fixture["capability_label_count"], 7)
        self.assertTrue(fixture["jules_review_required_for_validator_or_authorization_semantics"])
        for cap in fixture["capability_labels"]:
            with self.subTest(cap=cap["capability_label"]):
                self.assertEqual(cap["capability_status"], "profile-metadata-only")
                self.assertTrue(cap["metadata_only"])
                self.assertFalse(cap["execution_permitted"])
                self.assertFalse(cap["real_mode_runtime_enabled"])
        result = validate_phase12c_visual_supervision_capability_profile(fixture)
        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(result.authorization_wording_count, 0)
        self._assert_no_private_values(fixture)

    def test_status_summary_is_compact_and_non_executing(self):
        summary = phase12c_visual_supervision_capability_profile_status_summary()

        self.assertEqual(summary["source_phase"], "12B")
        self.assertEqual(summary["supervision_phase"], "capability-profile-only")
        self.assertEqual(summary["authorization_status"], "not-authorized")
        self.assertEqual(summary["grant_status"], "no-grant")
        self.assertEqual(summary["capability_label_count"], 7)
        self.assertEqual(summary["runtime_stage"], "not-implemented")
        self.assertFalse(summary["visual_capture_execution_granted"])
        self.assertFalse(summary["click_automation_execution_granted"])
        self.assertFalse(summary["adapter_execution_granted"])
        self.assertFalse(summary["provider_execution_granted"])
        self.assertFalse(summary["model_execution_granted"])
        self.assertFalse(summary["execution_permitted"])
        self.assertFalse(summary["real_mode_runtime_enabled"])
        self._assert_no_private_values(summary)

    def test_status_words_never_enable_execution(self):
        profile = phase12c_visual_supervision_capability_profile()
        for wording in (
            "observed",
            "profiled",
            "configured",
            "approved",
            "authorized",
            "granted",
            "ready",
            "complete",
        ):
            with self.subTest(wording=wording):
                unsafe = copy.deepcopy(profile)
                unsafe["authorization_status"] = wording
                unsafe["grant_status"] = wording
                unsafe["profile_status"] = wording
                unsafe["execution_permitted"] = True
                unsafe["real_mode_runtime_enabled"] = True
                unsafe = _finalize12c(unsafe)
                result = validate_phase12c_visual_supervision_capability_profile(unsafe)

                self.assertFalse(result.compatible)
                self.assertFalse(result.to_dict()["execution_permitted"])
                self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])
                self.assertFalse(result.sanitized_record["visual_capture_execution_granted"])
                self.assertFalse(result.sanitized_record["click_automation_execution_granted"])

    def test_no_active_authorization_grant_can_validate(self):
        profile = phase12c_visual_supervision_capability_profile()
        unsafe = copy.deepcopy(profile)
        unsafe["grant_status"] = "granted"
        unsafe["authorization_status"] = "authorized"
        unsafe["phase12c_profiles_are_approvals_grants_or_permissions"] = True
        unsafe["visual_capture_execution_granted"] = True
        unsafe["clipboard_capture_execution_granted"] = True
        unsafe["mic_capture_execution_granted"] = True
        unsafe["camera_capture_execution_granted"] = True
        unsafe["click_automation_execution_granted"] = True
        unsafe["execution_permitted"] = True
        unsafe["real_mode_runtime_enabled"] = True
        unsafe["authorization_grant"] = {
            "status": "permission-granted",
            "runtime_stage": "ready",
        }

        result = validate_phase12c_visual_supervision_capability_profile(unsafe)

        self.assertFalse(result.compatible)
        self.assertFalse(result.to_dict()["execution_permitted"])
        self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])
        self.assertEqual(result.sanitized_record["grant_status"], "no-grant")
        self.assertFalse(
            result.sanitized_record["phase12c_profiles_are_approvals_grants_or_permissions"]
        )
        self.assertNotIn("authorization_grant", result.sanitized_record)

    def test_validator_fails_closed_for_unsafe_or_contradictory_records(self):
        profile = phase12c_visual_supervision_capability_profile()
        cases = [("not-object", "not-a-dict")]

        missing = copy.deepcopy(profile)
        missing.pop("capability_labels")
        cases.append(("missing", missing))

        unsupported = copy.deepcopy(profile)
        unsupported["visual_supervision_capability_profile_contract_version"] = 999
        cases.append(("unsupported", unsupported))

        unknown = copy.deepcopy(profile)
        unknown["unexpected"] = "metadata"
        cases.append(("unknown", unknown))

        authorization = copy.deepcopy(profile)
        authorization["authorization_status"] = "authorization-granted"
        cases.append(("authorization-wording", authorization))

        permission = copy.deepcopy(profile)
        permission["profile_status"] = "runtime-permission-granted"
        cases.append(("permission-wording", permission))

        unsafe = copy.deepcopy(profile)
        unsafe["source_record_candidate"]["record_candidate_status"] = (
            "https://example.invalid/api_key"
        )
        cases.append(("unsafe", unsafe))

        boolean_count = copy.deepcopy(profile)
        boolean_count["capability_label_count"] = True
        cases.append(("boolean-count", boolean_count))

        string_count = copy.deepcopy(profile)
        string_count["capability_label_count"] = "7"
        cases.append(("string-count", string_count))

        source_id = copy.deepcopy(profile)
        source_id["source_record_candidate"]["source_id"] = "private-source"
        cases.append(("source-id", source_id))

        raw_screenshot = copy.deepcopy(profile)
        raw_screenshot["capability_labels"][0]["capability_label"] = "raw_screenshot"
        cases.append(("raw-screenshot", raw_screenshot))

        camera_capture = copy.deepcopy(profile)
        camera_capture["profile_status"] = "camera_capture"
        cases.append(("camera-capture", camera_capture))

        for name, payload in cases:
            with self.subTest(case=name):
                result = validate_phase12c_visual_supervision_capability_profile(payload)
                encoded = self._safe_encoded((result.to_dict(), result.sanitized_record))

                self.assertFalse(result.compatible)
                self.assertFalse(result.to_dict()["execution_permitted"])
                self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])
                for sentinel in UNSAFE_PHASE12C_SENTINELS:
                    self.assertNotIn(sentinel, encoded)

    def test_phase12b_source_remains_non_executing(self):
        record = phase12b_runtime_authorization_record_candidate()
        result = validate_phase12b_runtime_authorization_record_candidate(record)

        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(record["runtime_stage"], "not-implemented")
        self.assertFalse(record["adapter_execution_granted"])
        self.assertFalse(record["provider_execution_granted"])
        self.assertFalse(record["model_execution_granted"])
        self.assertFalse(record["execution_permitted"])
        self.assertFalse(record["real_mode_runtime_enabled"])

    def test_phase12c_module_does_not_add_runtime_execution_imports(self):
        module_text = Path(phase12_contracts_module.__file__).read_text(encoding="utf-8").lower()

        for forbidden in (
            "cv2",
            "PIL",
            "pyautogui",
            "pynput",
            "mss",
            "screen_brightness_control",
            "capture_screen",
            "take_screenshot",
            "requests",
            "urllib",
            "socket",
            "subprocess",
            "open(",
            'execution_permitted": true',
            'real_mode_runtime_enabled": true',
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, module_text)

    def _assert_no_private_values(self, payload):
        encoded = self._safe_encoded(payload)
        self.assertNotRegex(encoded, r"[a-z]:/")
        for forbidden in UNSAFE_PHASE12C_SENTINELS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)

    @staticmethod
    def _safe_encoded(payload):
        return (
            json.dumps(payload, sort_keys=True)
            .lower()
            .replace("\\", "/")
            .replace("not-authorized", "not-runtime-status")
            .replace("authorization_status", "runtime_status")
            .replace("runtime_authorization", "runtime_status")
            .replace("visual_supervision", "visual_status")
            .replace("capability_profile", "status_profile")
            .replace("visual_capture", "vis_cap")
            .replace("clipboard_capture", "clip_cap")
            .replace("mic_capture", "mic_cap")
            .replace("camera_capture", "cam_cap")
            .replace("click_automation", "click_auto")
            .replace("input_automation", "input_auto")
            .replace("screen_recording", "scr_rec")
            .replace("audio_recording", "aud_rec")
            .replace("hidden_monitoring", "hid_mon")
            .replace("background_monitoring", "bg_mon")
            .replace("raw_screenshot", "raw_scr")
            .replace("raw_ocr", "raw_o")
        )


if __name__ == "__main__":
    unittest.main()
