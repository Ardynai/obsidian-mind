import copy
import json
import tempfile
import unittest
from pathlib import Path

from somatic.sensors.registry import (
    CSI_EVIDENCE_PACK_ARTIFACT_REF,
    CSI_EVIDENCE_PROVIDER_ID,
    sanitize_sensor_evidence_input_spec,
    sensor_evidence_artifact_specs,
    sensor_evidence_provider_ids,
    sensor_evidence_provider_metadata,
    validate_sensor_evidence_workflow_config,
    workflow_sensor_evidence_fixture_refs,
    workflow_sensor_evidence_groups,
)
from somatic.workflow_loader import (
    WorkflowValidationError,
    load_workflow,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
NOF1_FIXTURE = REPO_ROOT / "fixtures" / "workflows" / "valid-n-of-1.yaml"
TOURNAMENT_FIXTURE = REPO_ROOT / "fixtures" / "workflows" / "valid-hypothesis-tournament.yaml"
TOY_EXAMPLE = REPO_ROOT / "examples" / "sensor-evidence-demo" / "toy-counter-fixture-workflow.yaml"
DOCUMENT_EXAMPLE = (
    REPO_ROOT / "examples" / "document-evidence-demo" / "document-fixture-workflow.yaml"
)


class SensorEvidenceRegistryTests(unittest.TestCase):
    def test_registry_lists_csi_environment_and_toy_with_sanitized_metadata(self):
        provider_ids = sensor_evidence_provider_ids()
        metadata = sensor_evidence_provider_metadata()
        specs = sensor_evidence_artifact_specs()

        self.assertEqual(
            provider_ids,
            ("wifi-csi", "environment-fixture", "toy-counter-fixture", "document-fixture"),
        )
        self.assertEqual(
            specs["csi_evidence_pack"]["evidence_kind"],
            "csi-evidence-pack",
        )
        self.assertEqual(
            specs["environment_evidence_pack"]["provider_kind"],
            "environment-fixture",
        )
        toy_metadata = next(
            item for item in metadata if item["provider_id"] == "toy-counter-fixture"
        )
        self.assertEqual(
            toy_metadata["artifact_ref"],
            "artifacts/toy_counter_evidence_pack.json",
        )
        self.assertEqual(
            specs["toy_counter_evidence_pack"]["provider_kind"],
            "toy-counter-fixture",
        )
        self.assertEqual(
            specs["document_evidence_pack"]["provider_kind"],
            "document-fixture",
        )
        self.assertEqual(
            specs["document_evidence_pack"]["evidence_kind"],
            "document-evidence-pack",
        )
        encoded = (
            json.dumps(metadata, sort_keys=True)
            .lower()
            .replace(
                "real-mode-authorization-missing",
                "real-mode-gap-missing",
            )
        )
        encoded = (
            encoded.replace("not-authorized", "not-runtime-status")
            .replace("authorization_status", "runtime_status")
            .replace(
                "runtime_authorization_gap_ledger_contract_version",
                "runtime_gap_ledger_contract_version",
            )
        )
        for forbidden in (
            "sample-esp32-csi",
            "sample-amplitude-phase",
            "sample-csi-jsonl",
            "environment-parsed.csv",
            "environment-mixed.csv",
            "toy-counter-parsed.csv",
            "toy-counter-mixed.csv",
            "fixture://",
            "fixtures/",
            "c:\\",
            "source_id",
            "source_ids",
            "private_ref",
            "unsafe_ref",
            "provider_payload",
            "provider_payload_body",
            "parser_report_body",
            "parser_summary_body",
            "api_key",
            "access_token",
            "secret_value",
            "authorization",
            "raw_values",
            "raw_signal",
            "signal_values",
            "medical",
            "clinical",
            "diagnosis",
            "treatment",
            "health",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)

    def test_valid_workflows_pass_sensor_evidence_config_validation(self):
        for fixture in (NOF1_FIXTURE, TOURNAMENT_FIXTURE, TOY_EXAMPLE, DOCUMENT_EXAMPLE):
            with self.subTest(fixture=fixture.name):
                workflow = load_workflow(fixture)
                result = validate_sensor_evidence_workflow_config(workflow)

                self.assertTrue(result.valid, result.errors)
                self.assertEqual(result.error_count, 0)
                self.assertGreaterEqual(result.input_count, 1)
                self.assertGreaterEqual(result.provider_count, 1)

        n_of_1 = load_workflow(NOF1_FIXTURE)
        self.assertEqual(
            workflow_sensor_evidence_fixture_refs(n_of_1, CSI_EVIDENCE_PROVIDER_ID),
            (
                "sample-esp32-csi.csv",
                "csi-tabular-fixture.csv",
                "sample-csi-jsonl.jsonl",
            ),
        )
        tournament = load_workflow(TOURNAMENT_FIXTURE)
        self.assertEqual(
            len(workflow_sensor_evidence_groups(tournament, CSI_EVIDENCE_PROVIDER_ID)),
            3,
        )
        toy = load_workflow(TOY_EXAMPLE)
        self.assertEqual(
            workflow_sensor_evidence_fixture_refs(toy, "toy-counter-fixture"),
            ("toy-counter-parsed.csv",),
        )

    def test_sanitizer_removes_csi_and_environment_fixture_refs(self):
        workflow = load_workflow(NOF1_FIXTURE)
        sanitized_inputs = [
            sanitize_sensor_evidence_input_spec(input_spec)
            for input_spec in workflow["inputs"]
            if input_spec.get("kind") in {"csi-parser-fixtures", "environment-fixture-rows"}
        ]

        by_kind = {item["kind"]: item for item in sanitized_inputs}
        csi = by_kind["csi-parser-fixtures"]
        environment = by_kind["environment-fixture-rows"]
        self.assertEqual(csi["provider_id"], "wifi-csi")
        self.assertEqual(csi["artifact_ref"], CSI_EVIDENCE_PACK_ARTIFACT_REF)
        self.assertEqual(csi["ref_count"], 3)
        self.assertTrue(csi["refs_sanitized"])
        self.assertEqual(environment["provider_id"], "environment-fixture")
        self.assertEqual(environment["ref_count"], 1)
        encoded = json.dumps(sanitized_inputs, sort_keys=True).lower()
        for forbidden in (
            "sample-esp32-csi",
            "csi-tabular-fixture.csv",
            "sample-csi-jsonl",
            "environment-parsed.csv",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)

        toy_workflow = load_workflow(TOY_EXAMPLE)
        toy_input = sanitize_sensor_evidence_input_spec(self._toy_input(toy_workflow))
        self.assertEqual(toy_input["provider_id"], "toy-counter-fixture")
        self.assertEqual(toy_input["ref_count"], 1)
        self.assertTrue(toy_input["refs_sanitized"])
        encoded_toy = json.dumps(toy_input, sort_keys=True).lower()
        self.assertNotIn("toy-counter-parsed.csv", encoded_toy)
        self.assertNotIn('"refs":', encoded_toy)

        document_workflow = load_workflow(DOCUMENT_EXAMPLE)
        document_input = sanitize_sensor_evidence_input_spec(
            self._document_input(document_workflow)
        )
        self.assertEqual(document_input["provider_id"], "document-fixture")
        self.assertEqual(document_input["evidence_kind"], "document-evidence-pack")
        self.assertEqual(document_input["artifact_name"], "document_evidence_pack")
        self.assertEqual(
            document_input["artifact_ref"],
            "artifacts/document_evidence_pack.json",
        )
        self.assertEqual(document_input["ref_count"], 1)
        self.assertLessEqual(document_input["ref_count"], document_input["max_ref_count"])
        self.assertTrue(document_input["refs_sanitized"])
        encoded_document = json.dumps(document_input, sort_keys=True).lower()
        self.assertNotIn("document-parsed.json", encoded_document)
        self.assertNotIn('"refs":', encoded_document)

    def test_unknown_provider_fails_closed_without_echoing_identifier(self):
        workflow = copy.deepcopy(load_workflow(NOF1_FIXTURE))
        self._environment_input(workflow)["provider_id"] = "unknown-live-provider"

        result = validate_sensor_evidence_workflow_config(workflow)

        self.assertFalse(result.valid)
        encoded = json.dumps(result.to_dict(), sort_keys=True).lower()
        self.assertIn("sensor_provider_unknown", encoded)
        self.assertNotIn("unknown-live-provider", encoded)

    def test_unsafe_toy_config_fails_closed_with_sanitized_errors(self):
        workflow = copy.deepcopy(load_workflow(TOY_EXAMPLE))
        toy = self._toy_input(workflow)
        toy["refs"] = [
            str(REPO_ROOT / "fixtures" / "sensors" / "toy-counter" / "toy-counter-parsed.csv"),
            "fixture://sensors/toy-counter/toy-counter-parsed.csv",
            "../private.csv",
            "fixtures/sensors/toy-counter/toy-counter-parsed.csv",
            "toy-counter-parsed.json",
            "extra-1.csv",
            "extra-2.csv",
            "extra-3.csv",
        ]
        toy["debug_ref"] = "toy-counter-parsed.csv"
        sensor_provider = next(
            provider for provider in workflow["providers"] if provider.get("class") == "sensor"
        )
        sensor_provider["constraints"]["allow_external_upload"] = True
        sensor_provider["constraints"]["allow_real_counter_source"] = True

        result = validate_sensor_evidence_workflow_config(workflow)

        self.assertFalse(result.valid)
        encoded = json.dumps(result.to_dict(), sort_keys=True).lower()
        self.assertIn("sensor_fixture_ref_count_exceeded", encoded)
        self.assertIn("sensor_fixture_ref_absolute_path_rejected", encoded)
        self.assertIn("sensor_fixture_ref_url_rejected", encoded)
        self.assertIn("sensor_fixture_ref_parent_traversal_rejected", encoded)
        self.assertIn("sensor_fixture_ref_unsafe", encoded)
        self.assertIn("sensor_fixture_ref_unsupported_format", encoded)
        self.assertIn("sensor_private_scalar_field_present", encoded)
        self.assertIn("sensor_provider_blocked_flag_enabled", encoded)
        self.assertIn("private_scalar", result.to_dict()["error_categories"])
        self.assertIn("offline_boundary_flag", result.to_dict()["error_categories"])
        for forbidden in (
            "toy-counter-parsed.csv",
            "fixture://",
            "fixtures/sensors",
            "private.csv",
            "allow_external_upload",
            "allow_real_counter_source",
            str(REPO_ROOT).replace("\\", "/").lower(),
        ):
            with self.subTest(toy_validation_forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)

    def test_unsafe_refs_and_excessive_counts_fail_with_sanitized_errors(self):
        workflow = copy.deepcopy(load_workflow(NOF1_FIXTURE))
        environment = self._environment_input(workflow)
        environment["refs"] = [
            str(REPO_ROOT / "fixtures" / "sensors" / "environment" / "environment-parsed.csv"),
            "https://example.invalid/private.csv",
            "../private.csv",
            "fixture://sensors/environment/environment-parsed.csv",
            "too-many.csv",
        ]

        result = validate_sensor_evidence_workflow_config(workflow)

        self.assertFalse(result.valid)
        encoded = json.dumps(result.to_dict(), sort_keys=True).lower()
        self.assertIn("sensor_fixture_ref_count_exceeded", encoded)
        self.assertIn("sensor_fixture_ref_absolute_path_rejected", encoded)
        self.assertIn("sensor_fixture_ref_url_rejected", encoded)
        self.assertIn("sensor_fixture_ref_parent_traversal_rejected", encoded)
        self._assert_sanitized_validation_text(encoded)

        tournament = copy.deepcopy(load_workflow(TOURNAMENT_FIXTURE))
        csi_groups = self._csi_group_input(tournament)
        csi_groups["groups"] = [
            {"id": f"group-{index}", "refs": ["sample-esp32-csi.csv"]} for index in range(9)
        ]
        group_result = validate_sensor_evidence_workflow_config(tournament)
        self.assertFalse(group_result.valid)
        self.assertIn(
            "sensor_fixture_group_count_exceeded",
            json.dumps(group_result.to_dict(), sort_keys=True),
        )

    def test_live_device_network_and_credential_fields_fail_closed(self):
        workflow = copy.deepcopy(load_workflow(NOF1_FIXTURE))
        csi = self._csi_parser_input(workflow)
        csi["api_key"] = "sk-private-value"
        csi["device_id"] = "adapter-private"
        sensor_provider = next(
            provider for provider in workflow["providers"] if provider.get("class") == "sensor"
        )
        sensor_provider["constraints"]["allow_network_calls"] = True
        sensor_provider["capabilities"].append("mystery-provider.evidence-pack")
        sensor_provider["notes"] = ["https://example.invalid/provider-private"]

        result = validate_sensor_evidence_workflow_config(workflow)

        self.assertFalse(result.valid)
        encoded = json.dumps(result.to_dict(), sort_keys=True).lower()
        self.assertIn("sensor_credential_field_present", encoded)
        self.assertIn("sensor_live_device_or_network_field_present", encoded)
        self.assertIn("sensor_provider_blocked_flag_enabled", encoded)
        self.assertIn("sensor_provider_unknown", encoded)
        self.assertIn("sensor_private_scalar_field_present", encoded)
        categories = result.to_dict()["error_categories"]
        self.assertIn("credential_like_field", categories)
        self.assertIn("live_device_network_field", categories)
        self.assertIn("unknown_provider", categories)
        self._assert_sanitized_validation_text(encoded)
        self.assertNotIn("api_key", encoded)
        self.assertNotIn("adapter-private", encoded)
        self.assertNotIn("mystery-provider", encoded)

    def test_unsupported_fixture_mode_fails_closed_without_echoing_value(self):
        workflow = copy.deepcopy(load_workflow(TOY_EXAMPLE))
        toy = self._toy_input(workflow)
        toy["fixture_mode"] = "private-live-mode-value"

        result = validate_sensor_evidence_workflow_config(workflow)

        self.assertFalse(result.valid)
        encoded = json.dumps(result.to_dict(), sort_keys=True).lower()
        self.assertIn("sensor_fixture_mode_unsupported", encoded)
        self.assertIn("unsupported_fixture_mode", result.to_dict()["error_categories"])
        self.assertNotIn("private-live-mode-value", encoded)

    def test_workflow_loader_rejects_unsupported_mode_without_echoing_value(self):
        text = TOY_EXAMPLE.read_text(encoding="utf-8").replace(
            "mode: hypothesis-tournament",
            "mode: private-live-mode-value",
            1,
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "unsafe-mode.yaml"
            path.write_text(text, encoding="utf-8")
            with self.assertRaises(WorkflowValidationError) as caught:
                load_workflow(path)

        message = str(caught.exception).lower()
        self.assertIn("workflow_mode_unsupported", message)
        self.assertNotIn("private-live-mode-value", message)
        self.assertNotRegex(message.replace("\\", "/"), r"[a-z]:/")

    def test_private_scalar_fields_fail_closed_and_sanitize_from_workflow_artifact(self):
        workflow = copy.deepcopy(load_workflow(NOF1_FIXTURE))
        csi = self._csi_parser_input(workflow)
        csi["description"] = (
            "C:/Users/Josh/private.csv https://example.invalid/x "
            "sample-esp32-csi.csv sk-private-value"
        )
        csi["note"] = "environment-parsed.csv should never be exported"
        csi["debug_ref"] = "fixture://sensors/csi/sample-esp32-csi.csv"

        result = validate_sensor_evidence_workflow_config(workflow)
        sanitized = sanitize_sensor_evidence_input_spec(csi)

        self.assertFalse(result.valid)
        encoded_errors = json.dumps(result.to_dict(), sort_keys=True).lower()
        self.assertIn("sensor_private_scalar_field_present", encoded_errors)
        self._assert_sanitized_validation_text(encoded_errors)
        encoded_sanitized = json.dumps(sanitized, sort_keys=True).lower()
        self.assertNotIn("description", encoded_sanitized)
        self.assertNotIn("note", encoded_sanitized)
        self.assertNotIn("debug_ref", encoded_sanitized)
        self._assert_sanitized_validation_text(encoded_sanitized)

    def test_workflow_loader_rejects_invalid_sensor_provider_config(self):
        text = NOF1_FIXTURE.read_text(encoding="utf-8").replace(
            "provider_id: environment-fixture",
            "provider_id: unknown-live-provider",
            1,
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "unsafe-sensor-evidence.yaml"
            path.write_text(text, encoding="utf-8")
            with self.assertRaises(WorkflowValidationError) as caught:
                load_workflow(path)

        message = str(caught.exception).lower()
        self.assertIn("sensor_provider_unknown", message)
        self.assertNotIn("unknown-live-provider", message)
        self.assertNotRegex(message.replace("\\", "/"), r"[a-z]:/")

    def _csi_parser_input(self, workflow):
        return next(
            item for item in workflow["inputs"] if item.get("kind") == "csi-parser-fixtures"
        )

    def _csi_group_input(self, workflow):
        return next(
            item
            for item in workflow["inputs"]
            if item.get("kind") == "csi-replay-evaluation-groups"
        )

    def _environment_input(self, workflow):
        return next(
            item for item in workflow["inputs"] if item.get("kind") == "environment-fixture-rows"
        )

    def _toy_input(self, workflow):
        return next(
            item for item in workflow["inputs"] if item.get("kind") == "toy-counter-fixture-rows"
        )

    def _document_input(self, workflow):
        return next(
            item for item in workflow["inputs"] if item.get("kind") == "document-fixture-metadata"
        )

    def _assert_sanitized_validation_text(self, encoded):
        for forbidden in (
            "environment-parsed.csv",
            "document-parsed.json",
            "document-mixed.json",
            "sample-esp32-csi",
            "example.invalid",
            "private.csv",
            "fixture://",
            "c:/",
            str(REPO_ROOT).replace("\\", "/").lower(),
            "sk-private-value",
            "device_id",
            "allow_network_calls",
        ):
            with self.subTest(validation_forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)


if __name__ == "__main__":
    unittest.main()
