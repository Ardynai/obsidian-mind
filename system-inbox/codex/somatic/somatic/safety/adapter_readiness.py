"""Shared real-mode readiness gates for future adapter runtimes.

The gate is descriptive only in this phase.  It records which review gates are
missing before any future real adapter could be considered, while keeping
runtime execution disabled.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field

REAL_MODE_READINESS_GATE_CONTRACT_VERSION = 1
REAL_MODE_READINESS_GATE_KIND = "real-mode-readiness-gate"
REAL_MODE_GATE_BLOCKED_STATUS = "blocked-fixture-reference-only"
REAL_MODE_GATE_REVIEWED_STATUS = "review-complete-runtime-disabled"
REAL_MODE_PHASE_RUNTIME = "not-implemented"
REAL_MODE_REQUIRED_GATES = (
    "consent",
    "license-review",
    "privacy-review",
    "hardware-review",
    "model-artifact-review",
    "dependency-review",
    "network-policy-review",
)


@dataclass(frozen=True)
class RealModeReadinessReviewRecord:
    """Explicit review acknowledgements for future real adapter mode."""

    consent: bool = False
    license_review: bool = False
    privacy_review: bool = False
    hardware_review: bool = False
    model_artifact_review: bool = False
    dependency_review: bool = False
    network_policy_review: bool = False

    @classmethod
    def from_mapping(
        cls,
        payload: Mapping[str, object] | None,
    ) -> RealModeReadinessReviewRecord:
        if not isinstance(payload, Mapping):
            return cls()
        return cls(
            consent=payload.get("consent") is True,
            license_review=(
                payload.get("license_review") is True or payload.get("license-review") is True
            ),
            privacy_review=(
                payload.get("privacy_review") is True or payload.get("privacy-review") is True
            ),
            hardware_review=(
                payload.get("hardware_review") is True or payload.get("hardware-review") is True
            ),
            model_artifact_review=(
                payload.get("model_artifact_review") is True
                or payload.get("model-artifact-review") is True
            ),
            dependency_review=(
                payload.get("dependency_review") is True or payload.get("dependency-review") is True
            ),
            network_policy_review=(
                payload.get("network_policy_review") is True
                or payload.get("network-policy-review") is True
            ),
        )

    @classmethod
    def from_satisfied_gates(
        cls,
        satisfied_gates: Iterable[object] | None,
    ) -> RealModeReadinessReviewRecord:
        gates = {_safe_gate_id(gate) for gate in (satisfied_gates or ())}
        return cls(
            consent="consent" in gates,
            license_review="license-review" in gates,
            privacy_review="privacy-review" in gates,
            hardware_review="hardware-review" in gates,
            model_artifact_review="model-artifact-review" in gates,
            dependency_review="dependency-review" in gates,
            network_policy_review="network-policy-review" in gates,
        )

    def satisfied_gate_ids(self) -> tuple[str, ...]:
        gates = []
        if self.consent:
            gates.append("consent")
        if self.license_review:
            gates.append("license-review")
        if self.privacy_review:
            gates.append("privacy-review")
        if self.hardware_review:
            gates.append("hardware-review")
        if self.model_artifact_review:
            gates.append("model-artifact-review")
        if self.dependency_review:
            gates.append("dependency-review")
        if self.network_policy_review:
            gates.append("network-policy-review")
        return tuple(gates)

    def to_dict(self) -> dict[str, bool]:
        return {
            "consent": self.consent,
            "license_review": self.license_review,
            "privacy_review": self.privacy_review,
            "hardware_review": self.hardware_review,
            "model_artifact_review": self.model_artifact_review,
            "dependency_review": self.dependency_review,
            "network_policy_review": self.network_policy_review,
        }


@dataclass(frozen=True)
class RealModeReadinessReport:
    """Sanitized adapter real-mode readiness report."""

    provider_kind: str
    adapter_kind: str
    current_mode: str
    required_gates: tuple[str, ...] = REAL_MODE_REQUIRED_GATES
    satisfied_gates: tuple[str, ...] = ()
    missing_gates: tuple[str, ...] = REAL_MODE_REQUIRED_GATES
    status: str = REAL_MODE_GATE_BLOCKED_STATUS
    ready: bool = False
    execution_permitted: bool = False
    runtime_stage: str = REAL_MODE_PHASE_RUNTIME
    metadata_only: bool = True
    sanitized: bool = True
    review_record: dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "gate_contract_version": REAL_MODE_READINESS_GATE_CONTRACT_VERSION,
            "gate_kind": REAL_MODE_READINESS_GATE_KIND,
            "provider_kind": self.provider_kind,
            "adapter_kind": self.adapter_kind,
            "current_mode": self.current_mode,
            "status": self.status,
            "ready": self.ready,
            "execution_permitted": self.execution_permitted,
            "runtime_stage": self.runtime_stage,
            "required_gates": list(self.required_gates),
            "satisfied_gates": list(self.satisfied_gates),
            "missing_gates": list(self.missing_gates),
            "required_gate_count": len(self.required_gates),
            "satisfied_gate_count": len(self.satisfied_gates),
            "missing_gate_count": len(self.missing_gates),
            "block_reasons": [f"missing-{gate}" for gate in self.missing_gates],
            "runtime_block_reasons": ["runtime-not-implemented"],
            "metadata_only": self.metadata_only,
            "sanitized": self.sanitized,
            "real_mode_runtime_enabled": False,
            "review_record": dict(self.review_record),
        }


def evaluate_real_mode_readiness(
    *,
    provider_kind: object,
    adapter_kind: object,
    current_mode: object,
    review_record: RealModeReadinessReviewRecord | Mapping[str, object] | None = None,
    satisfied_gates: Iterable[object] | None = None,
) -> RealModeReadinessReport:
    """Evaluate shared real-mode readiness without enabling a runtime."""

    if isinstance(review_record, RealModeReadinessReviewRecord):
        record = review_record
    elif isinstance(review_record, Mapping):
        record = RealModeReadinessReviewRecord.from_mapping(review_record)
    else:
        record = RealModeReadinessReviewRecord.from_satisfied_gates(satisfied_gates)
    satisfied = record.satisfied_gate_ids()
    missing = tuple(gate for gate in REAL_MODE_REQUIRED_GATES if gate not in satisfied)
    ready = not missing
    return RealModeReadinessReport(
        provider_kind=_safe_public_label(provider_kind, "unknown-provider"),
        adapter_kind=_safe_public_label(adapter_kind, "unknown-adapter"),
        current_mode=_safe_public_label(current_mode, "fixture-or-reference-only"),
        satisfied_gates=satisfied,
        missing_gates=missing,
        status=(REAL_MODE_GATE_REVIEWED_STATUS if ready else REAL_MODE_GATE_BLOCKED_STATUS),
        ready=ready,
        execution_permitted=False,
        review_record=record.to_dict(),
    )


def real_mode_readiness_gate_summary(value: object) -> dict[str, object]:
    """Return a compact public manifest/report summary for a gate payload."""

    if not isinstance(value, Mapping):
        return {}
    required = _safe_gate_list(value.get("required_gates"))
    missing = _safe_gate_list(value.get("missing_gates"))
    return {
        "gate_contract_version": _safe_int(value.get("gate_contract_version")),
        "gate_kind": _safe_public_label(
            value.get("gate_kind"),
            REAL_MODE_READINESS_GATE_KIND,
        ),
        "status": _safe_public_label(
            value.get("status"),
            REAL_MODE_GATE_BLOCKED_STATUS,
        ),
        "ready": bool(value.get("ready")),
        "execution_permitted": False,
        "runtime_stage": _safe_public_label(
            value.get("runtime_stage"),
            REAL_MODE_PHASE_RUNTIME,
        ),
        "required_gates": list(required),
        "missing_gates": list(missing),
        "required_gate_count": len(required),
        "missing_gate_count": len(missing),
        "real_mode_runtime_enabled": False,
        "metadata_only": True,
        "sanitized": True,
    }


def _safe_gate_list(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    gates = []
    for item in value:
        gate = _safe_gate_id(item)
        if gate in REAL_MODE_REQUIRED_GATES and gate not in gates:
            gates.append(gate)
    return tuple(gates)


def _safe_gate_id(value: object) -> str:
    text = str(value or "").strip().lower().replace("_", "-")
    safe = "".join(char if char.isalnum() or char == "-" else "-" for char in text)
    return "-".join(part for part in safe.split("-") if part)


def _safe_public_label(value: object, default: str) -> str:
    text = str(value or default).strip().lower().replace("_", "-")
    safe = "".join(char if char.isalnum() or char == "-" else "-" for char in text)
    compact = "-".join(part for part in safe.split("-") if part)
    return compact or default


def _safe_int(value: object) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return 0
    return number if number >= 0 else 0


__all__ = [
    "REAL_MODE_GATE_BLOCKED_STATUS",
    "REAL_MODE_GATE_REVIEWED_STATUS",
    "REAL_MODE_PHASE_RUNTIME",
    "REAL_MODE_READINESS_GATE_CONTRACT_VERSION",
    "REAL_MODE_READINESS_GATE_KIND",
    "REAL_MODE_REQUIRED_GATES",
    "RealModeReadinessReport",
    "RealModeReadinessReviewRecord",
    "evaluate_real_mode_readiness",
    "real_mode_readiness_gate_summary",
]
