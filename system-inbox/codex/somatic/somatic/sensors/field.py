"""Viz-ready Field snapshot: derived features only, never raw CSI.

The Field/Body view and `/api/sensors/field` share this shape so sandbox ticks
and live UDP ingest light up the same components.
"""

from __future__ import annotations

from typing import Any

FIELD_SCHEMA = "somatic.sensors.field.v1"
SANDBOX_DISCLAIMER = "Sandbox · synthetic · not a real person."
LIVE_DISCLAIMER = (
    "Live CSI features from loopback ingest. Not a clinical measurement. "
    "One radio yields motion, presence, breathing, and a heatmap. "
    "A recognizable body pose needs the founder-gated Part 4 model and multiple units."
)
LIVE_CAMERA_DISCLAIMER = (
    "Live on-device camera pose (MediaPipe). Features only — raw frames were not "
    "stored or exported. Not a clinical measurement."
)
CAMERA_POSE_ORIGINS = frozenset({"mediapipe-pose", "video", "video3d", "camera"})
HARDWARE_VALIDATION = "sandbox-verified; needs a real ESP32 to validate live"

# Joints the skeleton renderer already knows how to place. Extra names are
# drawn when present; missing names are skipped so later models can slot in.
KNOWN_JOINTS = (
    "head",
    "neck",
    "torso",
    "pelvis",
    "l_shoulder",
    "r_shoulder",
    "l_elbow",
    "r_elbow",
    "l_wrist",
    "r_wrist",
    "l_hip",
    "r_hip",
    "l_knee",
    "r_knee",
    "l_ankle",
    "r_ankle",
)

BONE_EDGES = (
    ("head", "neck"),
    ("head", "torso"),
    ("neck", "torso"),
    ("torso", "pelvis"),
    ("torso", "l_shoulder"),
    ("torso", "r_shoulder"),
    ("l_shoulder", "l_elbow"),
    ("r_shoulder", "r_elbow"),
    ("l_elbow", "l_wrist"),
    ("r_elbow", "r_wrist"),
    ("pelvis", "l_hip"),
    ("pelvis", "r_hip"),
    ("torso", "l_hip"),
    ("torso", "r_hip"),
    ("l_hip", "l_knee"),
    ("r_hip", "r_knee"),
    ("l_knee", "l_ankle"),
    ("r_knee", "r_ankle"),
)


def _as_float_list(value: object, *, limit: int = 128) -> list[float]:
    if not isinstance(value, (list, tuple)):
        return []
    out: list[float] = []
    for item in value[:limit]:
        try:
            out.append(round(float(item), 4))
        except (TypeError, ValueError):
            continue
    return out


def _as_heatmap(value: object, *, rows: int = 48, cols: int = 64) -> list[list[float]]:
    if not isinstance(value, list) or not value:
        return []
    if value and isinstance(value[0], (int, float)):
        row = _as_float_list(value, limit=cols)
        return [row] if row else []
    matrix: list[list[float]] = []
    for raw_row in value[:rows]:
        row = _as_float_list(raw_row, limit=cols)
        if row:
            matrix.append(row)
    return matrix


def _joints_from_pose(pose: object) -> dict[str, list[float]]:
    if not isinstance(pose, dict):
        return {}
    raw = pose.get("joints")
    if not isinstance(raw, dict):
        return {}
    joints: dict[str, list[float]] = {}
    for name, coords in raw.items():
        numbers = _as_float_list(coords, limit=3)
        if len(numbers) == 3:
            joints[str(name)] = numbers
    return joints


def field_snapshot(
    features: dict[str, Any] | None,
    *,
    mode: str,
    modality: str,
    tick: int = 0,
    unit_id: str = "",
    notes: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Return a UI-safe Field payload. Live CSI never copies a skeleton."""

    payload = dict(features or {})
    simulated = mode == "sandbox"
    envelope = _as_float_list(payload.get("envelope"))
    occupancy = _as_heatmap(payload.get("occupancy_row") or payload.get("amp_heatmap") or envelope)
    phase_map = _as_heatmap(payload.get("phase_heatmap") or payload.get("phase_row") or [])
    rate = payload.get("sandbox_peak_rate_per_min")
    if rate is None:
        rate = payload.get("breathing_rate_per_min")
    try:
        breathing = round(float(rate or 0.0), 2)
    except (TypeError, ValueError):
        breathing = 0.0
    try:
        motion = round(float(payload.get("motion_energy") or 0.0), 4)
    except (TypeError, ValueError):
        motion = 0.0
    try:
        coughs = int(payload.get("cough_event_count") or 0)
    except (TypeError, ValueError):
        coughs = 0
    try:
        speech_activity = round(float(payload.get("speech_activity_ratio") or 0.0), 4)
    except (TypeError, ValueError):
        speech_activity = 0.0
    presence_raw = payload.get("presence")
    if isinstance(presence_raw, bool):
        presence = presence_raw
    else:
        try:
            presence = float(presence_raw or 0.0) >= 0.5
        except (TypeError, ValueError):
            presence = bool(envelope) and max(abs(item) for item in envelope) > 0.2

    if simulated:
        pose = payload.get("pose3d") if isinstance(payload.get("pose3d"), dict) else {}
        joints = _joints_from_pose(pose)
        pose_block = {
            "origin": str(pose.get("origin") or modality),
            "simulated": True,
            "joints": joints,
            "known_joints": list(KNOWN_JOINTS),
            "bones": [list(edge) for edge in BONE_EDGES],
            "note": SANDBOX_DISCLAIMER,
        }
        disclaimer = SANDBOX_DISCLAIMER
        show_skeleton = bool(joints)
    else:
        pose = payload.get("pose3d") if isinstance(payload.get("pose3d"), dict) else {}
        origin = str(pose.get("origin") or "")
        camera_pose = modality in {"video", "video3d"} and origin in CAMERA_POSE_ORIGINS
        if camera_pose:
            joints = _joints_from_pose(pose)
            pose_block = {
                "origin": origin or "mediapipe-pose",
                "simulated": False,
                "joints": joints,
                "known_joints": list(KNOWN_JOINTS),
                "bones": [list(edge) for edge in BONE_EDGES],
                "note": LIVE_CAMERA_DISCLAIMER,
            }
            disclaimer = LIVE_CAMERA_DISCLAIMER
            show_skeleton = bool(joints)
        else:
            pose_block = {
                "origin": "none",
                "simulated": False,
                "joints": {},
                "known_joints": list(KNOWN_JOINTS),
                "bones": [list(edge) for edge in BONE_EDGES],
                "note": (
                    "Pose is not inferred from a single ESP32. The Part 4 model is "
                    "founder-gated and off."
                ),
            }
            disclaimer = LIVE_DISCLAIMER
            show_skeleton = False

    return {
        "schema": FIELD_SCHEMA,
        "mode": "sandbox" if simulated else "live",
        "modality": modality,
        "tick": int(tick),
        "unit_id": str(unit_id or payload.get("unit_id") or ("sandbox" if simulated else "")),
        "simulated": simulated,
        "live": not simulated,
        "features_only": True,
        "raw_export": False,
        "show_skeleton": show_skeleton,
        "disclaimer": disclaimer,
        "hardware_validation": HARDWARE_VALIDATION,
        "pose3d": pose_block,
        "envelope": envelope,
        "occupancy_row": occupancy[0] if occupancy else [],
        "amp_heatmap": occupancy,
        "phase_heatmap": phase_map,
        "breathing_rate_per_min": breathing,
        "motion_energy": motion,
        "presence": presence,
        "cough_event_count": coughs,
        "speech_activity_ratio": speech_activity,
        "confidence": payload.get("confidence"),
        "notes": list(notes),
        "not_a_clinical_normal": True,
    }
