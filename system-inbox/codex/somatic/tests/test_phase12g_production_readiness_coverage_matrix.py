import copy
import json
import unittest
from pathlib import Path

from somatic.safety import phase12_contracts as phase12_contracts_module
from somatic.safety.phase12_contracts import (
    PHASE12G_AUTHORIZATION_STATUS,
    PHASE12G_GRANT_STATUS,
    PHASE12G_PRODUCTION_READINESS_AREAS,
    PHASE12G_PRODUCTION_READINESS_MATRIX_CONTRACT_VERSION,
    PHASE12G_PRODUCTION_READINESS_MATRIX_KIND,
    PHASE12G_READINESS_PHASE,
    phase12a_runtime_authorization_design_charter,
    phase12b_runtime_authorization_record_candidate,
    phase12c_visual_supervision_capability_profile,
    phase12d_visual_desktop_consent_gate_requirements,
    phase12e_physiological_sensor_capability_profile,
    phase12f_secure_drop_consumer_boundary,
    phase12g_production_readiness_coverage_matrix,
    phase12g_production_readiness_coverage_matrix_status_summary,
    validate_phase12a_runtime_authorization_design_charter,
    validate_phase12b_runtime_authorization_record_candidate,
    validate_phase12c_visual_supervision_capability_profile,
    validate_phase12d_visual_desktop_consent_gate_requirements,
    validate_phase12e_physiological_sensor_capability_profile,
    validate_phase12f_secure_drop_consumer_boundary,
    validate_phase12g_production_readiness_coverage_matrix,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MATRIX_FIXTURE = (
    REPO_ROOT / "fixtures" / "reviews" / "phase-12g-production-readiness-coverage-matrix-v1.json"
)
UNSAFE_PHASE12G_SENTINELS = (
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
    "deployment-enabled",
    "runtime-enabled",
    "frontend-service-started",
    "backend-service-started",
    "database-connected",
    "secret-value-present",
    "secure-drop-send-executed",
)


class Phase12GProductionReadinessCoverageMatrixTests(unittest.TestCase):
    def test_fixture_matches_deterministic_helper(self):
        fixture = json.loads(MATRIX_FIXTURE.read_text(encoding="utf-8"))
        generated = phase12g_production_readiness_coverage_matrix()

        self.assertEqual(fixture, generated)
        self.assertEqual(
            fixture["production_readiness_matrix_contract_version"],
            PHASE12G_PRODUCTION_READINESS_MATRIX_CONTRACT_VERSION,
        )
        self.assertEqual(fixture["matrix_kind"], PHASE12G_PRODUCTION_READINESS_MATRIX_KIND)
        self.assertTrue(
            fixture["production_readiness_matrix_id"].startswith("p12g-production-matrix-")
        )
        self.assertEqual(fixture["readiness_phase"], PHASE12G_READINESS_PHASE)
        self.assertEqual(fixture["authorization_status"], PHASE12G_AUTHORIZATION_STATUS)
        self.assertEqual(fixture["grant_status"], PHASE12G_GRANT_STATUS)
        self.assertEqual(fixture["runtime_stage"], "not-implemented")
        self.assertFalse(fixture["phase12g_makes_somatic_production_ready"])
        self.assertFalse(fixture["phase12g_authorizes_runtime"])
        self.assertTrue(fixture["phase12g_coverage_labels_are_metadata_only"])
        self.assertEqual(fixture["production_readiness_area_count"], 19)
        self.assertEqual(fixture["somatic_direct_area_count"], 4)
        self.assertEqual(fixture["somatic_boundary_only_area_count"], 7)
        self.assertEqual(fixture["external_owner_area_count"], 8)
        self.assertEqual(fixture["not_applicable_yet_area_count"], 0)
        self.assertEqual(
            [area["area_id"] for area in fixture["production_readiness_areas"]],
            [area[0] for area in PHASE12G_PRODUCTION_READINESS_AREAS],
        )
        for field in self._runtime_flag_fields():
            with self.subTest(field=field):
                self.assertFalse(fixture[field])
        for area in fixture["production_readiness_areas"]:
            with self.subTest(area=area["area_id"]):
                self.assertTrue(area["metadata_only"])
                self.assertFalse(area["phase12g_area_grants_runtime"])
                self.assertFalse(area["external_owner_entry_grants_runtime"])
                self.assertFalse(area["execution_permitted"])
                self.assertFalse(area["real_mode_runtime_enabled"])
        result = validate_phase12g_production_readiness_coverage_matrix(fixture)
        self.assertTrue(result.compatible, result.errors)
        self.assertEqual(result.authorization_wording_count, 0)

    def test_status_summary_is_compact_and_non_executing(self):
        summary = phase12g_production_readiness_coverage_matrix_status_summary()

        self.assertEqual(summary["readiness_phase"], "coverage-matrix-only")
        self.assertEqual(summary["authorization_status"], "not-authorized")
        self.assertEqual(summary["grant_status"], "no-grant")
        self.assertEqual(summary["production_readiness_area_count"], 19)
        self.assertEqual(summary["somatic_direct_area_count"], 4)
        self.assertEqual(summary["somatic_boundary_only_area_count"], 7)
        self.assertEqual(summary["external_owner_area_count"], 8)
        self.assertFalse(summary["phase12g_makes_somatic_production_ready"])
        self.assertFalse(summary["phase12g_authorizes_runtime"])
        self.assertTrue(summary["phase12g_coverage_labels_are_metadata_only"])
        self.assertEqual(summary["runtime_stage"], "not-implemented")
        for field in self._runtime_flag_fields(include_active_grant=False):
            with self.subTest(field=field):
                self.assertFalse(summary[field])

    def test_status_words_never_enable_execution(self):
        matrix = phase12g_production_readiness_coverage_matrix()
        finalize = phase12_contracts_module._finalize_phase12g_production_readiness_coverage_matrix
        for wording in (
            "production-ready",
            "deployed",
            "available",
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
                unsafe["phase12g_makes_somatic_production_ready"] = True
                unsafe["phase12g_authorizes_runtime"] = True
                unsafe["deployment_code_added"] = True
                unsafe["execution_permitted"] = True
                unsafe["real_mode_runtime_enabled"] = True
                unsafe = finalize(unsafe)
                result = validate_phase12g_production_readiness_coverage_matrix(unsafe)

                self.assertFalse(result.compatible)
                self.assertFalse(result.to_dict()["phase12g_makes_somatic_production_ready"])
                self.assertFalse(result.to_dict()["phase12g_authorizes_runtime"])
                self.assertFalse(result.to_dict()["execution_permitted"])
                self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])

    def test_external_owner_entries_cannot_become_runtime_grants(self):
        matrix = phase12g_production_readiness_coverage_matrix()
        external_index = next(
            index
            for index, area in enumerate(matrix["production_readiness_areas"])
            if area["somatic_responsibility"] == "external-owner"
        )
        unsafe = copy.deepcopy(matrix)
        unsafe["production_readiness_areas"][external_index]["phase12g_area_grants_runtime"] = True
        unsafe["production_readiness_areas"][external_index][
            "external_owner_entry_grants_runtime"
        ] = True
        unsafe["production_readiness_areas"][external_index]["execution_permitted"] = True

        result = validate_phase12g_production_readiness_coverage_matrix(unsafe)

        self.assertFalse(result.compatible)
        safe_areas = result.sanitized_record["production_readiness_areas"]
        for area in safe_areas:
            self.assertFalse(area["phase12g_area_grants_runtime"])
            self.assertFalse(area["external_owner_entry_grants_runtime"])
            self.assertFalse(area["execution_permitted"])

    def test_production_runtime_fields_cannot_validate(self):
        for field in self._runtime_flag_fields():
            with self.subTest(field=field):
                unsafe = phase12g_production_readiness_coverage_matrix()
                unsafe[field] = True

                result = validate_phase12g_production_readiness_coverage_matrix(unsafe)

                self.assertFalse(result.compatible)
                self.assertFalse(result.sanitized_record[field])

    def test_validator_fails_closed_for_unsafe_or_contradictory_records(self):
        matrix = phase12g_production_readiness_coverage_matrix()
        cases = [("not-object", "not-a-dict")]

        missing = copy.deepcopy(matrix)
        missing.pop("production_readiness_areas")
        cases.append(("missing", missing))

        unsupported = copy.deepcopy(matrix)
        unsupported["production_readiness_matrix_contract_version"] = 999
        cases.append(("unsupported", unsupported))

        unknown = copy.deepcopy(matrix)
        unknown["unexpected"] = "metadata"
        cases.append(("unknown", unknown))

        production_ready = copy.deepcopy(matrix)
        production_ready["matrix_status"] = "production-ready"
        production_ready["phase12g_makes_somatic_production_ready"] = True
        cases.append(("production-ready-claim", production_ready))

        deployed = copy.deepcopy(matrix)
        deployed["matrix_status"] = "deployment-enabled"
        deployed["deployment_code_added"] = True
        cases.append(("deployment-enabled-claim", deployed))

        unsafe_url = copy.deepcopy(matrix)
        unsafe_url["production_readiness_areas"][0]["remaining_gap_summary"] = (
            "https://example.invalid"
        )
        cases.append(("url", unsafe_url))

        absolute_path = copy.deepcopy(matrix)
        absolute_path["production_readiness_areas"][0]["current_coverage_summary"] = (
            "C:\\Users\\Private"
        )
        cases.append(("absolute-path", absolute_path))

        boolean_count = copy.deepcopy(matrix)
        boolean_count["production_readiness_area_count"] = True
        cases.append(("boolean-count", boolean_count))

        string_count = copy.deepcopy(matrix)
        string_count["external_owner_area_count"] = "8"
        cases.append(("string-count", string_count))

        raw_payload = copy.deepcopy(matrix)
        raw_payload["source_secure_drop_consumer_boundary"]["raw_csi"] = "42"
        cases.append(("raw-sensor", raw_payload))

        clinical = copy.deepcopy(matrix)
        clinical["production_readiness_areas"][0]["remaining_gap_summary"] = "medical diagnosis"
        cases.append(("clinical", clinical))

        for name, payload in cases:
            with self.subTest(case=name):
                result = validate_phase12g_production_readiness_coverage_matrix(payload)
                encoded = self._safe_encoded((result.to_dict(), result.sanitized_record))

                self.assertFalse(result.compatible)
                self.assertFalse(result.to_dict()["execution_permitted"])
                self.assertFalse(result.to_dict()["real_mode_runtime_enabled"])
                for sentinel in UNSAFE_PHASE12G_SENTINELS:
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
            (
                phase12f_secure_drop_consumer_boundary(),
                validate_phase12f_secure_drop_consumer_boundary,
            ),
        )

        for payload, validator in sources:
            with self.subTest(kind=payload.get("profile_kind") or payload.get("boundary_kind")):
                result = validator(payload)

                self.assertTrue(result.compatible, result.errors)
                self.assertEqual(payload["runtime_stage"], "not-implemented")
                self.assertFalse(payload["execution_permitted"])
                self.assertFalse(payload["real_mode_runtime_enabled"])

    def test_phase12g_module_does_not_add_production_runtime_imports(self):
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
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, module_text)

    @staticmethod
    def _runtime_flag_fields(*, include_active_grant: bool = True):
        fields = (
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
            "execution_permitted",
            "real_mode_runtime_enabled",
        )
        if include_active_grant:
            return (*fields[:-2], "active_grant_present", *fields[-2:])
        return fields

    @staticmethod
    def _safe_encoded(payload):
        return (
            json.dumps(payload, sort_keys=True)
            .lower()
            .replace("\\", "/")
            .replace("not-authorized", "not-runtime-status")
            .replace("authorization_status", "runtime_status")
            .replace("phase12g_makes_somatic_production_ready", "p12g_prod_false")
            .replace("production_readiness", "prod_matrix")
            .replace("secure_drop", "secure_xfer")
            .replace("secrets_backend", "secret_store")
        )


if __name__ == "__main__":
    unittest.main()
