from somatic.core.scoring import SCORE_FIELDS, final_score


class BatchScorer:
    """Interface for batch scoring and pairwise comparison providers."""

    scorer_id = "batch-scorer-interface"
    mode = "interface"

    def score_batch(self, candidates):
        raise NotImplementedError("Batch scorers must implement score_batch")

    def compare_pairwise(self, left, right):
        raise NotImplementedError("Batch scorers must implement compare_pairwise")


class LocalMockBatchScorer(BatchScorer):
    """Deterministic local scorer used by the offline fixture tournament."""

    scorer_id = "local-mock-batch-scorer-v1"
    mode = "local-mock"

    def __init__(self, score_lookup=None):
        self.score_lookup = score_lookup or {}

    def score_batch(self, candidates):
        scored = []
        for candidate in candidates:
            scores = self._scores_for(candidate)
            scored.append(
                {
                    "candidate_id": candidate["id"],
                    "reviewer": self.scorer_id,
                    "scores": dict(scores),
                    "final_score": final_score(scores),
                    "scoring_note": (
                        "safety_risk is a risk score where lower is safer; "
                        "it is inverted for final_score."
                    ),
                    "mock": True,
                    "offline": True,
                }
            )
        return scored

    def compare_pairwise(self, left, right):
        left_id = left["id"]
        right_id = right["id"]
        left_scores = self._scores_for(left)
        right_scores = self._scores_for(right)
        left_total = final_score(left_scores)
        right_total = final_score(right_scores)
        winner_id = self._winner_id(left_id, left_scores, right_id, right_scores)
        return {
            "candidate_ids": [left_id, right_id],
            "winner_id": winner_id,
            "aggregate_scores": {
                left_id: left_total,
                right_id: right_total,
            },
            "dimension_scores": {
                left_id: dict(left_scores),
                right_id: dict(right_scores),
            },
            "dimension_winners": self._dimension_winners(
                left_id, left_scores, right_id, right_scores
            ),
            "debate_notes": {
                left_id: self._debate_notes(left_scores, left_total),
                right_id: self._debate_notes(right_scores, right_total),
            },
            "decision_basis": (
                "Deterministic aggregate score with evidence, falsifiability, "
                "feasibility, novelty, lower safety risk, data requirements, "
                "then candidate id as tie breakers."
            ),
            "mock": True,
            "offline": True,
        }

    def _scores_for(self, candidate):
        candidate_id = candidate["id"]
        if candidate_id in self.score_lookup:
            return dict(self.score_lookup[candidate_id])
        if "scores" in candidate:
            return dict(candidate["scores"])
        raise KeyError(f"No mock scores available for {candidate_id}")

    def _winner_id(self, left_id, left_scores, right_id, right_scores):
        left_key = self._comparison_key(left_scores)
        right_key = self._comparison_key(right_scores)
        if left_key > right_key:
            return left_id
        if right_key > left_key:
            return right_id
        return min(left_id, right_id)

    def _comparison_key(self, scores):
        return (
            final_score(scores),
            scores["evidence_alignment"],
            scores["falsifiability"],
            scores["feasibility"],
            scores["novelty"],
            100 - scores["safety_risk"],
            scores["data_requirements"],
        )

    def _dimension_winners(self, left_id, left_scores, right_id, right_scores):
        winners = {}
        for field in SCORE_FIELDS:
            left_value = left_scores[field]
            right_value = right_scores[field]
            if left_value == right_value:
                winners[field] = "tie"
            elif field == "safety_risk":
                winners[field] = left_id if left_value < right_value else right_id
            else:
                winners[field] = left_id if left_value > right_value else right_id
        return winners

    def _debate_notes(self, scores, aggregate_score):
        return {
            "pro": [
                f"Aggregate score {aggregate_score} in the deterministic mock review.",
                (
                    f"Evidence alignment {scores['evidence_alignment']} and "
                    f"falsifiability {scores['falsifiability']} support local review."
                ),
            ],
            "con": [
                f"Safety risk score {scores['safety_risk']} still requires human review.",
                (
                    f"Data requirements score {scores['data_requirements']} limits "
                    "how far the mock conclusion can be taken."
                ),
            ],
        }


class FutureTeamOrchestratorHook:
    """Disabled attachment point for a future Phase 2.5 team orchestrator."""

    hook_id = "phase-2-5-team-orchestrator-hook"
    status = "not-implemented"

    def describe(self):
        return {
            "hook_id": self.hook_id,
            "status": self.status,
            "attachment_point": "after_reflection_before_pairwise_debate",
            "allowed_current_behavior": "describe-only",
            "runtime_enabled": False,
        }
