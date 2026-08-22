import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .csi_adapter import (
    CSI_RUVIEW_DEPENDENCY_STATUS,
    fixture_csi_source_adapter_output,
    validate_csi_source_adapter_output,
    wifi_csi_source_adapter_status,
)
from .csi_formats import CSI_PARSER_CAPABILITIES

CSI_FEATURE_NAMES = (
    "respiratory_rate",
    "heart_rate_placeholder",
    "hrv_placeholder",
    "motion_score",
    "posture_state",
    "sleep_state_estimate",
    "fall_risk_placeholder",
    "pose3d_placeholder",
    "confidence",
)

CSI_FAKE_FEATURES = {
    "respiratory_rate": 14,
    "heart_rate_placeholder": "not-estimated-placeholder",
    "hrv_placeholder": "not-estimated-placeholder",
    "motion_score": 0.18,
    "posture_state": "upright-placeholder",
    "sleep_state_estimate": "awake-placeholder",
    "fall_risk_placeholder": "not-assessed-placeholder",
    "pose3d_placeholder": "not-reconstructed-placeholder",
    "confidence": "not-applicable",
}

CSI_ARTIFACT_NOISE_FLAGS = {
    "multipath_placeholder": False,
    "packet_loss_placeholder": False,
    "motion_artifact_placeholder": False,
    "device_calibration_placeholder": "not-performed",
}

CSI_REFERENCE_INVENTORY_REF = "fixtures/sensors/csi/csi-reference-inventory.json"
CSI_REFERENCE_INVENTORY_LABEL = "csi-reference-inventory-v1"
CSI_RUVIEW_STATUS = CSI_RUVIEW_DEPENDENCY_STATUS
CSI_METADATA_PUBLIC_SUPPORTED_FORMATS = (
    "csi-csv-fixture",
    "csi-tabular-fixture",
    "csi-jsonl-fixture",
)

CSI_BOUNDARY_STATEMENTS = (
    "fake-backed WiFi CSI planning only",
    "disabled by default",
    "no WiFi hardware access",
    "no ESP32, RTL8812AU, router, adapter, driver, monitor mode, or packet capture",
    "no WiFi device probing",
    "no network calls",
    "raw RF/CSI data is local-first and private by default",
    "no clinical interpretation, diagnosis, treatment, or emergency triage",
)


@dataclass(frozen=True)
class CsiPrivacyBoundary:
    id: str = "csi-privacy-boundary-placeholder"
    local_first: bool = True
    private_by_default: bool = True
    raw_rf_data_leaves_machine: bool = False
    raw_csi_data_leaves_machine: bool = False
    raw_rf_retention: str = "not-collected"
    raw_csi_retention: str = "not-collected"
    explicit_consent_required: bool = True
    remote_upload_allowed: bool = False
    export_allowed: bool = False
    packet_capture_allowed: bool = False
    wifi_network_probing_allowed: bool = False
    monitor_mode_allowed: bool = False
    clinical_interpretation_allowed: bool = False
    diagnosis_allowed: bool = False
    treatment_allowed: bool = False
    emergency_triage_allowed: bool = False
    notes: tuple[str, ...] = CSI_BOUNDARY_STATEMENTS
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class CsiHardwareProfile:
    id: str = "csi-hardware-profile-placeholder"
    profile_status: str = "placeholder"
    adapter_family: str = "none-placeholder"
    esp32_access: bool = False
    rtl8812au_access: bool = False
    router_access: bool = False
    wifi_adapter_access: bool = False
    driver_access: bool = False
    monitor_mode: bool = False
    packet_capture: bool = False
    wifi_network_probing: bool = False
    hardware_access: bool = False
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class CsiCapturePlan:
    id: str
    provider_id: str
    workflow_id: str
    mode: str
    hardware_profile: CsiHardwareProfile
    privacy_boundary: CsiPrivacyBoundary
    planned_features: tuple[str, ...] = CSI_FEATURE_NAMES
    source_refs: tuple[str, ...] = (
        "NTUMARS/Awesome-WiFi-CSI-Sensing",
        "thu4n/ESP32-WiFi-Sensing",
        "MaliosDark/wifi-3d-fusion",
    )
    reference_inventory_ref: str = CSI_REFERENCE_INVENTORY_LABEL
    fake_backed: bool = True
    offline: bool = True
    disabled_by_default: bool = True
    hardware_access: bool = False
    packet_capture: bool = False
    wifi_network_probing: bool = False
    monitor_mode: bool = False
    network_calls: bool = False
    raw_rf_data_collected: bool = False
    raw_csi_data_collected: bool = False
    real_monitoring: bool = False
    clinical_interpretation: bool = False
    medical_or_clinical_claim: bool = False
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class CsiFeaturePlan:
    id: str
    capture_plan_id: str
    planned_features: tuple[str, ...] = CSI_FEATURE_NAMES
    feature_derivation: str = "fixed deterministic placeholder metadata"
    fake_backed: bool = True
    offline: bool = True
    sample_pack_read: bool = False
    hardware_access: bool = False
    packet_capture: bool = False
    wifi_network_probing: bool = False
    monitor_mode: bool = False
    network_calls: bool = False
    clinical_interpretation: bool = False
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class CsiFeatureSet:
    id: str
    capture_plan_id: str
    feature_plan_id: str
    features: dict[str, object] = field(default_factory=lambda: dict(CSI_FAKE_FEATURES))
    artifact_noise_flags: dict[str, object] = field(
        default_factory=lambda: dict(CSI_ARTIFACT_NOISE_FLAGS)
    )
    fake_backed: bool = True
    offline: bool = True
    sample_pack_read: bool = False
    hardware_access: bool = False
    packet_capture: bool = False
    wifi_network_probing: bool = False
    monitor_mode: bool = False
    network_calls: bool = False
    raw_rf_data_collected: bool = False
    raw_csi_data_collected: bool = False
    real_monitoring: bool = False
    clinical_interpretation: bool = False
    medical_or_clinical_claim: bool = False
    limitations: tuple[str, ...] = CSI_BOUNDARY_STATEMENTS
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def build_csi_privacy_boundary() -> CsiPrivacyBoundary:
    return CsiPrivacyBoundary(
        metadata={
            "raw_rf_scope": "not collected",
            "raw_csi_scope": "not collected",
            "future_real_mode": "requires explicit consent, privacy review, and safety review",
        }
    )


def build_csi_hardware_profile() -> CsiHardwareProfile:
    return CsiHardwareProfile(
        metadata={
            "hardware_profile_scope": "placeholder metadata only",
            "excluded_hardware": ["ESP32", "RTL8812AU", "router", "WiFi adapter"],
        }
    )


def build_csi_capture_plan(workflow: dict[str, object]) -> CsiCapturePlan:
    return CsiCapturePlan(
        id="csi-capture-plan-placeholder",
        provider_id="sandbox-sensor-provider",
        workflow_id=str(workflow.get("id", "unknown-workflow")),
        mode=str(workflow.get("mode", "n-of-1")),
        hardware_profile=build_csi_hardware_profile(),
        privacy_boundary=build_csi_privacy_boundary(),
        metadata={
            "plan_status": "placeholder-metadata-only",
            "ruview_dependency": CSI_RUVIEW_STATUS,
            "booth_profile": "booth-first-single-subject-v1",
            "local_reference_inventory": CSI_REFERENCE_INVENTORY_LABEL,
        },
    )


def build_csi_feature_plan(capture_plan: CsiCapturePlan) -> CsiFeaturePlan:
    return CsiFeaturePlan(
        id="csi-feature-plan-placeholder",
        capture_plan_id=capture_plan.id,
        metadata={
            "feature_status": "placeholder-metadata-only",
            "feature_source": "fixed-sandbox-fixture",
        },
    )


def build_csi_feature_set(
    capture_plan: CsiCapturePlan,
    feature_plan: CsiFeaturePlan,
) -> CsiFeatureSet:
    return CsiFeatureSet(
        id="csi-feature-set-placeholder",
        capture_plan_id=capture_plan.id,
        feature_plan_id=feature_plan.id,
        metadata={
            "feature_status": "placeholder-metadata-only",
            "reference_inventory_ref": CSI_REFERENCE_INVENTORY_LABEL,
            "ruview_dependency": CSI_RUVIEW_STATUS,
            "booth_profile": "booth-first-single-subject-v1",
        },
    )


def build_fake_csi_observations(capture_plan: CsiCapturePlan) -> list[dict[str, object]]:
    return [
        {
            "id": "csi-observation-respiratory-rate-placeholder",
            "capture_plan_id": capture_plan.id,
            "feature_name": "respiratory_rate",
            "value": CSI_FAKE_FEATURES["respiratory_rate"],
            "unit": "breaths-per-minute-placeholder",
            "fake_backed": True,
            "hardware_access": False,
            "packet_capture": False,
            "wifi_network_probing": False,
            "clinical_interpretation": False,
        },
        {
            "id": "csi-observation-motion-score-placeholder",
            "capture_plan_id": capture_plan.id,
            "feature_name": "motion_score",
            "value": CSI_FAKE_FEATURES["motion_score"],
            "unit": "unitless-placeholder",
            "fake_backed": True,
            "hardware_access": False,
            "packet_capture": False,
            "wifi_network_probing": False,
            "clinical_interpretation": False,
        },
    ]


def build_csi_reference_inventory() -> dict[str, object]:
    fixture = _load_csi_reference_inventory_fixture()
    if fixture is not None:
        return fixture
    return {
        "schema_version": 1,
        "id": "csi-reference-inventory",
        "phase": "8A",
        "research_only": True,
        "staging_root": "C:\\AI\\external-sources\\somatic\\wifi-csi",
        "source_staging_git_clone_performed": True,
        "does_not_require_external_repos_in_ci": True,
        "future_real_mode_consent": (
            "Future real WiFi CSI use requires explicit consent from the operator, "
            "intended subject, and all potentially affected people in the sensing area."
        ),
        "sensitive_data_classes": [
            "WiFi CSI",
            "RSSI",
            "pcap",
            "serial CSI logs",
            "SD-card CSVs",
            "raw RF/CSI",
            "derived features",
            "embeddings",
            "ReID sequences",
            "pose outputs",
            "activity labels",
        ],
        "policy": {
            "read_only_source_inspection": True,
            "git_clone_or_fetch_only": True,
            "no_runtime_execution": True,
            "no_hardware_access": True,
            "no_dependency_install": True,
            "no_package_managers_run": True,
            "no_wifi_adapter_access": True,
            "no_packet_capture": True,
            "no_monitor_mode": True,
            "no_serial_capture": True,
            "no_sd_card_read_write": True,
            "no_mqtt_or_udp_listener": True,
            "no_esp32_or_router_tools": True,
            "no_external_apis_except_git_clone_fetch": True,
            "no_source_vendoring": True,
            "no_medical_or_clinical_claims": True,
        },
        "references": [
            {
                "repo": "NTUMARS/Awesome-WiFi-CSI-Sensing",
                "status": "staged_reference",
                "local_path": (
                    "C:\\AI\\external-sources\\somatic\\wifi-csi\\Awesome-WiFi-CSI-Sensing"
                ),
                "commit": "fc8e21f4392d16fa110f1e00952d7f6bfd8f78c0",
                "license": {"identifier": "MIT", "file": "LICENSE"},
                "runtime_dependency": False,
                "no_runtime_execution": True,
                "no_hardware_access": True,
                "no_dependency_install": True,
                "no_source_vendoring": True,
            },
            {
                "repo": "thu4n/ESP32-WiFi-Sensing",
                "status": "staged_reference",
                "local_path": "C:\\AI\\external-sources\\somatic\\wifi-csi\\ESP32-WiFi-Sensing",
                "commit": "9ebd9204cd695e9772a78f466532a7a99c790a67",
                "license": {
                    "identifier": "license-unclear",
                    "file": None,
                    "notes": "No root license file found; nested esp32-csi-tool/LICENSE is MIT.",
                },
                "runtime_dependency": False,
                "no_runtime_execution": True,
                "no_hardware_access": True,
                "no_dependency_install": True,
                "no_source_vendoring": True,
            },
            {
                "repo": "MaliosDark/wifi-3d-fusion",
                "status": "staged_reference",
                "local_path": "C:\\AI\\external-sources\\somatic\\wifi-csi\\wifi-3d-fusion",
                "commit": "0c0f99e6af9fa1a22d850c45b8f23aa75f34f328",
                "license": {
                    "identifier": "requires-review",
                    "file": "LICENSE",
                    "notes": "LICENSE says Apache-2.0; README badge says GPL-2.0.",
                },
                "runtime_dependency": False,
                "no_runtime_execution": True,
                "no_hardware_access": True,
                "no_dependency_install": True,
                "no_source_vendoring": True,
            },
            {
                "repo": "ruvnet/RuView",
                "status": CSI_RUVIEW_STATUS,
                "local_path": None,
                "commit": None,
                "license": {"identifier": "not-inspected", "file": None},
                "runtime_dependency": False,
                "no_runtime_execution": True,
                "no_hardware_access": True,
                "no_dependency_install": True,
                "no_source_vendoring": True,
                "reference_only": True,
                "reassessable": True,
                "v2_reassessment": {
                    "rust_workspace_reported": True,
                    "wifi_densepose_crates_reported": True,
                    "signal_pipeline_crates_reported": True,
                    "temporal_embedding_metric_reported": True,
                    "downstream_accuracy_validated": False,
                    "deployment_claims_verified": False,
                },
                "warning_history": [
                    "earlier-overclaims",
                    "incompatible-model-loading-concerns",
                    "unverified-deployment-claims",
                    "self-published-v2-materials-only",
                ],
                "failure_reason": None,
            },
        ],
    }


def _load_csi_reference_inventory_fixture() -> dict[str, object] | None:
    fixture_path = Path(__file__).resolve().parents[2] / CSI_REFERENCE_INVENTORY_REF
    if not fixture_path.exists():
        return None
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        return payload
    return None


def build_csi_metadata(workflow: dict[str, object]) -> dict[str, object]:
    capture_plan = build_csi_capture_plan(workflow)
    feature_plan = build_csi_feature_plan(capture_plan)
    feature_set = build_csi_feature_set(capture_plan, feature_plan)
    adapter_surfaces = safe_csi_source_adapter_surfaces()
    return {
        "schema_version": 1,
        "status": "placeholder-metadata-only",
        "planning_only": True,
        "disabled_by_default": True,
        "fake_backed": True,
        "offline": True,
        "parser_capabilities": _public_parser_capabilities(),
        "capture_plan": capture_plan.to_dict(),
        "feature_plan": feature_plan.to_dict(),
        "feature_set": feature_set.to_dict(),
        "fake_observations": build_fake_csi_observations(capture_plan),
        "reference_inventory_ref": CSI_REFERENCE_INVENTORY_LABEL,
        "boundary_statements": list(CSI_BOUNDARY_STATEMENTS),
        **adapter_surfaces,
    }


def _public_parser_capabilities() -> dict[str, object]:
    payload = dict(CSI_PARSER_CAPABILITIES)
    payload["supported_formats"] = list(CSI_METADATA_PUBLIC_SUPPORTED_FORMATS)
    return payload


def build_csi_evidence_metadata(
    feature_set_ref: str,
    feature_set_sha256: str,
    csi_metadata: dict[str, object],
    csi_evidence_scoring: dict[str, object] | None = None,
) -> dict[str, object]:
    feature_set = csi_metadata["feature_set"]
    adapter_surfaces = safe_csi_source_adapter_surfaces(csi_metadata)
    payload = {
        "schema_version": 1,
        "status": "placeholder-metadata-only",
        "planning_only": True,
        "fake_backed": True,
        "offline": True,
        "feature_set_ref": feature_set_ref,
        "feature_set_sha256": feature_set_sha256,
        "csi_feature_set_id": feature_set["id"],
        "mapped_feature_names": list(feature_set["features"]),
        "hardware_access": False,
        "packet_capture": False,
        "wifi_network_probing": False,
        "monitor_mode": False,
        "network_calls": False,
        "clinical_interpretation": False,
        "medical_or_clinical_claim": False,
        **adapter_surfaces,
    }
    if csi_evidence_scoring is not None:
        payload["evidence_scoring"] = dict(csi_evidence_scoring)
    return payload


def build_csi_summary_metadata(
    workflow_mode: object,
    provider_id: str,
    feature_set_id: str,
    sensor_evidence_record_id: str,
    csi_metadata: dict[str, object],
) -> dict[str, object]:
    csi_feature_set = csi_metadata["feature_set"]
    capture_plan = csi_metadata["capture_plan"]
    adapter_surfaces = safe_csi_source_adapter_surfaces(csi_metadata)
    return {
        "schema_version": 1,
        "status": "placeholder-metadata-only",
        "workflow_mode": workflow_mode,
        "provider_id": provider_id,
        "sensor_feature_set_id": feature_set_id,
        "sensor_evidence_record_id": sensor_evidence_record_id,
        "csi_capture_plan_id": capture_plan["id"],
        "csi_feature_set_id": csi_feature_set["id"],
        "mapped_feature_names": list(csi_feature_set["features"]),
        "reference_inventory_ref": CSI_REFERENCE_INVENTORY_LABEL,
        "planning_only": True,
        "disabled_by_default": True,
        "fake_backed": True,
        "hardware_access": False,
        "packet_capture": False,
        "wifi_network_probing": False,
        "monitor_mode": False,
        "network_calls": False,
        "raw_rf_data_collected": False,
        "raw_csi_data_collected": False,
        "raw_rf_data_exported": False,
        "raw_csi_data_exported": False,
        "clinical_interpretation": False,
        "medical_or_clinical_claim": False,
        **adapter_surfaces,
    }


def safe_csi_source_adapter_surfaces(
    csi_metadata: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Validate CSI source metadata before surfacing adapter fields."""

    adapter_output = fixture_csi_source_adapter_output()
    if isinstance(csi_metadata, Mapping):
        ruview = csi_metadata.get("ruview_reference")
        if isinstance(ruview, Mapping):
            adapter_output["ruview_reference"] = dict(ruview)
        booth_profile = csi_metadata.get("booth_planning_profile")
        if isinstance(booth_profile, Mapping):
            adapter_output["booth_planning_profile"] = dict(booth_profile)
    adapter_validation = validate_csi_source_adapter_output(adapter_output)
    sanitized_output = adapter_validation.sanitized_output
    return {
        "ruview_dependency": sanitized_output["ruview_reference"]["status"],
        "ruview_reference": dict(sanitized_output["ruview_reference"]),
        "booth_planning_profile": dict(sanitized_output["booth_planning_profile"]),
        "source_adapter_status": wifi_csi_source_adapter_status(),
        "source_adapter_output_validation": adapter_validation.to_dict(),
    }


__all__ = [
    "CSI_ARTIFACT_NOISE_FLAGS",
    "CSI_BOUNDARY_STATEMENTS",
    "CSI_FAKE_FEATURES",
    "CSI_FEATURE_NAMES",
    "CSI_METADATA_PUBLIC_SUPPORTED_FORMATS",
    "CSI_REFERENCE_INVENTORY_REF",
    "CSI_REFERENCE_INVENTORY_LABEL",
    "CSI_RUVIEW_STATUS",
    "CSI_PARSER_CAPABILITIES",
    "CsiCapturePlan",
    "CsiFeaturePlan",
    "CsiFeatureSet",
    "CsiHardwareProfile",
    "CsiPrivacyBoundary",
    "build_csi_capture_plan",
    "build_csi_evidence_metadata",
    "build_csi_feature_plan",
    "build_csi_feature_set",
    "build_csi_hardware_profile",
    "build_csi_metadata",
    "build_csi_privacy_boundary",
    "build_csi_reference_inventory",
    "build_csi_summary_metadata",
    "build_fake_csi_observations",
    "safe_csi_source_adapter_surfaces",
]
