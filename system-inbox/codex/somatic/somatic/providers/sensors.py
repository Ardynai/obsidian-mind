from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Protocol

from somatic.evidence_bus import RawEvidence, StructuredVerdict

SENSOR_MODALITIES = {
    "csi",
    "video",
    "video3d",
    "thermal",
    "audio",
    "wearable",
    "environmental",
}

SENSOR_BOUNDARY_STATEMENTS = (
    "simulated",
    "offline",
    "no hardware access",
    "no clinical interpretation",
    "no emergency triage",
    "no real monitoring",
)


@dataclass(frozen=True)
class SensorPrivacyPolicy:
    id: str
    local_first: bool = True
    private_by_default: bool = True
    raw_data_leaves_machine: bool = False
    explicit_consent_required: bool = True
    retention: str = "run-artifact-metadata-only"
    allowed_exports: tuple[str, ...] = ()
    blocked_exports: tuple[str, ...] = (
        "raw-camera",
        "raw-microphone",
        "raw-csi",
        "raw-wearable",
    )
    safety_review_required_for_real_mode: bool = True
    notes: tuple[str, ...] = SENSOR_BOUNDARY_STATEMENTS
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class SensorStreamPlan:
    id: str
    provider_id: str
    workflow_id: str
    mode: str
    modalities: tuple[str, ...]
    requested_features: tuple[str, ...]
    observation_window: str
    baseline_ref: str
    privacy_policy: SensorPrivacyPolicy
    simulated: bool = True
    offline: bool = True
    hardware_access: bool = False
    network_calls: bool = False
    clinical_interpretation: bool = False
    emergency_triage: bool = False
    real_monitoring: bool = False
    blocked_actions: tuple[str, ...] = SENSOR_BOUNDARY_STATEMENTS
    metadata: dict[str, object] = field(default_factory=dict)

    def __post_init__(self):
        unsupported = set(self.modalities) - SENSOR_MODALITIES
        if unsupported:
            raise ValueError("Unsupported sensor modalities: " + ", ".join(sorted(unsupported)))

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class SensorObservation:
    id: str
    stream_plan_id: str
    modality: str
    observed_at: str
    feature_name: str
    value: object
    unit: str | None = None
    simulated: bool = True
    offline: bool = True
    hardware_access: bool = False
    clinical_interpretation: bool = False
    emergency_triage: bool = False
    metadata: dict[str, object] = field(default_factory=dict)

    def __post_init__(self):
        if self.modality not in SENSOR_MODALITIES:
            raise ValueError(f"Unsupported sensor modality: {self.modality}")

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class SensorFeatureSet:
    id: str
    stream_plan_id: str
    provider_id: str
    features: dict[str, object]
    source_observation_ids: tuple[str, ...]
    simulated: bool = True
    offline: bool = True
    hardware_access: bool = False
    clinical_interpretation: bool = False
    emergency_triage: bool = False
    real_monitoring: bool = False
    limitations: tuple[str, ...] = SENSOR_BOUNDARY_STATEMENTS
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class SensorEvidenceRecord:
    id: str
    provider_id: str
    stream_plan_id: str
    raw_evidence: RawEvidence
    structured_verdict: StructuredVerdict
    feature_set_ref: str
    privacy_policy: SensorPrivacyPolicy
    simulated: bool = True
    offline: bool = True
    hardware_access: bool = False
    clinical_interpretation: bool = False
    emergency_triage: bool = False
    real_monitoring: bool = False
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "provider_id": self.provider_id,
            "stream_plan_id": self.stream_plan_id,
            "raw_evidence": self.raw_evidence.to_dict(),
            "structured_verdict": self.structured_verdict.to_dict(),
            "feature_set_ref": self.feature_set_ref,
            "privacy_policy": self.privacy_policy.to_dict(),
            "simulated": self.simulated,
            "offline": self.offline,
            "hardware_access": self.hardware_access,
            "clinical_interpretation": self.clinical_interpretation,
            "emergency_triage": self.emergency_triage,
            "real_monitoring": self.real_monitoring,
            "metadata": dict(self.metadata),
        }


class SensorProvider(Protocol):
    provider_id: str
    offline_supported: bool
    modalities: tuple[str, ...]

    def privacy_policy(self) -> SensorPrivacyPolicy:
        """Return the local-first privacy policy before planning any stream."""
        ...

    def plan_stream(self, workflow: dict[str, object]) -> SensorStreamPlan:
        """Describe a sensor stream without touching hardware."""
        ...

    def observations(self, plan: SensorStreamPlan) -> list[SensorObservation]:
        """Return deterministic observations from fixtures or sandbox data."""
        ...

    def features(
        self,
        plan: SensorStreamPlan,
        observations: list[SensorObservation],
    ) -> SensorFeatureSet:
        """Return deterministic feature metadata derived from observations."""
        ...

    def evidence_record(
        self,
        plan: SensorStreamPlan,
        feature_set: SensorFeatureSet,
    ) -> SensorEvidenceRecord:
        """Map feature metadata into Evidence Bus records."""
        ...

    def replay_csi_fixtures(
        self,
        fixture_refs: tuple[str, ...] | list[str],
        repo_root: str | Path | None = None,
    ) -> dict[str, object]:
        """Return sanitized parser report/summary metadata for local CSI fixtures."""
        ...


__all__ = [
    "SENSOR_BOUNDARY_STATEMENTS",
    "SENSOR_MODALITIES",
    "SensorEvidenceRecord",
    "SensorFeatureSet",
    "SensorObservation",
    "SensorPrivacyPolicy",
    "SensorProvider",
    "SensorStreamPlan",
]
