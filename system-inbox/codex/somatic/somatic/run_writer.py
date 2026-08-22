import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from somatic.sensors.evidence import build_sensor_evidence_artifact_ref
from somatic.sensors.registry import sensor_evidence_provider_by_artifact_name


def make_run_id():
    return datetime.now(UTC).strftime("run-%Y%m%dT%H%M%SZ")


def write_run_artifacts(
    output_root,
    run_id,
    workflow,
    provider_metadata,
    evidence,
    safety_response,
    hypotheses,
    report_markdown,
    next_iteration,
    extra_artifacts=None,
):
    run_dir = Path(output_root) / run_id
    for relative in ("inputs", "evidence", "artifacts", "safety", "reports"):
        (run_dir / relative).mkdir(parents=True, exist_ok=True)

    _write_json(run_dir / "workflow.json", workflow)
    _write_text(
        run_dir / "inputs" / "README.md",
        "# Inputs\n\nThis mock run used local fixture inputs only. "
        "No external API calls, provider secrets, network access, "
        "or real sensor/lab actions were used.\n",
    )
    _write_json(run_dir / "evidence" / "evidence.json", evidence)
    _write_json(run_dir / "artifacts" / "hypotheses.json", hypotheses)
    # This map is both the manifest index and the hash input list; keep names
    # stable unless every consumer of run manifests moves with the rename.
    artifact_refs = {
        "workflow": "workflow.json",
        "inputs": "inputs/README.md",
        "evidence": "evidence/evidence.json",
        "hypotheses": "artifacts/hypotheses.json",
        "safety_response": "safety/safety-response.json",
        "report": "reports/report.md",
        "next_iteration": "next_iteration.json",
    }
    for name, artifact in sorted((extra_artifacts or {}).items()):
        relative_path = artifact["relative_path"]
        _write_json(run_dir / relative_path, artifact["payload"])
        artifact_refs[name] = relative_path
    _write_json(run_dir / "safety" / "safety-response.json", safety_response)
    _write_text(run_dir / "reports" / "report.md", report_markdown)
    _write_json(run_dir / "next_iteration.json", next_iteration)

    hashes = _artifact_hashes(run_dir, artifact_refs)
    manifest = {
        "run_id": run_id,
        "schema_version": 1,
        "workflow_id": workflow.get("id"),
        "workflow_version": workflow.get("version"),
        "mode": workflow.get("mode"),
        "created_at": _utc_now(),
        "status": "mock-complete",
        "mock": True,
        "offline": True,
        "not_medical_advice": True,
        "providers": [
            {
                "ref": ref,
                "provider_id": metadata.get("provider_id") or metadata.get("id"),
                "class": metadata.get("class"),
                "version": metadata.get("version"),
                "offline_supported": metadata.get("offline_supported"),
            }
            for ref, metadata in sorted(provider_metadata.items())
        ],
        "artifacts": artifact_refs,
        "hashes": hashes,
    }
    sensor_evidence_refs = _sensor_evidence_artifact_refs(
        artifact_refs,
        hashes,
        extra_artifacts or {},
    )
    if sensor_evidence_refs:
        manifest["sensor_evidence_artifact_refs"] = sensor_evidence_refs
    _write_json(run_dir / "manifest.json", manifest)
    return run_dir


def _write_json(path, value):
    payload = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(payload)


def _write_text(path, value):
    path.write_text(value, encoding="utf-8")


def _artifact_hashes(run_dir, artifact_map):
    hashes = {}
    for name, relative in artifact_map.items():
        hashes[name] = _sha256(run_dir / relative)
    return hashes


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sensor_evidence_artifact_refs(artifact_refs, artifact_hashes, extra_artifacts):
    refs = {}
    for name, relative_path in sorted(artifact_refs.items()):
        artifact = extra_artifacts.get(name, {})
        if not isinstance(artifact, dict):
            artifact = {}
        payload = artifact.get("payload")
        marker = artifact.get("sensor_evidence_ref")
        if not isinstance(marker, dict):
            marker = {}
        provider_kind = marker.get("provider_kind")
        evidence_kind = marker.get("evidence_kind")
        if isinstance(payload, dict):
            provider_kind = provider_kind or payload.get("provider_kind")
            evidence_kind = evidence_kind or payload.get("evidence_kind")
        entry = sensor_evidence_provider_by_artifact_name(name)
        if entry is not None:
            provider_kind = provider_kind or entry.provider_kind
            evidence_kind = evidence_kind or entry.evidence_kind
        if not provider_kind or not evidence_kind:
            continue
        refs[name] = build_sensor_evidence_artifact_ref(
            name,
            relative_path,
            artifact_sha256=artifact_hashes.get(name),
            evidence_pack=payload if isinstance(payload, dict) else None,
            provider_kind=provider_kind,
            evidence_kind=evidence_kind,
        )
    return refs


def _utc_now():
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
