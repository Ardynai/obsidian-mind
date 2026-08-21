# Local Mock Batch Scorer

> 11 nodes · cohesion 0.29

## Key Concepts

- **LocalMockBatchScorer** (16 connections) — `somatic/agents/batch_scorer.py`
- **.compare_pairwise()** (6 connections) — `somatic/agents/batch_scorer.py`
- **._comparison_key()** (3 connections) — `somatic/agents/batch_scorer.py`
- **.score_batch()** (3 connections) — `somatic/agents/batch_scorer.py`
- **._scores_for()** (3 connections) — `somatic/agents/batch_scorer.py`
- **._winner_id()** (3 connections) — `somatic/agents/batch_scorer.py`
- **._debate_notes()** (2 connections) — `somatic/agents/batch_scorer.py`
- **._dimension_winners()** (2 connections) — `somatic/agents/batch_scorer.py`
- **.test_local_mock_batch_scorer_does_not_reward_safety_risk()** (2 connections) — `tests/test_tournament.py`
- **.__init__()** (1 connections) — `somatic/agents/batch_scorer.py`
- **Deterministic local scorer used by the offline fixture tournament.** (1 connections) — `somatic/agents/batch_scorer.py`

## Relationships

- [Hypothesis Tournament Management](Hypothesis_Tournament_Management.md) (3 shared connections)
- [Safety-Aware Item Ranking](Safety-Aware_Item_Ranking.md) (3 shared connections)
- [Batch Scoring Interfaces](Batch_Scoring_Interfaces.md) (2 shared connections)
- [Hypothesis Tournament Validation](Hypothesis_Tournament_Validation.md) (2 shared connections)

## Source Files

- `somatic/agents/batch_scorer.py`
- `tests/test_tournament.py`

## Audit Trail

- EXTRACTED: 33 (79%)
- INFERRED: 9 (21%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*