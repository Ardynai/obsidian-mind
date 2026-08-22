"""Evidence Bus adapters: one contract, many modalities.

The existing :class:`EvidenceSource` dataclass remains a record. Adapters are
the runnable providers. Core adapters are sandbox-only (tier 0) and never open
hardware or network. Advanced lanes live in optional extras and stay disabled
until explicitly installed and consented.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from somatic.consent.ledger import ConsentLedger
from somatic.evidence_bus.records import MeasurementPlan, RawEvidence

ADAPTER_TIERS = (0, 1, 2)  # sandbox, local hardware/GPU, cloud/lab
HYPOTHESIS_DOMAINS = ("discovery", "n-of-1", "sensing")


@dataclass(frozen=True)
class HypothesisSpec:
    """A testable claim the Evidence Bus can plan a measurement for."""

    id: str
    statement: str
    domain: str = "sensing"

    def __post_init__(self) -> None:
        if self.domain not in HYPOTHESIS_DOMAINS:
            raise ValueError(f"unsupported hypothesis domain: {self.domain}")
        if not str(self.statement or "").strip():
            raise ValueError("hypothesis statement must be non-empty")


@dataclass(frozen=True)
class EvidenceCost:
    """Sandbox cost is always zero dollars; compute_units are relative."""

    compute_units: float
    privacy_risk: str = "local-sandbox"
    dollars: float = 0.0
    hardware_required: bool = False

    def __post_init__(self) -> None:
        if self.dollars != 0.0:
            raise ValueError("sandbox evidence cost must not spend money")
        if self.hardware_required:
            raise ValueError("core adapters must not require hardware")


class EvidenceAdapter(Protocol):
    """Runnable evidence provider. Implementations must be sandbox-safe by default."""

    adapter_id: str
    modality: str
    tier: int

    def plan(self, hypothesis: HypothesisSpec, ledger: ConsentLedger) -> MeasurementPlan: ...

    def acquire(self, plan: MeasurementPlan, ledger: ConsentLedger) -> tuple[RawEvidence, ...]: ...

    def cost(self, plan: MeasurementPlan) -> EvidenceCost: ...

    def confidence(self, raw: RawEvidence) -> float: ...
