import copy
import json
import unittest
from pathlib import Path

from somatic.safety import phase12_contracts as phase12_contracts_module
from somatic.safety.phase12_contracts import (
    PHASE12D_AUTHORIZATION_STATUS,
    PHASE12D_CAPABILITY_CATEGORIES,
    PHASE12D_CONSENT_GATE_PROFILE_CONTRACT_VERSION,
    PHASE12D_CONSENT_GATE_PROFILE_KIND,
    PHASE12D_CONSENT_GATE_STATUS,
    PHASE12D_CONSENT_PHASE,
    PHASE12D_GRANT_STATUS,
    PHASE12D_REQUIRED_FUTURE_GATES,
    phase12a_runtime_authorization_design_charter,
    phase12b_runtime_authorization_record_candidate,
    phase12c_visual_supervision_capability_profile,
    phase12d_visual_desktop_consent_gate_requirements,
    phase12d_visual_desktop_consent_gate_requirements_status_summary,
    validate_phase12a_runtime_authorization_design_charter,
    validate_phase12b_runtime_authorization_record_candidate,
    validate_phase12c_visual_supervision_capability_profile,
    validate_phase12d_visual_desktop_consent_gate_requirements,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PROFILE_FIXTURE = (
    REPO_ROOT
    / "fixtures"
    / "reviews"
    / "phase-12d-visual-desktop-consent-gate-requirements-v1.json"
)
UNSAFE_PHASE12D_SENTINELS = (
    "raw_screenshot",
    "raw-screenshot",
    "raw_ocr",
    "raw-ocr",
    "raw_clipboard_text",
    "raw-clipboard-text",
    "screenshot_payload",
    "ocr_payload",
    "camera_payload",
    "microphone_payload",
    "audio_payload",
    "recording_payload",
    "raw_recording_payload",
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
    "consent-granted",
    "diagnosis",
    "treatment",
    "medical",
    "clinical",
)


class Phase12DVisualDesktopConsentGateRequirementsTests(unittest.TestCase):
    def test_fixture_matches_deterministic_helper(self):
        fixture = json.loads(PROFILE_FIXTURE.read_text(encoding="utf-8"))
        generated = phase12d_visual_desktop_consent_gate_requirements()

        self.assertEqual(fixture, generated)
        self.assertEqual(
            fixture["consent_gate_profile_contract_version"],
            PHASE12D_CONSENT_GATE_PROFILE_CONTRACT_VERSION,
        )
        self.assertEqual(fixture["profile_kind"], PHASE12D_CONSENT_GATE_PROFILE_KIND)
        self.assertTrue(fixture["consent_gate_profile_id"].startswith("p12d-consent-profile-"))
        self.assertEqual(fixture["source_phase_range"], "12A-12C")
        self.assertEqual(fixture["consent_phase"], PHASE12D_CONSENT_PHASE)
        self.assertEqual(fixture["authorization_status"], PHASE12D_AUTHORIZATION_STATUS)
        self.assertEqual(fixture["grant_status"], PHASE12D_GRANT_STATUS)
        self.assertEqual(fixture["consent_gate_status"], PHASE12D_CONSENT_GATE_STATUS)
        self.assertFalse(fixture["phase12d_satisfies_consent_gates"])
        self.assertFalse(fixture["phase12d_profiles_are_consents_approvals_grants_or_permissions"])
        self.assertEqual(fixture["runtime_stage"], "not-implemented")
        self.assertFalse(fixture["screen_capture_execution_granted"])
        self.assertFalse(fixture["ocr_execution_granted"])
        self.assertFalse(fixture["camera_capture_execution_granted"])
        self.assertFalse(fixture["microphone_capture_execution_granted"])
        self.assertFalse(fixture["clipboard_capture_execution_granted"])
        self.assertFalse(fixture["recording_execution_granted"])
        self.assertFalse(fixture["click_input_automation_execution_granted"])
        self.assertFalse(fixture["overlay_display_execution_granted"])
        self.assertFalse(fixture["notification_sending_execution_granted"])
        self.assertFalse(fixture["network_call_execution_granted"])
        self.assertFalse(fixture["runtime_adapter_execution_granted"])
        self.assertFalse(fixture["adapter_execution_granted"])
        self.assertFalse(fixture["provider_execution_granted"])
        self.assertFalse(fixture["model_execution_granted"])
        self.assertFalse(fixture["execution_permitted"])
        self.assertFalse(fixture["real_mode_runtime_enabled"])
        self.assertEqual(
            [category["capability_category"] for category in fixture["capability_categories"]],
            list(PHASE12D_CAPABILITY_CATEGORIES),
        )
        self.assertEqual(
            [gate["gate_id"] for gate in fixture["required_future_gates"]],
            list(PHASE12D_REQUIRED_FUTURE_GATES),
        )
        self.assertEqual(fixture["capability_category_count"], 12)
        self.assertEqual(fixture["required_future_gate_count"], 9)
        self.assertEqual(fixture["satisfied_consent_gate_count"], 0)
        self.assertEqual(fixture["passed_consent_gate_count"], 0)
        self.assertTrue(fixture["jules_review_required_for_validator_or_authorization_semantics"])
        for category in fixture["capability_categories"]:
            with self.subTest(category=category["capability_category"]):
                self.assertEqual(
                    category["category_status"],
                    "metadata-only-no-consent-satisfied",
                )
                self.assertTrue(category["metadata_only"])
                self.assertFalse(category["consent_granted_by_phase12d"])
                self.assertFalse(category["authorization_granted_by_phase12d"])
                self.assertFalse(category["execution_permitted"])
                self.assertFalse(category["real_mode_runtime_enabled"])
        for gate in fixture["required_future_gates"]:
            with self.subTest(gate=gate["gate_id"]):
                self.assertEqual(
                    gate["gate_status"],
                    "future-consent-gate-required-not-satisfied",
                )
                self.assertTrue(gate["required_before_visual_desktop_runtime"])
                self.assertTrue(gate["metadata_only"])
                self.assertFalse(gate["satisfied_by_phase12d"])
                self.assertFalse(gate["passed"])
                self.assertFalse(gate["execution_permitted"])
                self.assertFalse(gate["real_mode_runtime_enabled"])
        result = validate_phase12d_visual_desktop_consent_gate_requirements(fixture)
        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(result.authorization_wording_count, 0)
        self._assert_no_private_values(fixture)

    def test_status_summary_is_compact_and_non_executing(self):
        summary = phase12d_visual_desktop_consent_gate_requirements_status_summary()

        self.assertEqual(summary["source_phase_range"], "12A-12C")
        self.assertEqual(summary["consent_phase"], "gate-requirements-only")
        self.assertEqual(summary["authorization_status"], "not-authorized")
        self.assertEqual(summary["grant_status"], "no-grant")
        self.assertEqual(summary["capability_category_count"], 12)
        self.assertEqual(summary["required_future_gate_count"], 9)
        self.assertEqual(summary["satisfied_consent_gate_count"], 0)
        self.assertEqual(summary["passed_consent_gate_count"], 0)
        self.assertEqual(summary["runtime_stage"], "not-implemented")
        for field in (
            "screen_capture_execution_granted",
            "ocr_execution_granted",
            "camera_capture_execution_granted",
            "microphone_capture_execution_granted",
            "clipboard_capture_execution_granted",
            "recording_execution_granted",
            "click_input_automation_execution_granted",
            "overlay_display_execution_granted",
            "notification_sending_execution_granted",
            "network_call_execution_granted",
            "runtime_adapter_execution_granted",
            "adapter_execution_granted",
            "provider_execution_granted",
            "model_execution_granted",
            "execution_permitted",
            "real_mode_runtime_enabled",
        ):
            with self.subTest(field=field):
                self.assertFalse(summary[field])
        self._assert_no_private_values(summary)

    def test_status_words_never_enable_execution(self):
        profile = phase12d_visual_desktop_consent_gate_requirements()
        finalize = (
            phase12_contracts_module._finalize_phase12d_visual_desktop_consent_gate_requirements
        )
        for wording in (
            "consented",
            "approved",
            "authorized",
            "granted",
            "ready",
            "enabled",
            "configured",
            "gate-defined",
        ):
            with self.subTest(wording=wording):
                unsafe = copy.deepcopy(profile)
                unsafe["authorization_status"] = wording
                unsafe["grant_status"] = wording
                unsafe["consent_gate_status"] = wording
                unsafe["execution_permitted"] = True
                unsafe["real_mode_runtime_enabled"] = True
                unsafe = finalize(unsafe)
                result = validate_phase12d_visual_desktop_consent_gate_requirements(unsafe)

                self.assertFalse(result.compatible)
                self.assertFalse(result.to_dict()["execution_permitted"])
                self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])
                self.assertFalse(result.sanitized_record["screen_capture_execution_granted"])
                self.assertFalse(result.sanitized_record["ocr_execution_granted"])

    def test_future_gate_metadata_cannot_be_interpreted_as_consent(self):
        profile = phase12d_visual_desktop_consent_gate_requirements()
        finalize = (
            phase12_contracts_module._finalize_phase12d_visual_desktop_consent_gate_requirements
        )
        unsafe = copy.deepcopy(profile)
        unsafe["phase12d_satisfies_consent_gates"] = True
        unsafe["satisfied_consent_gate_count"] = 1
        unsafe["passed_consent_gate_count"] = 1
        unsafe["capability_categories"][0]["consent_granted_by_phase12d"] = True
        unsafe["capability_categories"][0]["authorization_granted_by_phase12d"] = True
        unsafe["required_future_gates"][0]["satisfied_by_phase12d"] = True
        unsafe["required_future_gates"][0]["passed"] = True
        unsafe = finalize(unsafe)

        result = validate_phase12d_visual_desktop_consent_gate_requirements(unsafe)

        self.assertFalse(result.compatible)
        self.assertFalse(result.to_dict()["execution_permitted"])
        self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])
        safe = result.sanitized_record
        self.assertFalse(safe["phase12d_satisfies_consent_gates"])
        self.assertEqual(safe["satisfied_consent_gate_count"], 0)
        self.assertEqual(safe["passed_consent_gate_count"], 0)
        for category in safe["capability_categories"]:
            self.assertFalse(category["consent_granted_by_phase12d"])
            self.assertFalse(category["authorization_granted_by_phase12d"])
        for gate in safe["required_future_gates"]:
            self.assertFalse(gate["satisfied_by_phase12d"])
            self.assertFalse(gate["passed"])

    def test_no_active_authorization_grant_can_validate(self):
        profile = phase12d_visual_desktop_consent_gate_requirements()
        unsafe = copy.deepcopy(profile)
        unsafe["authorization_status"] = "authorized"
        unsafe["grant_status"] = "granted"
        unsafe["phase12d_profiles_are_consents_approvals_grants_or_permissions"] = True
        unsafe["screen_capture_execution_granted"] = True
        unsafe["ocr_execution_granted"] = True
        unsafe["camera_capture_execution_granted"] = True
        unsafe["microphone_capture_execution_granted"] = True
        unsafe["clipboard_capture_execution_granted"] = True
        unsafe["recording_execution_granted"] = True
        unsafe["click_input_automation_execution_granted"] = True
        unsafe["overlay_display_execution_granted"] = True
        unsafe["notification_sending_execution_granted"] = True
        unsafe["network_call_execution_granted"] = True
        unsafe["runtime_adapter_execution_granted"] = True
        unsafe["execution_permitted"] = True
        unsafe["real_mode_runtime_enabled"] = True
        unsafe["active_grant"] = {
            "status": "permission-granted",
            "runtime_stage": "ready",
        }

        result = validate_phase12d_visual_desktop_consent_gate_requirements(unsafe)

        self.assertFalse(result.compatible)
        self.assertFalse(result.to_dict()["execution_permitted"])
        self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])
        self.assertEqual(result.sanitized_record["grant_status"], "no-grant")
        self.assertFalse(
            result.sanitized_record[
                "phase12d_profiles_are_consents_approvals_grants_or_permissions"
            ]
        )
        self.assertNotIn("active_grant", result.sanitized_record)

    def test_validator_fails_closed_for_unsafe_or_contradictory_records(self):
        profile = phase12d_visual_desktop_consent_gate_requirements()
        cases = [("not-object", "not-a-dict")]

        missing = copy.deepcopy(profile)
        missing.pop("capability_categories")
        cases.append(("missing", missing))

        unsupported = copy.deepcopy(profile)
        unsupported["consent_gate_profile_contract_version"] = 999
        cases.append(("unsupported", unsupported))

        unknown = copy.deepcopy(profile)
        unknown["unexpected"] = "metadata"
        cases.append(("unknown", unknown))

        authorization = copy.deepcopy(profile)
        authorization["authorization_status"] = "authorization-granted"
        cases.append(("authorization-wording", authorization))

        permission = copy.deepcopy(profile)
        permission["consent_gate_status"] = "runtime-permission-granted"
        cases.append(("permission-wording", permission))

        unsafe = copy.deepcopy(profile)
        unsafe["source_capability_profile"]["profile_status"] = "https://example.invalid/api_key"
        cases.append(("unsafe", unsafe))

        boolean_count = copy.deepcopy(profile)
        boolean_count["capability_category_count"] = True
        cases.append(("boolean-count", boolean_count))

        string_count = copy.deepcopy(profile)
        string_count["required_future_gate_count"] = "9"
        cases.append(("string-count", string_count))

        source_id = copy.deepcopy(profile)
        source_id["source_record_candidate"]["source_id"] = "private-source"
        cases.append(("source-id", source_id))

        raw_screenshot = copy.deepcopy(profile)
        raw_screenshot["capability_categories"][0]["capability_category"] = "raw_screenshot"
        cases.append(("raw-screenshot", raw_screenshot))

        raw_ocr = copy.deepcopy(profile)
        raw_ocr["capability_categories"][1]["capability_category"] = "raw_ocr"
        cases.append(("raw-ocr", raw_ocr))

        clipboard_text = copy.deepcopy(profile)
        clipboard_text["consent_gate_status"] = "raw_clipboard_text"
        cases.append(("raw-clipboard", clipboard_text))

        camera_payload = copy.deepcopy(profile)
        camera_payload["source_capability_profile"]["camera_payload"] = "frame"
        cases.append(("camera-payload", camera_payload))

        recording_payload = copy.deepcopy(profile)
        recording_payload["required_future_gates"][0]["gate_status"] = "recording_payload"
        cases.append(("recording-payload", recording_payload))

        for name, payload in cases:
            with self.subTest(case=name):
                result = validate_phase12d_visual_desktop_consent_gate_requirements(payload)
                encoded = self._safe_encoded((result.to_dict(), result.sanitized_record))

                self.assertFalse(result.compatible)
                self.assertFalse(result.to_dict()["execution_permitted"])
                self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])
                for sentinel in UNSAFE_PHASE12D_SENTINELS:
                    self.assertNotIn(sentinel, encoded)

    def test_phase12_sources_remain_non_executing(self):
        charter = phase12a_runtime_authorization_design_charter()
        record = phase12b_runtime_authorization_record_candidate()
        profile = phase12c_visual_supervision_capability_profile()

        charter_result = validate_phase12a_runtime_authorization_design_charter(charter)
        record_result = validate_phase12b_runtime_authorization_record_candidate(record)
        profile_result = validate_phase12c_visual_supervision_capability_profile(profile)

        self.assertTrue(charter_result.compatible, charter_result.errors)
        self.assertTrue(record_result.compatible, record_result.errors)
        self.assertTrue(profile_result.compatible, profile_result.errors)
        for payload in (charter, record, profile):
            self.assertEqual(payload["runtime_stage"], "not-implemented")
            self.assertFalse(payload["execution_permitted"])
            self.assertFalse(payload["real_mode_runtime_enabled"])

    def test_phase12d_module_does_not_add_runtime_execution_imports(self):
        module_text = Path(phase12_contracts_module.__file__).read_text(encoding="utf-8").lower()

        for forbidden in (
            "observer",
            "cv2",
            "pytesseract",
            "pyautogui",
            "pynput",
            "mss",
            "pillow",
            "imagegrab",
            "keyboard",
            "mouse",
            "notify2",
            "win10toast",
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
        for forbidden in UNSAFE_PHASE12D_SENTINELS:
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
            .replace("consent_gate", "cg")
            .replace("consent_granted", "cg_granted")
            .replace("authorization_granted", "auth_granted")
            .replace("capability_profile", "status_profile")
            .replace("click-input-automation-policy", "click-input-auto-policy")
            .replace("no-hidden-background-monitoring-declaration", "no-hbm-declaration")
            .replace("screen_capture", "scr_cap")
            .replace("ocr_execution", "ocr_exec")
            .replace("visual_capture", "vis_cap")
            .replace("clipboard_capture", "clip_cap")
            .replace("mic_capture", "mic_cap")
            .replace("microphone_capture", "mphone_cap")
            .replace("camera_capture", "cam_cap")
            .replace("click_input_automation", "click_input_auto")
            .replace("click_automation", "click_auto")
            .replace("input_automation", "input_auto")
            .replace("screen_recording", "scr_rec")
            .replace("recording_execution", "rec_exec")
            .replace("audio_recording", "aud_rec")
            .replace("hidden_monitoring", "hid_mon")
            .replace("background_monitoring", "bg_mon")
            .replace("raw_screenshot", "raw_scr")
            .replace("raw_ocr", "raw_o")
            .replace("raw_clipboard_text", "raw_clip")
            .replace("screenshot_payload", "scr_payload")
            .replace("ocr_payload", "ocr_pay")
            .replace("camera_payload", "cam_pay")
            .replace("microphone_payload", "mic_pay")
            .replace("audio_payload", "aud_pay")
            .replace("recording_payload", "rec_pay")
            .replace("raw_recording_payload", "raw_rec_pay")
        )


if __name__ == "__main__":
    unittest.main()
