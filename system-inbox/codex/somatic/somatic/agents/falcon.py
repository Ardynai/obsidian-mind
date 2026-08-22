from somatic.evidence_bus import EvidenceSource, MeasurementPlan


def build_measurement_plan(hypothesis, literature_context):
    sources = [
        EvidenceSource(
            id="src-robin-literature",
            modality="literature",
            provider_ref="sandbox",
            description="Fixture-backed literature context source.",
            metadata={"mock": True, "offline": True},
        ),
        EvidenceSource(
            id="src-robin-sim",
            modality="sim",
            provider_ref="sandbox",
            description="Fixture-backed simulation measurement source.",
            metadata={"mock": True, "offline": True},
        ),
        EvidenceSource(
            id="src-robin-wetlab",
            modality="wetlab",
            provider_ref="sandbox",
            description="Fixture-backed wetlab-shaped placeholder source.",
            metadata={"mock": True, "offline": True, "real_lab_action": False},
        ),
    ]
    return MeasurementPlan(
        id="plan-robin-sandbox-001",
        sources=sources,
        objective=f"Check whether local sandbox evidence can exercise: {hypothesis}",
        safety_profile="mock/offline/research-only",
        metadata={
            "mock": True,
            "offline": True,
            "agent_role": "Falcon",
            "literature_context_refs": [record["id"] for record in literature_context["records"]],
            "external_actions_allowed": False,
            "real_lab_action_requires_approval": True,
        },
    )


def build_measurement_plan_artifact(measurement_plan, hypothesis, literature_context):
    return {
        "schema_version": 1,
        "agent_role": "Falcon",
        "mock": True,
        "offline": True,
        "research_only": True,
        "boundary": "mock/offline/research-only",
        "hypothesis": hypothesis,
        "literature_context_refs": [record["id"] for record in literature_context["records"]],
        "measurement_plan": measurement_plan.to_dict(),
        "summary": (
            "Falcon planned deterministic sandbox acquisition for literature, sim, "
            "and wetlab-shaped mock records only."
        ),
    }
