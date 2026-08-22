import json
import tempfile
import unittest
from pathlib import Path

from somatic.mock_runtime import run_mock_workflow
from somatic.sensors.csi import (
    build_csi_evidence_metadata,
    build_csi_metadata,
    build_csi_reference_inventory,
    build_csi_summary_metadata,
)
from somatic.sensors.csi_adapter import (
    CSI_RUVIEW_REFERENCE_STATUS,
    CSI_SOURCE_ADAPTER_KIND,
    booth_first_csi_planning_profile,
    fixture_csi_source_adapter_output,
    validate_csi_source_adapter_output,
    wifi_csi_source_adapter_status,
)
from somatic.sensors.registry import sensor_evidence_provider_manifest
from somatic.sensors.sandbox import SandboxSensorProvider

REPO_ROOT = Path(__file__).resolve().parents[1]
NOF1_FIXTURE = REPO_ROOT / "fixtures" / "workflows" / "valid-n-of-1.yaml"


class WifiCsiRuViewBoothBoundaryTests(unittest.TestCase):
    def test_ruview_reassessment_is_conditional_reference_only(self):
        inventory = build_csi_reference_inventory()
        by_repo = {entry["repo"]: entry for entry in inventory["references"]}
        ruview = by_repo["ruvnet/RuView"]

        self.assertEqual(ruview["status"], CSI_RUVIEW_REFERENCE_STATUS)
        self.assertTrue(ruview["reference_only"])
        self.assertTrue(ruview["reassessable"])
        self.assertIsNone(ruview["local_path"])
        self.assertIsNone(ruview["commit"])
        self.assertNotIn("remote_url", ruview)
        self.assertFalse(ruview["runtime_dependency"])
        self.assertTrue(ruview["no_runtime_execution"])
        self.assertTrue(ruview["no_hardware_access"])
        self.assertTrue(ruview["no_dependency_install"])
        self.assertTrue(ruview["no_source_vendoring"])
        self.assertIn("earlier-overclaims", ruview["warning_history"])
        self.assertIn("incompatible-model-loading-concerns", ruview["warning_history"])
        self.assertIn("unverified-deployment-claims", ruview["warning_history"])
        self.assertTrue(ruview["v2_reassessment"]["rust_workspace_reported"])
        self.assertTrue(ruview["v2_reassessment"]["wifi_densepose_crates_reported"])
        self.assertTrue(ruview["v2_reassessment"]["temporal_embedding_metric_reported"])
        self.assertFalse(ruview["v2_reassessment"]["downstream_accuracy_validated"])
        self.assertFalse(ruview["v2_reassessment"]["deployment_claims_verified"])

    def test_booth_first_profile_is_future_metadata_only(self):
        inventory = build_csi_reference_inventory()
        profile = inventory["booth_first_planning_profile"]
        helper_profile = booth_first_csi_planning_profile()

        self.assertEqual(profile, helper_profile)
        self.assertEqual(profile["profile"], "booth-first-single-subject-v1")
        self.assertTrue(profile["single_subject"])
        self.assertEqual(profile["space"], "small-controlled-booth")
        self.assertEqual(profile["future_topology"], "fixed-ap-plus-4-to-6-receiver-nodes")
        self.assertEqual(profile["preferred_radio_family"], "esp32-s3")
        self.assertEqual(profile["empty_booth_baseline"], "planned-reference-concept")
        self.assertEqual(profile["room_adaptation_logic"], "skipped")
        self.assertIn("phase-variance", profile["research_note_labels"])
        self.assertIn("conjugation", profile["research_note_labels"])
        self.assertIn("temporal-embedding", profile["research_note_labels"])
        self.assertFalse(profile["hardware_access"])
        self.assertFalse(profile["packet_capture"])
        self.assertFalse(profile["model_execution"])
        self.assertFalse(profile["vitals_inference"])

    def test_csi_source_adapter_status_is_closed_and_fixture_backed(self):
        status = wifi_csi_source_adapter_status()

        self.assertEqual(status["adapter_kind"], CSI_SOURCE_ADAPTER_KIND)
        self.assertEqual(status["adapter_contract_version"], 1)
        self.assertTrue(status["metadata_only"])
        self.assertTrue(status["reference_only"])
        self.assertTrue(status["fixture_backed"])
        self.assertTrue(status["offline"])
        self.assertTrue(status["fail_closed_output_validation"])
        for flag in (
            "hardware_access",
            "packet_capture",
            "monitor_mode",
            "wifi_network_probing",
            "network_calls",
            "esp32_flashing",
            "router_ap_control",
            "mqtt_udp_listener",
            "smart_home_bridge",
            "model_download",
            "model_execution",
            "vitals_inference",
            "diagnosis",
            "treatment",
            "emergency_triage",
            "medical_or_clinical_claim",
            "raw_signal_export",
        ):
            with self.subTest(flag=flag):
                self.assertFalse(status[flag])
        phase11 = status["p11a_contract_status"]
        self.assertEqual(phase11["domain"], "wifi-csi-rf-booth")
        self.assertEqual(phase11["status"], "planning-only-runtime-disabled")
        self.assertTrue(phase11["planning_only"])
        self.assertTrue(phase11["metadata_only"])
        self.assertEqual(phase11["runtime_stage"], "not-implemented")
        self.assertEqual(phase11["readiness_gate_missing_count"], 7)
        self.assertFalse(phase11["execution_permitted"])
        self.assertFalse(phase11["real_mode_runtime_enabled"])
        self.assertIn("rf-booth-review-only", status["capability_labels"])
        self.assertIn("p11a-contract-spec-only", status["capability_labels"])
        self.assertIn("p11g-handoff-acceptance", status["capability_labels"])
        self.assertIn("p11h-followup-remediation", status["capability_labels"])
        self.assertIn("p11i-followup-queue-index", status["capability_labels"])
        self.assertIn("p11j-decision-closeout", status["capability_labels"])
        self.assertIn("p11k-review-trail-export", status["capability_labels"])
        self.assertIn("p11l-runtime-gap-ledger", status["capability_labels"])
        self.assertIn("p11m-governance-closeout", status["capability_labels"])
        p11g = status["p11g_handoff_acceptance_status"]
        self.assertEqual(
            p11g["status"],
            "accepted-for-planning-runtime-disabled",
        )
        self.assertTrue(p11g["accepted_for_planning"])
        self.assertFalse(p11g["blocked"])
        self.assertFalse(p11g["stale"])
        self.assertEqual(p11g["runtime_stage"], "not-implemented")
        self.assertFalse(p11g["execution_permitted"])
        self.assertFalse(p11g["real_mode_runtime_enabled"])
        p11h = status["p11h_acceptance_followup_status"]
        self.assertEqual(p11h["status"], "resolved-for-planning")
        self.assertEqual(p11h["followup_type"], "blocker-disposition")
        self.assertEqual(p11h["runtime_stage"], "not-implemented")
        self.assertFalse(p11h["execution_permitted"])
        self.assertFalse(p11h["real_mode_runtime_enabled"])
        p11i = status["p11i_followup_queue_index_status"]
        self.assertEqual(p11i["status"], "stale-queue")
        self.assertEqual(p11i["acceptance_status"], "stale-queue")
        self.assertEqual(p11i["runtime_stage"], "not-implemented")
        self.assertFalse(p11i["execution_permitted"])
        self.assertFalse(p11i["real_mode_runtime_enabled"])
        p11j = status["p11j_decision_closeout_status"]
        self.assertEqual(p11j["closeout_decision"], "deferred")
        self.assertEqual(p11j["closeout_status"], "incomplete")
        self.assertEqual(p11j["runtime_stage"], "not-implemented")
        self.assertFalse(p11j["execution_permitted"])
        self.assertFalse(p11j["real_mode_runtime_enabled"])
        p11k = status["p11k_review_trail_export_status"]
        self.assertEqual(p11k["phase_range"], "11A-11J")
        self.assertEqual(p11k["covered_phase_count"], 10)
        self.assertEqual(p11k["domain_label"], "wifi-csi-rf-booth")
        self.assertEqual(p11k["final_closeout_decision"], "deferred")
        self.assertEqual(p11k["final_closeout_status"], "incomplete")
        self.assertEqual(p11k["readiness_gap_summary"], "real-mode-authorization-missing")
        self.assertEqual(p11k["runtime_stage"], "not-implemented")
        self.assertFalse(p11k["execution_permitted"])
        self.assertFalse(p11k["real_mode_runtime_enabled"])
        p11l = status["p11l_runtime_gap_ledger_status"]
        self.assertEqual(p11l["source_phase_range"], "11A-11K")
        self.assertEqual(p11l["covered_phase_count"], 11)
        self.assertEqual(p11l["domain_label"], "wifi-csi-rf-booth")
        self.assertEqual(p11l["authorization_status"], "not-authorized")
        self.assertEqual(p11l["readiness_gap"], "real-mode-authorization-missing")
        self.assertEqual(p11l["missing_future_gate_count"], 9)
        self.assertEqual(p11l["runtime_stage"], "not-implemented")
        self.assertFalse(p11l["adapter_execution_granted"])
        self.assertFalse(p11l["provider_execution_granted"])
        self.assertFalse(p11l["model_execution_granted"])
        self.assertFalse(p11l["execution_permitted"])
        self.assertFalse(p11l["real_mode_runtime_enabled"])
        p11m = status["p11m_planning_governance_closeout_status"]
        self.assertEqual(p11m["phase_range"], "11A-11L")
        self.assertEqual(p11m["covered_phase_count"], 12)
        self.assertEqual(p11m["final_status"], "phase-11-planning-governance-complete")
        self.assertEqual(p11m["runtime_authorization_status"], "not-authorized")
        self.assertEqual(p11m["readiness_gap"], "real-mode-authorization-missing")
        self.assertEqual(p11m["missing_future_gate_count"], 9)
        self.assertEqual(p11m["runtime_stage"], "not-implemented")
        self.assertFalse(p11m["adapter_execution_granted"])
        self.assertFalse(p11m["provider_execution_granted"])
        self.assertFalse(p11m["model_execution_granted"])
        self.assertFalse(p11m["execution_permitted"])
        self.assertFalse(p11m["real_mode_runtime_enabled"])

    def test_csi_source_adapter_output_validates_before_planning_metadata(self):
        output = fixture_csi_source_adapter_output()
        result = validate_csi_source_adapter_output(output)

        self.assertEqual(result.classification, "compatible")
        self.assertTrue(result.compatible)
        self.assertEqual(result.privacy_violation_count, 0)
        self.assertEqual(result.sanitized_output["status"], "accepted")
        self.assertEqual(
            result.sanitized_output["ruview_reference"]["status"],
            CSI_RUVIEW_REFERENCE_STATUS,
        )
        self.assertEqual(
            result.sanitized_output["booth_planning_profile"]["profile"],
            "booth-first-single-subject-v1",
        )

        csi_metadata = build_csi_metadata({"id": "valid-n-of-1", "mode": "n-of-1"})
        self.assertEqual(
            csi_metadata["source_adapter_output_validation"]["classification"],
            "compatible",
        )
        self.assertEqual(csi_metadata["ruview_dependency"], CSI_RUVIEW_REFERENCE_STATUS)
        self.assertEqual(
            csi_metadata["booth_planning_profile"]["future_topology"],
            "fixed-ap-plus-4-to-6-receiver-nodes",
        )

    def test_adapter_rejects_altered_reference_claim_labels(self):
        output = fixture_csi_source_adapter_output()
        output["ruview_reference"]["status"] = "deployment-verified"
        output["ruview_reference"]["somatic_posture"] = "run-live-sensing"
        output["ruview_reference"]["v2_reassessment"]["deployment_claims_verified"] = True
        output["booth_planning_profile"]["profile"] = "whole-home-ready"
        output["booth_planning_profile"]["future_topology"] = "router-device-ready"

        result = validate_csi_source_adapter_output(output)
        encoded = json.dumps(result.sanitized_output, sort_keys=True).lower()

        self.assertEqual(result.classification, "incompatible")
        self.assertFalse(result.compatible)
        self.assertIn(
            "csi_source_adapter_ruview_status_not_reference_only",
            result.errors,
        )
        self.assertIn("csi_source_adapter_booth_profile_not_pinned", result.errors)
        self.assertEqual(
            result.sanitized_output["ruview_reference"]["status"],
            "rejected-fail-closed",
        )
        self.assertNotIn("deployment-verified", encoded)
        self.assertNotIn("whole-home-ready", encoded)
        self.assertNotIn("router-device-ready", encoded)

    def test_unsafe_adapter_outputs_fail_closed_without_echoing_private_values(self):
        output = fixture_csi_source_adapter_output()
        output["source_id"] = "private-source-001"
        output["device_id"] = "device-secret"
        output["router_id"] = "router-secret"
        output["remote_url"] = "https://example.invalid/ruview"
        output["model_weights"] = "private model weights"
        output["provider_body"] = {"raw_values": [1, 2, 3]}
        output["booth_planning_profile"]["fixture_refs"] = ["sample-esp32-csi.csv"]

        result = validate_csi_source_adapter_output(output)
        combined = json.dumps(
            (result.to_dict(), result.sanitized_output),
            sort_keys=True,
        ).lower()

        self.assertEqual(result.classification, "incompatible")
        self.assertFalse(result.compatible)
        self.assertIn("csi_source_adapter_output_privacy_boundary", result.errors)
        self.assertGreater(result.privacy_violation_count, 0)
        self.assertEqual(result.sanitized_output["status"], "rejected")
        for forbidden in self._private_surface_forbidden_terms():
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, combined)

    def test_run_summary_and_report_surface_sanitized_ruview_and_booth_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = run_mock_workflow(
                NOF1_FIXTURE,
                repo_root=REPO_ROOT,
                output_root=Path(tmp),
                run_id="run-phase-10g-csi-boundary",
            )
            summary = self._read_json(run_dir / "artifacts" / "n_of_1_summary.json")
            report = (run_dir / "reports" / "report.md").read_text(encoding="utf-8")

        csi = summary["csi_metadata"]
        self.assertEqual(csi["ruview_dependency"], CSI_RUVIEW_REFERENCE_STATUS)
        self.assertEqual(csi["ruview_reference"]["status"], CSI_RUVIEW_REFERENCE_STATUS)
        self.assertFalse(
            csi["ruview_reference"]["v2_reassessment"]["downstream_accuracy_validated"]
        )
        self.assertFalse(csi["ruview_reference"]["v2_reassessment"]["deployment_claims_verified"])
        self.assertEqual(
            csi["source_adapter_output_validation"]["classification"],
            "compatible",
        )
        self.assertEqual(
            csi["booth_planning_profile"]["profile"],
            "booth-first-single-subject-v1",
        )
        self.assertFalse(csi["source_adapter_status"]["model_download"])
        self.assertFalse(csi["source_adapter_status"]["model_execution"])
        self.assertFalse(csi["source_adapter_status"]["vitals_inference"])
        self.assertFalse(csi["source_adapter_status"]["medical_or_clinical_claim"])
        self.assertEqual(
            csi["source_adapter_status"]["real_mode_readiness_gate"]["status"],
            "blocked-fixture-reference-only",
        )
        self.assertEqual(
            csi["source_adapter_status"]["real_mode_readiness_gate"]["missing_gate_count"],
            7,
        )
        self.assertFalse(csi["source_adapter_status"]["real_mode_execution_permitted"])
        self.assertIn("RuView dependency: `conditional-reference-only`", report)
        self.assertIn("Booth-first profile: `booth-first-single-subject-v1`", report)
        self.assertIn("CSI source adapter validation: `compatible`", report)
        self.assertIn(
            "CSI real-mode readiness gate: `blocked-fixture-reference-only`",
            report,
        )
        self.assertIn("CSI real-mode missing gates: 7", report)

        encoded_csi = json.dumps(csi, sort_keys=True).lower()
        for forbidden in self._private_surface_forbidden_terms():
            with self.subTest(generated_csi_forbidden=forbidden):
                self.assertNotIn(forbidden, encoded_csi)
        self.assertNotRegex(encoded_csi.replace("\\", "/"), r"[a-z]:/")

    def test_direct_csi_metadata_helpers_revalidate_tainted_adapter_surfaces(self):
        csi_metadata = self._tainted_csi_metadata()

        evidence_metadata = build_csi_evidence_metadata(
            "artifacts/csi-feature-set.json",
            "0" * 64,
            csi_metadata,
        )
        summary_metadata = build_csi_summary_metadata(
            "n-of-1",
            "sandbox-sensor-provider",
            "sensor-feature-set-id",
            "sensor-evidence-record-id",
            csi_metadata,
        )

        for payload in (evidence_metadata, summary_metadata):
            with self.subTest(surface=payload["schema_version"]):
                self.assertEqual(payload["ruview_dependency"], "rejected-fail-closed")
                self.assertEqual(
                    payload["source_adapter_output_validation"]["classification"],
                    "incompatible",
                )
                self.assertEqual(
                    payload["ruview_reference"]["status"],
                    "rejected-fail-closed",
                )
                encoded = json.dumps(payload, sort_keys=True).lower()
                for forbidden in self._private_surface_forbidden_terms():
                    self.assertNotIn(forbidden, encoded)

    def test_sandbox_evidence_record_revalidates_tainted_csi_metadata(self):
        provider = SandboxSensorProvider()
        plan = provider.plan_stream({"id": "phase-10g-taint", "mode": "n-of-1"})
        feature_set = provider.features(plan, provider.observations(plan))
        feature_set.metadata["csi"] = self._tainted_csi_metadata()

        evidence_record = provider.evidence_record(plan, feature_set).to_dict()
        csi = evidence_record["metadata"]["csi"]
        encoded = json.dumps(csi, sort_keys=True).lower()

        self.assertEqual(csi["ruview_dependency"], "rejected-fail-closed")
        self.assertEqual(
            csi["source_adapter_output_validation"]["classification"],
            "incompatible",
        )
        self.assertEqual(csi["ruview_reference"]["status"], "rejected-fail-closed")
        for forbidden in self._private_surface_forbidden_terms():
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)

    def test_provider_manifest_surfaces_only_sanitized_csi_adapter_labels(self):
        manifest = sensor_evidence_provider_manifest()
        wifi = manifest["providers"][0]
        encoded = json.dumps(wifi, sort_keys=True).lower()

        self.assertEqual(wifi["provider_id"], "wifi-csi")
        self.assertEqual(wifi["adapter_kind"], CSI_SOURCE_ADAPTER_KIND)
        self.assertEqual(wifi["adapter_contract_version"], 1)
        self.assertIn("reference-only", wifi["adapter_boundary_labels"])
        self.assertIn("no-esp32-flashing", wifi["adapter_boundary_labels"])
        self.assertIn("no-smart-home-bridge", wifi["adapter_boundary_labels"])
        self.assertIn("no-model-download", wifi["adapter_boundary_labels"])
        self.assertIn("no-model-execution", wifi["adapter_boundary_labels"])
        self.assertIn("no-vitals-inference", wifi["adapter_boundary_labels"])
        self.assertIn("no-care-claim", wifi["adapter_boundary_labels"])
        self.assertIn("rf-booth-review-only", wifi["adapter_boundary_labels"])
        self.assertIn("p11a-contract-spec-only", wifi["adapter_boundary_labels"])
        self.assertIn("real-mode-planning-only", wifi["adapter_boundary_labels"])
        self.assertIn("no-runtime-enable", wifi["adapter_boundary_labels"])
        self.assertNotIn("phase-variance", encoded)
        self.assertNotIn("source_id", encoded)
        self.assertNotIn("raw_values", encoded)
        self.assertNotIn("medical", encoded)
        self.assertNotIn("clinical", encoded)

    @staticmethod
    def _private_surface_forbidden_terms():
        return (
            "sample-esp32-csi",
            "sample-amplitude-phase",
            "sample-csi-jsonl",
            "fixture://",
            "https://",
            "http://",
            "example.invalid",
            "c:/private",
            "source_id",
            "source_ids",
            "private-source",
            "device_id",
            "device_ids",
            "device-secret",
            "router_id",
            "router-secret",
            "bssid-secret",
            "ssid-secret",
            "mac-secret",
            "api_key",
            "access_token",
            "password",
            "private-token",
            "bearer private",
            "secret_value",
            "raw-csi-secret",
            "raw-rf-secret",
            "raw-signal-secret",
            "raw_values",
            "model_body",
            "model body",
            "model weights",
            "diagnosis-result",
            "clinical-ready",
            "provider_body",
        )

    def _tainted_csi_metadata(self):
        csi_metadata = build_csi_metadata({"id": "phase-10g-taint", "mode": "n-of-1"})
        csi_metadata["ruview_reference"] = {
            "repo": "ruvnet/RuView",
            "status": "deployment-verified",
            "reference_only": True,
            "reassessable": True,
            "runtime_dependency": False,
            "local_source_staged": False,
            "source_vendored": False,
            "source_copied": False,
            "source_imported": False,
            "source_executed": False,
            "source_ids": ["private-source"],
            "device_ids": ["device-secret"],
            "bssid": "bssid-secret",
            "ssid": "ssid-secret",
            "mac": "mac-secret",
            "v2_reassessment": {
                "rust_workspace_reported": True,
                "wifi_densepose_crates_reported": True,
                "signal_pipeline_crates_reported": True,
                "temporal_embedding_metric_reported": True,
                "downstream_accuracy_validated": False,
                "deployment_claims_verified": True,
            },
            "warning_history": [
                "earlier-overclaims",
                "incompatible-model-loading-concerns",
                "unverified-deployment-claims",
                "self-published-v2-materials-only",
            ],
            "somatic_posture": "run-live-sensing",
        }
        csi_metadata["booth_planning_profile"] = {
            "profile": "whole-home-ready",
            "status": "future-planning-metadata-only",
            "single_subject": True,
            "space": "small-controlled-booth",
            "future_topology": "router-secret",
            "preferred_radio_family": "esp32-s3",
            "empty_booth_baseline": "planned-reference-concept",
            "room_adaptation_logic": "broad-room-adaptation",
            "research_note_labels": [
                "phase-variance",
                "conjugation",
                "temporal-embedding",
            ],
            "reference_only": True,
            "metadata_only": True,
            "hardware_access": False,
            "packet_capture": False,
            "model_execution": False,
            "vitals_inference": False,
            "fixture_refs": ["sample-esp32-csi.csv"],
            "raw_csi": "raw-csi-secret",
            "raw_rf": "raw-rf-secret",
            "raw_signal": "raw-signal-secret",
            "remote_url": "https://example.invalid/ruview",
            "absolute_path": "C:/private/fixture.csv",
            "model_body": "private model body",
            "model_weights": "private model weights",
            "password": "secret",
            "token": "private-token",
            "authorization": "bearer private",
            "diagnosis": "diagnosis-result",
            "clinical": "clinical-ready",
            "provider_body": {"raw_values": [1, 2, 3]},
        }
        csi_metadata["source_adapter_status"] = {
            "model_download": True,
            "model_execution": True,
            "vitals_inference": True,
            "device_id": "device-secret",
        }
        csi_metadata["source_adapter_output_validation"] = {
            "classification": "compatible",
            "provider_body": {"raw_values": [1, 2, 3]},
        }
        return csi_metadata

    @staticmethod
    def _read_json(path):
        return json.loads(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
