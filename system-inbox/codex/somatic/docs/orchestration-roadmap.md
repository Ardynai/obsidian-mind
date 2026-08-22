# Orchestration Roadmap

Phase 2.5 keeps orchestration minimal. The CLI can run a fixture workflow, load mock providers, write artifacts, and route the `hypothesis-tournament` mode through the deterministic offline tournament path with pairwise debate, Elo-style refinement, and a mock TeamOrchestrator scaffold.

## Current Commands

- `somatic run <workflow>`
- `somatic launch --config <yaml>`
- `somatic doctor`
- `somatic replay <commit-or-run-id>`
- `python -m somatic run <workflow>`

## Current Local Runtime Paths

- `literature-only`: Phase 1B baseline mock run artifacts.
- `hypothesis-tournament`: Phase 2.5 deterministic candidate generation, reflection, aggregate scoring, pairwise debate, Elo rating, bracket, refinement, team orchestration, ranking, and report rendering.

## Batch Scorer Hook

`somatic/agents/batch_scorer.py` defines the current `BatchScorer` interface and `LocalMockBatchScorer`. The interface is intentionally small so future local or cloud scorers can attach behind the same methods after safety, secrets, and provider boundaries are implemented.

`somatic/agents/team_orchestrator.py` now provides the deterministic scaffold. It creates local team roster, critique, blackboard, evidence-budget, reorganization, and summary artifacts. Phase 5E adds lifecycle, confidence estimate, critique gate, stall/no-stall reason, blackboard contribution, evidence spend decision, reorganization trigger, next action, and future AutoScientists hook metadata. It does not run agents or call providers.

The remaining future hook is a disabled describe-only attachment point for a real team orchestrator implementation. It does not run agents, call providers, or leave mock/offline mode.

Phase 5A adds `somatic.providers.team_orchestration` as the Somatic-owned
boundary for future AutoScientists-style adapters. Phase 5E adds the
`AutoScientistsTeamOrchestrationProvider` reference scaffold. It is disabled,
fake-backed, and fail-closed because the staged AutoScientists source has no
license file. A future adapter should return reviewable plans and summaries
before any live team, tool, or provider runtime is started.

## Planned Orchestration Layers

1. Schema validation.
2. Provider capability matching.
3. Mock provider registry.
4. Local replay.
5. Safety gate enforcement.
6. Optional agent orchestration.
7. Optional engine-specific runtimes.

## Non-Goals for Phase 2.5

- No real provider API calls.
- No network runtime.
- No Fabric transport.
- No biomodel execution.
- No live sensor capture.
- No clinical workflow execution.
- No LangGraph runtime.
- No real team orchestrator runtime.
- No AutoScientists dependency or runtime.

## Phase 5A Team-Orchestration Boundary

- Critique happens before evidence-budget planning.
- Live agents remain disabled until explicit configuration and safety review.
- External team frameworks cannot own Somatic workflow manifests, Evidence Bus
  records, run artifacts, or report language.
- Provider metadata must not include raw secrets or private user data.
