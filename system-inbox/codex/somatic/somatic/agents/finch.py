from somatic.evidence_bus import StructuredVerdict


def analyze_raw_evidence(raw_evidence):
    records = list(raw_evidence)
    raw_refs = [record.id for record in records]
    modalities = [record.source.modality for record in records]
    modality_counts = {modality: modalities.count(modality) for modality in sorted(set(modalities))}
    mock_signal_values = [
        record.metadata.get("payload", {}).get("mock_signal_mean")
        for record in records
        if record.metadata.get("payload", {}).get("mock_signal_mean") is not None
    ]
    mean_mock_signal = (
        round(sum(mock_signal_values) / len(mock_signal_values), 3) if mock_signal_values else None
    )
    stats = {
        "raw_record_count": len(records),
        "modality_counts": modality_counts,
        "mean_mock_signal": mean_mock_signal,
        "all_records_mock": all(record.metadata.get("mock") is True for record in records),
        "all_records_offline": all(record.metadata.get("offline") is True for record in records),
    }
    interpretation = (
        "The sandbox records are internally consistent with a Robin-shaped loop. "
        "They do not support diagnosis, treatment, lab action, or a real scientific conclusion."
    )
    verdict = StructuredVerdict(
        id="verdict-robin-sandbox-001",
        raw_evidence_refs=raw_refs,
        summary=(
            "Mock offline evidence supports only that the local Crow-Falcon-Sandbox-Finch "
            "artifact loop executed deterministically."
        ),
        confidence="low",
        limitations=[
            "Synthetic sandbox records only.",
            "No external literature search, API call, sensor runtime, biomodel, Fabric, "
            "or real wetlab action.",
            "No medical advice and no real scientific conclusion.",
        ],
        metadata={
            "mock": True,
            "offline": True,
            "research_only": True,
            "not_medical_advice": True,
            "not_real_scientific_conclusion": True,
            "stats": stats,
            "interpretation": interpretation,
        },
    )
    return {
        "schema_version": 1,
        "agent_role": "Finch",
        "mock": True,
        "offline": True,
        "research_only": True,
        "boundary": "mock/offline/research-only",
        "analysis": {
            "stats": stats,
            "interpretation": interpretation,
            "limitations": list(verdict.limitations),
        },
        "structured_verdict": verdict.to_dict(),
    }


def build_structured_verdict_artifact(finch_analysis):
    return {
        "schema_version": 1,
        "agent_role": "Finch",
        "mock": True,
        "offline": True,
        "research_only": True,
        "boundary": "mock/offline/research-only",
        "structured_verdict": dict(finch_analysis["structured_verdict"]),
    }
