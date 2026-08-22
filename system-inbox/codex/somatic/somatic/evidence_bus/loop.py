"""Consent-gated Evidence Bus loop: plan → acquire → verdict for many modalities."""

from __future__ import annotations

from dataclasses import dataclass

from somatic.consent.ledger import ConsentLedger
from somatic.consent.scopes import ANALYSIS_INSIGHT
from somatic.evidence_bus.adapter import EvidenceAdapter, EvidenceCost, HypothesisSpec
from somatic.evidence_bus.records import StructuredVerdict
from somatic.evidence_bus.sandbox_adapters import sandbox_adapters
from somatic.safety.core import (
    EMERGENCY_GUIDANCE,
    AdvisoryFramingError,
    EvidenceGrade,
    emergency_screen,
    frame_advisory,
    require_consent,
)


@dataclass(frozen=True)
class EvidenceStep:
    modality: str
    raw_id: str
    sha256: str
    confidence: float
    cost: EvidenceCost
    features: dict[str, object]


@dataclass(frozen=True)
class EvidenceLoopReport:
    hypothesis_id: str
    steps: tuple[EvidenceStep, ...]
    verdict: StructuredVerdict
    emergency_triggered: bool
    notes: tuple[str, ...]


def run_evidence_loop(
    ledger: ConsentLedger,
    hypothesis: HypothesisSpec,
    *,
    modalities: tuple[str, ...] | list[str] | None = None,
    seed: int = 0,
    adapters: dict[str, EvidenceAdapter] | None = None,
    simulated: bool = True,
) -> EvidenceLoopReport:
    """Acquire evidence for ``hypothesis``. Requires ANALYSIS_INSIGHT.

    ``simulated=True`` (default) is the sandbox path. Live adapters pass
    ``simulated=False`` so the verdict does not claim a sandbox measurement.
    """

    require_consent(ledger, ANALYSIS_INSIGHT)
    screen = emergency_screen(hypothesis.statement)
    if screen.triggered:
        verdict = StructuredVerdict(
            id="verdict-emergency",
            raw_evidence_refs=[],
            summary=screen.guidance or EMERGENCY_GUIDANCE,
            confidence=EvidenceGrade.NONE,
            limitations=["Emergency screen short-circuited the Evidence Bus."],
            metadata={"emergency": True, "kind": screen.kind},
        )
        return EvidenceLoopReport(
            hypothesis_id=hypothesis.id,
            steps=(),
            verdict=verdict,
            emergency_triggered=True,
            notes=("emergency-screen",),
        )

    registry = adapters if adapters is not None else sandbox_adapters(seed=seed)
    requested = tuple(modalities) if modalities else tuple(sorted(registry))
    steps: list[EvidenceStep] = []
    raw_ids: list[str] = []
    for modality in requested:
        adapter = registry.get(modality)
        if adapter is None:
            raise ValueError(f"no Evidence Bus adapter for modality: {modality}")
        plan = adapter.plan(hypothesis, ledger)
        cost = adapter.cost(plan)
        acquired = adapter.acquire(plan, ledger)
        for raw in acquired:
            conf = adapter.confidence(raw)
            features = raw.metadata.get("features")
            feature_map = dict(features) if isinstance(features, dict) else {}
            steps.append(
                EvidenceStep(
                    modality=modality,
                    raw_id=raw.id,
                    sha256=raw.sha256,
                    confidence=conf,
                    cost=cost,
                    features=feature_map,
                )
            )
            raw_ids.append(raw.id)

    mean_conf = sum(step.confidence for step in steps) / len(steps) if steps else 0.0
    if simulated:
        summary = (
            f"Sandbox Evidence Bus acquired {len(steps)} simulated modality record(s) "
            f"for hypothesis {hypothesis.id}. Mean adapter confidence {mean_conf:.2f}. "
            "Informational only; no hardware was opened and no diagnosis was made."
        )
        sources = ("evidence-bus-sandbox", *(step.modality for step in steps))
        limitations = [
            "Sandbox-simulated evidence only.",
            "No live sensor, lab, or literature HTTP was used.",
        ]
        note_kind = ("sandbox", "local-first", "hardware-closed")
    else:
        live_modalities = {step.modality for step in steps}
        if live_modalities <= {"csi"}:
            summary = (
                f"Local Evidence Bus acquired {len(steps)} derived CSI feature record(s) "
                f"for hypothesis {hypothesis.id}. Mean adapter confidence {mean_conf:.2f}. "
                "Informational only; raw CSI was not stored and no diagnosis was made."
            )
            sources = ("evidence-bus-live-csi", *(step.modality for step in steps))
            limitations = [
                "Derived CSI features only; raw IQ discarded.",
                "Loopback ingest; needs a real ESP32 to validate live capture.",
            ]
            note_kind = ("live-csi", "local-first", "features-only")
        else:
            summary = (
                f"Local Evidence Bus acquired {len(steps)} derived on-device feature "
                f"record(s) for hypothesis {hypothesis.id}. Mean adapter confidence "
                f"{mean_conf:.2f}. Informational only; raw frames were not stored "
                "and no diagnosis was made."
            )
            sources = ("evidence-bus-live-on-device", *(step.modality for step in steps))
            limitations = [
                "Derived features only; raw camera frames and CSI IQ were not stored.",
                "On-device only; nothing left this machine.",
            ]
            note_kind = ("live-on-device", "local-first", "features-only")
    try:
        framed = frame_advisory(
            summary=summary,
            evidence_grade=EvidenceGrade.NONE,
            sources=sources,
            consent_scope=ANALYSIS_INSIGHT,
            authoritative_scan=True,
        )
        summary_text = framed.summary
        grade = framed.evidence_grade
        notice = framed.informational_notice
        routing = framed.professional_routing
    except AdvisoryFramingError:
        summary_text = (
            "Sandbox evidence was acquired, but the summary could not be framed "
            "as informational. Consult a licensed professional."
        )
        grade = EvidenceGrade.NONE
        notice = ""
        routing = ""
    verdict = StructuredVerdict(
        id=f"verdict-{hypothesis.id}",
        raw_evidence_refs=raw_ids,
        summary=summary_text,
        confidence=grade,
        limitations=limitations,
        metadata={
            "informational_notice": notice,
            "professional_routing": routing,
            "simulated": simulated,
        },
    )
    return EvidenceLoopReport(
        hypothesis_id=hypothesis.id,
        steps=tuple(steps),
        verdict=verdict,
        emergency_triggered=False,
        notes=note_kind,
    )
