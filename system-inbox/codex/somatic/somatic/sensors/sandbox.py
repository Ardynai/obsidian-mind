import json
from hashlib import sha256

from somatic.evidence_bus import EvidenceSource, RawEvidence, StructuredVerdict
from somatic.providers.sensors import (
    SENSOR_BOUNDARY_STATEMENTS,
    SensorEvidenceRecord,
    SensorFeatureSet,
    SensorObservation,
    SensorPrivacyPolicy,
    SensorStreamPlan,
)
from somatic.sensors.csi import (
    CSI_REFERENCE_INVENTORY_LABEL,
    build_csi_metadata,
    safe_csi_source_adapter_surfaces,
)
from somatic.sensors.csi_formats import (
    CSI_PARSER_BOUNDARY_FALSE_FLAGS,
    CSI_PARSER_BOUNDARY_TRUE_FLAGS,
    CSI_PARSER_CONTRACT_VERSION,
    CSI_PARSER_ID,
)
from somatic.sensors.csi_parser import build_csi_parser_artifacts

SANDBOX_SENSOR_FEATURES = {
    "respiratory_rate": 14,
    "movement_score": 0.18,
    "posture_state": "upright-placeholder",
    "sleep_state_estimate": "awake-placeholder",
    "audio_event_placeholder": "none-observed-placeholder",
    "environmental_context_placeholder": "room-context-placeholder",
}


class SandboxSensorProvider:
    provider_id = "sandbox-sensor-provider"
    offline_supported = True
    modalities = (
        "csi",
        "video",
        "video3d",
        "thermal",
        "audio",
        "wearable",
        "environmental",
    )

    def privacy_policy(self) -> SensorPrivacyPolicy:
        return SensorPrivacyPolicy(
            id="sensor-privacy-policy-placeholder",
            metadata={
                "policy_status": "placeholder",
                "future_real_mode": "requires explicit consent and safety review",
            },
        )

    def plan_stream(self, workflow: dict[str, object]) -> SensorStreamPlan:
        csi_metadata = build_csi_metadata(workflow)
        return SensorStreamPlan(
            id="sensor-stream-plan-n-of-1-sandbox",
            provider_id=self.provider_id,
            workflow_id=str(workflow.get("id", "unknown-workflow")),
            mode=str(workflow.get("mode", "n-of-1")),
            modalities=self.modalities,
            requested_features=tuple(SANDBOX_SENSOR_FEATURES),
            observation_window="placeholder-window-local-only",
            baseline_ref="artifacts/n_of_1_baseline_placeholder.json",
            privacy_policy=self.privacy_policy(),
            metadata={
                "provider_mode": "sandbox",
                "fake_backed": True,
                "research_only": True,
                "capture_devices_opened": False,
                "raw_sensor_data_collected": False,
                "wifi_csi_planning_only": True,
                "wifi_csi_capture": False,
                "wifi_csi_reference_inventory_ref": CSI_REFERENCE_INVENTORY_LABEL,
                "csi_capture_plan_id": csi_metadata["capture_plan"]["id"],
                "future_real_sensor_mode": (
                    "requires explicit user consent, local-first privacy policy, and safety review"
                ),
            },
        )

    def observations(self, plan: SensorStreamPlan) -> list[SensorObservation]:
        return [
            SensorObservation(
                id="sensor-observation-respiratory-rate",
                stream_plan_id=plan.id,
                modality="csi",
                observed_at="placeholder-t+00m",
                feature_name="respiratory_rate",
                value=SANDBOX_SENSOR_FEATURES["respiratory_rate"],
                unit="breaths-per-minute-placeholder",
                metadata={"capture": "simulated", "source": "fixed-sandbox-fixture"},
            ),
            SensorObservation(
                id="sensor-observation-movement-score",
                stream_plan_id=plan.id,
                modality="wearable",
                observed_at="placeholder-t+01m",
                feature_name="movement_score",
                value=SANDBOX_SENSOR_FEATURES["movement_score"],
                unit="unitless-placeholder",
                metadata={"capture": "simulated", "source": "fixed-sandbox-fixture"},
            ),
            SensorObservation(
                id="sensor-observation-posture-state",
                stream_plan_id=plan.id,
                modality="video3d",
                observed_at="placeholder-t+02m",
                feature_name="posture_state",
                value=SANDBOX_SENSOR_FEATURES["posture_state"],
                metadata={"capture": "simulated", "source": "fixed-sandbox-fixture"},
            ),
            SensorObservation(
                id="sensor-observation-sleep-state-estimate",
                stream_plan_id=plan.id,
                modality="thermal",
                observed_at="placeholder-t+03m",
                feature_name="sleep_state_estimate",
                value=SANDBOX_SENSOR_FEATURES["sleep_state_estimate"],
                metadata={"capture": "simulated", "source": "fixed-sandbox-fixture"},
            ),
            SensorObservation(
                id="sensor-observation-audio-event-placeholder",
                stream_plan_id=plan.id,
                modality="audio",
                observed_at="placeholder-t+04m",
                feature_name="audio_event_placeholder",
                value=SANDBOX_SENSOR_FEATURES["audio_event_placeholder"],
                metadata={"capture": "simulated", "source": "fixed-sandbox-fixture"},
            ),
            SensorObservation(
                id="sensor-observation-environmental-context-placeholder",
                stream_plan_id=plan.id,
                modality="environmental",
                observed_at="placeholder-t+05m",
                feature_name="environmental_context_placeholder",
                value=SANDBOX_SENSOR_FEATURES["environmental_context_placeholder"],
                metadata={"capture": "simulated", "source": "fixed-sandbox-fixture"},
            ),
        ]

    def features(
        self,
        plan: SensorStreamPlan,
        observations: list[SensorObservation],
    ) -> SensorFeatureSet:
        csi_metadata = build_csi_metadata({"id": plan.workflow_id, "mode": plan.mode})
        return SensorFeatureSet(
            id="sensor-feature-set-n-of-1-sandbox",
            stream_plan_id=plan.id,
            provider_id=self.provider_id,
            features=dict(SANDBOX_SENSOR_FEATURES),
            source_observation_ids=tuple(observation.id for observation in observations),
            metadata={
                "feature_status": "placeholder",
                "feature_derivation": "fixed deterministic sandbox values",
                "capture_devices_opened": False,
                "raw_sensor_data_collected": False,
                "research_only": True,
                "csi": csi_metadata,
                "csi_feature_names": list(csi_metadata["feature_set"]["features"]),
                "csi_reference_inventory_ref": CSI_REFERENCE_INVENTORY_LABEL,
            },
        )

    def evidence_record(
        self,
        plan: SensorStreamPlan,
        feature_set: SensorFeatureSet,
    ) -> SensorEvidenceRecord:
        feature_payload = {"schema_version": 1} | feature_set.to_dict()
        feature_sha = _payload_sha256(feature_payload)
        csi_metadata = feature_set.metadata.get("csi", {})
        csi_adapter_surfaces = safe_csi_source_adapter_surfaces(
            csi_metadata if isinstance(csi_metadata, dict) else {}
        )
        source = EvidenceSource(
            id="sensor-evidence-source-n-of-1-sandbox",
            modality="environmental",
            provider_ref=self.provider_id,
            description=(
                "Sandbox sensor EvidenceSource for fake-backed n-of-1 planning; "
                "no hardware capture or clinical interpretation."
            ),
            metadata={
                "sensor_modalities": list(plan.modalities),
                "simulated": True,
                "offline": True,
                "hardware_access": False,
                "clinical_interpretation": False,
                "emergency_triage": False,
                "real_monitoring": False,
                "wifi_csi_planning_only": True,
                "wifi_csi_capture": False,
                "packet_capture": False,
                "wifi_network_probing": False,
                "monitor_mode": False,
                "csi_reference_inventory_ref": CSI_REFERENCE_INVENTORY_LABEL,
            },
        )
        raw = RawEvidence(
            id="sensor-raw-evidence-n-of-1-sandbox",
            source=source,
            payload_ref="artifacts/sensor_feature_set.json",
            sha256=feature_sha,
            metadata={
                "feature_set_id": feature_set.id,
                "feature_names": list(feature_set.features),
                "boundary": "fake-backed/offline/research-only",
                "simulated": True,
                "hardware_access": False,
                "csi_status": "placeholder-metadata-only",
                "csi_planning_only": True,
                "csi_feature_set_id": csi_metadata.get("feature_set", {}).get("id"),
                "csi_reference_inventory_ref": CSI_REFERENCE_INVENTORY_LABEL,
            },
        )
        verdict = StructuredVerdict(
            id="sensor-structured-verdict-n-of-1-sandbox",
            raw_evidence_refs=[raw.id],
            summary=(
                "Sandbox sensor features are planning placeholders only; no real "
                "monitoring, diagnosis, treatment, or emergency triage was performed."
            ),
            confidence="not-applicable",
            limitations=[
                "Fixed mock values only.",
                "No CSI, camera, microphone, wearable, thermal, environmental, or network capture.",
                "No clinical interpretation or emergency triage.",
            ],
            metadata={
                "research_only": True,
                "simulated": True,
                "offline": True,
                "clinical_claim": False,
                "real_monitoring": False,
                "csi_status": "placeholder-metadata-only",
                "csi_planning_only": True,
            },
        )
        return SensorEvidenceRecord(
            id="sensor-evidence-record-n-of-1-sandbox",
            provider_id=self.provider_id,
            stream_plan_id=plan.id,
            raw_evidence=raw,
            structured_verdict=verdict,
            feature_set_ref="artifacts/sensor_feature_set.json",
            privacy_policy=plan.privacy_policy,
            metadata={
                "boundary_statements": list(SENSOR_BOUNDARY_STATEMENTS),
                "feature_set_sha256": feature_sha,
                "research_only": True,
                "csi": {
                    "status": "placeholder-metadata-only",
                    "planning_only": True,
                    "csi_feature_set_id": csi_metadata.get("feature_set", {}).get("id"),
                    "reference_inventory_ref": CSI_REFERENCE_INVENTORY_LABEL,
                    "hardware_access": False,
                    "packet_capture": False,
                    "wifi_network_probing": False,
                    "monitor_mode": False,
                    "network_calls": False,
                    "clinical_interpretation": False,
                    "medical_or_clinical_claim": False,
                    **csi_adapter_surfaces,
                },
            },
        )

    def replay_csi_fixtures(
        self,
        fixture_refs: tuple[str, ...] | list[str],
        repo_root=None,
    ) -> dict[str, object]:
        refs = tuple(str(ref) for ref in fixture_refs)
        report_payload, summary_payload = build_csi_parser_artifacts(
            refs,
            repo_root=repo_root,
        )
        replay_provider = self._csi_replay_provider_metadata(
            report_payload=report_payload,
            summary_payload=summary_payload,
        )
        report_payload = dict(report_payload)
        summary_payload = dict(summary_payload)
        csi_evidence_scoring = dict(report_payload.get("csi_evidence_scoring", {}))
        report_payload["replay_provider"] = dict(replay_provider)
        summary_payload["replay_provider"] = dict(replay_provider)
        payload = {
            "schema_version": 1,
            "contract_version": CSI_PARSER_CONTRACT_VERSION,
            "id": "csi-fixture-replay-provider-output",
            "provider_id": self.provider_id,
            "mode": "fixture-replay",
            "parser_id": CSI_PARSER_ID,
            "status": report_payload["status"],
            "fixture_count": report_payload["fixture_count"],
            "fixture_refs": list(report_payload["fixture_refs"]),
            "source_formats": list(summary_payload["source_formats"]),
            "frame_count": report_payload["frame_count"],
            "sample_count": report_payload["sample_count"],
            "malformed_rows": report_payload["malformed_rows"],
            "csi_evidence_scoring": csi_evidence_scoring,
            "report": report_payload,
            "summary": summary_payload,
            "replay_provider": replay_provider,
            "scope": "local fixture replay through sanitized parser metadata",
            "raw_signal_values_exported": False,
        }
        payload.update(CSI_PARSER_BOUNDARY_TRUE_FLAGS)
        payload.update(CSI_PARSER_BOUNDARY_FALSE_FLAGS)
        return payload

    def status(self) -> dict[str, object]:
        return {
            "provider_id": self.provider_id,
            "class": "sensor",
            "mode": "sandbox",
            "offline_supported": self.offline_supported,
            "csi_fixture_replay_supported": True,
            "csi_fixture_replay_mode": "fixture-replay",
            "csi_fixture_replay_output": "sanitized parser report and summary metadata",
            "csi_fixture_replay_contract_version": CSI_PARSER_CONTRACT_VERSION,
            "csi_evidence_scoring_supported": True,
            "csi_evidence_scoring_output": "sanitized replay metadata score",
            "csi_batch_replay_evaluation_supported": True,
            "csi_batch_replay_evaluation_output": ("sanitized fixture-group readiness metadata"),
            "modalities": list(self.modalities),
            "simulated": True,
            "hardware_access": False,
            "network_calls": False,
            "clinical_interpretation": False,
            "emergency_triage": False,
            "real_monitoring": False,
            "wifi_csi_planning_only": True,
            "wifi_csi_capture": False,
            "wifi_csi_hardware_access": False,
            "packet_capture": False,
            "wifi_network_probing": False,
            "monitor_mode": False,
            "raw_signal_values_exported": False,
            "csi_reference_inventory_ref": CSI_REFERENCE_INVENTORY_LABEL,
        }

    def _csi_replay_provider_metadata(
        self,
        *,
        report_payload: dict[str, object],
        summary_payload: dict[str, object],
    ) -> dict[str, object]:
        metadata = {
            "schema_version": 1,
            "provider_id": self.provider_id,
            "mode": "fixture-replay",
            "parser_id": CSI_PARSER_ID,
            "contract_version": CSI_PARSER_CONTRACT_VERSION,
            "status": report_payload["status"],
            "fixture_count": report_payload["fixture_count"],
            "source_formats": list(summary_payload["source_formats"]),
            "frame_count": report_payload["frame_count"],
            "sample_count": report_payload["sample_count"],
            "malformed_rows": report_payload["malformed_rows"],
            "evidence_quality": report_payload.get("csi_evidence_scoring", {}).get(
                "evidence_quality"
            ),
            "replay_integrity": report_payload.get("csi_evidence_scoring", {}).get(
                "replay_integrity"
            ),
            "csi_evidence_scoring_supported": True,
            "artifact_refs": {
                "report": "artifacts/csi_parser_report.json",
                "summary": "artifacts/csi_parsed_summary.json",
            },
            "summary_output_only": True,
            "fixture_only": True,
            "offline": True,
            "hardware_access": False,
            "network_calls": False,
            "serial_access": False,
            "mqtt_udp_listener": False,
            "packet_capture": False,
            "monitor_mode": False,
            "wifi_network_probing": False,
            "live_capture": False,
            "raw_signal_values_exported": False,
            "medical_or_clinical_claim": False,
        }
        return metadata


def _payload_sha256(payload: dict[str, object]) -> str:
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    return sha256(encoded).hexdigest()


__all__ = [
    "SANDBOX_SENSOR_FEATURES",
    "SandboxSensorProvider",
]
