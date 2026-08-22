"""Falsifier: pick the cheapest unused sandbox modality by expected information gain."""

from __future__ import annotations

from somatic.evidence_bus.records import EvidenceSource, MeasurementPlan
from somatic.evidence_bus.sandbox_adapters import sandbox_adapters
from somatic.science.belief import HypothesisBelief


def propose_next_measurement(
    belief: HypothesisBelief,
    already_used: tuple[str, ...] | list[str],
    *,
    seed: int = 0,
) -> dict[str, object]:
    """Return the unused modality with the highest entropy / cost ratio."""

    used = set(already_used)
    adapters = sandbox_adapters(seed=seed)
    ranked: list[tuple[float, str, float]] = []
    for modality, adapter in adapters.items():
        if modality in used:
            continue
        source = EvidenceSource(
            id=f"falsifier-{modality}",
            modality=modality,
            provider_ref=adapter.adapter_id,
            description="Falsifier probe plan; sandbox only.",
        )
        plan = MeasurementPlan(
            id="falsifier-probe",
            sources=[source],
            objective="sandbox falsifier probe",
        )
        cost = adapter.cost(plan)
        eig = belief.entropy() / max(0.1, cost.compute_units)
        ranked.append((eig, modality, cost.compute_units))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    if not ranked:
        return {
            "modality": "",
            "reason": "no unused sandbox modalities remain",
            "expected_information_gain": 0.0,
        }
    eig, modality, units = ranked[0]
    return {
        "modality": modality,
        "reason": "highest sandbox entropy/cost among unused modalities",
        "expected_information_gain": round(eig, 4),
        "compute_units": units,
        "dollars": 0.0,
        "hardware_required": False,
    }
