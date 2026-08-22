"""Evidence Bus record types. Adapters live in sibling modules."""

from dataclasses import asdict, dataclass, field

EVIDENCE_MODALITIES = {
    "sim",
    "wetlab",
    "csi",
    "video",
    "video3d",
    "thermal",
    "audio",
    "wearable",
    "environmental",
    "literature",
}


@dataclass(frozen=True)
class EvidenceSource:
    id: str
    modality: str
    provider_ref: str
    description: str
    metadata: dict[str, object] = field(default_factory=dict)

    def __post_init__(self):
        if self.modality not in EVIDENCE_MODALITIES:
            raise ValueError(f"Unsupported evidence modality: {self.modality}")

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class MeasurementPlan:
    id: str
    sources: list[EvidenceSource]
    objective: str
    safety_profile: str = "research-only"
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class RawEvidence:
    id: str
    source: EvidenceSource
    payload_ref: str
    sha256: str
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class StructuredVerdict:
    id: str
    raw_evidence_refs: list[str]
    summary: str
    confidence: str
    limitations: list[str] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)
