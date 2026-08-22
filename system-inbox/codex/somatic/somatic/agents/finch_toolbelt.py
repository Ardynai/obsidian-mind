from pathlib import Path

from somatic.analysis.dose_response import summarize_dose_response
from somatic.analysis.provenance import build_analysis_provenance
from somatic.analysis.provider import FinchExtrasProvider
from somatic.analysis.tables import profile_csv_table, read_csv_table


def analyze_robin_tables(raw_records, repo_root):
    """Analyze local CSV fixture references embedded in sandbox raw evidence."""
    table_refs = _collect_table_refs(raw_records)
    profiles = []
    source_files = []
    dose_summary = summarize_dose_response([], dose_column="dose", response_column="response")

    for table_ref in table_refs:
        path = Path(repo_root) / table_ref["relative_path"]
        source_files.append(path)
        profile = profile_csv_table(path)
        profile["relative_path"] = table_ref["relative_path"]
        profile["raw_evidence_ref"] = table_ref["raw_evidence_ref"]
        profile["role"] = table_ref["role"]
        profiles.append(profile)
        if table_ref["role"] == "dose-response" and not dose_summary["points"]:
            dose_summary = summarize_dose_response(
                read_csv_table(path),
                dose_column="dose",
                response_column="response",
            )
            dose_summary["source_file"] = path.name
            dose_summary["relative_path"] = table_ref["relative_path"]
            dose_summary["raw_evidence_ref"] = table_ref["raw_evidence_ref"]

    table_profile = {
        "schema_version": 1,
        "agent_role": "Finch",
        "mock": True,
        "offline": True,
        "research_only": True,
        "boundary": "mock/offline/research-only",
        "table_count": len(profiles),
        "tables": profiles,
    }
    toolbelt_summary = {
        "schema_version": 1,
        "agent_role": "Finch",
        "mock": True,
        "offline": True,
        "research_only": True,
        "boundary": "mock/offline/research-only",
        "toolbelt_status": "standard-library-local",
        "table_count": len(profiles),
        "numeric_table_count": sum(1 for profile in profiles if profile["numeric_columns"]),
        "dose_response_available": bool(dose_summary["points"]),
        "effect_direction": dose_summary["effect_direction"],
        "evidence_quality_score": dose_summary["evidence_quality_score"],
        "capabilities": [
            "csv_parsing",
            "table_profile",
            "missing_value_counts",
            "numeric_descriptive_stats",
            "dose_response_summary",
            "artifact_hashing",
        ],
        "limitations": [
            "Standard-library local analysis only.",
            "No pandas, scipy, numpy, scanpy, biopython, external APIs, or network calls.",
            "Outputs are deterministic research artifacts, not clinical or scientific conclusions.",
        ],
        "optional_extras": FinchExtrasProvider().status(),
    }
    provenance = build_analysis_provenance(
        source_files=source_files,
        artifacts={
            "finch_toolbelt_summary": toolbelt_summary,
            "table_profile": table_profile,
            "dose_response_summary": dose_summary,
        },
    )
    return {
        "finch_toolbelt_summary": toolbelt_summary,
        "table_profile": table_profile,
        "dose_response_summary": dose_summary,
        "analysis_provenance": provenance,
    }


def _collect_table_refs(raw_records):
    refs = []
    seen = set()
    for record in raw_records:
        payload = record.metadata.get("payload", {})
        for item in payload.get("table_refs", []):
            relative_path = item["path"]
            key = (record.id, relative_path)
            if key in seen:
                continue
            seen.add(key)
            refs.append(
                {
                    "raw_evidence_ref": record.id,
                    "relative_path": relative_path,
                    "role": item.get("role", "table"),
                }
            )
    return refs
