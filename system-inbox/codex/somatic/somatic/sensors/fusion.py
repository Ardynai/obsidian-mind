"""Sandbox RF↔vision fusion plus multi-unit CSI occupancy fusion.

`fuse_rf_vision` averages simulated CSI + depth joints. `fuse_csi_units`
averages occupancy rows from tagged ESP32 unit-ids. Neither invents a
recognizable silhouette; the Part 4 pose model stays founder-gated and off.
"""

from __future__ import annotations

from somatic.consent.ledger import ConsentLedger
from somatic.consent.scopes import ANALYSIS_INSIGHT, DATA_INGESTION
from somatic.evidence_bus.adapter import HypothesisSpec
from somatic.evidence_bus.loop import run_evidence_loop
from somatic.safety.core import require_consent


def fuse_rf_vision(
    ledger: ConsentLedger,
    *,
    seed: int = 0,
    rf_features: dict[str, object] | None = None,
    vision_features: dict[str, object] | None = None,
) -> dict[str, object]:
    """Fuse CSI (RF) and camera/video3d pose joints into one body-state dict.

    Default path is sandbox. Pass live feature dicts to fuse the camera-pose
    complement onto CSI occupancy without opening hardware here.
    """

    require_consent(ledger, DATA_INGESTION)
    require_consent(ledger, ANALYSIS_INSIGHT)
    if rf_features is None and vision_features is None:
        hypothesis = HypothesisSpec(
            id="rf-vision-fusion",
            statement="Sandbox RF↔vision 3D-pose fusion of simulated CSI and depth joints.",
            domain="sensing",
        )
        report = run_evidence_loop(
            ledger,
            hypothesis,
            modalities=("csi", "video3d"),
            seed=seed,
        )
        poses: list[dict[str, object]] = []
        for step in report.steps:
            pose = step.features.get("pose3d")
            if isinstance(pose, dict):
                poses.append(pose)
        fused_joints = _average_joints(poses)
        return {
            "schema": "somatic.fusion.rf_vision.v1",
            "simulated": True,
            "hardware_access": False,
            "sources": [step.modality for step in report.steps],
            "fused_joints": fused_joints,
            "raw_ids": [step.raw_id for step in report.steps],
            "sha256s": [step.sha256 for step in report.steps],
            "emergency_triggered": report.emergency_triggered,
            "notes": [
                "Sandbox fusion only; not a clinical gait or fall assessment.",
                "Raw CSI IQ and depth frames were not exported.",
            ],
        }
    poses = []
    sources: list[str] = []
    if isinstance(rf_features, dict):
        sources.append("csi")
        pose = rf_features.get("pose3d")
        if isinstance(pose, dict):
            poses.append(pose)
    if isinstance(vision_features, dict):
        sources.append("video3d")
        pose = vision_features.get("pose3d")
        if isinstance(pose, dict):
            poses.append(pose)
    fused_joints = _average_joints(poses)
    return {
        "schema": "somatic.fusion.rf_vision.v1",
        "simulated": False,
        "hardware_access": False,
        "sources": sources,
        "fused_joints": fused_joints,
        "raw_ids": [],
        "sha256s": [],
        "emergency_triggered": False,
        "notes": [
            "RF↔vision fusion of caller-supplied features; not a clinical assessment.",
            "Raw CSI IQ and camera frames were not exported.",
        ],
    }


def fuse_csi_units(
    ledger: ConsentLedger,
    unit_features: list[dict[str, object]] | tuple[dict[str, object], ...] | None = None,
    *,
    enable_pose_model: bool = False,
) -> dict[str, object]:
    """Average occupancy rows across tagged ESP32 unit-ids.

    Does not invent a skeleton. The pose model stays off unless the founder
    enables it (env + weights + extra). Sandbox-verified software path only.
    """

    require_consent(ledger, DATA_INGESTION)
    require_consent(ledger, ANALYSIS_INSIGHT)
    rows: list[list[float]] = []
    unit_ids: list[str] = []
    for item in unit_features or ():
        if not isinstance(item, dict):
            continue
        unit_ids.append(str(item.get("unit_id") or ""))
        occupancy = item.get("occupancy_row") or item.get("envelope")
        if not isinstance(occupancy, list) or not occupancy:
            continue
        try:
            rows.append([float(value) for value in occupancy])
        except (TypeError, ValueError):
            continue
    fused_row: list[float] = []
    if rows:
        width = min(len(row) for row in rows)
        count = len(rows)
        fused_row = [round(sum(row[index] for row in rows) / count, 4) for index in range(width)]
    pose: dict[str, object]
    if enable_pose_model:
        from somatic.sensors.pose_model import infer_pose

        pose = infer_pose({"occupancy_row": fused_row, "units": unit_ids})
    else:
        from somatic.sensors.pose_model import pose_model_status

        status = pose_model_status()
        pose = {
            "origin": "none",
            "simulated": False,
            "available": False,
            "joints": {},
            "status": status,
            "note": (
                "Multi-unit occupancy fusion only. A recognizable silhouette "
                "needs the founder-gated Part 4 pose model."
            ),
        }
    return {
        "schema": "somatic.fusion.csi_units.v1",
        "simulated": False,
        "hardware_access": False,
        "hardware_validation": "sandbox-verified; needs a real ESP32 to validate live",
        "unit_ids": unit_ids,
        "fused_occupancy_row": fused_row,
        "pose3d": pose,
        "pose_model_requested": bool(enable_pose_model),
        "notes": [
            "Time alignment is nearest-frame / caller-supplied snapshots, not a PTP clock.",
            "Raw CSI IQ was not fused or exported.",
        ],
    }


def _average_joints(poses: list[dict[str, object]]) -> dict[str, list[float]]:
    collected: dict[str, list[list[float]]] = {}
    for pose in poses:
        joints = pose.get("joints")
        if not isinstance(joints, dict):
            continue
        for name, coords in joints.items():
            if not isinstance(coords, list) or len(coords) != 3:
                continue
            try:
                numbers = [float(item) for item in coords]
            except (TypeError, ValueError):
                continue
            collected.setdefault(str(name), []).append(numbers)
    fused: dict[str, list[float]] = {}
    for name, series in sorted(collected.items()):
        count = len(series)
        fused[name] = [round(sum(point[axis] for point in series) / count, 4) for axis in range(3)]
    return fused
