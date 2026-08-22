# Team Orchestrator

Phase 2.5 adds a deterministic mock TeamOrchestrator scaffold for the offline hypothesis tournament. Phase 5E deepens the AutoScientists-style mapping while keeping the implementation Somatic-owned and local. It is inspired by self-organizing scientific teams, but it is only local data generation. It does not import or run AutoScientists, LangGraph, real agents, provider APIs, Fabric, biomodels, sensors, or network code.

## Runtime Boundary

The orchestrator is mock/offline and research-only. It creates plain Python dictionaries that describe team formation, critique, shared blackboard state, evidence-budget planning, and reorganization decisions. It does not spend evidence, call providers, start agents, or perform any real-world action.

## Teams

The scaffold creates five deterministic teams around the top hypotheses:

- `GeneratorTeam`: proposes bounded refinements and alternate mechanisms.
- `FalsifierTeam`: identifies falsification checks before evidence spend.
- `EvidenceTeam`: maps evidence gaps and local fixture requests.
- `SafetyTeam`: enforces mock/offline, research-only, non-medical boundaries.
- `SynthesisTeam`: folds critiques into conservative next-step recommendations.

Each team records `team_id`, `focus_hypothesis_ids`, `role`, `critique_goals`, `evidence_requests`, `risk_flags`, and `decision`.

Phase 5E also records deterministic deeper-mapping fields for every team:

- `lifecycle_stage`
- `confidence_estimate`
- `critique_gate`
- `stall_status`
- `blackboard_contribution`
- `evidence_spend_decision`
- `reorganization_trigger`
- `next_team_action`
- `future_provider_hook`

## Ordering

Critique happens before evidence-budget planning. The `shared_blackboard.json` event log records this order with a `critique` event before the `evidence_budget` event, and then records deterministic team contribution events. The budget is deterministic mock evidence points only and has `external_evidence_spend_allowed: false`.

## Artifacts

Tournament runs now add:

- `artifacts/team_roster.json`
- `artifacts/team_critiques.json`
- `artifacts/shared_blackboard.json`
- `artifacts/evidence_budget.json`
- `artifacts/reorganization_log.json`
- `artifacts/team_orchestrator_summary.json`

The summary includes disabled future hooks for a real team orchestrator implementation and the reference-only AutoScientists provider boundary. AutoScientists source inspection is documented in `docs/autoscientists-source-inspection.md`; the concept mapping is documented in `docs/autoscientists-mapping.md`. No AutoScientists license file was found in the staged source, so the hook remains metadata-only.
