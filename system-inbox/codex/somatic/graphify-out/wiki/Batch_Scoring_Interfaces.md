# Batch Scoring Interfaces

> 8 nodes · cohesion 0.25

## Key Concepts

- **BatchScorer** (5 connections) — `somatic/agents/batch_scorer.py`
- **FutureTeamOrchestratorHook** (4 connections) — `somatic/agents/batch_scorer.py`
- **batch_scorer.py** (3 connections) — `somatic/agents/batch_scorer.py`
- **.compare_pairwise()** (1 connections) — `somatic/agents/batch_scorer.py`
- **.score_batch()** (1 connections) — `somatic/agents/batch_scorer.py`
- **.describe()** (1 connections) — `somatic/agents/batch_scorer.py`
- **Disabled attachment point for a future Phase 2.5 team orchestrator.** (1 connections) — `somatic/agents/batch_scorer.py`
- **Interface for batch scoring and pairwise comparison providers.** (1 connections) — `somatic/agents/batch_scorer.py`

## Relationships

- [Local Mock Batch Scorer](Local_Mock_Batch_Scorer.md) (2 shared connections)
- [Hypothesis Tournament Management](Hypothesis_Tournament_Management.md) (1 shared connections)

## Source Files

- `somatic/agents/batch_scorer.py`

## Audit Trail

- EXTRACTED: 16 (94%)
- INFERRED: 1 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*