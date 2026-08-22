from somatic.sensors.csi_batch import build_csi_batch_tournament_readiness
from somatic.sensors.csi_scoring import build_csi_tournament_readiness

TEAM_ROLES = (
    "GeneratorTeam",
    "FalsifierTeam",
    "EvidenceTeam",
    "SafetyTeam",
    "SynthesisTeam",
)

AUTOSCIENTISTS_REFERENCE_HOOK = {
    "provider_id": "autoscientists-reference",
    "adapter_status": "metadata-only",
    "reference_only": True,
    "runtime_enabled": False,
    "runtime_import_allowed": False,
    "license_status": "unresolved-no-license-file-found",
    "reference_location": "external-source-inventory/autoscientists-reference",
    "staged_location_disclosed": False,
    "source_commit": "c71a92343b9a488ed10134be805845b9473ad18f",
}

TEAM_CONFIDENCE = {
    "GeneratorTeam": (0.52, "mock-low-moderate"),
    "FalsifierTeam": (0.6, "mock-moderate"),
    "EvidenceTeam": (0.58, "mock-moderate"),
    "SafetyTeam": (0.66, "mock-moderate"),
    "SynthesisTeam": (0.55, "mock-moderate"),
}

NEXT_TEAM_ACTIONS = {
    "GeneratorTeam": "draft-one-bounded-local-refinement-per-focus-hypothesis",
    "FalsifierTeam": "write-local-null-case-and-contradiction-checks",
    "EvidenceTeam": "prioritize-provenance-complete-fixture-additions",
    "SafetyTeam": "review-language-for-research-only-and-non-clinical-boundaries",
    "SynthesisTeam": "merge-team-notes-into-human-review-brief",
}


def run_team_orchestrator(
    ranked_hypotheses,
    reflection_notes,
    refined_hypotheses,
    pairwise_debates,
    elo_ratings,
    evidence_scoring_metadata=None,
    csi_batch_evaluation_metadata=None,
):
    focus_ids = _focus_hypothesis_ids(ranked_hypotheses, refined_hypotheses)
    roster = _build_team_roster(focus_ids)
    critiques = _build_team_critiques(roster, reflection_notes)
    reorganization_log = _build_reorganization_log(roster)
    evidence_budget = _build_evidence_budget(roster)
    blackboard = _build_blackboard(roster, critiques, reorganization_log, evidence_budget)
    summary = _build_summary(
        roster=roster,
        focus_ids=focus_ids,
        evidence_budget=evidence_budget,
        pairwise_debates=pairwise_debates,
        elo_ratings=elo_ratings,
        evidence_scoring_metadata=evidence_scoring_metadata,
        csi_batch_evaluation_metadata=csi_batch_evaluation_metadata,
    )
    return {
        "team_roster": roster,
        "team_critiques": critiques,
        "shared_blackboard": blackboard,
        "evidence_budget": evidence_budget,
        "reorganization_log": reorganization_log,
        "team_orchestrator_summary": summary,
    }


def _focus_hypothesis_ids(ranked_hypotheses, refined_hypotheses):
    ranked_ids = [item["id"] for item in ranked_hypotheses[:3]]
    if ranked_ids:
        return ranked_ids
    return [item["id"] for item in refined_hypotheses[:3]]


def _build_team_roster(focus_ids):
    team_specs = (
        (
            "team-generator",
            "GeneratorTeam",
            ["Find bounded refinements and alternative mechanisms."],
            ["Request one local counterexample fixture for each top hypothesis."],
            ["novelty-overreach"],
            "propose-bounded-refinements",
        ),
        (
            "team-falsifier",
            "FalsifierTeam",
            ["Identify falsifiable checks before any evidence spend."],
            ["Request local null-case fixtures and contradiction notes."],
            ["weak-falsifiability"],
            "require-falsification-plan",
        ),
        (
            "team-evidence",
            "EvidenceTeam",
            ["Map evidence gaps and prioritize fixture additions."],
            ["Request provenance-complete supporting and opposing evidence records."],
            ["single-record-evidence-base"],
            "budget-local-fixture-review",
        ),
        (
            "team-safety",
            "SafetyTeam",
            ["Keep all outputs mock, offline, research-only, and non-medical."],
            ["Request safety language review before any downstream expansion."],
            ["medical-or-clinical-overclaim"],
            "block-real-world-action",
        ),
        (
            "team-synthesis",
            "SynthesisTeam",
            ["Merge critiques into a conservative next-step plan."],
            ["Request a human-review checklist tied to the ranked shortlist."],
            ["summary-overconfidence"],
            "synthesize-human-review-brief",
        ),
    )
    return {
        "schema_version": 1,
        "mock": True,
        "offline": True,
        "teams": [
            _build_team_record(
                team_id=team_id,
                focus_ids=focus_ids,
                role=role,
                critique_goals=critique_goals,
                evidence_requests=evidence_requests,
                risk_flags=risk_flags,
                decision=decision,
            )
            for (
                team_id,
                role,
                critique_goals,
                evidence_requests,
                risk_flags,
                decision,
            ) in team_specs
        ],
    }


def _build_team_record(
    team_id,
    focus_ids,
    role,
    critique_goals,
    evidence_requests,
    risk_flags,
    decision,
):
    return {
        "team_id": team_id,
        "focus_hypothesis_ids": list(focus_ids),
        "role": role,
        "critique_goals": list(critique_goals),
        "evidence_requests": list(evidence_requests),
        "risk_flags": list(risk_flags),
        "decision": decision,
        "lifecycle_stage": "formed-for-offline-review",
        "confidence_estimate": _confidence_estimate(role),
        "critique_gate": _critique_gate_result(),
        "stall_status": _stall_status(),
        "blackboard_contribution": {
            "contribution_id": f"{team_id}-contribution",
            "event_type": "team_contribution",
            "summary": f"{role} contributed {decision} to the shared mock blackboard.",
        },
        "evidence_spend_decision": _evidence_spend_decision(),
        "reorganization_trigger": _reorganization_trigger(),
        "next_team_action": NEXT_TEAM_ACTIONS[role],
        "future_provider_hook": dict(AUTOSCIENTISTS_REFERENCE_HOOK),
    }


def _build_team_critiques(roster, reflection_notes):
    reflection_count = len(reflection_notes)
    critiques = []
    for team in roster["teams"]:
        critiques.append(
            {
                "team_id": team["team_id"],
                "role": team["role"],
                "focus_hypothesis_ids": list(team["focus_hypothesis_ids"]),
                "critique_before_evidence_spend": True,
                "critique_goals": list(team["critique_goals"]),
                "findings": [
                    f"Reviewed {reflection_count} mock reflection notes before budget planning.",
                    f"Decision: {team['decision']}.",
                ],
                "critique_gate_result": dict(team["critique_gate"]),
                "confidence_estimate": dict(team["confidence_estimate"]),
                "stall_status": dict(team["stall_status"]),
                "next_team_action": team["next_team_action"],
                "risk_flags": list(team["risk_flags"]),
                "mock": True,
                "offline": True,
            }
        )
    return {
        "schema_version": 1,
        "mock": True,
        "offline": True,
        "critiques": critiques,
    }


def _build_reorganization_log(roster):
    trigger = _reorganization_trigger()
    stall_summary = _stall_summary(roster)
    return {
        "schema_version": 1,
        "mock": True,
        "offline": True,
        "events": [
            {
                "event_id": "reorg-001",
                "event_type": "no_reorganization",
                "affected_team_ids": [team["team_id"] for team in roster["teams"]],
                "reason": (
                    "All five scaffold teams have distinct responsibilities and "
                    "share the same top-hypothesis focus set."
                ),
                "decision": "keep-roster-stable",
                "trigger": trigger,
                "stall_summary": stall_summary,
                "reorganization_trigger": trigger,
            }
        ],
    }


def _build_evidence_budget(roster):
    budget_points = {
        "team-generator": 15,
        "team-falsifier": 25,
        "team-evidence": 30,
        "team-safety": 20,
        "team-synthesis": 10,
    }
    allocations = []
    for team in roster["teams"]:
        allocations.append(
            {
                "team_id": team["team_id"],
                "role": team["role"],
                "point_budget": budget_points[team["team_id"]],
                "evidence_requests": list(team["evidence_requests"]),
                "evidence_spend_decision": dict(team["evidence_spend_decision"]),
                "critique_gate_passed": team["critique_gate"]["passed"],
                "spend_status": "planned-not-spent",
            }
        )
    return {
        "schema_version": 1,
        "mock": True,
        "offline": True,
        "currency": "mock-evidence-points",
        "total_points": sum(item["point_budget"] for item in allocations),
        "critique_completed_before_budget": True,
        "external_evidence_spend_allowed": False,
        "allocations": allocations,
    }


def _build_blackboard(roster, critiques, reorganization_log, evidence_budget):
    focus_ids = list(roster["teams"][0]["focus_hypothesis_ids"])
    team_events = [
        {
            "event_id": f"blackboard-{index:03d}",
            "team_id": team["team_id"],
            **team["blackboard_contribution"],
        }
        for index, team in enumerate(roster["teams"], start=2)
    ]
    reorganization_event_id = f"blackboard-{len(team_events) + 2:03d}"
    evidence_budget_event_id = f"blackboard-{len(team_events) + 3:03d}"
    return {
        "schema_version": 1,
        "mock": True,
        "offline": True,
        "state_id": "mock-team-blackboard-v1",
        "focus_hypothesis_ids": focus_ids,
        "events": [
            {
                "event_id": "blackboard-001",
                "event_type": "critique",
                "summary": f"{len(critiques['critiques'])} team critiques recorded.",
            },
            *team_events,
            {
                "event_id": reorganization_event_id,
                "event_type": "reorganization",
                "summary": reorganization_log["events"][0]["decision"],
            },
            {
                "event_id": evidence_budget_event_id,
                "event_type": "evidence_budget",
                "summary": (
                    f"{evidence_budget['total_points']} mock evidence points "
                    "planned after critique."
                ),
            },
        ],
    }


def _build_summary(
    roster,
    focus_ids,
    evidence_budget,
    pairwise_debates,
    elo_ratings,
    evidence_scoring_metadata,
    csi_batch_evaluation_metadata,
):
    return {
        "schema_version": 1,
        "mock": True,
        "offline": True,
        "orchestrator_id": "local-mock-team-orchestrator-v1",
        "orchestrator_status": "scaffold-only",
        "team_count": len(roster["teams"]),
        "focus_hypothesis_ids": list(focus_ids),
        "critique_before_evidence_spend": True,
        "team_lifecycle_stages": {
            team["team_id"]: team["lifecycle_stage"] for team in roster["teams"]
        },
        "confidence_estimates": {
            team["team_id"]: dict(team["confidence_estimate"]) for team in roster["teams"]
        },
        "critique_gate": _critique_gate_result(),
        "stall_summary": _stall_summary(roster),
        "reorganization_trigger": _reorganization_trigger(),
        "next_team_actions": {
            team["team_id"]: team["next_team_action"] for team in roster["teams"]
        },
        "evidence_budget_points": evidence_budget["total_points"],
        "pairwise_matchups_seen": pairwise_debates.get("matchup_count", 0),
        "elo_candidates_seen": len(elo_ratings.get("ratings", [])),
        "csi_evidence_scoring_readiness": _build_csi_readiness(
            evidence_scoring_metadata,
            csi_batch_evaluation_metadata,
        ),
        "future_hook": {
            "hook_id": "phase-5e-autoscientists-team-orchestrator",
            "status": "not-implemented",
            "runtime_enabled": False,
            "allowed_current_behavior": "describe-only",
        },
        "future_provider_hook": dict(AUTOSCIENTISTS_REFERENCE_HOOK),
        "limitations": [
            "Plain deterministic local data structures only.",
            "No live agents, external providers, dependency installs, or network calls.",
        ],
    }


def _build_csi_readiness(evidence_scoring_metadata, csi_batch_evaluation_metadata):
    if csi_batch_evaluation_metadata is not None:
        return build_csi_batch_tournament_readiness(csi_batch_evaluation_metadata)
    return build_csi_tournament_readiness(evidence_scoring_metadata)


def _confidence_estimate(role):
    score, label = TEAM_CONFIDENCE[role]
    return {
        "score": score,
        "label": label,
        "basis": "deterministic role-risk scaffold; not a scientific confidence claim",
        "source": "local-mock-team-orchestrator",
    }


def _critique_gate_result():
    return {
        "gate_id": "critique-before-evidence",
        "required": True,
        "passed": True,
        "result": "passed-before-evidence-budget",
        "reason": "team critiques are emitted before the mock evidence budget artifact",
    }


def _stall_status():
    return {
        "is_stalled": False,
        "reason": "no prior team rotation history in deterministic mock run",
        "rotation_count": 0,
        "supported_keeps": 0,
        "refuted_discards": 0,
    }


def _stall_summary(roster):
    return {
        "stalled_team_ids": [
            team["team_id"] for team in roster["teams"] if team["stall_status"]["is_stalled"]
        ],
        "reason": "no-stall-detected",
        "stagnation_policy": "future adapters may reorganize only after explicit stall evidence",
    }


def _evidence_spend_decision():
    return {
        "decision": "allow-mock-budget-only",
        "reason": "critique gate passed, but external evidence spend remains disabled",
        "external_spend_allowed": False,
    }


def _reorganization_trigger():
    return {
        "triggered": False,
        "reason": "no-stall-detected",
        "source": "deterministic-local-scaffold",
    }
