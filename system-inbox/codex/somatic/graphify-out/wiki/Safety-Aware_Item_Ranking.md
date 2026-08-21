# Safety-Aware Item Ranking

> 5 nodes · cohesion 0.80

## Key Concepts

- **final_score()** (8 connections) — `somatic/core/scoring.py`
- **rank_scored_items()** (5 connections) — `somatic/core/scoring.py`
- **_normalized_scores()** (3 connections) — `somatic/core/scoring.py`
- **scoring.py** (3 connections) — `somatic/core/scoring.py`
- **.test_final_score_penalizes_safety_risk_and_ranks_descending()** (3 connections) — `tests/test_tournament.py`

## Relationships

- [Local Mock Batch Scorer](Local_Mock_Batch_Scorer.md) (3 shared connections)
- [Hypothesis Tournament Management](Hypothesis_Tournament_Management.md) (2 shared connections)
- [Hypothesis Tournament Validation](Hypothesis_Tournament_Validation.md) (1 shared connections)

## Source Files

- `somatic/core/scoring.py`
- `tests/test_tournament.py`

## Audit Trail

- EXTRACTED: 13 (59%)
- INFERRED: 9 (41%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*