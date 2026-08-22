"""Biomodel artifact provenance and Fabric pack planning helpers."""

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

BIOMODEL_PROVENANCE_ARTIFACT_ORDER = (
    "biomodel_request",
    "biomodel_readiness_report",
    "biomodel_consent_record",
    "biomodel_plan",
    "biomodel_result",
    "biomodel_evidence_record",
    "biomodel_raw_evidence",
    "biomodel_structured_verdict",
)

BIOMODEL_ARTIFACT_ROLES = {
    "biomodel_request": "request",
    "biomodel_readiness_report": "readiness",
    "biomodel_consent_record": "consent",
    "biomodel_plan": "plan",
    "biomodel_result": "result",
    "biomodel_evidence_record": "evidence-record",
    "biomodel_raw_evidence": "raw-evidence",
    "biomodel_structured_verdict": "structured-verdict",
}

ALLOWED_BIOMODEL_PACK_CANDIDATE_TYPES = {"dataset", "document"}


@dataclass(frozen=True)
class BiomodelArtifactRef:
    id: str
    relative_path: str
    sha256: str
    role: str
    content_type: str = "application/json"
    local_only: bool = True
    research_only: bool = True

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "BiomodelArtifactRef":
        return cls(
            id=str(payload["id"]),
            relative_path=str(payload["relative_path"]),
            sha256=str(payload["sha256"]),
            role=str(payload["role"]),
            content_type=str(payload.get("content_type", "application/json")),
            local_only=bool(payload.get("local_only", True)),
            research_only=bool(payload.get("research_only", True)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "relative_path": self.relative_path,
            "sha256": self.sha256,
            "role": self.role,
            "content_type": self.content_type,
            "local_only": self.local_only,
            "research_only": self.research_only,
        }


@dataclass(frozen=True)
class BiomodelProvenanceBundle:
    id: str
    provider_id: str
    provider_version: str
    provider_scaffold_status: str
    source: dict[str, Any]
    artifact_refs: tuple[BiomodelArtifactRef, ...]
    phase: str = "6D"
    workflow_id: str | None = None
    assumptions: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    mock: bool = True
    offline: bool = True
    research_only: bool = True
    runtime_execution: bool = False
    model_downloads: bool = False
    msa_server: bool = False
    network_calls: bool = False
    gpu_execution: bool = False
    fabric_publish_enabled: bool = False
    fabric_transport_enabled: bool = False
    fabric_install_enabled: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "BiomodelProvenanceBundle":
        return cls(
            id=str(payload["id"]),
            provider_id=str(payload["provider_id"]),
            provider_version=str(payload["provider_version"]),
            provider_scaffold_status=str(payload["provider_scaffold_status"]),
            source=dict(payload.get("source", {})),
            artifact_refs=tuple(
                BiomodelArtifactRef.from_dict(item) for item in payload.get("artifact_refs", ())
            ),
            phase=str(payload.get("phase", "6D")),
            workflow_id=payload.get("workflow_id"),
            assumptions=tuple(payload.get("assumptions", ())),
            limitations=tuple(payload.get("limitations", ())),
            mock=bool(payload.get("mock", True)),
            offline=bool(payload.get("offline", True)),
            research_only=bool(payload.get("research_only", True)),
            runtime_execution=bool(payload.get("runtime_execution", False)),
            model_downloads=bool(payload.get("model_downloads", False)),
            msa_server=bool(payload.get("msa_server", False)),
            network_calls=bool(payload.get("network_calls", False)),
            gpu_execution=bool(payload.get("gpu_execution", False)),
            fabric_publish_enabled=bool(payload.get("fabric_publish_enabled", False)),
            fabric_transport_enabled=bool(payload.get("fabric_transport_enabled", False)),
            fabric_install_enabled=bool(payload.get("fabric_install_enabled", False)),
            metadata=dict(payload.get("metadata", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "id": self.id,
            "provider_id": self.provider_id,
            "provider_version": self.provider_version,
            "provider_scaffold_status": self.provider_scaffold_status,
            "source": dict(self.source),
            "artifact_refs": [item.to_dict() for item in self.artifact_refs],
            "phase": self.phase,
            "workflow_id": self.workflow_id,
            "assumptions": list(self.assumptions),
            "limitations": list(self.limitations),
            "mock": self.mock,
            "offline": self.offline,
            "research_only": self.research_only,
            "runtime_execution": self.runtime_execution,
            "model_downloads": self.model_downloads,
            "msa_server": self.msa_server,
            "network_calls": self.network_calls,
            "gpu_execution": self.gpu_execution,
            "fabric_publish_enabled": self.fabric_publish_enabled,
            "fabric_transport_enabled": self.fabric_transport_enabled,
            "fabric_install_enabled": self.fabric_install_enabled,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class BiomodelPackPlan:
    id: str
    bundle_id: str
    bundle_sha256: str
    phase: str = "6D"
    status: str = "planned-not-packed"
    pack_class: str = "data"
    candidate_type: str = "dataset"
    alternate_candidate_type: str = "document"
    code_pack: bool = False
    executable_files: tuple[str, ...] = ()
    publishing_enabled: bool = False
    catalog_publish_enabled: bool = False
    transport_status: str = "absent-future"
    signing_enabled: bool = False
    signed_pack_created: bool = False
    draft_pack_manifest: bool = False
    license_review_required: bool = True
    public_seeding_allowed: bool = False
    artifacts_local_research_outputs: bool = True
    recommended_files: tuple[BiomodelArtifactRef, ...] = ()
    requirements_before_public_packaging: tuple[str, ...] = (
        "license review before public seeding",
        "provenance review",
        "safety review",
        "hash verification",
        "explicit publication approval",
    )
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "BiomodelPackPlan":
        return cls(
            id=str(payload["id"]),
            bundle_id=str(payload["bundle_id"]),
            bundle_sha256=str(payload["bundle_sha256"]),
            phase=str(payload.get("phase", "6D")),
            status=str(payload.get("status", "planned-not-packed")),
            pack_class=str(payload.get("pack_class", "data")),
            candidate_type=str(payload.get("candidate_type", "dataset")),
            alternate_candidate_type=str(payload.get("alternate_candidate_type", "document")),
            code_pack=bool(payload.get("code_pack", False)),
            executable_files=tuple(payload.get("executable_files", ())),
            publishing_enabled=bool(payload.get("publishing_enabled", False)),
            catalog_publish_enabled=bool(payload.get("catalog_publish_enabled", False)),
            transport_status=str(payload.get("transport_status", "absent-future")),
            signing_enabled=bool(payload.get("signing_enabled", False)),
            signed_pack_created=bool(payload.get("signed_pack_created", False)),
            draft_pack_manifest=bool(payload.get("draft_pack_manifest", False)),
            license_review_required=bool(payload.get("license_review_required", True)),
            public_seeding_allowed=bool(payload.get("public_seeding_allowed", False)),
            artifacts_local_research_outputs=bool(
                payload.get("artifacts_local_research_outputs", True)
            ),
            recommended_files=tuple(
                BiomodelArtifactRef.from_dict(item) for item in payload.get("recommended_files", ())
            ),
            requirements_before_public_packaging=tuple(
                payload.get("requirements_before_public_packaging", ())
            ),
            metadata=dict(payload.get("metadata", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "id": self.id,
            "bundle_id": self.bundle_id,
            "bundle_sha256": self.bundle_sha256,
            "phase": self.phase,
            "status": self.status,
            "pack_class": self.pack_class,
            "candidate_type": self.candidate_type,
            "alternate_candidate_type": self.alternate_candidate_type,
            "code_pack": self.code_pack,
            "executable_files": list(self.executable_files),
            "publishing_enabled": self.publishing_enabled,
            "catalog_publish_enabled": self.catalog_publish_enabled,
            "transport_status": self.transport_status,
            "signing_enabled": self.signing_enabled,
            "signed_pack_created": self.signed_pack_created,
            "draft_pack_manifest": self.draft_pack_manifest,
            "license_review_required": self.license_review_required,
            "public_seeding_allowed": self.public_seeding_allowed,
            "artifacts_local_research_outputs": (self.artifacts_local_research_outputs),
            "recommended_files": [item.to_dict() for item in self.recommended_files],
            "requirements_before_public_packaging": list(self.requirements_before_public_packaging),
            "metadata": dict(self.metadata),
        }


def hash_artifact_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_artifact_payload(payload: dict[str, Any]) -> str:
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def collect_run_artifact_refs(
    run_dir: str | Path,
    artifact_names: tuple[str, ...] = BIOMODEL_PROVENANCE_ARTIFACT_ORDER,
) -> tuple[BiomodelArtifactRef, ...]:
    root = Path(run_dir)
    refs = []
    for name in artifact_names:
        relative_path = f"artifacts/{name}.json"
        refs.append(
            BiomodelArtifactRef(
                id=name,
                relative_path=relative_path,
                sha256=hash_artifact_file(root / relative_path),
                role=BIOMODEL_ARTIFACT_ROLES.get(name, name),
            )
        )
    return tuple(refs)


def build_biomodel_provenance_bundle(
    artifact_payloads: dict[str, dict[str, Any]],
    provider_status: dict[str, Any] | None = None,
    workflow_id: str | None = None,
) -> BiomodelProvenanceBundle:
    provider_status = provider_status or {}
    plan = artifact_payloads.get("biomodel_plan", {})
    result = artifact_payloads.get("biomodel_result", {})
    plan_provenance = dict(plan.get("provenance", {}))
    provider_id = str(
        plan.get("provider_id")
        or result.get("metadata", {}).get("provider_id")
        or provider_status.get("provider_id")
        or "unknown-biomodel-provider"
    )
    provider_version = str(
        plan.get("model_version")
        or provider_status.get("default_model")
        or provider_status.get("version")
        or "unknown"
    )
    artifact_refs = _artifact_refs_from_payloads(artifact_payloads)
    bundle_id = (
        f"biomodel-provenance-{workflow_id}"
        if workflow_id
        else "biomodel-provenance-"
        + _stable_digest(
            {
                "provider_id": provider_id,
                "provider_version": provider_version,
                "artifact_refs": [item.to_dict() for item in artifact_refs],
            }
        )[:12]
    )
    return BiomodelProvenanceBundle(
        id=bundle_id,
        provider_id=provider_id,
        provider_version=provider_version,
        provider_scaffold_status=str(provider_status.get("status") or "scaffolded"),
        source={
            "source_path": plan_provenance.get("source_path")
            or provider_status.get("staged_source_path"),
            "inspected_commit": plan_provenance.get("inspected_commit")
            or provider_status.get("inspected_commit"),
            "license": plan_provenance.get("license") or provider_status.get("license"),
            "source_staged": plan_provenance.get("source_staged"),
            "optional_dependency_available": plan_provenance.get("optional_dependency_available"),
        },
        artifact_refs=artifact_refs,
        workflow_id=workflow_id,
        assumptions=_stable_strings(plan.get("assumptions", ()), result.get("assumptions", ())),
        limitations=_stable_strings(plan.get("limitations", ()), result.get("limitations", ())),
        metadata={
            "phase": "6D",
            "provenance_scope": "fake-backed-biomodel-planning-artifacts",
            "fabric_packaging": "planning-only",
            "no_fabric_publish": True,
            "no_fabric_transport": True,
            "no_fabric_install": True,
        },
    )


def build_biomodel_provenance_bundle_from_run(
    run_dir: str | Path,
    provider_status: dict[str, Any] | None = None,
) -> BiomodelProvenanceBundle:
    root = Path(run_dir)
    payloads = {
        name: json.loads((root / f"artifacts/{name}.json").read_text(encoding="utf-8"))
        for name in BIOMODEL_PROVENANCE_ARTIFACT_ORDER
    }
    manifest = {}
    manifest_path = root / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if provider_status is None:
        provider_status = {}
        for provider in manifest.get("providers", ()):
            if provider.get("class") == "biomodel":
                provider_status = dict(provider)
                break
    manifest_workflow_id = manifest.get("workflow_id")
    return build_biomodel_provenance_bundle(payloads, provider_status, manifest_workflow_id)


def build_biomodel_pack_plan(
    bundle: BiomodelProvenanceBundle | dict[str, Any],
    *,
    candidate_type: str = "dataset",
    draft: bool = False,
) -> BiomodelPackPlan:
    if candidate_type not in ALLOWED_BIOMODEL_PACK_CANDIDATE_TYPES:
        raise ValueError("Biomodel pack plan candidate_type must be 'dataset' or 'document'.")
    bundle_obj = BiomodelProvenanceBundle.from_dict(bundle) if isinstance(bundle, dict) else bundle
    bundle_payload = bundle_obj.to_dict()
    bundle_sha256 = hash_artifact_payload(bundle_payload)
    plan_id = (
        "biomodel-pack-plan-"
        + _stable_digest(
            {
                "bundle_id": bundle_obj.id,
                "bundle_sha256": bundle_sha256,
                "candidate_type": candidate_type,
                "draft": draft,
            }
        )[:12]
    )
    return BiomodelPackPlan(
        id=plan_id,
        bundle_id=bundle_obj.id,
        bundle_sha256=bundle_sha256,
        candidate_type=candidate_type,
        draft_pack_manifest=draft,
        recommended_files=bundle_obj.artifact_refs,
        metadata={
            "phase": "6D",
            "pack_planning_only": True,
            "future_transport": "not implemented",
            "future_publication": "not approved",
            "source_bundle_provider_id": bundle_obj.provider_id,
            "all_artifacts_local_test_fixtures_or_research_outputs": True,
        },
    )


def _artifact_refs_from_payloads(
    artifact_payloads: dict[str, dict[str, Any]],
) -> tuple[BiomodelArtifactRef, ...]:
    refs = []
    for name in BIOMODEL_PROVENANCE_ARTIFACT_ORDER:
        if name not in artifact_payloads:
            continue
        refs.append(
            BiomodelArtifactRef(
                id=name,
                relative_path=f"artifacts/{name}.json",
                sha256=hash_artifact_payload(artifact_payloads[name]),
                role=BIOMODEL_ARTIFACT_ROLES.get(name, name),
            )
        )
    return tuple(refs)


def _stable_strings(*values: Any) -> tuple[str, ...]:
    seen = set()
    result = []
    for value in values:
        for item in value or ():
            text = str(item)
            if text not in seen:
                seen.add(text)
                result.append(text)
    return tuple(result)


def _stable_digest(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
