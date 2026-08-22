from itertools import combinations

from somatic.agents.batch_scorer import FutureTeamOrchestratorHook, LocalMockBatchScorer
from somatic.agents.team_orchestrator import run_team_orchestrator
from somatic.core.scoring import SCORE_FIELDS, final_score, rank_scored_items

BASE_SCORES = {
    "hyp-tournament-001": {
        "evidence_alignment": 82,
        "novelty": 64,
        "feasibility": 78,
        "falsifiability": 84,
        "safety_risk": 12,
        "data_requirements": 76,
    },
    "hyp-tournament-002": {
        "evidence_alignment": 68,
        "novelty": 82,
        "feasibility": 61,
        "falsifiability": 73,
        "safety_risk": 22,
        "data_requirements": 58,
    },
    "hyp-tournament-003": {
        "evidence_alignment": 76,
        "novelty": 70,
        "feasibility": 72,
        "falsifiability": 80,
        "safety_risk": 18,
        "data_requirements": 68,
    },
    "hyp-tournament-004": {
        "evidence_alignment": 60,
        "novelty": 88,
        "feasibility": 52,
        "falsifiability": 69,
        "safety_risk": 26,
        "data_requirements": 50,
    },
    "hyp-tournament-005": {
        "evidence_alignment": 84,
        "novelty": 58,
        "feasibility": 82,
        "falsifiability": 77,
        "safety_risk": 10,
        "data_requirements": 80,
    },
}

REFINEMENT_DELTA = {
    "evidence_alignment": 3,
    "novelty": -2,
    "feasibility": 3,
    "falsifiability": 4,
    "safety_risk": -2,
    "data_requirements": 3,
}


def run_hypothesis_tournament(
    workflow,
    evidence,
    evidence_scoring_metadata=None,
    csi_batch_evaluation_metadata=None,
):
    scorer = LocalMockBatchScorer(score_lookup=BASE_SCORES)
    candidates = generate_candidate_hypotheses(workflow, evidence)
    reflections = reflect_on_candidates(candidates)
    review_scores = score_candidates(candidates, scorer=scorer)
    bracket = build_tournament_bracket(review_scores)
    refined = refine_top_candidates(candidates, reflections, review_scores)
    team_orchestrator = run_team_orchestrator(
        ranked_hypotheses=refined,
        reflection_notes=reflections,
        refined_hypotheses=refined,
        pairwise_debates={"matchup_count": 0, "matchups": []},
        elo_ratings={"ratings": []},
        evidence_scoring_metadata=evidence_scoring_metadata,
        csi_batch_evaluation_metadata=csi_batch_evaluation_metadata,
    )
    pairwise_debates = generate_pairwise_debates(candidates, review_scores, scorer)
    elo_ratings = calculate_elo_ratings(pairwise_debates, review_scores)
    ranked = rank_final_hypotheses(candidates, review_scores, refined, elo_ratings)
    return {
        "candidate_hypotheses": candidates,
        "reflection_notes": reflections,
        "review_scores": review_scores,
        "pairwise_debates": pairwise_debates,
        "elo_ratings": elo_ratings,
        "tournament_bracket": bracket,
        "refined_hypotheses": refined,
        "ranked_hypotheses": ranked,
        "team_orchestrator": team_orchestrator,
        "orchestration_hook": FutureTeamOrchestratorHook().describe(),
    }


def generate_candidate_hypotheses(workflow, evidence):
    evidence_id = evidence.get("id")
    workflow_id = workflow.get("id")
    return [
        {
            "id": "hyp-tournament-001",
            "statement": "Replayable provenance checks can improve trust in offline "
            "research summaries.",
            "rationale": "The fixture evidence already carries provenance, hashes, and "
            "review state.",
            "supporting_evidence_refs": [evidence_id],
            "assumptions": [
                "Evidence records remain locally available.",
                "Human reviewers inspect generated summaries before reuse.",
            ],
            "limitations": ["Validated only against a synthetic fixture record."],
            "workflow_ref": workflow_id,
            "mock": True,
            "offline": True,
        },
        {
            "id": "hyp-tournament-002",
            "statement": "Counterevidence prompts can reduce overconfident conclusions in "
            "mock reports.",
            "rationale": "The workflow contract requires limitations and counterevidence sections.",
            "supporting_evidence_refs": [evidence_id],
            "assumptions": [
                "Report consumers read limitations before acting on recommendations.",
                "Future fixtures include contradictory records.",
            ],
            "limitations": ["No contradictory fixture corpus is present in this phase."],
            "workflow_ref": workflow_id,
            "mock": True,
            "offline": True,
        },
        {
            "id": "hyp-tournament-003",
            "statement": "A structured review pass can expose data gaps before provider "
            "integration.",
            "rationale": "Local scoring can separate evidence fit from feasibility and data needs.",
            "supporting_evidence_refs": [evidence_id],
            "assumptions": [
                "Mock criteria approximate the review dimensions needed by later providers.",
                "Scores are treated as ordering hints rather than conclusions.",
            ],
            "limitations": ["Criteria weights are deterministic placeholders."],
            "workflow_ref": workflow_id,
            "mock": True,
            "offline": True,
        },
        {
            "id": "hyp-tournament-004",
            "statement": "Novel hypothesis mutations may reveal research paths missed by "
            "fixed templates.",
            "rationale": "A mutation round can preserve provenance while exploring "
            "alternate framing.",
            "supporting_evidence_refs": [evidence_id],
            "assumptions": [
                "Mutation remains bounded by safety and evidence constraints.",
                "Human reviewers reject speculative claims that outrun available evidence.",
            ],
            "limitations": ["The mock mutation does not use a real ideation model."],
            "workflow_ref": workflow_id,
            "mock": True,
            "offline": True,
        },
        {
            "id": "hyp-tournament-005",
            "statement": "Safety-gated artifact manifests can make mock research runs "
            "easier to audit.",
            "rationale": "The Phase 1B run layout already records safety responses and "
            "artifact hashes.",
            "supporting_evidence_refs": [evidence_id],
            "assumptions": [
                "Auditors can inspect manifests without provider credentials.",
                "No automated real-world action is attached to the report.",
            ],
            "limitations": ["Audit usefulness is limited by the small fixture set."],
            "workflow_ref": workflow_id,
            "mock": True,
            "offline": True,
        },
    ]


def reflect_on_candidates(candidates):
    notes_by_id = {
        "hyp-tournament-001": {
            "strengths": [
                "Strong evidence provenance fit.",
                "Straightforward local validation path.",
            ],
            "concerns": ["Limited novelty because it extends the existing run layout."],
            "suggested_refinement": "Add explicit counterevidence and reviewer checkpoints.",
        },
        "hyp-tournament-002": {
            "strengths": ["Targets a real report-quality failure mode."],
            "concerns": ["Needs a richer corpus before claims can be evaluated."],
            "suggested_refinement": "Define fixtures with supporting and contradictory records.",
        },
        "hyp-tournament-003": {
            "strengths": [
                "Separates data gaps from hypothesis merit.",
                "Useful before external providers exist.",
            ],
            "concerns": ["Placeholder weights could bias shortlist order."],
            "suggested_refinement": "Record why each score was assigned.",
        },
        "hyp-tournament-004": {
            "strengths": ["Highest novelty among the mock pool."],
            "concerns": ["More speculative and harder to validate with current fixtures."],
            "suggested_refinement": "Constrain mutations to fixture-backed claims.",
        },
        "hyp-tournament-005": {
            "strengths": [
                "Low safety risk and strong auditability.",
                "Aligns with current manifest outputs.",
            ],
            "concerns": ["Primarily infrastructure-focused rather than scientific."],
            "suggested_refinement": "Tie audit checks to a falsifiable follow-up task.",
        },
    }
    return [
        {
            "candidate_id": candidate["id"],
            "reviewer": "mock-reflection-panel-v1",
            "mock": True,
            **notes_by_id[candidate["id"]],
        }
        for candidate in candidates
    ]


def score_candidates(candidates, scorer=None):
    active_scorer = scorer or LocalMockBatchScorer(score_lookup=BASE_SCORES)
    return active_scorer.score_batch(candidates)


def generate_pairwise_debates(candidates, review_scores, scorer=None):
    active_scorer = scorer or LocalMockBatchScorer(score_lookup=BASE_SCORES)
    scores_by_id = {item["candidate_id"]: item["scores"] for item in review_scores}
    candidates_by_id = {candidate["id"]: candidate for candidate in candidates}
    matchups = []
    for index, (left_id, right_id) in enumerate(combinations(sorted(candidates_by_id), 2), start=1):
        left = dict(candidates_by_id[left_id], scores=scores_by_id[left_id])
        right = dict(candidates_by_id[right_id], scores=scores_by_id[right_id])
        comparison = active_scorer.compare_pairwise(left, right)
        comparison["matchup_id"] = f"pairwise-{index:03d}"
        matchups.append(comparison)

    return {
        "schema_version": 1,
        "mock": True,
        "offline": True,
        "scorer_id": active_scorer.scorer_id,
        "matchup_count": len(matchups),
        "matchups": matchups,
    }


def calculate_elo_ratings(pairwise_debates, review_scores, base_rating=1500, k_factor=32):
    aggregate_scores = {item["candidate_id"]: item["final_score"] for item in review_scores}
    candidate_ids = sorted(aggregate_scores)
    ratings = {candidate_id: float(base_rating) for candidate_id in candidate_ids}
    records = {
        candidate_id: {"wins": 0, "losses": 0, "matches": 0} for candidate_id in candidate_ids
    }
    update_log = []

    for matchup in pairwise_debates["matchups"]:
        left_id, right_id = matchup["candidate_ids"]
        winner_id = matchup["winner_id"]
        left_before = ratings[left_id]
        right_before = ratings[right_id]
        left_expected = _elo_expected(left_before, right_before)
        right_expected = _elo_expected(right_before, left_before)
        left_result = 1.0 if winner_id == left_id else 0.0
        right_result = 1.0 if winner_id == right_id else 0.0

        ratings[left_id] = left_before + k_factor * (left_result - left_expected)
        ratings[right_id] = right_before + k_factor * (right_result - right_expected)
        for candidate_id, result in ((left_id, left_result), (right_id, right_result)):
            records[candidate_id]["matches"] += 1
            if result == 1.0:
                records[candidate_id]["wins"] += 1
            else:
                records[candidate_id]["losses"] += 1

        update_log.append(
            {
                "matchup_id": matchup["matchup_id"],
                "candidate_ids": [left_id, right_id],
                "winner_id": winner_id,
                "before": {
                    left_id: round(left_before, 2),
                    right_id: round(right_before, 2),
                },
                "expected": {
                    left_id: round(left_expected, 4),
                    right_id: round(right_expected, 4),
                },
                "after": {
                    left_id: round(ratings[left_id], 2),
                    right_id: round(ratings[right_id], 2),
                },
            }
        )

    table = []
    for candidate_id in candidate_ids:
        record = records[candidate_id]
        table.append(
            {
                "candidate_id": candidate_id,
                "rating": round(ratings[candidate_id], 2),
                "aggregate_score": aggregate_scores[candidate_id],
                "matches": record["matches"],
                "wins": record["wins"],
                "losses": record["losses"],
            }
        )
    table.sort(key=lambda item: (-item["rating"], -item["aggregate_score"], item["candidate_id"]))
    for index, item in enumerate(table, start=1):
        item["rank"] = index

    return {
        "schema_version": 1,
        "mock": True,
        "offline": True,
        "base_rating": base_rating,
        "k_factor": k_factor,
        "ratings": table,
        "updates": update_log,
    }


def build_tournament_bracket(review_scores):
    if len(review_scores) != 5:
        raise ValueError("Mock tournament bracket requires exactly 5 candidates")
    seeded = sorted(review_scores, key=lambda item: (-item["final_score"], item["candidate_id"]))
    seed_ids = [item["candidate_id"] for item in seeded]

    round_one_matches = [
        _match("r1-m1", seed_ids[0], seed_ids[4], review_scores),
        _match("r1-m2", seed_ids[1], seed_ids[3], review_scores),
        _bye("r1-bye", seed_ids[2]),
    ]
    round_one_winners = [match["winner_id"] for match in round_one_matches]

    round_two_matches = [
        _match("r2-m1", round_one_winners[0], round_one_winners[1], review_scores),
        _bye("r2-bye", round_one_winners[2]),
    ]
    round_two_winners = [match["winner_id"] for match in round_two_matches]

    final_match = _match("r3-final", round_two_winners[0], round_two_winners[1], review_scores)
    return {
        "schema_version": 1,
        "mock": True,
        "offline": True,
        "seeding": [
            {
                "seed": index,
                "candidate_id": item["candidate_id"],
                "final_score": item["final_score"],
            }
            for index, item in enumerate(seeded, start=1)
        ],
        "rounds": [
            {"id": "round-1", "name": "Seeded review", "matches": round_one_matches},
            {"id": "round-2", "name": "Shortlist review", "matches": round_two_matches},
            {"id": "round-3", "name": "Bracket final", "matches": [final_match]},
        ],
        "winner_id": final_match["winner_id"],
        "shortlist_ids": seed_ids[:3],
        "selection_rule": "Higher deterministic final_score advances; ties sort by candidate id.",
    }


def refine_top_candidates(candidates, reflections, review_scores, count=3):
    candidates_by_id = {candidate["id"]: candidate for candidate in candidates}
    reflections_by_id = {note["candidate_id"]: note for note in reflections}
    top_scores = sorted(
        review_scores, key=lambda item: (-item["final_score"], item["candidate_id"])
    )[:count]
    refined = []
    for score in top_scores:
        parent = candidates_by_id[score["candidate_id"]]
        refined_scores = _apply_refinement_delta(score["scores"])
        refined.append(
            {
                "id": f"{parent['id']}-r1",
                "parent_id": parent["id"],
                "mutation_round": 1,
                "statement": (
                    f"{parent['statement']} The first follow-up should be a local, "
                    "human-reviewed falsification check before any provider integration."
                ),
                "rationale": (
                    f"Refined from mock reflection: "
                    f"{reflections_by_id[parent['id']]['suggested_refinement']}"
                ),
                "supporting_evidence_refs": list(parent["supporting_evidence_refs"]),
                "assumptions": parent["assumptions"]
                + ["The refinement remains mock/offline and research-only."],
                "limitations": parent["limitations"]
                + ["The mutation is deterministic and not generated by a real model."],
                "scores": refined_scores,
                "final_score": final_score(refined_scores),
                "mock": True,
                "offline": True,
            }
        )
    return refined


def rank_final_hypotheses(candidates, review_scores, refined_hypotheses, elo_ratings=None):
    refined_parent_ids = {item["parent_id"] for item in refined_hypotheses}
    candidate_by_id = {candidate["id"]: candidate for candidate in candidates}
    final_items = []
    for refined in refined_hypotheses:
        final_items.append(_rankable_hypothesis(refined, refined["scores"], source="refined"))
    for score in review_scores:
        if score["candidate_id"] in refined_parent_ids:
            continue
        candidate = candidate_by_id[score["candidate_id"]]
        final_items.append(_rankable_hypothesis(candidate, score["scores"], source="original"))

    ranked = rank_scored_items(final_items)
    elo_by_id = {item["candidate_id"]: item for item in (elo_ratings or {}).get("ratings", [])}
    for item in ranked:
        source_candidate_id = item.get("parent_id") or item["id"]
        elo = elo_by_id.get(source_candidate_id, {})
        item["aggregate_score"] = item["final_score"]
        item["elo_rating"] = elo.get("rating")
        item["elo_rank"] = elo.get("rank")
        item["scoring_note"] = (
            "Aggregate score is computed from this hypothesis scores; Elo is computed "
            "on the parent/original candidate when refined hypotheses inherit parent Elo."
        )
    return ranked


def _rankable_hypothesis(hypothesis, scores, source):
    return {
        "id": hypothesis["id"],
        "parent_id": hypothesis.get("parent_id"),
        "source": source,
        "statement": hypothesis["statement"],
        "rationale": hypothesis["rationale"],
        "supporting_evidence_refs": list(hypothesis["supporting_evidence_refs"]),
        "assumptions": list(hypothesis["assumptions"]),
        "limitations": list(hypothesis["limitations"]),
        "scores": dict(scores),
        "mock": True,
        "offline": True,
    }


def _apply_refinement_delta(scores):
    refined = {}
    for field in SCORE_FIELDS:
        value = scores[field]
        refined[field] = min(100, max(0, value + REFINEMENT_DELTA[field]))
    return refined


def _match(match_id, candidate_a, candidate_b, review_scores):
    scores = {item["candidate_id"]: item["final_score"] for item in review_scores}
    winner = min((candidate_a, candidate_b), key=lambda item: (-scores[item], item))
    return {
        "match_id": match_id,
        "candidate_ids": [candidate_a, candidate_b],
        "winner_id": winner,
        "scores": {
            candidate_a: scores[candidate_a],
            candidate_b: scores[candidate_b],
        },
        "basis": "higher deterministic final_score",
    }


def _bye(match_id, candidate_id):
    return {
        "match_id": match_id,
        "candidate_ids": [candidate_id],
        "winner_id": candidate_id,
        "basis": "single-candidate bye",
    }


def _elo_expected(candidate_rating, opponent_rating):
    return 1 / (1 + 10 ** ((opponent_rating - candidate_rating) / 400))
