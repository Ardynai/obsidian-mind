"""Consent-gated personal insights package."""

from .engine import (
    ABOVE_REFERENCE,
    BELOW_REFERENCE,
    TREND_FALLING,
    TREND_RISING,
    TREND_STABLE,
    WITHIN_REFERENCE,
    ReferenceRange,
    grade_metric,
    summarize_series,
)

__all__ = [
    "ABOVE_REFERENCE",
    "BELOW_REFERENCE",
    "TREND_FALLING",
    "TREND_RISING",
    "TREND_STABLE",
    "WITHIN_REFERENCE",
    "ReferenceRange",
    "grade_metric",
    "summarize_series",
]
