"""Disabled Finch optional-extras provider scaffold."""

from dataclasses import dataclass

from somatic.analysis.extras import (
    EXTRA_DEFINITIONS,
    all_optional_extra_statuses,
    optional_extra_status,
)


class FinchExtrasRuntimeNotEnabledError(RuntimeError):
    """Raised when package-backed Finch analysis is requested before enablement."""


@dataclass(frozen=True)
class FinchExtrasProviderConfig:
    """Configuration for the disabled Finch optional-extras scaffold."""

    enabled: bool = False
    mode: str = "mock"
    selected_extra: str | None = None
    allow_real_computation: bool = False


class FinchExtrasProvider:
    """Provider-shaped metadata for future package-backed Finch analysis."""

    provider_id = "finch-extras-provider"

    def __init__(self, config: FinchExtrasProviderConfig | None = None):
        self.config = config or FinchExtrasProviderConfig()

    def status(self) -> dict:
        """Return deterministic fake-backed provider and dependency status."""
        return {
            "schema_version": 1,
            "provider_id": self.provider_id,
            "status": "scaffolded",
            "fake_backed": True,
            "disabled_by_default": True,
            "runtime_enabled": False,
            "mode": self.config.mode,
            "selected_extra": self.config.selected_extra,
            "default_path": "standard-library-finch",
            "standard_library_fallback_active": True,
            "network_calls_allowed": False,
            "external_runtime_enabled": False,
            "clinical_or_genomic_interpretation": False,
            "extras": all_optional_extra_statuses(),
            "limitations": [
                "Availability is checked lazily with importlib.util.find_spec.",
                "Optional packages are not imported or required by the basic install.",
                "Package-backed Finch analysis is future work and disabled by default.",
            ],
        }

    def require_real_extra(self, extra_id: str) -> dict:
        """Fail closed unless a future real optional-extra path is explicitly added."""
        definition = _definition_for(extra_id)
        status = optional_extra_status(definition)
        if status["availability"] != "available":
            raise FinchExtrasRuntimeNotEnabledError(
                f"{extra_id} optional dependency is unavailable; "
                "Finch remains on the standard-library fallback."
            )
        if (
            self.config.mode != "real"
            or not self.config.enabled
            or not self.config.allow_real_computation
        ):
            raise FinchExtrasRuntimeNotEnabledError(
                f"{extra_id} package-backed analysis is disabled by default; "
                "enablement requires a future reviewed runtime path."
            )
        raise FinchExtrasRuntimeNotEnabledError(
            f"{extra_id} package-backed analysis is not implemented in this scaffold."
        )


def _definition_for(extra_id: str):
    for definition in EXTRA_DEFINITIONS:
        if definition.id == extra_id:
            return definition
    known = ", ".join(definition.id for definition in EXTRA_DEFINITIONS)
    raise FinchExtrasRuntimeNotEnabledError(
        f"unknown Finch optional extra {extra_id}; known: {known}"
    )
