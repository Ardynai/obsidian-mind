"""Consent-gated n-of-1 experiment designer (own-baseline only)."""

from .n_of_1 import (
    AWAITING_FOLLOWUP,
    AWAY_FROM_BASELINE,
    INSUFFICIENT_BASELINE,
    SPREAD_TOO_SMALL,
    STABLE,
    TOWARD_BASELINE,
    ExperimentReport,
    InterventionTag,
    evaluate_n_of_1,
)
from .store import (
    EXPERIMENT_PATH_ENV,
    append_tag,
    default_experiment_path,
    erase_stored_tags,
    load_tags,
    save_tags,
)

__all__ = [
    "AWAITING_FOLLOWUP",
    "AWAY_FROM_BASELINE",
    "EXPERIMENT_PATH_ENV",
    "ExperimentReport",
    "INSUFFICIENT_BASELINE",
    "InterventionTag",
    "SPREAD_TOO_SMALL",
    "STABLE",
    "TOWARD_BASELINE",
    "append_tag",
    "default_experiment_path",
    "erase_stored_tags",
    "evaluate_n_of_1",
    "load_tags",
    "save_tags",
]
