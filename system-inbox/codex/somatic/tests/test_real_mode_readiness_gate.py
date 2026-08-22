import json
import unittest

from somatic.evidence.document_adapter import (
    DOCUMENT_ADAPTER_KIND,
    document_adapter_real_mode_readiness_gate,
    document_fixture_adapter_status,
)
from somatic.evidence.document_fixture import DocumentFixtureEvidenceProvider
from somatic.safety.adapter_readiness import (
    REAL_MODE_GATE_BLOCKED_STATUS,
    REAL_MODE_GATE_REVIEWED_STATUS,
    REAL_MODE_PHASE_RUNTIME,
    REAL_MODE_READINESS_GATE_CONTRACT_VERSION,
    REAL_MODE_READINESS_GATE_KIND,
    REAL_MODE_REQUIRED_GATES,
    RealModeReadinessReviewRecord,
    evaluate_real_mode_readiness,
)
from somatic.safety.phase11_contracts import (
    phase11_document_ingestion_contract_spec,
    phase11_wifi_csi_rf_booth_contract_spec,
    validate_phase11_contract_spec,
)
from somatic.sensors.csi_adapter import (
    CSI_SOURCE_ADAPTER_KIND,
    wifi_csi_real_mode_readiness_gate,
    wifi_csi_source_adapter_status,
)

FORBIDDEN_GATE_TERMS = (
    "fixture://",
    "fixtures/",
    "source_id",
    "source_ids",
    "api_key",
    "access_token",
    "refresh_token",
    "secret_value",
    "authorization",
    "bearer private",
    "raw_csi",
    "raw_rf",
    "raw document text",
    "provider_body",
    "parser_body",
    "model weights",
    "example.invalid",
)


class RealModeReadinessGateTests(unittest.TestCase):
    def test_default_gate_blocks_fixture_or_reference_mode(self):
        report = evaluate_real_mode_readiness(
            provider_kind="document-fixture",
            adapter_kind=DOCUMENT_ADAPTER_KIND,
            current_mode="fixture-only",
        ).to_dict()

        self.assertEqual(report["gate_contract_version"], 1)
        self.assertEqual(report["gate_kind"], REAL_MODE_READINESS_GATE_KIND)
        self.assertEqual(report["status"], REAL_MODE_GATE_BLOCKED_STATUS)
        self.assertFalse(report["ready"])
        self.assertFalse(report["execution_permitted"])
        self.assertFalse(report["real_mode_runtime_enabled"])
        self.assertEqual(report["runtime_stage"], REAL_MODE_PHASE_RUNTIME)
        self.assertEqual(report["required_gates"], list(REAL_MODE_REQUIRED_GATES))
        self.assertEqual(report["missing_gates"], list(REAL_MODE_REQUIRED_GATES))
        self.assertEqual(report["missing_gate_count"], len(REAL_MODE_REQUIRED_GATES))
        self._assert_gate_sanitized(report)

    def test_all_required_gates_can_be_recorded_without_enabling_runtime(self):
        report = evaluate_real_mode_readiness(
            provider_kind="wifi-csi",
            adapter_kind=CSI_SOURCE_ADAPTER_KIND,
            current_mode="reference-only",
            satisfied_gates=REAL_MODE_REQUIRED_GATES,
        ).to_dict()

        self.assertEqual(report["status"], REAL_MODE_GATE_REVIEWED_STATUS)
        self.assertTrue(report["ready"])
        self.assertEqual(report["missing_gates"], [])
        self.assertEqual(report["missing_gate_count"], 0)
        self.assertEqual(report["satisfied_gates"], list(REAL_MODE_REQUIRED_GATES))
        self.assertFalse(report["execution_permitted"])
        self.assertFalse(report["real_mode_runtime_enabled"])
        self.assertEqual(report["runtime_block_reasons"], ["runtime-not-implemented"])
        self._assert_gate_sanitized(report)

    def test_each_missing_required_gate_fails_closed(self):
        for missing_gate in REAL_MODE_REQUIRED_GATES:
            with self.subTest(missing_gate=missing_gate):
                satisfied = [gate for gate in REAL_MODE_REQUIRED_GATES if gate != missing_gate]
                report = evaluate_real_mode_readiness(
                    provider_kind="wifi-csi",
                    adapter_kind=CSI_SOURCE_ADAPTER_KIND,
                    current_mode="reference-only",
                    satisfied_gates=satisfied,
                ).to_dict()

                self.assertEqual(report["status"], REAL_MODE_GATE_BLOCKED_STATUS)
                self.assertFalse(report["ready"])
                self.assertIn(missing_gate, report["missing_gates"])
                self.assertIn(f"missing-{missing_gate}", report["block_reasons"])
                self.assertFalse(report["execution_permitted"])
                self.assertFalse(report["real_mode_runtime_enabled"])
                self._assert_gate_sanitized(report)

    def test_mapping_review_record_requires_explicit_true_values(self):
        incomplete = {
            "consent": True,
            "license_review": True,
            "privacy_review": True,
            "hardware_review": True,
            "model_artifact_review": True,
            "dependency_review": True,
            "network_policy_review": False,
        }
        report = evaluate_real_mode_readiness(
            provider_kind="document-fixture",
            adapter_kind=DOCUMENT_ADAPTER_KIND,
            current_mode="fixture-only",
            review_record=incomplete,
        ).to_dict()

        self.assertFalse(report["ready"])
        self.assertIn("network-policy-review", report["missing_gates"])

        complete = dict(incomplete, network_policy_review=True)
        ready_report = evaluate_real_mode_readiness(
            provider_kind="document-fixture",
            adapter_kind=DOCUMENT_ADAPTER_KIND,
            current_mode="fixture-only",
            review_record=complete,
        ).to_dict()

        self.assertTrue(ready_report["ready"])
        self.assertEqual(ready_report["missing_gates"], [])
        self.assertFalse(ready_report["execution_permitted"])
        self._assert_gate_sanitized(ready_report)

    def test_review_record_dataclass_matches_required_gate_ids(self):
        record = RealModeReadinessReviewRecord(
            consent=True,
            license_review=True,
            privacy_review=True,
            hardware_review=True,
            model_artifact_review=True,
            dependency_review=True,
            network_policy_review=True,
        )

        self.assertEqual(record.satisfied_gate_ids(), REAL_MODE_REQUIRED_GATES)
        self.assertTrue(record.to_dict()["network_policy_review"])

    def test_document_and_csi_adapters_surface_shared_gate(self):
        for status in (
            document_fixture_adapter_status(),
            DocumentFixtureEvidenceProvider().status(),
            wifi_csi_source_adapter_status(),
        ):
            with self.subTest(adapter=status["adapter_kind"]):
                gate = status["real_mode_readiness_gate"]
                self.assertEqual(
                    gate["gate_contract_version"],
                    REAL_MODE_READINESS_GATE_CONTRACT_VERSION,
                )
                self.assertEqual(gate["gate_kind"], REAL_MODE_READINESS_GATE_KIND)
                self.assertEqual(gate["status"], REAL_MODE_GATE_BLOCKED_STATUS)
                self.assertEqual(gate["missing_gates"], list(REAL_MODE_REQUIRED_GATES))
                self.assertFalse(gate["execution_permitted"])
                self.assertFalse(status["real_mode_execution_permitted"])
                self._assert_gate_sanitized(status)

    def test_adapter_specific_gate_helpers_keep_modes_distinct(self):
        document_gate = document_adapter_real_mode_readiness_gate()
        csi_gate = wifi_csi_real_mode_readiness_gate()

        self.assertEqual(document_gate["current_mode"], "fixture-only")
        self.assertEqual(csi_gate["current_mode"], "reference-only")
        self.assertEqual(document_gate["adapter_kind"], DOCUMENT_ADAPTER_KIND)
        self.assertEqual(csi_gate["adapter_kind"], CSI_SOURCE_ADAPTER_KIND)
        self.assertEqual(document_gate["missing_gate_count"], 7)
        self.assertEqual(csi_gate["missing_gate_count"], 7)
        self.assertFalse(document_gate["execution_permitted"])
        self.assertFalse(csi_gate["execution_permitted"])

    def test_phase11a_specs_can_record_review_without_runtime_enablement(self):
        review_record = {
            "consent": True,
            "license_review": True,
            "privacy_review": True,
            "hardware_review": True,
            "model_artifact_review": True,
            "dependency_review": True,
            "network_policy_review": True,
        }

        for spec in (
            phase11_document_ingestion_contract_spec(review_record),
            phase11_wifi_csi_rf_booth_contract_spec(review_record),
        ):
            with self.subTest(domain=spec["domain"]):
                self.assertTrue(validate_phase11_contract_spec(spec).compatible)
                self.assertEqual(
                    spec["readiness_gate"]["status"],
                    REAL_MODE_GATE_REVIEWED_STATUS,
                )
                self.assertEqual(spec["readiness_gate"]["missing_gate_count"], 0)
                self.assertFalse(spec["readiness_gate"]["execution_permitted"])
                self.assertFalse(spec["readiness_gate"]["real_mode_runtime_enabled"])
                self.assertFalse(spec["execution_permitted"])
                self.assertFalse(spec["real_mode_runtime_enabled"])

    def _assert_gate_sanitized(self, payload):
        encoded = json.dumps(payload, sort_keys=True).lower().replace("\\", "/")
        encoded = encoded.replace(
            "real-mode-authorization-missing",
            "real-mode-gap-missing",
        )
        encoded = encoded.replace("not-authorized", "not-runtime-status")
        encoded = encoded.replace("authorization_status", "runtime_status")
        encoded = encoded.replace(
            "runtime_authorization_gap_ledger_contract_version",
            "runtime_gap_ledger_contract_version",
        )
        self.assertNotRegex(encoded, r"[a-z]:/")
        self.assertNotIn("://", encoded)
        for forbidden in FORBIDDEN_GATE_TERMS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)


if __name__ == "__main__":
    unittest.main()
