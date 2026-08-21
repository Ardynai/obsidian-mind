# Hypothesis Tournament Management

> 16 nodes · cohesion 0.23

## Key Concepts

- **tournament.py** (15 connections) — `somatic/agents/tournament.py`
- **run_hypothesis_tournament()** (14 connections) — `somatic/agents/tournament.py`
- **build_tournament_bracket()** (5 connections) — `somatic/agents/tournament.py`
- **rank_final_hypotheses()** (4 connections) — `somatic/agents/tournament.py`
- **refine_top_candidates()** (4 connections) — `somatic/agents/tournament.py`
- **_apply_refinement_delta()** (3 connections) — `somatic/agents/tournament.py`
- **calculate_elo_ratings()** (3 connections) — `somatic/agents/tournament.py`
- **generate_pairwise_debates()** (3 connections) — `somatic/agents/tournament.py`
- **score_candidates()** (3 connections) — `somatic/agents/tournament.py`
- **_bye()** (2 connections) — `somatic/agents/tournament.py`
- **_elo_expected()** (2 connections) — `somatic/agents/tournament.py`
- **generate_candidate_hypotheses()** (2 connections) — `somatic/agents/tournament.py`
- **_match()** (2 connections) — `somatic/agents/tournament.py`
- **_rankable_hypothesis()** (2 connections) — `somatic/agents/tournament.py`
- **reflect_on_candidates()** (2 connections) — `somatic/agents/tournament.py`
- **.test_bracket_rejects_unsupported_candidate_counts()** (2 connections) — `tests/test_tournament.py`

## Relationships

- [Local Mock Batch Scorer](Local_Mock_Batch_Scorer.md) (3 shared connections)
- [Hypothesis Tournament Validation](Hypothesis_Tournament_Validation.md) (2 shared connections)
- [Workflow Evidence Analysis](Workflow_Evidence_Analysis.md) (2 shared connections)
- [Safety-Aware Item Ranking](Safety-Aware_Item_Ranking.md) (2 shared connections)
- [Batch Scoring Interfaces](Batch_Scoring_Interfaces.md) (1 shared connections)
- [Blackboard Build Logic](Blackboard_Build_Logic.md) (1 shared connections)
- [Consent Ledger Management](Consent_Ledger_Management.md) (1 shared connections)

## Source Files

- `somatic/agents/tournament.py`
- `tests/test_tournament.py`

## Audit Trail

- EXTRACTED: 57 (84%)
- INFERRED: 11 (16%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*