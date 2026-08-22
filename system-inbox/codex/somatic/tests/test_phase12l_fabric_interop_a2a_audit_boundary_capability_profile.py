import copy
import json
import unittest
from pathlib import Path

from somatic.safety import phase12_contracts as phase12_contracts_module
from somatic.safety.phase11_contracts import (
    phase11_planning_governance_closeout_status_summary,
    phase11_runtime_authorization_gap_ledger_status_summary,
)
from somatic.safety.phase12_contracts import (
    PHASE12L_A2A_TRANSPORT_STATUS,
    PHASE12L_AUTHORIZATION_STATUS,
    PHASE12L_CAPABILITY_PHASE,
    PHASE12L_CREDENTIAL_POLICY,
    PHASE12L_FABRIC_CAPABILITY_LABELS,
    PHASE12L_FABRIC_INTEROP_A2A_AUDIT_PROFILE_CONTRACT_VERSION,
    PHASE12L_FABRIC_INTEROP_A2A_AUDIT_PROFILE_KIND,
    PHASE12L_FABRIC_INTEROP_STATUS,
    PHASE12L_FORBIDDEN_OUT_OF_SCOPE_LABELS,
    PHASE12L_GRANT_STATUS,
    PHASE12L_MCP_INTEROP_STATUS,
    PHASE12L_MESSAGE_CODEC_STATUS,
    PHASE12L_REQUIRED_FUTURE_GATES,
    PHASE12L_SECURE_DROP_STATUS,
    PHASE12L_SOURCE_PHASE_RANGE,
    phase12a_runtime_authorization_design_charter,
    phase12b_runtime_authorization_record_candidate,
    phase12c_visual_supervision_capability_profile,
    phase12d_visual_desktop_consent_gate_requirements,
    phase12e_physiological_sensor_capability_profile,
    phase12f_secure_drop_consumer_boundary,
    phase12g_production_readiness_coverage_matrix,
    phase12h_somatic_standalone_production_readiness_ownership_map,
    validate_phase12a_runtime_authorization_design_charter,
    validate_phase12b_runtime_authorization_record_candidate,
    validate_phase12c_visual_supervision_capability_profile,
    validate_phase12d_visual_desktop_consent_gate_requirements,
    validate_phase12e_physiological_sensor_capability_profile,
    validate_phase12f_secure_drop_consumer_boundary,
    validate_phase12g_production_readiness_coverage_matrix,
    validate_phase12h_somatic_standalone_production_readiness_ownership_map,
)

phase12i_profile = (
    phase12_contracts_module.phase12i_integrative_herbal_nutrition_knowledge_capability_profile
)
PHASE12I_VALIDATOR_ATTR = (
    "validate_phase12i_integrative_herbal_nutrition_knowledge_capability_profile"
)
validate_phase12i_profile = getattr(phase12_contracts_module, PHASE12I_VALIDATOR_ATTR)
phase12k_profile = (
    phase12_contracts_module.phase12k_external_compute_quantum_backend_capability_profile
)
validate_phase12k_profile = (
    phase12_contracts_module.validate_phase12k_external_compute_quantum_backend_capability_profile
)
phase12l_profile = (
    phase12_contracts_module.phase12l_fabric_interop_a2a_audit_boundary_capability_profile
)
PHASE12L_STATUS_SUMMARY_ATTR = (
    "phase12l_fabric_interop_a2a_audit_boundary_capability_profile_status_summary"
)
phase12l_status_summary = getattr(phase12_contracts_module, PHASE12L_STATUS_SUMMARY_ATTR)
validate_phase12l_profile = (
    phase12_contracts_module.validate_phase12l_fabric_interop_a2a_audit_boundary_capability_profile
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PROFILE_FIXTURE = (
    REPO_ROOT
    / "fixtures"
    / "reviews"
    / "phase-12l-fabric-interop-a2a-audit-boundary-capability-profile-v1.json"
)


class Phase12LFabricInteropA2AAuditBoundaryCapabilityProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generated_profile = phase12l_profile()
        cls.fixture = json.loads(PROFILE_FIXTURE.read_text(encoding="utf-8"))

    def _profile(self):
        return copy.deepcopy(self.generated_profile)

    def test_fixture_matches_deterministic_helper(self):
        fixture = self.fixture
        generated = self.generated_profile

        self.assertEqual(fixture, generated)
        self.assertEqual(
            fixture["fabric_interop_a2a_audit_profile_contract_version"],
            PHASE12L_FABRIC_INTEROP_A2A_AUDIT_PROFILE_CONTRACT_VERSION,
        )
        self.assertEqual(
            fixture["profile_kind"],
            PHASE12L_FABRIC_INTEROP_A2A_AUDIT_PROFILE_KIND,
        )
        self.assertTrue(fixture["profile_id"].startswith("p12l-fabric-a2a-audit-profile-"))
        self.assertEqual(fixture["source_phase_range"], PHASE12L_SOURCE_PHASE_RANGE)
        self.assertEqual(fixture["capability_phase"], PHASE12L_CAPABILITY_PHASE)
        self.assertEqual(fixture["authorization_status"], PHASE12L_AUTHORIZATION_STATUS)
        self.assertEqual(fixture["grant_status"], PHASE12L_GRANT_STATUS)
        self.assertEqual(fixture["fabric_interop_status"], PHASE12L_FABRIC_INTEROP_STATUS)
        self.assertEqual(fixture["message_codec_status"], PHASE12L_MESSAGE_CODEC_STATUS)
        self.assertEqual(fixture["a2a_transport_status"], PHASE12L_A2A_TRANSPORT_STATUS)
        self.assertEqual(fixture["mcp_interop_status"], PHASE12L_MCP_INTEROP_STATUS)
        self.assertEqual(fixture["secure_drop_status"], PHASE12L_SECURE_DROP_STATUS)
        self.assertEqual(fixture["credential_policy"], PHASE12L_CREDENTIAL_POLICY)
        self.assertEqual(
            [ref["phase_label"] for ref in fixture["source_phase_references"]],
            ["12A", "12B", "12C", "12D", "12E", "12F", "12G", "12H", "12I", "12K"],
        )
        self.assertEqual(
            [item["fabric_capability_label"] for item in fixture["fabric_capability_labels"]],
            list(PHASE12L_FABRIC_CAPABILITY_LABELS),
        )
        self.assertEqual(
            [item["forbidden_label"] for item in fixture["forbidden_out_of_scope_labels"]],
            list(PHASE12L_FORBIDDEN_OUT_OF_SCOPE_LABELS),
        )
        self.assertEqual(
            [item["future_gate_label"] for item in fixture["required_future_gates"]],
            list(PHASE12L_REQUIRED_FUTURE_GATES),
        )
        self.assertTrue(fixture["metadata_only"])
        self.assertTrue(fixture["non_authorizing_proof"])
        self.assertTrue(fixture["security_review_required"])
        self.assertTrue(fixture["fabric_safety_review_required"])
        self.assertTrue(fixture["plaintext_json_default_future_requirement_only"])
        self.assertTrue(fixture["decode_to_audit_future_requirement_only"])
        self.assertTrue(fixture["secure_drop_user_initiated_boundary_only"])
        self.assertFalse(fixture["opaque_traffic_allowed"])
        self.assertFalse(fixture["untrusted_content_executable"])
        self.assertFalse(fixture["cross_repo_mutation_allowed"])
        for field in self._runtime_false_fields():
            with self.subTest(field=field):
                self.assertFalse(fixture[field])
        result = validate_phase12l_profile(fixture)
        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(result.privacy_violation_count, 0)
        self.assertEqual(result.authorization_wording_count, 0)

    def test_status_summary_is_non_authorizing(self):
        summary = phase12l_status_summary()

        self.assertEqual(summary["source_phase_range"], PHASE12L_SOURCE_PHASE_RANGE)
        self.assertEqual(
            summary["capability_phase"],
            "fabric-interop-a2a-audit-boundary-profile-only",
        )
        self.assertEqual(summary["authorization_status"], "not-authorized")
        self.assertEqual(summary["grant_status"], "no-grant")
        self.assertEqual(summary["fabric_interop_status"], "metadata-only")
        self.assertEqual(summary["message_codec_status"], "not-implemented")
        self.assertEqual(summary["a2a_transport_status"], "not-implemented")
        self.assertEqual(summary["mcp_interop_status"], "not-implemented")
        self.assertEqual(summary["secure_drop_status"], "consumer-boundary-only")
        self.assertEqual(summary["credential_policy"], "phase-h-vault-reference-only")
        self.assertEqual(summary["fabric_capability_label_count"], 15)
        self.assertEqual(summary["forbidden_out_of_scope_label_count"], 12)
        self.assertEqual(summary["required_future_gate_count"], 10)
        self.assertTrue(summary["metadata_only"])
        self.assertTrue(summary["non_authorizing_proof"])
        self.assertTrue(summary["plaintext_json_default_future_requirement_only"])
        self.assertTrue(summary["decode_to_audit_future_requirement_only"])
        self.assertTrue(summary["secure_drop_user_initiated_boundary_only"])
        self.assertFalse(summary["opaque_traffic_allowed"])
        self.assertFalse(summary["untrusted_content_executable"])
        self.assertFalse(summary["cross_repo_mutation_allowed"])
        for field in self._runtime_false_fields():
            with self.subTest(field=field):
                self.assertFalse(summary[field])

    def test_fabric_and_forbidden_labels_are_metadata_only(self):
        profile = self._profile()

        for item in profile["fabric_capability_labels"]:
            with self.subTest(capability=item["fabric_capability_label"]):
                self.assertTrue(item["metadata_only"])
                self.assertTrue(item["future_requirement_only"])
                self.assertFalse(item["implementation_added"])
                self.assertFalse(item["execution_permitted"])
                self.assertFalse(item["real_mode_runtime_enabled"])
        for item in profile["forbidden_out_of_scope_labels"]:
            with self.subTest(forbidden=item["forbidden_label"]):
                self.assertTrue(item["metadata_only"])
                self.assertTrue(item["out_of_scope"])
                self.assertFalse(item["allowed"])
                self.assertFalse(item["execution_permitted"])
                self.assertFalse(item["real_mode_runtime_enabled"])

    def test_status_words_never_create_grants(self):
        finalize = phase12_contracts_module._finalize_phase12l_fabric_interop_a2a_audit_profile
        for wording in (
            "codec",
            "handshake",
            "MCP",
            "agent-protocol",
            "Fusion",
            "Secure Drop",
            "pack",
            "connector",
            "installed",
            "enabled",
            "configured",
            "authorized",
            "approved",
            "ready",
        ):
            with self.subTest(wording=wording):
                unsafe = self._profile()
                unsafe["authorization_status"] = wording
                unsafe["grant_status"] = wording
                unsafe["profile_status"] = wording
                unsafe["phase12l_authorizes_runtime"] = True
                unsafe["phase12l_allows_fabric_runtime"] = True
                unsafe["phase12l_allows_a2a_transport"] = True
                unsafe["phase12l_allows_mcp_runtime"] = True
                unsafe["phase12l_allows_secure_drop_send_receive"] = True
                unsafe["execution_permitted"] = True
                unsafe["real_mode_runtime_enabled"] = True
                unsafe = finalize(unsafe)
                result = validate_phase12l_profile(unsafe)

                self.assertFalse(result.compatible)
                safe = result.to_dict()
                self.assertFalse(safe["phase12l_authorizes_runtime"])
                self.assertFalse(safe["phase12l_allows_fabric_runtime"])
                self.assertFalse(safe["phase12l_allows_a2a_transport"])
                self.assertFalse(safe["phase12l_allows_mcp_runtime"])
                self.assertFalse(safe["phase12l_allows_secure_drop_send_receive"])
                self.assertFalse(safe["execution_permitted"])
                self.assertFalse(safe["real_mode_runtime_enabled"])

    def test_runtime_and_interop_action_fields_cannot_validate(self):
        for field in self._runtime_false_fields():
            with self.subTest(field=field):
                unsafe = self._profile()
                unsafe[field] = True

                result = validate_phase12l_profile(unsafe)

                self.assertFalse(result.compatible)
                self.assertFalse(result.sanitized_record[field])

    def test_plaintext_json_and_decode_to_audit_are_future_requirements_only(self):
        profile = self._profile()

        self.assertTrue(profile["plaintext_json_default_future_requirement_only"])
        self.assertTrue(profile["decode_to_audit_future_requirement_only"])
        self.assertEqual(profile["message_codec_status"], "not-implemented")
        self.assertFalse(profile["message_codec_implementation_added"])
        self.assertFalse(profile["a2a_transport_implementation_added"])
        self.assertFalse(profile["mcp_server_implementation_added"])
        self.assertFalse(profile["mcp_client_implementation_added"])
        self.assertFalse(profile["fabric_transfer_execution_granted"])
        self.assertFalse(profile["execution_permitted"])

    def test_secure_drop_remains_user_initiated_content_fabric_boundary_only(self):
        unsafe = self._profile()
        unsafe["secure_drop_user_initiated_boundary_only"] = False
        unsafe["phase12l_allows_secure_drop_send_receive"] = True
        unsafe["agent_invoked_secure_drop_allowed"] = True
        unsafe["automation_invoked_secure_drop_allowed"] = True
        unsafe["secure_drop_send_permitted"] = True
        unsafe["secure_drop_receive_permitted"] = True

        result = validate_phase12l_profile(unsafe)

        self.assertFalse(result.compatible)
        safe = result.to_dict()
        self.assertTrue(safe["secure_drop_user_initiated_boundary_only"])
        self.assertFalse(safe["phase12l_allows_secure_drop_send_receive"])
        self.assertFalse(safe["agent_invoked_secure_drop_allowed"])
        self.assertFalse(safe["automation_invoked_secure_drop_allowed"])
        self.assertFalse(safe["secure_drop_send_permitted"])
        self.assertFalse(safe["secure_drop_receive_permitted"])

    def test_hidden_fabric_runtime_semantics_fail_closed(self):
        profile = self._profile()
        cases = [("not-object", "not-a-dict")]

        missing = copy.deepcopy(profile)
        missing.pop("fabric_capability_labels")
        cases.append(("missing", missing))

        unsupported = copy.deepcopy(profile)
        unsupported["fabric_interop_a2a_audit_profile_contract_version"] = 999
        cases.append(("unsupported", unsupported))

        unknown = copy.deepcopy(profile)
        unknown["unexpected"] = "metadata"
        cases.append(("unknown", unknown))

        nested_unknown = copy.deepcopy(profile)
        nested_unknown["fabric_capability_labels"][0]["runner"] = "execute"
        cases.append(("nested-unknown", nested_unknown))

        unsafe_strings = {
            "opaque-traffic": ("fabric_boundary_statement", "opaque traffic allowed"),
            "covert-channel": ("fabric_boundary_statement", "covert channel"),
            "agpl-codec": ("fabric_boundary_statement", "bundled AGPL codec"),
            "glossopetrae": ("fabric_boundary_statement", "GLOSSOPETRAE vendoring"),
            "st3gg": ("fabric_boundary_statement", "ST3GG vendoring"),
            "embedded-secret": ("fabric_boundary_statement", "secret access"),
            "vault-access": ("fabric_boundary_statement", "vault access"),
            "env-access": ("fabric_boundary_statement", "env access"),
            "api-key": ("fabric_boundary_statement", "api_key"),
            "network-call": ("fabric_boundary_statement", "network call"),
            "crypto": ("fabric_boundary_statement", "crypto implementation"),
            "transport": ("fabric_boundary_statement", "A2A transport"),
            "connector-install": ("fabric_boundary_statement", "connector install"),
            "pack-registration": ("fabric_boundary_statement", "pack registration"),
            "mcp-serving": ("fabric_boundary_statement", "MCP serving"),
            "mcp-client": ("fabric_boundary_statement", "MCP client"),
            "filesystem-autoscan": ("fabric_boundary_statement", "filesystem autoscan"),
            "provider-execution": ("fabric_boundary_statement", "provider execution"),
            "model-execution": ("fabric_boundary_statement", "model execution"),
            "cross-repo-mutation": ("fabric_boundary_statement", "cross-repo mutation"),
            "runtime-adapter": ("fabric_boundary_statement", "runtime adapter"),
            "real-mode": ("fabric_boundary_statement", "real-mode authorization"),
        }
        for name, (field, value) in unsafe_strings.items():
            payload = copy.deepcopy(profile)
            payload[field] = value
            cases.append((name, payload))

        for name, payload in cases:
            with self.subTest(case=name):
                result = validate_phase12l_profile(payload)

                self.assertFalse(result.compatible)
                safe = result.to_dict()
                self.assertFalse(safe["phase12l_authorizes_runtime"])
                self.assertFalse(safe["message_codec_implementation_added"])
                self.assertFalse(safe["a2a_transport_implementation_added"])
                self.assertFalse(safe["mcp_server_implementation_added"])
                self.assertFalse(safe["mcp_client_implementation_added"])
                self.assertFalse(safe["secure_drop_send_permitted"])
                self.assertFalse(safe["secure_drop_receive_permitted"])
                self.assertFalse(safe["crypto_implementation_added"])
                self.assertFalse(safe["credential_loading_added"])
                self.assertFalse(safe["vault_env_access_granted"])
                self.assertFalse(safe["secrets_access_granted"])
                self.assertFalse(safe["network_call_execution_granted"])
                self.assertFalse(safe["filesystem_autoscan_added"])
                self.assertFalse(safe["connector_installation_added"])
                self.assertFalse(safe["pack_registration_added"])
                self.assertFalse(safe["cross_repo_mutation_allowed"])
                self.assertFalse(safe["execution_permitted"])
                self.assertFalse(safe["real_mode_runtime_enabled"])

    def test_phase11_and_phase12_sources_remain_non_executing(self):
        phase11_summaries = (
            phase11_runtime_authorization_gap_ledger_status_summary(),
            phase11_planning_governance_closeout_status_summary(),
        )
        for summary in phase11_summaries:
            phase_label = summary.get("source_phase_range") or summary.get("phase_range")
            with self.subTest(phase11=phase_label):
                self.assertEqual(summary["runtime_stage"], "not-implemented")
                self.assertFalse(summary["execution_permitted"])
                self.assertFalse(summary["real_mode_runtime_enabled"])

        phase12_sources = (
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
            (
                phase12f_secure_drop_consumer_boundary(),
                validate_phase12f_secure_drop_consumer_boundary,
            ),
            (
                phase12g_production_readiness_coverage_matrix(),
                validate_phase12g_production_readiness_coverage_matrix,
            ),
            (
                phase12h_somatic_standalone_production_readiness_ownership_map(),
                validate_phase12h_somatic_standalone_production_readiness_ownership_map,
            ),
            (
                phase12i_profile(),
                validate_phase12i_profile,
            ),
            (
                phase12k_profile(),
                validate_phase12k_profile,
            ),
        )
        for payload, validator in phase12_sources:
            with self.subTest(kind=payload.get("profile_kind") or payload.get("matrix_kind")):
                result = validator(payload)

                self.assertTrue(result.compatible, result.errors)
                self.assertEqual(payload["runtime_stage"], "not-implemented")
                self.assertFalse(payload["execution_permitted"])
                self.assertFalse(payload["real_mode_runtime_enabled"])

    def test_phase12l_module_does_not_add_runtime_imports_or_true_flags(self):
        module_text = Path(phase12_contracts_module.__file__).read_text(encoding="utf-8").lower()

        for forbidden in (
            "class messagecodec",
            "def encode_message",
            "def decode_message",
            "import requests",
            "from requests",
            "urllib.",
            "socket.",
            "subprocess.",
            "mcp.server",
            "mcp.client",
            "websocket.",
            "httpx.",
            "aiohttp.",
            '"execution_permitted": true',
            '"real_mode_runtime_enabled": true',
            '"message_codec_implementation_added": true',
            '"a2a_transport_implementation_added": true',
            '"mcp_server_implementation_added": true',
            '"mcp_client_implementation_added": true',
            '"secure_drop_send_permitted": true',
            '"secure_drop_receive_permitted": true',
            '"crypto_implementation_added": true',
            '"network_call_execution_granted": true',
            '"connector_installation_added": true',
            '"pack_registration_added": true',
            '"cross_repo_mutation_allowed": true',
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, module_text)

    @staticmethod
    def _runtime_false_fields():
        return (
            "message_codec_implementation_added",
            "a2a_transport_implementation_added",
            "mcp_server_implementation_added",
            "mcp_client_implementation_added",
            "secure_drop_send_permitted",
            "secure_drop_receive_permitted",
            "crypto_implementation_added",
            "credential_loading_added",
            "vault_env_access_granted",
            "secrets_access_granted",
            "network_call_execution_granted",
            "filesystem_autoscan_added",
            "connector_installation_added",
            "pack_registration_added",
            "provider_execution_granted",
            "provider_call_execution_granted",
            "model_execution_granted",
            "runtime_model_execution_granted",
            "runtime_adapter_execution_granted",
            "active_grant_present",
            "real_mode_authorization_added",
            "connector_grant_present",
            "fabric_transfer_execution_granted",
            "ws_stream_execution_granted",
            "http_execution_granted",
            "mcp_tool_exposure_added",
            "task_execution_granted",
            "service_discovery_runtime_added",
            "schedule_enforcement_added",
            "filesystem_access_granted",
            "process_control_granted",
            "db_storage_write_added",
            "agent_invoked_secure_drop_allowed",
            "automation_invoked_secure_drop_allowed",
            "bundled_agpl_codec_allowed",
            "glossopetrae_vendoring_allowed",
            "st3gg_vendoring_allowed",
            "covert_channel_allowed",
            "opaque_message_acting_allowed",
            "untrusted_content_execution_added",
            "production_ready",
            "execution_permitted",
            "real_mode_runtime_enabled",
        )


if __name__ == "__main__":
    unittest.main()
