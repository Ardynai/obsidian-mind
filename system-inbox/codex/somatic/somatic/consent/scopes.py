"""Frozen catalog of granular consent scopes.

Every scope defaults OFF. Callers must obtain an explicit grant from a
user-owned :class:`~somatic.consent.ledger.ConsentLedger` before acting.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConsentScope:
    """One granular consent capability the user may grant or revoke."""

    id: str
    human_label: str
    description: str
    limits: str


DATA_INGESTION = ConsentScope(
    id="data-ingestion",
    human_label="Data ingestion",
    description="Ingest the user's own local data into Somatic for analysis.",
    limits="Local user-owned data only; no third-party collection or network upload.",
)
ANALYSIS_INSIGHT = ConsentScope(
    id="analysis-insight",
    human_label="Analysis insight",
    description="Compute descriptive insights and evidence-graded summaries on granted data.",
    limits="Informational analysis only; does not authorize diagnosis or treatment.",
)
AI_ADVISORY = ConsentScope(
    id="ai-advisory",
    human_label="AI advisory",
    description="Produce informational, evidence-graded advisory suggestions on granted data.",
    limits="Decision-support framing only; must route to licensed professionals.",
)
AUTONOMOUS_RESEARCH = ConsentScope(
    id="autonomous-research",
    human_label="Autonomous research",
    description="Run research loops against literature and local evidence packs.",
    limits=(
        "Offline fixture corpus by default. Optional live lookup "
        "(SOMATIC_RESEARCH_LIVE) is public literature APIs only, https, "
        "host-allowlisted, never sensor data."
    ),
)
PROACTIVE_SUGGESTIONS = ConsentScope(
    id="proactive-suggestions",
    human_label="Proactive suggestions",
    description="Surface unsolicited informational suggestions based on granted data patterns.",
    limits="Suggestions remain informational; user may dismiss or revoke at any time.",
)
PROFESSIONAL_SHARING = ConsentScope(
    id="professional-sharing",
    human_label="Professional sharing",
    description="Prepare user-selected packets for sharing with a licensed professional.",
    limits="User-initiated export only; no autonomous send or third-party upload.",
)
REMEDY_LIBRARY = ConsentScope(
    id="remedy-library",
    human_label="Remedy library",
    description="Browse and suggest informational remedy/library options with evidence grades.",
    limits="Informational library access only; not a prescription or dosing authority.",
)

CONSENT_SCOPES: tuple[ConsentScope, ...] = (
    DATA_INGESTION,
    ANALYSIS_INSIGHT,
    AI_ADVISORY,
    AUTONOMOUS_RESEARCH,
    PROACTIVE_SUGGESTIONS,
    PROFESSIONAL_SHARING,
    REMEDY_LIBRARY,
)

_SCOPE_BY_ID: dict[str, ConsentScope] = {scope.id: scope for scope in CONSENT_SCOPES}


def get_scope(scope_id: str) -> ConsentScope | None:
    """Return the catalog entry for ``scope_id``, or None if unknown."""

    return _SCOPE_BY_ID.get(str(scope_id))


def resolve_scope(scope: ConsentScope | str) -> ConsentScope:
    """Resolve a scope object or id string to a catalog :class:`ConsentScope`."""

    if isinstance(scope, ConsentScope):
        if scope.id not in _SCOPE_BY_ID:
            raise ValueError(f"unknown consent scope: {scope.id}")
        return _SCOPE_BY_ID[scope.id]
    resolved = _SCOPE_BY_ID.get(str(scope))
    if resolved is None:
        raise ValueError(f"unknown consent scope: {scope}")
    return resolved
