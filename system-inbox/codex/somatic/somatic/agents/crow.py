def build_literature_context(workflow_goal, evidence_requirements):
    accepted_types = list(evidence_requirements.get("accepted_source_types", []))
    return {
        "schema_version": 1,
        "agent_role": "Crow",
        "mock": True,
        "offline": True,
        "research_only": True,
        "boundary": "mock/offline/research-only",
        "workflow_goal": workflow_goal,
        "evidence_requirements": {
            "min_records": evidence_requirements.get("min_records"),
            "accepted_source_types": accepted_types,
            "citation_required": evidence_requirements.get("citation_required"),
            "provenance_required": evidence_requirements.get("provenance_required"),
            "limitations_required": evidence_requirements.get("limitations_required"),
            "counterevidence_required": evidence_requirements.get("counterevidence_required"),
        },
        "records": [
            {
                "id": "crow-context-001",
                "source_type": "paper",
                "title": "Mock provenance boundary note",
                "citation": "mock-literature://crow/context/001",
                "summary": "Offline context says any evidence claim must stay fixture-bound.",
                "limitations": ["Synthetic record; not a literature search result."],
                "supports_measurement_planning": True,
            },
            {
                "id": "crow-context-002",
                "source_type": "dataset",
                "title": "Mock sandbox evidence requirement note",
                "citation": "mock-literature://crow/context/002",
                "summary": "Context requires literature, simulation, and wetlab-shaped "
                "fixture records.",
                "limitations": ["Synthetic record; not an empirical dataset."],
                "supports_measurement_planning": True,
            },
        ],
        "summary": (
            "Crow produced deterministic fixture context for planning only. "
            "It is not a real literature review or scientific conclusion."
        ),
    }
