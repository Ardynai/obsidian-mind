"""Autonomous-science harness: tournament + teams + Evidence Bus + belief + falsifier."""

from __future__ import annotations

from dataclasses import dataclass

from somatic.agents.tournament import run_hypothesis_tournament
from somatic.consent.ledger import ConsentLedger
from somatic.consent.scopes import ANALYSIS_INSIGHT, AUTONOMOUS_RESEARCH
from somatic.evidence_bus.adapter import HypothesisSpec
from somatic.evidence_bus.loop import EvidenceLoopReport, run_evidence_loop
from somatic.safety.core import (
    EMERGENCY_GUIDANCE,
    AdvisoryFramingError,
    EvidenceGrade,
    emergency_screen,
    frame_advisory,
    require_consent,
)
from somatic.science.belief import BeliefLedger
from somatic.science.biosecurity import screen_biosecurity
from somatic.science.falsifier import propose_next_measurement


@dataclass(frozen=True)
class ScienceHarnessReport:
    goal: str
    ranked_hypothesis_id: str
    ranked_statement: str
    evidence: EvidenceLoopReport | None
    belief: dict[str, dict[str, float | int | str]]
    next_measurement: dict[str, object]
    team_focus: tuple[str, ...]
    blocked: str
    summary: str


def run_science_loop(
    ledger: ConsentLedger,
    goal: str,
    *,
    seed: int = 0,
    modalities: tuple[str, ...] = ("literature", "sim", "csi"),
) -> ScienceHarnessReport:
    """Run one sandbox science cycle. Requires research + insight. Never spends money."""

    require_consent(ledger, AUTONOMOUS_RESEARCH)
    require_consent(ledger, ANALYSIS_INSIGHT)
    text = str(goal or "").strip()
    if not text:
        raise ValueError("science goal must be non-empty")

    emergency = emergency_screen(text)
    if emergency.triggered:
        return _blocked(text, emergency.guidance or EMERGENCY_GUIDANCE, "emergency")

    bio = screen_biosecurity(text)
    if bio.blocked:
        return _blocked(text, bio.guidance, "biosecurity")

    workflow = {"id": "masterplan-science", "mode": "discovery", "goal": text}
    evidence = {"id": "sandbox-science-evidence", "goal": text}
    tournament = run_hypothesis_tournament(workflow, evidence)
    ranked = list(tournament.get("ranked_hypotheses") or [])
    top = ranked[0] if ranked else {"id": "hyp-none", "statement": text}
    hid = str(top.get("id") or "hyp-none")
    statement = str(top.get("statement") or text)
    teams = tournament.get("team_orchestrator") or {}
    roster = teams.get("team_roster") if isinstance(teams, dict) else {}
    team_rows = roster.get("teams") if isinstance(roster, dict) else []
    focus: tuple[str, ...] = ()
    if team_rows and isinstance(team_rows[0], dict):
        focus = tuple(str(item) for item in team_rows[0].get("focus_hypothesis_ids") or [])
    spec = HypothesisSpec(id=hid, statement=statement, domain="discovery")
    loop = run_evidence_loop(ledger, spec, modalities=modalities, seed=seed)

    ledger_belief = BeliefLedger()
    for step in loop.steps:
        ledger_belief.update(hid, support=step.confidence >= 0.4, weight=step.confidence)
    belief = ledger_belief.prior(hid)
    nxt = propose_next_measurement(belief, [step.modality for step in loop.steps], seed=seed)

    summary = (
        f"Sandbox science cycle for goal {text!r} ranked {hid}. "
        f"Belief mean {belief.mean():.2f} after {belief.updates} update(s). "
        "Informational research only; no lab action, no diagnosis, no spend."
    )
    try:
        framed = frame_advisory(
            summary=summary,
            evidence_grade=EvidenceGrade.NONE,
            sources=("science-harness-sandbox", "evidence-bus-sandbox"),
            consent_scope=AUTONOMOUS_RESEARCH,
            authoritative_scan=True,
        )
        summary_text = framed.summary
    except AdvisoryFramingError:
        summary_text = (
            "The science cycle completed in sandbox, but the summary could not be "
            "framed as informational research. Consult a licensed professional."
        )

    return ScienceHarnessReport(
        goal=text,
        ranked_hypothesis_id=hid,
        ranked_statement=statement,
        evidence=loop,
        belief=ledger_belief.snapshot(),
        next_measurement=nxt,
        team_focus=focus,
        blocked="",
        summary=summary_text,
    )


def _blocked(goal: str, guidance: str, kind: str) -> ScienceHarnessReport:
    return ScienceHarnessReport(
        goal=goal,
        ranked_hypothesis_id="",
        ranked_statement="",
        evidence=None,
        belief={},
        next_measurement={},
        team_focus=(),
        blocked=kind,
        summary=guidance,
    )
