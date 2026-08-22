"""Planning-only Fabric pack scaffold for n-of-1 report packets."""

from dataclasses import asdict, dataclass, field
from pathlib import Path

from somatic.sensors.evidence import (
    build_sensor_evidence_artifact_ref,
    classify_sensor_evidence_artifact_ref,
    safe_sensor_artifact_ref,
)

from .n_of_1_packet import (
    EXPECTED_N_OF_1_PACKET_ARTIFACTS,
    N_OF_1_SENSOR_EVIDENCE_ARTIFACTS,
    artifact_payload_sha256,
)

LOCAL_DIAGNOSTIC_N_OF_1_ARTIFACTS = (
    "csi_parser_report",
    "csi_parsed_summary",
)
N_OF_1_FABRIC_PLAN_LIMITATIONS = (
    "Planning-only Fabric data-pack candidate for local n-of-1 report packet artifacts.",
    "This is not a Content Fabric pack.json manifest.",
    "No Fabric signing, catalog publication, transport, magnet, WebSeed, seeding, upload, "
    "install, or execution is enabled.",
    "No publisher, keyring, catalog entry, manifest digest, transport, magnet URI, "
    "WebSeed, install target, or code-pack permission surface is created.",
    "No real personal data, personal health data, baseline data, raw sensor data, raw "
    "RF/CSI data, or health record is exported.",
    "Hashes are for local reproducibility/provenance only and do not imply clinical "
    "validity, monitoring, intervention effectiveness, treatment guidance, or advice.",
    "The plan is not medical advice, not a medical record, not a health record, and not a "
    "clinical or effectiveness claim.",
)

N_OF_1_FABRIC_PLAN_FUTURE_REQUIREMENTS = (
    "explicit consent",
    "redaction review",
    "license review",
    "privacy review",
    "safety review",
    "human review",
    "local-first storage controls",
    "retention and export controls",
    "separate publication approval",
)


@dataclass(frozen=True)
class NOf1FabricFilePlan:
    id: str
    path: str
    sha256: str | None
    source: str
    kind: str
    present: bool
    retention: str
    content_type: str = "application/json"
    local_only: bool = True
    research_only: bool = True
    role: str | None = None
    created_by_stage: str | None = None
    loop_stage: str | None = None
    include_in_candidate: bool = True
    executable: bool = False
    contains_code: bool = False
    contains_real_personal_data: bool = False
    personal_health_data_exported: bool = False

    def to_dict(self) -> dict[str, object]:
        return _json_ready(asdict(self))


@dataclass(frozen=True)
class NOf1FabricPackPlan:
    id: str
    run_id: str
    source_run_dir: str
    generated_at: str
    report_packet_id: str
    report_packet_ref: str
    report_packet_sha256: str
    report_packet_artifact_count: int
    artifact_hashes: dict[str, str | None]
    sensor_evidence_artifact_refs: dict[str, dict[str, object]]
    planned_sensor_evidence_artifact_ids: tuple[str, ...]
    planned_file_ids: tuple[str, ...]
    file_plans: tuple[dict[str, object], ...]
    file_count: int
    summary: dict[str, object]
    schema_version: int = 1
    status: str = "planned-not-packed"
    planning_only: bool = True
    pack_planning_only: bool = True
    local_only: bool = True
    pack_class: str = "data"
    pack_class_recommendation: str = "data"
    suggested_type: str = "document"
    candidate_type: str = "document"
    alternate_suggested_type: str = "dataset"
    alternate_candidate_type: str = "dataset"
    license_status: str = "placeholder-review-required"
    license_review_status: str = "not-reviewed"
    privacy_review_status: str = "not-reviewed"
    redaction_status: str = "not-reviewed"
    safety_review_status: str = "not-reviewed"
    human_review_status: str = "not-reviewed"
    private_only_by_default: bool = True
    seedable: bool = False
    public_seeding_allowed: bool = False
    publishing_enabled: bool = False
    catalog_publish_enabled: bool = False
    catalog_publication_enabled: bool = False
    signing_enabled: bool = False
    signed_pack_created: bool = False
    draft_pack_manifest: bool = False
    pack_json_created: bool = False
    transport_status: str = "absent-future"
    transport_enabled: bool = False
    torrent_created: bool = False
    magnet_uri_created: bool = False
    webseed_created: bool = False
    upload_enabled: bool = False
    install_enabled: bool = False
    execution_enabled: bool = False
    code_pack: bool = False
    contains_code: bool = False
    contains_executable_files: bool = False
    executable_files: tuple[str, ...] = ()
    contains_real_personal_data: bool = False
    real_personal_data_exported: bool = False
    personal_data_exported: bool = False
    personal_health_data_exported: bool = False
    baseline_data_exported: bool = False
    raw_real_health_data_allowed: bool = False
    raw_sensor_data_collected: bool = False
    raw_rf_csi_data_exported: bool = False
    hardware_access: bool = False
    live_sensor_access: bool = False
    network_calls: bool = False
    database_access: bool = False
    external_memory: bool = False
    medical_advice: bool = False
    medical_record: bool = False
    health_record: bool = False
    clinical_interpretation: bool = False
    medical_or_clinical_claim: bool = False
    effectiveness_claim: bool = False
    diagnosis: bool = False
    emergency_triage: bool = False
    limitations: tuple[str, ...] = N_OF_1_FABRIC_PLAN_LIMITATIONS
    future_real_packaging_requirements: tuple[str, ...] = N_OF_1_FABRIC_PLAN_FUTURE_REQUIREMENTS
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        payload = _json_ready(asdict(self))
        payload["class"] = payload.pop("pack_class")
        return payload


def build_n_of_1_fabric_pack_plan(
    *,
    run_dir: str | Path,
    report_packet: dict[str, object],
    generated_at: str | None = None,
) -> NOf1FabricPackPlan:
    run_id = str(report_packet.get("run_id") or Path(run_dir).name)
    report_packet_ref = str(
        report_packet.get("report_packet_ref") or "artifacts/n_of_1_report_packet.json"
    )
    report_packet_sha256 = artifact_payload_sha256(report_packet)
    artifact_hashes = _ordered_artifact_hashes(report_packet)
    sensor_evidence_artifact_refs = _sensor_evidence_artifact_refs(report_packet)
    file_plan_items = _file_plans(
        report_packet=report_packet,
        report_packet_ref=report_packet_ref,
        report_packet_sha256=report_packet_sha256,
    )
    planned_file_ids = tuple(item.id for item in file_plan_items)
    planned_sensor_evidence_artifact_ids = tuple(sensor_evidence_artifact_refs)
    return NOf1FabricPackPlan(
        id="n-of-1-fabric-pack-plan",
        run_id=run_id,
        source_run_dir=_stable_run_dir(run_dir),
        generated_at=str(generated_at or run_id),
        report_packet_id=str(report_packet.get("id", "n-of-1-report-packet")),
        report_packet_ref=report_packet_ref,
        report_packet_sha256=report_packet_sha256,
        report_packet_artifact_count=int(report_packet.get("artifact_count") or 0),
        artifact_hashes=artifact_hashes,
        sensor_evidence_artifact_refs=sensor_evidence_artifact_refs,
        planned_sensor_evidence_artifact_ids=planned_sensor_evidence_artifact_ids,
        planned_file_ids=planned_file_ids,
        file_plans=tuple(item.to_dict() for item in file_plan_items),
        file_count=len(file_plan_items),
        summary={
            "text": (
                "Planning-only private Fabric data-pack candidate for local "
                "n-of-1 report packet artifacts."
            ),
            "planning_only": True,
            "private_only_by_default": True,
            "pack_class_recommendation": "data",
            "candidate_type": "document",
            "alternate_candidate_type": "dataset",
            "file_count": len(file_plan_items),
            "sensor_evidence_artifact_ref_count": len(sensor_evidence_artifact_refs),
            "report_packet_ref": report_packet_ref,
            "hash_scope": "json-dumps-indent-2-sort-keys-newline",
            "hashes_for": "local reproducibility/provenance only",
            "disabled_surfaces": [
                "signing",
                "catalog publication",
                "transport",
                "magnet",
                "webseed",
                "seeding",
                "upload",
                "install",
                "execution",
                "code pack",
            ],
        },
        metadata={
            "fixture_ref": "n-of-1-fabric-pack-plan-template-v1",
            "source": "n_of_1_report_packet",
            "not_content_fabric_manifest": True,
            "manifest_fields_intentionally_absent": [
                "publisher",
                "keyring",
                "catalog",
                "transport",
                "magnetUri",
                "webSeed",
                "installTarget",
                "signatures",
                "manifestDigest",
                "infohash",
            ],
        },
    )


def _file_plans(
    *,
    report_packet: dict[str, object],
    report_packet_ref: str,
    report_packet_sha256: str,
) -> tuple[NOf1FabricFilePlan, ...]:
    refs = report_packet.get("artifact_refs", {})
    if not isinstance(refs, dict):
        refs = {}
    names = _artifact_ref_names(report_packet, refs)
    items = [
        NOf1FabricFilePlan(
            id="n_of_1_report_packet",
            path=report_packet_ref,
            sha256=report_packet_sha256,
            source="report_packet",
            kind="report-packet",
            present=True,
            retention="run",
            role="n-of-1-report-packet",
        )
    ]
    artifact_hashes = report_packet.get("artifact_hashes", {})
    if not isinstance(artifact_hashes, dict):
        artifact_hashes = {}
    for name in names:
        ref = refs.get(name, {})
        if not isinstance(ref, dict):
            ref = {}
        path = safe_sensor_artifact_ref(
            ref.get("relative_path") or ref.get("path_or_uri") or f"artifacts/{name}.json"
        )
        present = bool(path and ref.get("present", name in artifact_hashes))
        items.append(
            NOf1FabricFilePlan(
                id=name,
                path=path,
                sha256=(artifact_hashes.get(name) or ref.get("sha256")) if path else None,
                source="report_packet.artifact_refs",
                kind=str(ref.get("kind") or "run-artifact"),
                present=present,
                retention=str(ref.get("retention") or "run"),
                role=ref.get("role") if isinstance(ref.get("role"), str) else None,
                created_by_stage=ref.get("created_by_stage")
                if isinstance(ref.get("created_by_stage"), str)
                else None,
                loop_stage=ref.get("loop_stage")
                if isinstance(ref.get("loop_stage"), str)
                else None,
                include_in_candidate=name not in LOCAL_DIAGNOSTIC_N_OF_1_ARTIFACTS,
            )
        )
    return tuple(items)


def _sensor_evidence_artifact_refs(
    report_packet: dict[str, object],
) -> dict[str, dict[str, object]]:
    raw_refs = report_packet.get("sensor_evidence_artifact_refs", {})
    if isinstance(raw_refs, dict) and raw_refs:
        refs = {}
        for name, raw_ref in sorted(raw_refs.items()):
            classified = classify_sensor_evidence_artifact_ref(raw_ref)
            refs[str(name)] = classified.to_dict()
        return refs

    artifact_refs = report_packet.get("artifact_refs", {})
    artifact_hashes = report_packet.get("artifact_hashes", {})
    if not isinstance(artifact_refs, dict) or not isinstance(artifact_hashes, dict):
        return {}
    refs = {}
    for name, spec in sorted(N_OF_1_SENSOR_EVIDENCE_ARTIFACTS.items()):
        if name not in artifact_refs and name not in artifact_hashes:
            continue
        artifact_ref = artifact_refs.get(name, {})
        if not isinstance(artifact_ref, dict):
            continue
        refs[name] = build_sensor_evidence_artifact_ref(
            name,
            artifact_ref.get("relative_path")
            or artifact_ref.get("path_or_uri")
            or f"artifacts/{name}.json",
            artifact_sha256=artifact_hashes.get(name),
            provider_kind=spec["provider_kind"],
            evidence_kind=spec["evidence_kind"],
        )
    return refs


def _artifact_ref_names(
    report_packet: dict[str, object], refs: dict[str, object]
) -> tuple[str, ...]:
    names = [name for name in EXPECTED_N_OF_1_PACKET_ARTIFACTS if name in refs]
    extras = sorted(str(name) for name in refs if str(name) not in set(names))
    if names or extras:
        return tuple(names + extras)
    return tuple()


def _ordered_artifact_hashes(report_packet: dict[str, object]) -> dict[str, str | None]:
    raw_hashes = report_packet.get("artifact_hashes", {})
    if not isinstance(raw_hashes, dict):
        return {}
    refs = report_packet.get("artifact_refs", {})
    if not isinstance(refs, dict):
        refs = {}
    names = _artifact_ref_names(report_packet, refs)
    if not names:
        names = tuple(sorted(str(name) for name in raw_hashes))
    return {name: raw_hashes.get(name) for name in names}


def _stable_run_dir(run_dir: str | Path) -> str:
    path = Path(run_dir)
    if path.parent.name == "runs":
        return f"runs/{path.name}"
    return path.name


def _json_ready(value):
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    return value


__all__ = [
    "LOCAL_DIAGNOSTIC_N_OF_1_ARTIFACTS",
    "N_OF_1_FABRIC_PLAN_FUTURE_REQUIREMENTS",
    "N_OF_1_FABRIC_PLAN_LIMITATIONS",
    "NOf1FabricFilePlan",
    "NOf1FabricPackPlan",
    "build_n_of_1_fabric_pack_plan",
]
