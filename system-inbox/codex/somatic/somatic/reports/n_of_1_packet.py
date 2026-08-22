"""Consolidated n-of-1 report packet helpers."""

import json
from dataclasses import asdict, dataclass, field
from hashlib import sha256

from somatic.sensors.evidence import build_sensor_evidence_artifact_ref
from somatic.sensors.registry import (
    list_sensor_evidence_providers,
    sensor_evidence_artifact_specs,
)

EXPECTED_N_OF_1_PACKET_ARTIFACTS = (
    "sensor_stream_plan",
    "sensor_observations",
    "sensor_feature_set",
    "csi_parser_report",
    "csi_parsed_summary",
    "csi_evidence_pack",
    "sensor_evidence_record",
    "n_of_1_baseline_placeholder",
    "personal_profile",
    "baseline_graph",
    "baseline_comparison",
    "intervention_tag",
    "intervention_context",
    "response_evaluation_plan",
    "mock_intervention_ledger",
    "follow_up_observation_window",
    "follow_up_sensor_snapshot",
    "response_comparison",
    "response_evaluation_summary",
    "n_of_1_summary",
)
# These optional specs extend the packet schema without changing the required
# artifact contract that older fixtures and report verifiers depend on.
N_OF_1_OPTIONAL_ARTIFACTS = {
    "environment_evidence_pack": {
        "role": "environment-evidence-pack",
        "kind": "environment-tabular-evidence-pack",
        "created_by_stage": "emit-sandbox-observations",
        "loop_stage": "observation",
        "retention": "run",
    },
    "toy_counter_evidence_pack": {
        "role": "toy-counter-evidence-pack",
        "kind": "toy-counter-evidence-pack",
        "created_by_stage": "emit-sandbox-observations",
        "loop_stage": "observation",
        "retention": "run",
    },
    "document_evidence_pack": {
        "role": "document-evidence-pack",
        "kind": "document-evidence-pack",
        "created_by_stage": "emit-sandbox-observations",
        "loop_stage": "observation",
        "retention": "run",
    },
}
N_OF_1_SENSOR_EVIDENCE_ARTIFACTS = sensor_evidence_artifact_specs()

N_OF_1_LOOP_STAGE_ARTIFACTS = (
    (
        "observation",
        (
            "sensor_stream_plan",
            "sensor_observations",
            "sensor_feature_set",
            "csi_parser_report",
            "csi_parsed_summary",
            "csi_evidence_pack",
            "sensor_evidence_record",
        ),
    ),
    (
        "baseline",
        (
            "n_of_1_baseline_placeholder",
            "personal_profile",
            "baseline_graph",
            "baseline_comparison",
        ),
    ),
    (
        "intervention_tag",
        (
            "intervention_tag",
            "intervention_context",
            "response_evaluation_plan",
            "mock_intervention_ledger",
        ),
    ),
    (
        "follow_up",
        (
            "follow_up_observation_window",
            "follow_up_sensor_snapshot",
        ),
    ),
    (
        "response_comparison",
        (
            "response_comparison",
            "response_evaluation_summary",
            "n_of_1_summary",
        ),
    ),
)

N_OF_1_ARTIFACT_ROLES = {
    "sensor_stream_plan": "observation-plan",
    "sensor_observations": "observation-records",
    "sensor_feature_set": "feature-set",
    "csi_parser_report": "csi-parser-report",
    "csi_parsed_summary": "csi-parsed-summary",
    "csi_evidence_pack": "csi-evidence-pack",
    "environment_evidence_pack": "environment-evidence-pack",
    "document_evidence_pack": "document-evidence-pack",
    "sensor_evidence_record": "evidence-bus-record",
    "n_of_1_baseline_placeholder": "baseline-placeholder",
    "personal_profile": "local-profile-placeholder",
    "baseline_graph": "baseline-graph",
    "baseline_comparison": "baseline-comparison",
    "intervention_tag": "intervention-tag",
    "intervention_context": "intervention-context",
    "response_evaluation_plan": "response-evaluation-plan",
    "mock_intervention_ledger": "mock-intervention-ledger",
    "follow_up_observation_window": "follow-up-window",
    "follow_up_sensor_snapshot": "follow-up-snapshot",
    "response_comparison": "response-comparison",
    "response_evaluation_summary": "response-evaluation-summary",
    "n_of_1_summary": "n-of-1-summary",
}

N_OF_1_ARTIFACT_KINDS = {
    "sensor_stream_plan": "sensor-stream-plan",
    "sensor_observations": "sensor-observations",
    "sensor_feature_set": "sensor-feature-set",
    "csi_parser_report": "csi-parser-report",
    "csi_parsed_summary": "csi-parsed-summary",
    "csi_evidence_pack": "csi-evidence-pack",
    "environment_evidence_pack": "environment-tabular-evidence-pack",
    "document_evidence_pack": "document-evidence-pack",
    "sensor_evidence_record": "sensor-evidence-record",
    "n_of_1_baseline_placeholder": "baseline-placeholder",
    "personal_profile": "personal-profile",
    "baseline_graph": "baseline-graph",
    "baseline_comparison": "baseline-comparison",
    "intervention_tag": "intervention-tag",
    "intervention_context": "intervention-context",
    "response_evaluation_plan": "response-evaluation-plan",
    "mock_intervention_ledger": "intervention-ledger",
    "follow_up_observation_window": "follow-up-observation-window",
    "follow_up_sensor_snapshot": "follow-up-sensor-snapshot",
    "response_comparison": "response-comparison",
    "response_evaluation_summary": "response-evaluation-summary",
    "n_of_1_summary": "report-packet-summary",
}

N_OF_1_CREATED_BY_STAGE = {
    "sensor_stream_plan": "plan-sandbox-sensor-stream",
    "n_of_1_baseline_placeholder": "plan-sandbox-sensor-stream",
    "personal_profile": "plan-sandbox-sensor-stream",
    "baseline_graph": "plan-sandbox-sensor-stream",
    "sensor_observations": "emit-sandbox-observations",
    "sensor_feature_set": "emit-sandbox-observations",
    "csi_parser_report": "emit-sandbox-observations",
    "csi_parsed_summary": "emit-sandbox-observations",
    "csi_evidence_pack": "emit-sandbox-observations",
    "environment_evidence_pack": "emit-sandbox-observations",
    "document_evidence_pack": "emit-sandbox-observations",
    "sensor_evidence_record": "emit-sandbox-observations",
    "baseline_comparison": "render-n-of-1-report",
    "intervention_tag": "render-n-of-1-report",
    "intervention_context": "render-n-of-1-report",
    "response_evaluation_plan": "render-n-of-1-report",
    "mock_intervention_ledger": "render-n-of-1-report",
    "follow_up_observation_window": "render-n-of-1-report",
    "follow_up_sensor_snapshot": "render-n-of-1-report",
    "response_comparison": "render-n-of-1-report",
    "response_evaluation_summary": "render-n-of-1-report",
    "n_of_1_summary": "render-n-of-1-report",
}

N_OF_1_PACKET_LIMITATIONS = (
    "Fake-backed local research-only report packet.",
    "Fake-backed local research-only planning only.",
    "Hashes are for reproducibility/provenance only.",
    "Packet is not a medical record.",
    "Packet is not a health record.",
    "No effectiveness claim or advice is generated.",
    "No recommendation, prescription, treatment recommendation, medication action, "
    "clinician action, diagnosis, or emergency triage is generated.",
    "No intervention effectiveness is claimed.",
    "No real monitoring, reminder, automation, notification, or scheduling is created.",
    "No hardware, sensor device, network, database, or external-memory runtime is used.",
)

N_OF_1_PACKET_FUTURE_REAL_USE_REQUIREMENTS = (
    "explicit consent",
    "privacy review",
    "safety review",
    "human review",
    "clinical review where applicable",
    "local-first storage controls",
    "retention and export controls",
    "separate opt-in configuration",
    "no emergency-triage substitution",
)

N_OF_1_PACKET_SAFETY_BOUNDARY_FLAGS = {
    "fake_backed": True,
    "no_hardware": True,
    "no_real_health_data": True,
    "no_diagnosis": True,
    "no_treatment": True,
    "no_recommendation": True,
    "no_prescription": True,
    "no_emergency_triage": True,
    "no_effectiveness_claim": True,
    "no_monitoring": True,
    "no_scheduling": True,
}


@dataclass(frozen=True)
class NOf1ArtifactRef:
    name: str
    relative_path: str
    sha256: str | None
    role: str
    kind: str
    path_or_uri: str
    created_by_stage: str
    retention: str
    loop_stage: str
    present: bool
    missing_reason: str | None = None

    def to_dict(self) -> dict[str, object]:
        return _json_ready(asdict(self))


@dataclass(frozen=True)
class NOf1ReportPacket:
    id: str
    run_id: str
    workflow_id: str
    workflow_mode: str
    generated_at: str
    artifact_refs: dict[str, dict[str, object]]
    artifact_hashes: dict[str, str | None]
    sensor_evidence_artifact_refs: dict[str, dict[str, object]]
    artifacts: tuple[dict[str, object], ...]
    artifact_count: int
    present_artifact_count: int
    missing_artifacts: tuple[str, ...]
    packet_complete: bool
    packet_status: str
    loop_stages: tuple[dict[str, object], ...]
    safety_boundary_flags: dict[str, bool]
    summary: dict[str, object]
    limitations: tuple[str, ...] = N_OF_1_PACKET_LIMITATIONS
    future_real_use_requirements: tuple[str, ...] = N_OF_1_PACKET_FUTURE_REAL_USE_REQUIREMENTS
    schema_version: int = 1
    mock: bool = True
    offline: bool = True
    research_only: bool = True
    sandbox_only: bool = True
    simulated: bool = True
    fake_backed: bool = True
    local_only: bool = True
    medical_record: bool = False
    advice_generated: bool = False
    recommendation_generated: bool = False
    prescription_generated: bool = False
    treatment_recommendation: bool = False
    medical_advice: bool = False
    effectiveness_claim: bool = False
    no_effectiveness_claim: bool = True
    claim_effectiveness: bool = False
    real_health_data_loaded: bool = False
    real_profile_storage: bool = False
    personal_data_exported: bool = False
    personal_health_data_exported: bool = False
    baseline_data_exported: bool = False
    raw_sensor_data_collected: bool = False
    hardware_access: bool = False
    live_sensor_access: bool = False
    network_calls: bool = False
    database_access: bool = False
    external_memory: bool = False
    diagnosis: bool = False
    emergency_triage: bool = False
    real_monitoring: bool = False
    real_response_monitoring: bool = False
    real_scheduling: bool = False
    notification_automation: bool = False
    reminder_automation: bool = False
    real_intervention_performed: bool = False
    clinical_interpretation: bool = False
    medical_or_clinical_claim: bool = False
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return _json_ready(asdict(self))


def collect_n_of_1_artifact_refs(
    artifact_payloads: dict[str, dict[str, object]],
) -> tuple[NOf1ArtifactRef, ...]:
    refs = []
    loop_stage_by_name = _loop_stage_by_name()
    for name in EXPECTED_N_OF_1_PACKET_ARTIFACTS:
        payload = artifact_payloads.get(name)
        present = isinstance(payload, dict)
        refs.append(
            NOf1ArtifactRef(
                name=name,
                relative_path=f"artifacts/{name}.json",
                sha256=artifact_payload_sha256(payload) if present else None,
                role=N_OF_1_ARTIFACT_ROLES[name],
                kind=N_OF_1_ARTIFACT_KINDS[name],
                path_or_uri=f"artifacts/{name}.json",
                created_by_stage=N_OF_1_CREATED_BY_STAGE[name],
                retention="run",
                loop_stage=loop_stage_by_name[name],
                present=present,
                missing_reason=None if present else "missing-required-n-of-1-artifact",
            )
        )
    return tuple(refs)


def collect_n_of_1_optional_artifact_refs(
    artifact_payloads: dict[str, dict[str, object]],
) -> tuple[NOf1ArtifactRef, ...]:
    refs = []
    for name, spec in sorted(_n_of_1_optional_artifacts().items()):
        payload = artifact_payloads.get(name)
        if not isinstance(payload, dict):
            continue
        refs.append(
            NOf1ArtifactRef(
                name=name,
                relative_path=f"artifacts/{name}.json",
                sha256=artifact_payload_sha256(payload),
                role=str(spec["role"]),
                kind=str(spec["kind"]),
                path_or_uri=f"artifacts/{name}.json",
                created_by_stage=str(spec["created_by_stage"]),
                retention=str(spec["retention"]),
                loop_stage=str(spec["loop_stage"]),
                present=True,
            )
        )
    return tuple(refs)


def _n_of_1_optional_artifacts() -> dict[str, dict[str, object]]:
    specs = dict(N_OF_1_OPTIONAL_ARTIFACTS)
    for entry in list_sensor_evidence_providers():
        if entry.artifact_name in EXPECTED_N_OF_1_PACKET_ARTIFACTS:
            continue
        specs.setdefault(
            entry.artifact_name,
            {
                "role": f"{entry.provider_id}-evidence-pack",
                "kind": entry.evidence_kind,
                "created_by_stage": "emit-sandbox-observations",
                "loop_stage": "observation",
                "retention": "run",
            },
        )
    return specs


def build_n_of_1_report_packet(
    *,
    run_id: str,
    workflow: dict[str, object],
    artifact_payloads: dict[str, dict[str, object]],
    generated_at: str | None = None,
) -> NOf1ReportPacket:
    required_refs = collect_n_of_1_artifact_refs(artifact_payloads)
    optional_refs = collect_n_of_1_optional_artifact_refs(artifact_payloads)
    refs = required_refs + optional_refs
    ref_payloads = {ref.name: ref.to_dict() for ref in refs}
    artifact_hashes = {ref.name: ref.sha256 for ref in refs}
    sensor_evidence_artifact_refs = collect_n_of_1_sensor_evidence_artifact_refs(
        artifact_payloads,
        artifact_refs=ref_payloads,
        artifact_hashes=artifact_hashes,
    )
    missing = tuple(ref.name for ref in required_refs if not ref.present)
    present_count = len([ref for ref in refs if ref.present])
    packet_complete = not missing
    packet_status = "complete" if packet_complete else "missing-required-artifacts"
    return NOf1ReportPacket(
        id="n-of-1-report-packet",
        run_id=str(run_id),
        workflow_id=str(workflow.get("id", "unknown-workflow")),
        workflow_mode=str(workflow.get("mode", "unknown-mode")),
        generated_at=str(generated_at or run_id),
        artifact_refs=ref_payloads,
        artifact_hashes=artifact_hashes,
        sensor_evidence_artifact_refs=sensor_evidence_artifact_refs,
        artifacts=tuple(ref.to_dict() for ref in refs),
        artifact_count=len(refs),
        present_artifact_count=present_count,
        missing_artifacts=missing,
        packet_complete=packet_complete,
        packet_status=packet_status,
        loop_stages=_loop_stages(ref_payloads),
        safety_boundary_flags=dict(N_OF_1_PACKET_SAFETY_BOUNDARY_FLAGS),
        summary=_packet_summary(
            workflow=workflow,
            artifact_payloads=artifact_payloads,
            artifact_count=len(refs),
            present_count=present_count,
            missing=missing,
        ),
        metadata={
            "fixture_ref": "n-of-1-report-packet-template-v1",
            "artifact_ref_count": len(refs),
            "sensor_evidence_artifact_ref_count": len(sensor_evidence_artifact_refs),
            "hash_algorithm": "sha256",
            "hash_scope": "json-dumps-indent-2-sort-keys-newline",
            "hashes_for": "reproducibility/provenance only",
            "medical_record": False,
        },
    )


def collect_n_of_1_sensor_evidence_artifact_refs(
    artifact_payloads: dict[str, dict[str, object]],
    *,
    artifact_refs: dict[str, dict[str, object]] | None = None,
    artifact_hashes: dict[str, str | None] | None = None,
) -> dict[str, dict[str, object]]:
    refs = artifact_refs or {
        ref.name: ref.to_dict()
        for ref in (
            collect_n_of_1_artifact_refs(artifact_payloads)
            + collect_n_of_1_optional_artifact_refs(artifact_payloads)
        )
    }
    hashes = artifact_hashes or {
        ref.name: ref.sha256
        for ref in (
            collect_n_of_1_artifact_refs(artifact_payloads)
            + collect_n_of_1_optional_artifact_refs(artifact_payloads)
        )
    }
    sensor_refs = {}
    for name, spec in sorted(N_OF_1_SENSOR_EVIDENCE_ARTIFACTS.items()):
        ref = refs.get(name, {})
        if not isinstance(ref, dict):
            ref = {}
        payload = artifact_payloads.get(name)
        if not isinstance(payload, dict) and not ref.get("present"):
            continue
        sensor_refs[name] = build_sensor_evidence_artifact_ref(
            name,
            ref.get("relative_path") or ref.get("path_or_uri") or f"artifacts/{name}.json",
            artifact_sha256=hashes.get(name),
            evidence_pack=payload if isinstance(payload, dict) else None,
            provider_kind=spec["provider_kind"],
            evidence_kind=spec["evidence_kind"],
        )
    return sensor_refs


def artifact_payload_sha256(payload: dict[str, object]) -> str:
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    return sha256(encoded).hexdigest()


def _packet_summary(
    *,
    workflow: dict[str, object],
    artifact_payloads: dict[str, dict[str, object]],
    artifact_count: int,
    present_count: int,
    missing: tuple[str, ...],
) -> dict[str, object]:
    n_of_1_summary = artifact_payloads.get("n_of_1_summary", {})
    if not isinstance(n_of_1_summary, dict):
        n_of_1_summary = {}
    return {
        "text": ("Consolidated fake-backed n-of-1 report packet for local research-only planning."),
        "workflow_id": workflow.get("id"),
        "workflow_mode": workflow.get("mode"),
        "artifact_count": artifact_count,
        "present_artifact_count": present_count,
        "missing_artifact_count": len(missing),
        "missing_artifacts": list(missing),
        "hash_summary": {
            "algorithm": "sha256",
            "scope": "json-dumps-indent-2-sort-keys-newline",
            "purpose": "reproducibility/provenance only",
        },
        "loop_summary": {
            "observation_count": n_of_1_summary.get("observation_count"),
            "baseline_comparison_summary": n_of_1_summary.get("baseline_comparison_summary", {}),
            "intervention_summary": n_of_1_summary.get("intervention_summary", {}),
            "response_trend_summary": n_of_1_summary.get("response_trend_summary", {}),
        },
        "boundary_summary": {
            "medical_record": False,
            "advice_generated": False,
            "effectiveness_claim": False,
            "real_monitoring": False,
            "real_scheduling": False,
        },
    }


def _loop_stages(
    ref_payloads: dict[str, dict[str, object]],
) -> tuple[dict[str, object], ...]:
    stages = []
    for stage, artifact_names in N_OF_1_LOOP_STAGE_ARTIFACTS:
        missing = [name for name in artifact_names if not ref_payloads[name]["present"]]
        stages.append(
            {
                "stage": stage,
                "artifact_names": list(artifact_names),
                "present_count": len(artifact_names) - len(missing),
                "missing_count": len(missing),
                "missing_artifacts": missing,
                "status": "complete" if not missing else "missing-required-artifacts",
            }
        )
    return tuple(stages)


def _loop_stage_by_name() -> dict[str, str]:
    return {
        name: stage
        for stage, artifact_names in N_OF_1_LOOP_STAGE_ARTIFACTS
        for name in artifact_names
    }


def _json_ready(value):
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    return value


__all__ = [
    "EXPECTED_N_OF_1_PACKET_ARTIFACTS",
    "N_OF_1_ARTIFACT_KINDS",
    "N_OF_1_ARTIFACT_ROLES",
    "N_OF_1_CREATED_BY_STAGE",
    "N_OF_1_LOOP_STAGE_ARTIFACTS",
    "N_OF_1_OPTIONAL_ARTIFACTS",
    "N_OF_1_PACKET_FUTURE_REAL_USE_REQUIREMENTS",
    "N_OF_1_PACKET_LIMITATIONS",
    "N_OF_1_PACKET_SAFETY_BOUNDARY_FLAGS",
    "N_OF_1_SENSOR_EVIDENCE_ARTIFACTS",
    "NOf1ArtifactRef",
    "NOf1ReportPacket",
    "artifact_payload_sha256",
    "build_n_of_1_report_packet",
    "collect_n_of_1_artifact_refs",
    "collect_n_of_1_optional_artifact_refs",
    "collect_n_of_1_sensor_evidence_artifact_refs",
]
