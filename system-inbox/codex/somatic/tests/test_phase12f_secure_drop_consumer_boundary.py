import copy
import json
import unittest
from pathlib import Path

from somatic.safety import phase12_contracts as phase12_contracts_module
from somatic.safety.phase12_contracts import (
    PHASE12F_ALLOWED_USER_SELECTED_ARTIFACT_LABELS,
    PHASE12F_AUTHORIZATION_STATUS,
    PHASE12F_CANONICAL_OWNER,
    PHASE12F_CANONICAL_REFERENCE,
    PHASE12F_CONSUMER_PHASE,
    PHASE12F_CONTENT_FABRIC_SECURE_DROP_MERGE_SHA,
    PHASE12F_GRANT_STATUS,
    PHASE12F_PROHIBITED_AUTONOMOUS_SOURCES,
    PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_CONTRACT_VERSION,
    PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_KIND,
    phase12a_runtime_authorization_design_charter,
    phase12b_runtime_authorization_record_candidate,
    phase12c_visual_supervision_capability_profile,
    phase12d_visual_desktop_consent_gate_requirements,
    phase12e_physiological_sensor_capability_profile,
    phase12f_secure_drop_consumer_boundary,
    phase12f_secure_drop_consumer_boundary_status_summary,
    validate_phase12a_runtime_authorization_design_charter,
    validate_phase12b_runtime_authorization_record_candidate,
    validate_phase12c_visual_supervision_capability_profile,
    validate_phase12d_visual_desktop_consent_gate_requirements,
    validate_phase12e_physiological_sensor_capability_profile,
    validate_phase12f_secure_drop_consumer_boundary,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_FIXTURE = (
    REPO_ROOT / "fixtures" / "reviews" / "phase-12f-secure-drop-consumer-boundary-v1.json"
)
UNSAFE_PHASE12F_SENTINELS = (
    "plaintext payload",
    "sk-live",
    "c:/users",
    "https://example.invalid",
    "source_id",
    "device_id",
    "router_id",
    "raw_document_text",
    "raw_csi",
    "raw_rf",
    "raw_bia",
    "raw_acoustic",
    "raw_ultrasound",
    "raw_screenshot",
    "raw_ocr",
    "medical diagnosis",
    "clinical recommendation",
    "runtime-permission-granted",
    "send-executed",
    "receive-executed",
    "unencrypted-transfer-permitted",
    "anonymous-recipient",
    "stego-security-boundary",
)


class Phase12FSecureDropConsumerBoundaryTests(unittest.TestCase):
    def test_fixture_matches_deterministic_helper(self):
        fixture = json.loads(BOUNDARY_FIXTURE.read_text(encoding="utf-8"))
        generated = phase12f_secure_drop_consumer_boundary()

        self.assertEqual(fixture, generated)
        self.assertEqual(
            fixture["secure_drop_consumer_boundary_contract_version"],
            PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_CONTRACT_VERSION,
        )
        self.assertEqual(fixture["boundary_kind"], PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_KIND)
        self.assertTrue(
            fixture["secure_drop_consumer_boundary_id"].startswith("p12f-secure-drop-boundary-")
        )
        self.assertEqual(fixture["consumer_phase"], PHASE12F_CONSUMER_PHASE)
        self.assertEqual(fixture["canonical_owner"], PHASE12F_CANONICAL_OWNER)
        self.assertEqual(fixture["canonical_reference"], PHASE12F_CANONICAL_REFERENCE)
        self.assertEqual(fixture["authorization_status"], PHASE12F_AUTHORIZATION_STATUS)
        self.assertEqual(fixture["grant_status"], PHASE12F_GRANT_STATUS)
        self.assertEqual(fixture["runtime_stage"], "not-implemented")
        self.assertFalse(fixture["phase12f_implements_secure_drop"])
        self.assertFalse(fixture["phase12f_authorizes_secure_drop"])
        self.assertTrue(fixture["encryption_required"])
        self.assertTrue(fixture["concealment_optional"])
        self.assertFalse(fixture["concealment_is_security_boundary"])
        self.assertTrue(fixture["audit_metadata_only_required"])
        for field in self._runtime_flag_fields():
            with self.subTest(field=field):
                self.assertFalse(fixture[field])
        self.assertEqual(
            [
                artifact["artifact_label"]
                for artifact in fixture["allowed_future_user_selected_artifact_labels"]
            ],
            list(PHASE12F_ALLOWED_USER_SELECTED_ARTIFACT_LABELS),
        )
        self.assertEqual(
            [source["source_label"] for source in fixture["prohibited_future_autonomous_sources"]],
            list(PHASE12F_PROHIBITED_AUTONOMOUS_SOURCES),
        )
        self.assertEqual(fixture["allowed_future_user_selected_artifact_label_count"], 6)
        self.assertEqual(fixture["prohibited_future_autonomous_source_count"], 11)
        source_contract = fixture["source_content_fabric_secure_drop_contract"]
        self.assertEqual(source_contract["canonical_owner"], "content-fabric")
        self.assertEqual(
            source_contract["merge_commit_sha"],
            PHASE12F_CONTENT_FABRIC_SECURE_DROP_MERGE_SHA,
        )
        self.assertTrue(source_contract["design_contract_only"])
        self.assertFalse(source_contract["somatic_owns_secure_drop_implementation"])
        result = validate_phase12f_secure_drop_consumer_boundary(fixture)
        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(result.authorization_wording_count, 0)

    def test_status_summary_is_compact_and_non_executing(self):
        summary = phase12f_secure_drop_consumer_boundary_status_summary()

        self.assertEqual(summary["consumer_phase"], "boundary-profile-only")
        self.assertEqual(summary["canonical_owner"], "content-fabric")
        self.assertEqual(summary["canonical_reference"], PHASE12F_CANONICAL_REFERENCE)
        self.assertEqual(summary["authorization_status"], "not-authorized")
        self.assertEqual(summary["grant_status"], "no-grant")
        self.assertEqual(summary["allowed_future_user_selected_artifact_label_count"], 6)
        self.assertEqual(summary["prohibited_future_autonomous_source_count"], 11)
        self.assertTrue(summary["encryption_required"])
        self.assertTrue(summary["concealment_optional"])
        self.assertFalse(summary["concealment_is_security_boundary"])
        self.assertTrue(summary["audit_metadata_only_required"])
        self.assertEqual(summary["runtime_stage"], "not-implemented")
        for field in (
            "secure_drop_send_permitted",
            "secure_drop_receive_permitted",
            "agent_invocation_permitted",
            "automation_invocation_permitted",
            "filesystem_autoscan_permitted",
            "vault_env_secret_access_permitted",
            "crypto_implementation_added",
            "transport_implementation_added",
            "stego_implementation_added",
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

    def test_status_words_never_enable_execution(self):
        boundary = phase12f_secure_drop_consumer_boundary()
        finalize = phase12_contracts_module._finalize_phase12f_secure_drop_consumer_boundary
        for wording in (
            "sent",
            "received",
            "encrypted",
            "concealed",
            "approved",
            "authorized",
            "ready",
            "configured",
            "user-selected",
        ):
            with self.subTest(wording=wording):
                unsafe = copy.deepcopy(boundary)
                unsafe["authorization_status"] = wording
                unsafe["grant_status"] = wording
                unsafe["boundary_status"] = wording
                unsafe["execution_permitted"] = True
                unsafe["real_mode_runtime_enabled"] = True
                unsafe = finalize(unsafe)
                result = validate_phase12f_secure_drop_consumer_boundary(unsafe)

                self.assertFalse(result.compatible)
                self.assertFalse(result.to_dict()["secure_drop_send_permitted"])
                self.assertFalse(result.to_dict()["secure_drop_receive_permitted"])
                self.assertFalse(result.to_dict()["execution_permitted"])
                self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])

    def test_metadata_labels_cannot_enable_send_receive_or_sources(self):
        boundary = phase12f_secure_drop_consumer_boundary()
        finalize = phase12_contracts_module._finalize_phase12f_secure_drop_consumer_boundary
        unsafe = copy.deepcopy(boundary)
        unsafe["allowed_future_user_selected_artifact_labels"][0]["selected_by_phase12f"] = True
        unsafe["allowed_future_user_selected_artifact_labels"][0]["send_permitted"] = True
        unsafe["allowed_future_user_selected_artifact_labels"][1]["receive_permitted"] = True
        unsafe["prohibited_future_autonomous_sources"][0]["permitted_by_phase12f"] = True
        unsafe["prohibited_future_autonomous_sources"][0]["send_permitted"] = True
        unsafe["secure_drop_send_permitted"] = True
        unsafe["secure_drop_receive_permitted"] = True
        unsafe = finalize(unsafe)

        result = validate_phase12f_secure_drop_consumer_boundary(unsafe)

        self.assertFalse(result.compatible)
        safe = result.sanitized_record
        self.assertFalse(safe["secure_drop_send_permitted"])
        self.assertFalse(safe["secure_drop_receive_permitted"])
        for artifact in safe["allowed_future_user_selected_artifact_labels"]:
            self.assertFalse(artifact["selected_by_phase12f"])
            self.assertFalse(artifact["send_permitted"])
            self.assertFalse(artifact["receive_permitted"])
        for source in safe["prohibited_future_autonomous_sources"]:
            self.assertFalse(source["permitted_by_phase12f"])
            self.assertFalse(source["send_permitted"])

    def test_forbidden_invocation_and_source_access_cannot_validate(self):
        for field in (
            "agent_invocation_permitted",
            "automation_invocation_permitted",
            "connector_invocation_permitted",
            "scheduled_task_invocation_permitted",
            "avatar_invocation_permitted",
            "server_endpoint_invocation_permitted",
            "workflow_invocation_permitted",
            "filesystem_autoscan_permitted",
            "vault_env_secret_access_permitted",
            "raw_sensor_capture_attachment_permitted",
            "automatic_document_attachment_permitted",
        ):
            with self.subTest(field=field):
                unsafe = phase12f_secure_drop_consumer_boundary()
                unsafe[field] = True

                result = validate_phase12f_secure_drop_consumer_boundary(unsafe)

                self.assertFalse(result.compatible)
                self.assertFalse(result.sanitized_record[field])

    def test_unencrypted_anonymous_stego_and_audit_payloads_cannot_validate(self):
        cases = []
        unencrypted = phase12f_secure_drop_consumer_boundary()
        unencrypted["encryption_required"] = False
        unencrypted["encryption_requirement_status"] = "unencrypted-transfer-permitted"
        cases.append(("unencrypted", unencrypted))

        anonymous = phase12f_secure_drop_consumer_boundary()
        anonymous["source_content_fabric_secure_drop_contract"]["recipient"] = "anonymous-recipient"
        cases.append(("anonymous", anonymous))

        stego_boundary = phase12f_secure_drop_consumer_boundary()
        stego_boundary["concealment_is_security_boundary"] = True
        stego_boundary["concealment_status"] = "stego-security-boundary"
        cases.append(("stego-security", stego_boundary))

        audit_payload = phase12f_secure_drop_consumer_boundary()
        audit_payload["audit_payload"] = "plaintext payload"
        cases.append(("audit-payload", audit_payload))

        keyring = phase12f_secure_drop_consumer_boundary()
        keyring["recipient_did"] = "did:example:unreviewedrecipient"
        keyring["keyring_id"] = "runtime-keyring"
        cases.append(("keyring-did", keyring))

        for name, payload in cases:
            with self.subTest(case=name):
                result = validate_phase12f_secure_drop_consumer_boundary(payload)
                encoded = self._safe_encoded((result.to_dict(), result.sanitized_record))

                self.assertFalse(result.compatible)
                self.assertFalse(result.to_dict()["secure_drop_send_permitted"])
                self.assertFalse(result.to_dict()["execution_permitted"])
                for sentinel in UNSAFE_PHASE12F_SENTINELS:
                    self.assertNotIn(sentinel, encoded)

    def test_validator_fails_closed_for_unsafe_or_contradictory_records(self):
        boundary = phase12f_secure_drop_consumer_boundary()
        cases = [("not-object", "not-a-dict")]

        missing = copy.deepcopy(boundary)
        missing.pop("allowed_future_user_selected_artifact_labels")
        cases.append(("missing", missing))

        unsupported = copy.deepcopy(boundary)
        unsupported["secure_drop_consumer_boundary_contract_version"] = 999
        cases.append(("unsupported", unsupported))

        unknown = copy.deepcopy(boundary)
        unknown["unexpected"] = "metadata"
        cases.append(("unknown", unknown))

        permission = copy.deepcopy(boundary)
        permission["boundary_status"] = "runtime-permission-granted"
        cases.append(("permission-wording", permission))

        unsafe_url = copy.deepcopy(boundary)
        unsafe_url["source_content_fabric_secure_drop_contract"]["canonical_reference"] = (
            "https://example.invalid/secure-drop"
        )
        cases.append(("url", unsafe_url))

        absolute_path = copy.deepcopy(boundary)
        absolute_path["source_content_fabric_secure_drop_contract"]["repository"] = (
            "C:\\Users\\Private"
        )
        cases.append(("absolute-path", absolute_path))

        boolean_count = copy.deepcopy(boundary)
        boolean_count["allowed_future_user_selected_artifact_label_count"] = True
        cases.append(("boolean-count", boolean_count))

        string_count = copy.deepcopy(boundary)
        string_count["prohibited_future_autonomous_source_count"] = "11"
        cases.append(("string-count", string_count))

        raw_payload = copy.deepcopy(boundary)
        raw_payload["source_physiological_sensor_profile"]["raw_bia"] = "42"
        cases.append(("raw-sensor", raw_payload))

        clinical = copy.deepcopy(boundary)
        clinical["source_content_fabric_secure_drop_contract"]["claim"] = "medical diagnosis"
        cases.append(("clinical", clinical))

        for name, payload in cases:
            with self.subTest(case=name):
                result = validate_phase12f_secure_drop_consumer_boundary(payload)
                encoded = self._safe_encoded((result.to_dict(), result.sanitized_record))

                self.assertFalse(result.compatible)
                self.assertFalse(result.to_dict()["execution_permitted"])
                self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])
                for sentinel in UNSAFE_PHASE12F_SENTINELS:
                    self.assertNotIn(sentinel, encoded)

    def test_phase11_and_phase12_sources_remain_non_executing(self):
        sources = (
            (
                phase12a_runtime_authorization_design_charter(),
                validate_phase12a_runtime_authorization_design_charter,
            ),
            (
                phase12b_runtime_authorization_record_candidate(),
                validate_phase12b_runtime_authorization_record_candidate,
            ),
            (
                phase12c_visual_supervision_capability_profile(),
                validate_phase12c_visual_supervision_capability_profile,
            ),
            (
                phase12d_visual_desktop_consent_gate_requirements(),
                validate_phase12d_visual_desktop_consent_gate_requirements,
            ),
            (
                phase12e_physiological_sensor_capability_profile(),
                validate_phase12e_physiological_sensor_capability_profile,
            ),
        )

        for payload, validator in sources:
            with self.subTest(kind=payload.get("profile_kind") or payload.get("record_kind")):
                result = validator(payload)

                self.assertTrue(result.compatible, result.errors)
                self.assertEqual(payload["runtime_stage"], "not-implemented")
                self.assertFalse(payload["execution_permitted"])
                self.assertFalse(payload["real_mode_runtime_enabled"])

    def test_phase12f_module_does_not_add_secure_drop_runtime_imports(self):
        module_text = Path(phase12_contracts_module.__file__).read_text(encoding="utf-8").lower()

        for forbidden in (
            "libsodium",
            "import steganography",
            "from steganography",
            "securedropclient",
            "import cryptography",
            "from cryptography",
            "import nacl",
            "from nacl",
            "requests",
            "urllib",
            "socket",
            "subprocess",
            "websocket",
            "fetch(",
            "xmlhttprequest",
            "open(",
            '"execution_permitted": true',
            '"real_mode_runtime_enabled": true',
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, module_text)

    @staticmethod
    def _runtime_flag_fields():
        return (
            "secure_drop_send_permitted",
            "secure_drop_receive_permitted",
            "agent_invocation_permitted",
            "automation_invocation_permitted",
            "connector_invocation_permitted",
            "scheduled_task_invocation_permitted",
            "avatar_invocation_permitted",
            "server_endpoint_invocation_permitted",
            "workflow_invocation_permitted",
            "filesystem_autoscan_permitted",
            "vault_env_secret_access_permitted",
            "raw_sensor_capture_attachment_permitted",
            "automatic_document_attachment_permitted",
            "crypto_implementation_added",
            "transport_implementation_added",
            "stego_implementation_added",
            "keyring_implementation_added",
            "did_implementation_added",
            "send_inbox_ui_added",
            "network_call_execution_granted",
            "runtime_adapter_execution_granted",
            "adapter_execution_granted",
            "provider_execution_granted",
            "model_execution_granted",
            "active_grant_present",
            "execution_permitted",
            "real_mode_runtime_enabled",
        )

    @staticmethod
    def _safe_encoded(payload):
        return (
            json.dumps(payload, sort_keys=True)
            .lower()
            .replace("\\", "/")
            .replace("not-authorized", "not-runtime-status")
            .replace("authorization_status", "runtime_status")
            .replace("runtime_authorization", "runtime_status")
            .replace("vault-secret", "vault-src-blocked")
            .replace("env-var", "env-src-blocked")
            .replace("api-key", "api-src-blocked")
            .replace("raw-document-body", "doc-body-blocked")
            .replace("raw-csi-rf-capture", "csi-rf-blocked")
            .replace("raw-bia-reading", "bia-reading-blocked")
            .replace("raw-acoustic-ultrasound-data", "acoustic-us-blocked")
            .replace("screenshot-or-ocr-dump", "visual-dump-blocked")
            .replace("keyring_implementation", "keyring_impl")
            .replace("did_implementation", "did_impl")
            .replace("secure_drop", "secure_xfer")
            .replace("send_permitted", "send_perm")
            .replace("receive_permitted", "receive_perm")
        )


if __name__ == "__main__":
    unittest.main()
