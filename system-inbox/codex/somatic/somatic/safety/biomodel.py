"""Biomodel readiness gates for future real model runtimes."""

from dataclasses import dataclass, field
from typing import Any

BLOCK_RUNTIME_EXECUTION_DISABLED = "runtime-execution-disabled"
BLOCK_MODEL_DOWNLOADS_DISABLED = "model-downloads-disabled"
BLOCK_MSA_SERVER_DISABLED = "msa-server-disabled"
BLOCK_NETWORK_CALLS_DISABLED = "network-calls-disabled"
BLOCK_GPU_EXECUTION_DISABLED = "gpu-execution-disabled"
BLOCK_MISSING_RESOURCE_REVIEW = "missing-resource-review"
BLOCK_MISSING_PROVENANCE_PLAN = "missing-provenance-plan"
BLOCK_MISSING_USER_CONSENT = "missing-user-consent"
BLOCK_RESEARCH_ONLY_NOT_ACKNOWLEDGED = "research-only-boundary-not-acknowledged"

DEFAULT_BLOCK_REASON_ORDER = (
    BLOCK_RUNTIME_EXECUTION_DISABLED,
    BLOCK_MODEL_DOWNLOADS_DISABLED,
    BLOCK_MSA_SERVER_DISABLED,
    BLOCK_NETWORK_CALLS_DISABLED,
    BLOCK_GPU_EXECUTION_DISABLED,
    BLOCK_MISSING_RESOURCE_REVIEW,
    BLOCK_MISSING_PROVENANCE_PLAN,
    BLOCK_MISSING_USER_CONSENT,
    BLOCK_RESEARCH_ONLY_NOT_ACKNOWLEDGED,
)


class BiomodelReadinessGateError(RuntimeError):
    """Raised when biomodel runtime gates reject requested behavior."""


@dataclass(frozen=True)
class BiomodelRuntimePolicy:
    runtime_execution_enabled: bool = False
    model_downloads_enabled: bool = False
    msa_server_enabled: bool = False
    network_calls_enabled: bool = False
    gpu_execution_enabled: bool = False
    resource_review_complete: bool = False
    provenance_plan_complete: bool = False
    require_user_consent: bool = True
    require_research_only_acknowledgement: bool = True
    policy_version: str = "phase-6c-safe-default"
    runtime_boundary: str = "future-real-runtime-only"
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "BiomodelRuntimePolicy":
        fields = {
            "runtime_execution_enabled",
            "model_downloads_enabled",
            "msa_server_enabled",
            "network_calls_enabled",
            "gpu_execution_enabled",
            "resource_review_complete",
            "provenance_plan_complete",
            "require_user_consent",
            "require_research_only_acknowledgement",
            "policy_version",
            "runtime_boundary",
            "metadata",
        }
        kwargs = {key: payload[key] for key in fields if key in payload}
        return cls(**kwargs)

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_version": self.policy_version,
            "runtime_boundary": self.runtime_boundary,
            "runtime_execution_enabled": self.runtime_execution_enabled,
            "model_downloads_enabled": self.model_downloads_enabled,
            "msa_server_enabled": self.msa_server_enabled,
            "network_calls_enabled": self.network_calls_enabled,
            "gpu_execution_enabled": self.gpu_execution_enabled,
            "resource_review_complete": self.resource_review_complete,
            "provenance_plan_complete": self.provenance_plan_complete,
            "require_user_consent": self.require_user_consent,
            "require_research_only_acknowledgement": (self.require_research_only_acknowledgement),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class BiomodelConsentRecord:
    user_consent: bool = False
    research_only_acknowledged: bool = False
    resource_review_acknowledged: bool = False
    provenance_plan_acknowledged: bool = False
    model_downloads_acknowledged: bool = False
    msa_server_acknowledged: bool = False
    network_calls_acknowledged: bool = False
    gpu_execution_acknowledged: bool = False
    consent_scope: str = "none"
    recorded_by: str = "somatic-fixture-placeholder"
    recorded_at: str = "not-recorded"
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "BiomodelConsentRecord":
        fields = {
            "user_consent",
            "research_only_acknowledged",
            "resource_review_acknowledged",
            "provenance_plan_acknowledged",
            "model_downloads_acknowledged",
            "msa_server_acknowledged",
            "network_calls_acknowledged",
            "gpu_execution_acknowledged",
            "consent_scope",
            "recorded_by",
            "recorded_at",
            "metadata",
        }
        kwargs = {key: payload[key] for key in fields if key in payload}
        return cls(**kwargs)

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_consent": self.user_consent,
            "research_only_acknowledged": self.research_only_acknowledged,
            "resource_review_acknowledged": self.resource_review_acknowledged,
            "provenance_plan_acknowledged": self.provenance_plan_acknowledged,
            "model_downloads_acknowledged": self.model_downloads_acknowledged,
            "msa_server_acknowledged": self.msa_server_acknowledged,
            "network_calls_acknowledged": self.network_calls_acknowledged,
            "gpu_execution_acknowledged": self.gpu_execution_acknowledged,
            "consent_scope": self.consent_scope,
            "recorded_by": self.recorded_by,
            "recorded_at": self.recorded_at,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class BiomodelReadinessReport:
    ready: bool
    execution_permitted: bool
    block_reasons: tuple[str, ...]
    runtime_boundary: str = "future-real-runtime-only"
    phase_runtime: str = "not-implemented"
    research_only: bool = True
    policy: dict[str, Any] = field(default_factory=dict)
    consent: dict[str, Any] = field(default_factory=dict)
    plan: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "BiomodelReadinessReport":
        fields = {
            "ready",
            "execution_permitted",
            "runtime_boundary",
            "phase_runtime",
            "research_only",
            "policy",
            "consent",
            "plan",
            "metadata",
        }
        kwargs = {key: payload[key] for key in fields if key in payload}
        kwargs["block_reasons"] = tuple(payload.get("block_reasons", ()))
        return cls(**kwargs)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ready": self.ready,
            "execution_permitted": self.execution_permitted,
            "runtime_boundary": self.runtime_boundary,
            "phase_runtime": self.phase_runtime,
            "research_only": self.research_only,
            "block_reasons": list(self.block_reasons),
            "policy": dict(self.policy),
            "consent": dict(self.consent),
            "plan": dict(self.plan),
            "metadata": dict(self.metadata),
        }


def evaluate_biomodel_readiness(
    plan: Any,
    policy: BiomodelRuntimePolicy,
    consent: BiomodelConsentRecord,
) -> BiomodelReadinessReport:
    """Evaluate deterministic gates before any future real biomodel execution."""

    block_reasons: list[str] = []
    if not policy.runtime_execution_enabled:
        block_reasons.append(BLOCK_RUNTIME_EXECUTION_DISABLED)
    if not policy.model_downloads_enabled:
        block_reasons.append(BLOCK_MODEL_DOWNLOADS_DISABLED)
    if not policy.msa_server_enabled:
        block_reasons.append(BLOCK_MSA_SERVER_DISABLED)
    if not policy.network_calls_enabled:
        block_reasons.append(BLOCK_NETWORK_CALLS_DISABLED)
    if not policy.gpu_execution_enabled:
        block_reasons.append(BLOCK_GPU_EXECUTION_DISABLED)
    if not policy.resource_review_complete:
        block_reasons.append(BLOCK_MISSING_RESOURCE_REVIEW)
    if not policy.provenance_plan_complete:
        block_reasons.append(BLOCK_MISSING_PROVENANCE_PLAN)
    if policy.require_user_consent and not consent.user_consent:
        block_reasons.append(BLOCK_MISSING_USER_CONSENT)
    if policy.require_research_only_acknowledgement and not consent.research_only_acknowledged:
        block_reasons.append(BLOCK_RESEARCH_ONLY_NOT_ACKNOWLEDGED)

    return BiomodelReadinessReport(
        ready=not block_reasons,
        execution_permitted=False,
        block_reasons=tuple(block_reasons),
        runtime_boundary=policy.runtime_boundary,
        phase_runtime="not-implemented",
        research_only=True,
        policy=policy.to_dict(),
        consent=consent.to_dict(),
        plan=_plan_summary(plan),
        metadata={
            "schema": "somatic.biomodel_readiness_report",
            "phase": "6C",
            "real_runtime_enabled_in_this_phase": False,
            "fake_backed_in_silico_available": True,
            "default_block_reason_order": list(DEFAULT_BLOCK_REASON_ORDER),
        },
    )


def _plan_summary(plan: Any) -> dict[str, Any]:
    if hasattr(plan, "to_dict"):
        payload = plan.to_dict()
    elif isinstance(plan, dict):
        payload = plan
    else:
        payload = {"description": str(plan)}

    return {
        "id": payload.get("id"),
        "provider_id": payload.get("provider_id"),
        "request_id": payload.get("request_id"),
        "status": payload.get("status"),
        "objective": payload.get("objective"),
    }
