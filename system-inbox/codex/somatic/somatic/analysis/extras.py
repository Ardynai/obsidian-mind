"""Lazy optional-analysis dependency status for Finch.

The helpers in this module only inspect import availability. They do not import
or execute optional scientific packages.
"""

import importlib.util
from dataclasses import dataclass


@dataclass(frozen=True)
class FinchExtraDefinition:
    """Metadata for a future package-backed Finch analysis lane."""

    id: str
    package: str
    purpose: str
    future_boundary: str
    clinical_or_genomic_interpretation: bool = False


EXTRA_DEFINITIONS = (
    FinchExtraDefinition(
        id="pandas",
        package="pandas",
        purpose="future tabular dataframe analysis",
        future_boundary="optional local table backend only after explicit configuration",
    ),
    FinchExtraDefinition(
        id="scipy",
        package="scipy",
        purpose="future statistical tests and curve fitting",
        future_boundary="optional local statistics backend only after safety review",
    ),
    FinchExtraDefinition(
        id="numpy",
        package="numpy",
        purpose="future numeric array operations",
        future_boundary="optional local numeric backend only after explicit configuration",
    ),
    FinchExtraDefinition(
        id="scanpy",
        package="scanpy",
        purpose="future single-cell analysis planning",
        future_boundary="metadata-only until explicit bioinformatics validation exists",
    ),
    FinchExtraDefinition(
        id="biopython",
        package="Bio",
        purpose="future sequence and format parsing",
        future_boundary="metadata-only until explicit sequence-analysis validation exists",
    ),
)


def is_extra_available(definition: FinchExtraDefinition) -> bool:
    """Return True when an optional package can be found without importing it."""
    try:
        return importlib.util.find_spec(definition.package) is not None
    except (ImportError, ValueError):
        return False


def optional_extra_status(definition: FinchExtraDefinition) -> dict:
    """Build deterministic status metadata for a single optional extra."""
    available = is_extra_available(definition)
    return {
        "id": definition.id,
        "package": definition.package,
        "purpose": definition.purpose,
        "future_boundary": definition.future_boundary,
        "availability": "available" if available else "unavailable",
        "status": "disabled-by-default",
        "runtime_enabled": False,
        "fake_backed": True,
        "disabled_by_default": True,
        "clinical_or_genomic_interpretation": definition.clinical_or_genomic_interpretation,
    }


def all_optional_extra_statuses() -> list[dict]:
    """Return status metadata for all known Finch optional extras."""
    return [optional_extra_status(definition) for definition in EXTRA_DEFINITIONS]
