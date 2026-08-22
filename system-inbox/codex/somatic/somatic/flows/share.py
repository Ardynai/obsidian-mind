"""Consent-gated professional share flow.

Reformats an already safety-framed AnalysisReport into a clinician-facing
Markdown document. Adds no diagnosis, dosing, or new interpretation.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from somatic.consent.ledger import ConsentLedger
from somatic.consent.scopes import PROFESSIONAL_SHARING
from somatic.flows.analyze import AnalysisReport
from somatic.safety.core import (
    INFORMATIONAL_NOTICE,
    PROFESSIONAL_ROUTING,
    AdvisoryResult,
    require_consent,
)

SHARE_TITLE = "Patient-generated informational summary - not a diagnosis"
SAMPLE_SIZE_LEGEND = (
    "Sample-size labels (not GRADE evidence): none = no comparison; "
    "preliminary = 1-2 readings; limited = 3-5; moderate = 6+ with a "
    "signal. Labels describe the user's own series, not literature grade."
)
_REPEATED_DISCLAIMERS = (
    "This is informational only and is not a diagnosis; confirm with a "
    "licensed professional if concerns remain.",
    "This is informational only and may be worth discussing with a licensed professional.",
)


def render_professional_summary(
    ledger: ConsentLedger,
    report: AnalysisReport,
    *,
    patient_label: str = "",
    clinician_note: str = "",
) -> str:
    """Render a clinician-facing Markdown summary behind PROFESSIONAL_SHARING."""

    require_consent(ledger, PROFESSIONAL_SHARING)
    if not isinstance(report, AnalysisReport):
        raise TypeError("report must be an AnalysisReport")

    generated = report.generated_at or _utc_now_iso()
    lines: list[str] = [f"# {SHARE_TITLE}", "", f"Generated (UTC): {generated}", ""]
    label = _safe_markdown_field(patient_label)
    if label:
        lines.append(f"Patient label: {label}")
        lines.append("")
    note = _safe_markdown_field(clinician_note)
    if note:
        lines.append(f"Requesting note: {note}")
        lines.append("")
    lines.append(
        "This document is user-owned, patient-generated informational data for "
        "discussion with a professional."
    )
    lines.append(INFORMATIONAL_NOTICE)
    lines.append("")
    lines.append(PROFESSIONAL_ROUTING)
    lines.append("")
    lines.append(SAMPLE_SIZE_LEGEND)
    lines.append("")

    for index, result in enumerate(report.results, start=1):
        lines.extend(_render_result_block(index, result))
        lines.append("")

    lines.append("## Notes")
    lines.append("")
    if report.notes:
        for item in report.notes:
            lines.append(f"- {_safe_markdown_field(item)}")
    else:
        lines.append("- (none)")
    lines.append("")
    lines.append("## Provenance appendix")
    lines.append("")
    if report.results:
        for index, result in enumerate(report.results, start=1):
            debug_sources = ", ".join(str(source) for source in result.sources) or "(none)"
            lines.append(f"- Finding {index} debug tokens: {debug_sources}")
    else:
        lines.append("- (none)")
    lines.append("")
    return "\n".join(lines)


def render_fhir_bundle(
    ledger: ConsentLedger,
    report: AnalysisReport,
    *,
    patient_label: str = "",
) -> dict[str, Any]:
    """Return a FHIR-shaped JSON sidecar. Not a claim of FHIR R4 conformance."""

    require_consent(ledger, PROFESSIONAL_SHARING)
    if not isinstance(report, AnalysisReport):
        raise TypeError("report must be an AnalysisReport")
    generated = report.generated_at or _utc_now_iso()
    entries: list[dict[str, Any]] = []
    for index, result in enumerate(report.results, start=1):
        entries.append(
            {
                "resource": {
                    "resourceType": "Observation",
                    "status": "preliminary",
                    "code": {"text": f"Finding {index}"},
                    "issued": generated,
                    "note": [{"text": _strip_repeated_disclaimer(result.summary)}],
                    "interpretation": [
                        {
                            "text": (
                                f"sample-size label: {result.evidence_grade} (not GRADE evidence)"
                            )
                        }
                    ],
                }
            }
        )
    return {
        "resourceType": "Bundle",
        "type": "collection",
        "timestamp": generated,
        "entry": entries,
        "somatic": report.to_dict(),
        "patient_label": _safe_markdown_field(patient_label),
        "informational_notice": INFORMATIONAL_NOTICE,
        "professional_routing": PROFESSIONAL_ROUTING,
    }


def _render_result_block(index: int, result: AdvisoryResult) -> list[str]:
    provenance = _human_provenance(result.sources)
    provenance_line = "; ".join(provenance) if provenance else "(see provenance appendix)"
    observed = _observed_dates(result.sources)
    lines = [
        f"## Finding {index}",
        "",
        _safe_markdown_field(_strip_repeated_disclaimer(result.summary)),
        "",
        f"- sample_size_label: {result.evidence_grade} (not GRADE evidence)",
        f"- data_source: {provenance_line}",
    ]
    if observed:
        lines.append(f"- observed: {', '.join(observed)}")
    return lines


def _human_provenance(sources: tuple[str, ...]) -> list[str]:
    human: list[str] = []
    for source in sources:
        text = str(source)
        if text.startswith("reference-source:"):
            human.append(text.split(":", 1)[1])
        elif text.startswith("metric:"):
            human.append(f"metric {text.split(':', 1)[1]}")
    return human


def _observed_dates(sources: tuple[str, ...]) -> list[str]:
    dates: list[str] = []
    for source in sources:
        text = str(source)
        if text.startswith("observed:"):
            dates.append(text.split(":", 1)[1])
    return dates


def _strip_repeated_disclaimer(summary: str) -> str:
    text = str(summary or "")
    for snippet in _REPEATED_DISCLAIMERS:
        text = text.replace(snippet, "")
    return " ".join(text.split())


def _safe_markdown_field(value: object) -> str:
    """Collapse interior newlines and neutralize leading Markdown markers."""

    text = " ".join(str(value or "").split())
    if text[:1] in {"#", "-", "*", ">"}:
        return f"\\{text}"
    return text


def _utc_now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
