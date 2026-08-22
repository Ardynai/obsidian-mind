"""Stdlib belief ledger: Beta posteriors over hypotheses. No NumPyro in core."""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class HypothesisBelief:
    hypothesis_id: str
    alpha: float = 1.0
    beta: float = 1.0
    updates: int = 0

    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    def variance(self) -> float:
        total = self.alpha + self.beta
        return (self.alpha * self.beta) / ((total**2) * (total + 1.0))

    def entropy(self) -> float:
        p = min(0.999, max(0.001, self.mean()))
        return -p * math.log(p) - (1.0 - p) * math.log(1.0 - p)


@dataclass
class BeliefLedger:
    """Independent Beta posteriors; each modality update is a weighted coin-flip."""

    beliefs: dict[str, HypothesisBelief] = field(default_factory=dict)

    def prior(self, hypothesis_id: str) -> HypothesisBelief:
        return self.beliefs.setdefault(hypothesis_id, HypothesisBelief(hypothesis_id=hypothesis_id))

    def update(self, hypothesis_id: str, *, support: bool, weight: float) -> HypothesisBelief:
        belief = self.prior(hypothesis_id)
        mass = max(0.0, min(5.0, float(weight)))
        if support:
            belief.alpha += mass
        else:
            belief.beta += mass
        belief.updates += 1
        return belief

    def snapshot(self) -> dict[str, dict[str, float | int | str]]:
        return {
            hid: {
                "hypothesis_id": belief.hypothesis_id,
                "mean": round(belief.mean(), 4),
                "variance": round(belief.variance(), 6),
                "entropy": round(belief.entropy(), 4),
                "updates": belief.updates,
            }
            for hid, belief in sorted(self.beliefs.items())
        }
