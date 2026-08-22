"""Founder-gated CSI pose model seam. Wired, off, no weights, no core dep.

A recognizable body pose from WiFi-CSI is research-grade and needs training
data or a pretrained model, ideally multiple units (see wifi-3d-fusion and
related open CSI-pose work). Enabling this lane, and any model weights, is
founder-gated.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

POSE_MODEL_ENABLED_ENV = "SOMATIC_CSI_POSE_MODEL"
POSE_MODEL_WEIGHTS_ENV = "SOMATIC_CSI_POSE_WEIGHTS"


def pose_model_status() -> dict[str, Any]:
    enabled_flag = os.environ.get(POSE_MODEL_ENABLED_ENV, "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    weights = os.environ.get(POSE_MODEL_WEIGHTS_ENV, "").strip()
    weights_path = Path(weights) if weights else None
    weights_present = bool(weights_path and weights_path.is_file())
    extra_ok = False
    try:
        import numpy  # noqa: F401

        extra_ok = True
    except ImportError:
        extra_ok = False
    enabled = enabled_flag and weights_present and extra_ok
    return {
        "schema": "somatic.sensors.pose_model.v1",
        "founder_gated": True,
        "research_grade": True,
        "enabled": enabled,
        "env_enabled": enabled_flag,
        "weights_present": weights_present,
        "extra_available": extra_ok,
        "core_dependency": False,
        "note": (
            "Off unless SOMATIC_CSI_POSE_MODEL is set, weights exist on this "
            "machine, and the csi extra is installed. No weights ship in-repo."
        ),
    }


def infer_pose(features: dict[str, Any] | None) -> dict[str, Any]:
    """Map CSI features to joints only when the founder-gated model is on.

    The default path returns empty joints so the Field view cannot imply a
    real body scan from one ESP32.
    """

    status = pose_model_status()
    if not status["enabled"]:
        return {
            "origin": "csi-pose-model",
            "simulated": False,
            "available": False,
            "joints": {},
            "status": status,
            "note": status["note"],
        }
    del features
    return {
        "origin": "csi-pose-model",
        "simulated": False,
        "available": False,
        "joints": {},
        "status": status,
        "note": (
            "Model flag is on but no in-repo inference implementation ships "
            "until the founder supplies weights and enables this lane."
        ),
    }
