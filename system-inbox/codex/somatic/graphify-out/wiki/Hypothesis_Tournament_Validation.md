# Hypothesis Tournament Validation

> 13 nodes · cohesion 0.24

## Key Concepts

- **HypothesisTournamentTests** (16 connections) — `tests/test_tournament.py`
- **._assert_csi_readiness_is_sanitized()** (5 connections) — `tests/test_tournament.py`
- **.test_tournament_run_writes_ranked_artifacts_and_report_boundaries()** (4 connections) — `tests/test_tournament.py`
- **._assert_environment_readiness_is_sanitized()** (3 connections) — `tests/test_tournament.py`
- **._assert_no_absolute_paths()** (3 connections) — `tests/test_tournament.py`
- **._assert_no_forbidden_csi_readiness_keys()** (2 connections) — `tests/test_tournament.py`
- **._assert_no_forbidden_csi_readiness_words()** (2 connections) — `tests/test_tournament.py`
- **._assert_no_tournament_report_leaks()** (2 connections) — `tests/test_tournament.py`
- **.test_refinement_delta_ignores_unknown_score_fields()** (2 connections) — `tests/test_tournament.py`
- **.test_elo_ratings_are_deterministic_across_runs()** (1 connections) — `tests/test_tournament.py`
- **.test_fixture_loads_as_hypothesis_tournament()** (1 connections) — `tests/test_tournament.py`
- **.test_no_network_or_external_api_surfaces_in_tournament_runtime()** (1 connections) — `tests/test_tournament.py`
- **test_tournament.py** (1 connections) — `tests/test_tournament.py`

## Relationships

- [Local Mock Batch Scorer](Local_Mock_Batch_Scorer.md) (2 shared connections)
- [Hypothesis Tournament Management](Hypothesis_Tournament_Management.md) (2 shared connections)
- [Safety-Aware Item Ranking](Safety-Aware_Item_Ranking.md) (1 shared connections)

## Source Files

- `tests/test_tournament.py`

## Audit Trail

- EXTRACTED: 41 (95%)
- INFERRED: 2 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*