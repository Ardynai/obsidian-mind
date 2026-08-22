# Hypothesis Tournament

Phase 2 adds the first deterministic Co-Scientist-style mock tournament. It runs entirely from local fixtures with Python standard-library code.

Run:

```powershell
python -m somatic run fixtures/workflows/valid-hypothesis-tournament.yaml
```

## Boundary

The Phase 2 tournament is mock/offline and research-only. It does not call external APIs, use provider secrets, run Fabric, execute biomodels, capture WiFi CSI or sensor data, use LangGraph, or perform lab or clinical actions. The output is not medical advice and is not a real scientific conclusion.

## Flow

1. Load and validate the `hypothesis-tournament` workflow fixture.
2. Generate a fixed pool of mock candidate hypotheses.
3. Run a deterministic reflection pass.
4. Score candidates across evidence alignment, novelty, feasibility, falsifiability, safety risk, and data requirements.
5. Generate deterministic pairwise debate notes and matchup winners.
6. Update an Elo-style rating table from pairwise results.
7. Build a ranked shortlist and bracket artifact.
8. Refine the top candidates once.
9. Run the deterministic TeamOrchestrator scaffold over the ranked shortlist.
10. Produce final ranked hypotheses and mirror them to the legacy `artifacts/hypotheses.json` path.

## Scoring

Scores are integers from 0 to 100. Higher is better for evidence alignment, novelty, feasibility, falsifiability, and data requirements. `safety_risk` is a risk score where lower is safer, so it is inverted when computing `final_score`.

The default deterministic weights live in `somatic/core/scoring.py`. The mock candidate pool and review notes live in `somatic/agents/tournament.py`.

Phase 8E does not add CSI as a core tournament scoring dimension. The
TeamOrchestrator summary includes
`csi_evidence_scoring_readiness`, a metadata-only readiness object for future
tournament-style consumers that may receive sanitized CSI replay scoring
metadata. It records that `evidence_quality` and `replay_integrity` are accepted
sanitized metadata fields, but they are not ranking inputs and do not modify
`SCORE_FIELDS`, final scores, Elo ratings, bracket selection, or ranked
hypotheses.

Phase 8F extends that readiness object for configured local CSI fixture groups.
The mock runtime finds optional `kind: csi-replay-evaluation-groups` inputs in
the workflow fixture, evaluates each group through
`SandboxSensorProvider.replay_csi_fixtures(...)`, and embeds sanitized batch
metadata under the same `csi_evidence_scoring_readiness` key. The batch fields
include `csi_batch_evaluation_contract_version`, `group_count`,
`evaluated_group_count`, `rejected_group_count`, `aggregate_evidence_quality`,
`aggregate_replay_integrity`, scorer/contract identifiers, and sanitized
per-group status/score summaries. It does not export fixture refs or fixture
filenames, and over-limit group/ref inputs fail closed with rejected metadata.

CSI batch readiness uses sanitized metadata only and fails closed with the
minimum group score when any group rejects. The informational
`average_group_score` is not a ranking input. Phase 8F still does not change
`SCORE_FIELDS`, final scores, pairwise winners, Elo ratings, bracket selection,
winner selection, or final rankings.

Phase 8G adds `artifacts/csi_evidence_pack.json` for CSI-configured tournament
runs. The pack is deterministic portable JSON over sanitized batch readiness
metadata only: contract versions, group/status counts, aggregate
`evidence_quality` and `replay_integrity`, fail-closed readiness status,
sanitized diagnostic counts/categories, and a stable SHA-256 fingerprint.
`team_orchestrator_summary.json` links only the pack ref/fingerprint under
`csi_evidence_pack`. The pack does not export fixture refs, fixture filenames,
source IDs, absolute paths, unsafe refs, raw CSI arrays, provider payload
bodies, parser reports, parser summaries, or signal values. It remains
readiness metadata only and does not modify `SCORE_FIELDS`, candidate scoring,
Elo ratings, bracket selection, winner selection, or rankings.

Phase 9C adds `artifacts/environment_evidence_pack.json` as a second
fixture-only provider proof for the generic sensor-evidence contract. The pack
reports neutral row/count/status readiness metadata only and is referenced
through `team_orchestrator_summary.sensor_evidence_artifact_refs` with a
run-relative path and SHA-256. It is additive readiness metadata only:
`ranking_input`, `core_tournament_scores_modified`, and
`tournament_rankings_modified` stay false, and candidate scoring, Elo ratings,
bracket selection, winner selection, and rankings are unchanged.

Phase 9D routes configured CSI and environment evidence-provider inputs through
`somatic.sensors.registry` before tournament execution. The registry exposes
only sanitized provider metadata and validation limits. Tournament configs must
use known provider IDs, bounded CSI group/ref counts, fixture-only local refs,
closed sensor constraints, and sanitized validation errors. The registry does
not change `artifacts/csi_evidence_pack.json`,
`artifacts/environment_evidence_pack.json`, pack fingerprints, compatibility
behavior, candidate scoring, Elo ratings, brackets, winners, or rankings.

## Phase 2.1 Pairwise and Elo Layer

Phase 2.1 adds `somatic/agents/batch_scorer.py` with a `BatchScorer` interface and `LocalMockBatchScorer`. The local scorer is deterministic and mock-only. It can score candidate batches and compare pairs without external providers, cloud calls, or network access.

Pairwise comparisons are generated across the original candidate pool. Each matchup records pro/con notes for both candidates, dimension scores, dimension winners, aggregate scores, and the deterministic winner. Safety risk is treated as a risk value where lower is safer; it does not boost rankings.

Elo ratings start from a shared base rating and update after each pairwise result. Final ranked hypotheses remain ordered by aggregate score for compatibility, and now include `aggregate_score`, `elo_rating`, and `elo_rank`.

## Phase 2.5 TeamOrchestrator Scaffold

Phase 2.5 adds `somatic/agents/team_orchestrator.py`. It forms deterministic local teams around the top hypotheses, records team critiques before evidence-budget planning, writes shared blackboard state, produces a mock evidence budget, and records a deterministic reorganization decision.

The team scaffold is not a live agent system. It does not run AutoScientists, LangGraph, provider APIs, cloud scorers, Fabric, biomodels, or sensors. It preserves a describe-only future hook where a real orchestrator could attach after safety, secrets, and provider boundaries exist. The CSI readiness metadata is also describe-only and uses only configured local fake/sample fixture groups routed through sanitized replay metadata.

## Artifacts

Tournament runs preserve the Phase 1B baseline artifacts and add:

- `artifacts/candidate_hypotheses.json`
- `artifacts/pairwise_debates.json`
- `artifacts/elo_ratings.json`
- `artifacts/team_roster.json`
- `artifacts/team_critiques.json`
- `artifacts/shared_blackboard.json`
- `artifacts/evidence_budget.json`
- `artifacts/reorganization_log.json`
- `artifacts/team_orchestrator_summary.json`
- `artifacts/reflection_notes.json`
- `artifacts/review_scores.json`
- `artifacts/tournament_bracket.json`
- `artifacts/csi_evidence_pack.json`
- `artifacts/environment_evidence_pack.json`
- `artifacts/refined_hypotheses.json`
- `artifacts/ranked_hypotheses.json`

The report at `reports/report.md` includes the workflow mode, candidate count, aggregate score ranking, Elo ranking, pairwise debate summary, team orchestration summary, evidence budget summary, score table, safety summary, limitations, next-step recommendations, and explicit mock/offline/non-medical boundaries.
