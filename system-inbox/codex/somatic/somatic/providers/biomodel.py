from dataclasses import asdict, dataclass, field
from typing import Protocol

from somatic.evidence_bus import EvidenceSource, RawEvidence, StructuredVerdict


@dataclass(frozen=True)
class BiomodelRequest:
    objective: str
    target_refs: tuple[str, ...] = ()
    input_artifact_refs: tuple[str, ...] = ()
    constraints: dict[str, object] = field(default_factory=dict)
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class BiomodelPlan:
    id: str
    provider_id: str
    request_id: str
    objective: str
    status: str
    model_family: str
    model_version: str
    command_shape: tuple[str, ...] = ()
    input_artifact_refs: tuple[str, ...] = ()
    output_artifact_refs: tuple[str, ...] = ()
    required_local_artifacts: tuple[str, ...] = ()
    blocked_actions: tuple[str, ...] = ()
    consent_requirements: tuple[str, ...] = ()
    resource_requirements: dict[str, object] = field(default_factory=dict)
    assumptions: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    provenance: dict[str, object] = field(default_factory=dict)
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class BiomodelResult:
    id: str
    status: str
    artifact_refs: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class BiomodelEvidenceRecord:
    id: str
    provider_id: str
    result_id: str
    raw_evidence: RawEvidence
    structured_verdict: StructuredVerdict
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "provider_id": self.provider_id,
            "result_id": self.result_id,
            "raw_evidence": self.raw_evidence.to_dict(),
            "structured_verdict": self.structured_verdict.to_dict(),
            "metadata": dict(self.metadata),
        }


def biomodel_result_to_evidence_record(
    request: BiomodelRequest,
    result: BiomodelResult,
    *,
    provider_id: str,
) -> BiomodelEvidenceRecord:
    """Map biomodel result metadata into Somatic Evidence Bus records.

    Biomodel output is represented as simulation-shaped research evidence until
    the Evidence Bus gets a dedicated biomodel modality.
    """
    source = EvidenceSource(
        id=f"{result.id}-source",
        modality="sim",
        provider_ref=provider_id,
        description="Biomodel scaffold output mapped as simulation-shaped research evidence.",
        metadata={
            "submodality": "biomodel",
            "objective": request.objective,
            "research_only": True,
            "clinical_or_lab_conclusion": False,
        },
    )
    raw = RawEvidence(
        id=f"{result.id}-raw-evidence",
        source=source,
        payload_ref=(
            result.artifact_refs[0]
            if result.artifact_refs
            else f"biomodel://{provider_id}/{result.id}/metadata-only"
        ),
        sha256=str(result.metadata.get("sha256", "0" * 64)),
        metadata={
            "provider_result_id": result.id,
            "assumptions": list(result.assumptions),
            "limitations": list(result.limitations),
            "mock": bool(result.metadata.get("mock", False)),
            "runtime_execution": bool(result.metadata.get("runtime_execution", False)),
            "model_downloads": bool(result.metadata.get("model_downloads", False)),
            "msa_server": bool(result.metadata.get("msa_server", False)),
            "network_calls": bool(result.metadata.get("network_calls", False)),
            "gpu_execution": bool(result.metadata.get("gpu_execution", False)),
            "readiness_report": dict(result.metadata.get("readiness_report", {})),
        },
    )
    verdict = StructuredVerdict(
        id=f"{result.id}-structured-verdict",
        raw_evidence_refs=[raw.id],
        summary=(
            "Biomodel scaffold metadata only; no model prediction, lab action, "
            "clinical conclusion, or efficacy claim was produced."
        ),
        confidence="not-applicable",
        limitations=list(result.limitations),
        metadata={
            "provider_result_id": result.id,
            "result_status": result.status,
            "research_only": True,
        },
    )
    return BiomodelEvidenceRecord(
        id=f"{result.id}-evidence-record",
        provider_id=provider_id,
        result_id=result.id,
        raw_evidence=raw,
        structured_verdict=verdict,
        metadata={
            "mapping": "biomodel-result-to-raw-evidence-and-structured-verdict",
            "submodality": "biomodel",
        },
    )


class BiomodelProvider(Protocol):
    provider_id: str
    offline_supported: bool

    def plan(self, request: BiomodelRequest) -> BiomodelPlan:
        """Describe a model run before any execution, download, or data release."""
        ...

    def run(self, request: BiomodelRequest) -> BiomodelResult:
        """Execute only when explicitly configured by a future integration phase."""
        ...
