import copy
import json
import unittest
from pathlib import Path

from somatic.safety import phase12_contracts as phase12_contracts_module
from somatic.safety.phase12_contracts import (
    PHASE12G_PRODUCTION_READINESS_AREAS,
    PHASE12G_PRODUCTION_READINESS_MATRIX_KIND,
    PHASE12H_AUTHORIZATION_STATUS,
    PHASE12H_GRANT_STATUS,
    PHASE12H_LOCUS_OPTIONAL_UI_STATEMENT,
    PHASE12H_NON_AUTHORIZATION_STATEMENT,
    PHASE12H_OPTIONAL_INTEGRATION_PEERS,
    PHASE12H_OPTIONAL_INTEGRATION_ROLES,
    PHASE12H_PEER_INTEGRATION_STATEMENT,
    PHASE12H_READINESS_PHASE,
    PHASE12H_SECURE_DROP_STATEMENT,
    PHASE12H_SOMATIC_STANDALONE_AREAS,
    PHASE12H_STANDALONE_OWNERSHIP_MATRIX_CONTRACT_VERSION,
    PHASE12H_STANDALONE_OWNERSHIP_MATRIX_KIND,
    PHASE12H_STANDALONE_UI_STATEMENT,
    phase12a_runtime_authorization_design_charter,
    phase12b_runtime_authorization_record_candidate,
    phase12c_visual_supervision_capability_profile,
    phase12d_visual_desktop_consent_gate_requirements,
    phase12e_physiological_sensor_capability_profile,
    phase12f_secure_drop_consumer_boundary,
    phase12g_production_readiness_coverage_matrix,
    phase12h_somatic_standalone_production_readiness_ownership_map,
    phase12h_somatic_standalone_production_readiness_ownership_map_status_summary,
    validate_phase12a_runtime_authorization_design_charter,
    validate_phase12b_runtime_authorization_record_candidate,
    validate_phase12c_visual_supervision_capability_profile,
    validate_phase12d_visual_desktop_consent_gate_requirements,
    validate_phase12e_physiological_sensor_capability_profile,
    validate_phase12f_secure_drop_consumer_boundary,
    validate_phase12g_production_readiness_coverage_matrix,
    validate_phase12h_somatic_standalone_production_readiness_ownership_map,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
OWNERSHIP_FIXTURE = (
    REPO_ROOT
    / "fixtures"
    / "reviews"
    / "phase-12h-somatic-standalone-production-readiness-ownership-map-v1.json"
)
UNSAFE_PHASE12H_SENTINELS = (
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
    "raw_screenshot",
    "raw_ocr",
    "medical diagnosis",
    "clinical recommendation",
    "runtime-permission-granted",
    "production-ready",
    "deployment-enabled",
    "runtime-enabled",
    "cross-repo-mutation-executed",
    "frontend-service-started",
    "backend-service-started",
    "database-connected",
    "secure-drop-send-executed",
)


class Phase12HSomaticStandaloneProductionReadinessOwnershipMapTests(unittest.TestCase):
    def test_fixture_matches_deterministic_helper(self):
        fixture = json.loads(OWNERSHIP_FIXTURE.read_text(encoding="utf-8"))
        generated = phase12h_somatic_standalone_production_readiness_ownership_map()

        self.assertEqual(fixture, generated)
        self.assertEqual(
            fixture["standalone_ownership_matrix_contract_version"],
            PHASE12H_STANDALONE_OWNERSHIP_MATRIX_CONTRACT_VERSION,
        )
        self.assertEqual(fixture["matrix_kind"], PHASE12H_STANDALONE_OWNERSHIP_MATRIX_KIND)
        self.assertTrue(
            fixture["standalone_ownership_matrix_id"].startswith("p12h-standalone-ownership-")
        )
        self.assertEqual(fixture["source_phase"], "12G")
        self.assertEqual(fixture["readiness_phase"], PHASE12H_READINESS_PHASE)
        self.assertEqual(fixture["authorization_status"], PHASE12H_AUTHORIZATION_STATUS)
        self.assertEqual(fixture["grant_status"], PHASE12H_GRANT_STATUS)
        self.assertEqual(fixture["runtime_stage"], "not-implemented")
        self.assertFalse(fixture["phase12h_marks_somatic_production_ready"])
        self.assertFalse(fixture["phase12h_authorizes_runtime"])
        self.assertTrue(fixture["somatic_standalone_ownership_retained"])
        self.assertTrue(fixture["external_integrations_optional"])
        self.assertTrue(fixture["optional_peer_labels_are_integration_metadata_only"])
        self.assertFalse(fixture["external_repo_integration_replaces_somatic_standalone_path"])
        self.assertFalse(fixture["cross_repo_mutation_permitted"])
        self.assertFalse(fixture["external_repo_tasks_executed_by_somatic"])
        self.assertFalse(fixture["production_ready"])
        self.assertEqual(fixture["standalone_ownership_entry_count"], 19)
        self.assertEqual(fixture["somatic_standalone_area_count"], 19)
        self.assertEqual(fixture["repo_production_ready_count"], 0)
        self.assertEqual(
            fixture["source_production_readiness_coverage_matrix"]["matrix_kind"],
            PHASE12G_PRODUCTION_READINESS_MATRIX_KIND,
        )
        self.assertEqual(fixture["standalone_ui_statement"], PHASE12H_STANDALONE_UI_STATEMENT)
        self.assertEqual(
            fixture["locus_optional_ui_statement"], PHASE12H_LOCUS_OPTIONAL_UI_STATEMENT
        )
        self.assertEqual(fixture["peer_integration_statement"], PHASE12H_PEER_INTEGRATION_STATEMENT)
        self.assertEqual(fixture["secure_drop_statement"], PHASE12H_SECURE_DROP_STATEMENT)
        self.assertEqual(
            fixture["phase12h_non_authorization_statement"],
            PHASE12H_NON_AUTHORIZATION_STATEMENT,
        )
        self.assertEqual(
            [entry["production_area_id"] for entry in fixture["standalone_ownership_entries"]],
            [area[0] for area in PHASE12G_PRODUCTION_READINESS_AREAS],
        )
        self.assertEqual(
            [entry["production_area_id"] for entry in fixture["standalone_ownership_entries"]],
            [area[0] for area in PHASE12H_SOMATIC_STANDALONE_AREAS],
        )
        self.assertEqual(
            fixture["optional_integration_peer_count"],
            sum(
                entry["optional_integration_peer_count"]
                for entry in fixture["standalone_ownership_entries"]
            ),
        )
        for field in self._runtime_flag_fields():
            with self.subTest(field=field):
                self.assertFalse(fixture[field])
        result = validate_phase12h_somatic_standalone_production_readiness_ownership_map(fixture)
        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(result.authorization_wording_count, 0)

    def test_status_summary_is_compact_and_non_executing(self):
        summary = phase12h_somatic_standalone_production_readiness_ownership_map_status_summary()

        self.assertEqual(summary["source_phase"], "12G")
        self.assertEqual(
            summary["readiness_phase"], "standalone-ownership-and-integration-map-only"
        )
        self.assertEqual(summary["authorization_status"], "not-authorized")
        self.assertEqual(summary["grant_status"], "no-grant")
        self.assertEqual(summary["standalone_ownership_entry_count"], 19)
        self.assertEqual(summary["somatic_standalone_area_count"], 19)
        self.assertEqual(summary["repo_production_ready_count"], 0)
        self.assertFalse(summary["phase12h_marks_somatic_production_ready"])
        self.assertFalse(summary["phase12h_authorizes_runtime"])
        self.assertTrue(summary["somatic_standalone_ownership_retained"])
        self.assertTrue(summary["external_integrations_optional"])
        self.assertFalse(summary["external_repo_integration_replaces_somatic_standalone_path"])
        self.assertFalse(summary["cross_repo_mutation_permitted"])
        self.assertFalse(summary["external_repo_tasks_executed_by_somatic"])
        self.assertEqual(summary["runtime_stage"], "not-implemented")
        for field in self._runtime_flag_fields():
            with self.subTest(field=field):
                self.assertFalse(summary[field])

    def test_somatic_retains_standalone_ownership_for_all_areas(self):
        matrix = phase12h_somatic_standalone_production_readiness_ownership_map()

        self.assertEqual(len(matrix["standalone_ownership_entries"]), 19)
        for entry in matrix["standalone_ownership_entries"]:
            with self.subTest(area=entry["production_area_id"]):
                self.assertIn("Somatic", entry["somatic_standalone_responsibility"])
                self.assertIn("Somatic", entry["current_somatic_coverage"])
                self.assertTrue(entry["external_integration_optional"])
                self.assertFalse(entry["external_integration_replaces_somatic_standalone_path"])
                self.assertTrue(entry["runtime_blocked"])
                self.assertTrue(entry["metadata_only"])
                self.assertFalse(entry["execution_permitted"])
                self.assertFalse(entry["real_mode_runtime_enabled"])
                for peer in entry["optional_integration_peers"]:
                    self.assertIn(peer["peer_label"], PHASE12H_OPTIONAL_INTEGRATION_PEERS)
                    self.assertIn(peer["integration_role"], PHASE12H_OPTIONAL_INTEGRATION_ROLES)
                    self.assertTrue(peer["optional_integration_metadata_only"])
                    self.assertFalse(peer["required_dependency_for_somatic"])
                    self.assertFalse(peer["replaces_somatic_standalone_path"])
                    self.assertFalse(peer["runtime_grant_created"])
                    self.assertFalse(peer["cross_repo_mutation_permitted"])
                    self.assertFalse(peer["execution_permitted"])
                    self.assertFalse(peer["real_mode_runtime_enabled"])

    def test_optional_integration_peers_cannot_become_required_or_runtime_grants(self):
        matrix = phase12h_somatic_standalone_production_readiness_ownership_map()
        unsafe = copy.deepcopy(matrix)
        peer = next(
            peer
            for entry in unsafe["standalone_ownership_entries"]
            for peer in entry["optional_integration_peers"]
        )
        peer["required_dependency_for_somatic"] = True
        peer["replaces_somatic_standalone_path"] = True
        peer["runtime_grant_created"] = True
        peer["cross_repo_mutation_permitted"] = True
        peer["execution_permitted"] = True
        peer["real_mode_runtime_enabled"] = True

        result = validate_phase12h_somatic_standalone_production_readiness_ownership_map(unsafe)

        self.assertFalse(result.compatible)
        for entry in result.sanitized_record["standalone_ownership_entries"]:
            for safe_peer in entry["optional_integration_peers"]:
                self.assertFalse(safe_peer["required_dependency_for_somatic"])
                self.assertFalse(safe_peer["replaces_somatic_standalone_path"])
                self.assertFalse(safe_peer["runtime_grant_created"])
                self.assertFalse(safe_peer["cross_repo_mutation_permitted"])
                self.assertFalse(safe_peer["execution_permitted"])
                self.assertFalse(safe_peer["real_mode_runtime_enabled"])

    def test_status_and_owner_words_never_enable_execution(self):
        matrix = phase12h_somatic_standalone_production_readiness_ownership_map()
        finalize = phase12_contracts_module._finalize_phase12h_standalone_ownership_matrix
        for wording in (
            "handoff",
            "routed",
            "owned",
            "integrated",
            "connected",
            "production-ready",
            "deployed",
            "authorized",
            "approved",
            "ready",
            "enabled",
            "configured",
        ):
            with self.subTest(wording=wording):
                unsafe = copy.deepcopy(matrix)
                unsafe["authorization_status"] = wording
                unsafe["grant_status"] = wording
                unsafe["matrix_status"] = wording
                unsafe["phase12h_marks_somatic_production_ready"] = True
                unsafe["phase12h_authorizes_runtime"] = True
                unsafe["cross_repo_mutation_permitted"] = True
                unsafe["production_ready"] = True
                unsafe["execution_permitted"] = True
                unsafe["real_mode_runtime_enabled"] = True
                unsafe = finalize(unsafe)
                result = validate_phase12h_somatic_standalone_production_readiness_ownership_map(
                    unsafe
                )

                self.assertFalse(result.compatible)
                self.assertFalse(result.to_dict()["phase12h_marks_somatic_production_ready"])
                self.assertFalse(result.to_dict()["phase12h_authorizes_runtime"])
                self.assertFalse(result.to_dict()["cross_repo_mutation_permitted"])
                self.assertFalse(result.to_dict()["production_ready"])
                self.assertFalse(result.to_dict()["execution_permitted"])
                self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])

    def test_external_labels_cannot_imply_somatic_lacks_standalone_ownership(self):
        matrix = phase12h_somatic_standalone_production_readiness_ownership_map()
        unsafe = copy.deepcopy(matrix)
        unsafe["somatic_standalone_ownership_retained"] = False
        unsafe["external_integrations_optional"] = False
        unsafe["external_repo_integration_replaces_somatic_standalone_path"] = True
        unsafe["standalone_ownership_entries"][0]["somatic_standalone_responsibility"] = (
            "external-owner handoff owner; somatic lacks standalone"
        )

        result = validate_phase12h_somatic_standalone_production_readiness_ownership_map(unsafe)

        self.assertFalse(result.compatible)
        self.assertIn("phase12h_ownership_map_standalone_ownership_contradiction", result.errors)
        self.assertTrue(result.sanitized_record["somatic_standalone_ownership_retained"])
        self.assertTrue(result.sanitized_record["external_integrations_optional"])
        self.assertFalse(
            result.sanitized_record["external_repo_integration_replaces_somatic_standalone_path"]
        )

    def test_no_other_repo_mutation_is_introduced(self):
        matrix = phase12h_somatic_standalone_production_readiness_ownership_map()
        unsafe = copy.deepcopy(matrix)
        unsafe["cross_repo_mutation_permitted"] = True
        unsafe["external_repo_tasks_executed_by_somatic"] = True
        unsafe["standalone_ownership_entries"][0]["optional_integration_peers"][0][
            "cross_repo_mutation_permitted"
        ] = True

        result = validate_phase12h_somatic_standalone_production_readiness_ownership_map(unsafe)

        self.assertFalse(result.compatible)
        self.assertFalse(result.sanitized_record["cross_repo_mutation_permitted"])
        self.assertFalse(result.sanitized_record["external_repo_tasks_executed_by_somatic"])

    def test_production_runtime_fields_cannot_validate(self):
        for field in self._runtime_flag_fields():
            with self.subTest(field=field):
                unsafe = phase12h_somatic_standalone_production_readiness_ownership_map()
                unsafe[field] = True

                result = validate_phase12h_somatic_standalone_production_readiness_ownership_map(
                    unsafe
                )

                self.assertFalse(result.compatible)
                self.assertFalse(result.sanitized_record[field])

    def test_validator_fails_closed_for_unsafe_or_contradictory_records(self):
        matrix = phase12h_somatic_standalone_production_readiness_ownership_map()
        cases = [("not-object", "not-a-dict")]

        missing = copy.deepcopy(matrix)
        missing.pop("standalone_ownership_entries")
        cases.append(("missing", missing))

        unsupported = copy.deepcopy(matrix)
        unsupported["standalone_ownership_matrix_contract_version"] = 999
        cases.append(("unsupported", unsupported))

        unknown = copy.deepcopy(matrix)
        unknown["unexpected"] = "metadata"
        cases.append(("unknown", unknown))

        nested_unknown = copy.deepcopy(matrix)
        nested_unknown["standalone_ownership_entries"][0]["task"] = "execute"
        cases.append(("nested-unknown", nested_unknown))

        peer_unknown = copy.deepcopy(matrix)
        peer_unknown["standalone_ownership_entries"][0]["optional_integration_peers"][0][
            "repo_task"
        ] = "execute"
        cases.append(("peer-unknown", peer_unknown))

        production_ready = copy.deepcopy(matrix)
        production_ready["matrix_status"] = "production-ready"
        production_ready["phase12h_marks_somatic_production_ready"] = True
        production_ready["production_ready"] = True
        cases.append(("production-ready-claim", production_ready))

        deployed = copy.deepcopy(matrix)
        deployed["matrix_status"] = "deployment-enabled"
        deployed["deployment_code_added"] = True
        cases.append(("deployment-enabled-claim", deployed))

        unsafe_url = copy.deepcopy(matrix)
        unsafe_url["standalone_ownership_entries"][0]["remaining_somatic_gap"] = (
            "https://example.invalid"
        )
        cases.append(("url", unsafe_url))

        absolute_path = copy.deepcopy(matrix)
        absolute_path["standalone_ownership_entries"][0]["remaining_somatic_gap"] = (
            "C:\\Users\\Private"
        )
        cases.append(("absolute-path", absolute_path))

        api_key = copy.deepcopy(matrix)
        api_key["standalone_ownership_entries"][0]["current_somatic_coverage"] = "sk-live"
        cases.append(("api-key", api_key))

        vault_ref = copy.deepcopy(matrix)
        vault_ref["standalone_ownership_entries"][0]["current_somatic_coverage"] = "vault://secret"
        cases.append(("vault-ref", vault_ref))

        source_id = copy.deepcopy(matrix)
        source_id["source_production_readiness_coverage_matrix"]["source_id"] = "source_id"
        cases.append(("source-id", source_id))

        raw_payload = copy.deepcopy(matrix)
        raw_payload["standalone_ownership_entries"][0]["current_somatic_coverage"] = "raw_csi"
        cases.append(("raw-sensor", raw_payload))

        screenshot = copy.deepcopy(matrix)
        screenshot["standalone_ownership_entries"][0]["current_somatic_coverage"] = "raw_screenshot"
        cases.append(("screenshot", screenshot))

        clinical = copy.deepcopy(matrix)
        clinical["standalone_ownership_entries"][1]["somatic_standalone_responsibility"] = (
            "medical diagnosis"
        )
        cases.append(("clinical", clinical))

        boolean_count = copy.deepcopy(matrix)
        boolean_count["standalone_ownership_entry_count"] = True
        cases.append(("boolean-count", boolean_count))

        string_count = copy.deepcopy(matrix)
        string_count["optional_integration_peer_count"] = "15"
        cases.append(("string-count", string_count))

        mutation = copy.deepcopy(matrix)
        mutation["cross_repo_mutation_permitted"] = True
        mutation["standalone_ownership_entries"][2]["optional_integration_peers"][0][
            "cross_repo_mutation_permitted"
        ] = True
        cases.append(("cross-repo-mutation", mutation))

        for name, payload in cases:
            with self.subTest(case=name):
                result = validate_phase12h_somatic_standalone_production_readiness_ownership_map(
                    payload
                )
                encoded = self._safe_encoded(result.sanitized_record)

                self.assertFalse(result.compatible)
                self.assertFalse(result.to_dict()["execution_permitted"])
                self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])
                self.assertFalse(result.to_dict()["production_ready"])
                for sentinel in UNSAFE_PHASE12H_SENTINELS:
                    self.assertNotIn(sentinel, encoded)

    def test_phase12_sources_remain_non_executing(self):
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
            (
                phase12f_secure_drop_consumer_boundary(),
                validate_phase12f_secure_drop_consumer_boundary,
            ),
            (
                phase12g_production_readiness_coverage_matrix(),
                validate_phase12g_production_readiness_coverage_matrix,
            ),
        )

        for payload, validator in sources:
            with self.subTest(kind=payload.get("packet_kind") or payload.get("matrix_kind")):
                result = validator(payload)

                self.assertTrue(result.compatible, result.errors)
                self.assertEqual(payload["runtime_stage"], "not-implemented")
                self.assertFalse(payload["execution_permitted"])
                self.assertFalse(payload["real_mode_runtime_enabled"])

    def test_phase12h_module_does_not_add_production_runtime_imports_or_true_flags(self):
        module_text = Path(phase12_contracts_module.__file__).read_text(encoding="utf-8").lower()

        for forbidden in (
            "import fastapi",
            "from fastapi",
            "import django",
            "from django",
            "import flask",
            "from flask",
            "import sqlalchemy",
            "from sqlalchemy",
            "import psycopg",
            "from psycopg",
            "import redis",
            "from redis",
            "import boto3",
            "from boto3",
            "import kubernetes",
            "from kubernetes",
            "requests.",
            "urllib.",
            "socket.",
            "subprocess.",
            "uvicorn",
            "gunicorn",
            "nginx",
            "terraform",
            '"execution_permitted": true',
            '"real_mode_runtime_enabled": true',
            '"cross_repo_mutation_permitted": true',
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, module_text)

    @staticmethod
    def _runtime_flag_fields():
        return (
            "frontend_implementation_added",
            "backend_service_added",
            "production_api_service_added",
            "database_storage_added",
            "auth_runtime_added",
            "rate_limiting_runtime_added",
            "cache_runtime_added",
            "cdn_runtime_added",
            "load_balancer_runtime_added",
            "logging_service_added",
            "secrets_backend_runtime_added",
            "service_registry_runtime_added",
            "service_discovery_runtime_added",
            "deployment_code_added",
            "hosting_runtime_added",
            "cloud_compute_runtime_added",
            "network_call_execution_granted",
            "runtime_adapter_execution_granted",
            "device_connection_execution_granted",
            "sensor_processing_execution_granted",
            "secure_drop_send_permitted",
            "secure_drop_receive_permitted",
            "provider_execution_granted",
            "model_execution_granted",
            "active_grant_present",
            "real_mode_authorization_added",
            "production_ready",
            "execution_permitted",
            "real_mode_runtime_enabled",
        )

    @staticmethod
    def _safe_encoded(payload):
        return (
            json.dumps(payload, sort_keys=True)
            .lower()
            .replace("\\", "/")
            .replace("production-ready", "prod-ready-claim")
        )


if __name__ == "__main__":
    unittest.main()
