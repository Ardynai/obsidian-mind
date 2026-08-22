# AutoScientists Mapping

Phase 5E maps AutoScientists team-orchestration concepts into Somatic-owned
offline structures. The mapping is conceptual and deterministic. It does not
create an AutoScientists runtime adapter.

## Current Boundary

- Source: `C:\AI\external-sources\somatic\AutoScientists`
- Commit: `c71a92343b9a488ed10134be805845b9473ad18f`
- License state: no license file found in staged source
- Somatic status: reference-only, disabled by default, fake-backed metadata
- Runtime state: no external imports, no dependency installs, no network calls,
  no live agents, no ClawInstitute service, no Claude Code runtime

## Concept Map

| AutoScientists reference concept | Somatic Phase 5E mapping | Current artifact |
| --- | --- | --- |
| Hypothesis-centered team formation | Five deterministic teams share the top ranked hypotheses and record role-specific critique goals | `team_roster.json` |
| Lifecycle stage | Each team records `formed-for-offline-review` | `team_roster.json` |
| Team confidence and status | Each team records a mock confidence estimate with an explicit non-scientific basis | `team_roster.json`, `team_orchestrator_summary.json` |
| Discussion before queue or compute | Each team passes a `critique-before-evidence` gate before budget planning | `team_critiques.json`, `evidence_budget.json` |
| Shared blackboard | Each team emits a deterministic `team_contribution` event | `shared_blackboard.json` |
| Evidence or compute budget | Budget remains local mock evidence points, not external spend | `evidence_budget.json` |
| Monitor and stagnation detection | Current run records no stall due no prior rotation history | `reorganization_log.json`, `team_orchestrator_summary.json` |
| Reorganization after stagnation | Current run records no reorganization and explains the trigger state | `reorganization_log.json` |
| Next team action | Each team records the next local review action | `team_roster.json`, `team_orchestrator_summary.json` |
| Future provider hook | Metadata names the reference-only AutoScientists hook and unresolved license state | `team_roster.json`, `team_orchestrator_summary.json`, provider fixture |

## Provider Boundary

`somatic.providers.team_orchestration` now includes
`AutoScientistsTeamOrchestrationProvider` as a disabled, reference-only
placeholder. It can produce fake-backed plan and summary metadata for tests, but
it fails closed if live execution is requested.

The provider scaffold guarantees:

- `reference_only: true`
- `fake_backed: true`
- `runtime_enabled: false`
- `runtime_import_allowed: false`
- `live_execution_allowed: false`
- `license_status: unresolved-no-license-file-found`

## Non-Adoption Rules

Somatic must not:

- Import AutoScientists modules.
- Copy AutoScientists templates or task code.
- Start ClawInstitute, AnonAPI, Claude Code, GPU agents, or benchmark tasks.
- Spend evidence, run experiments, train models, or launch live agents.
- Make clinical, lab, or scientific validity claims from scaffold output.

## Future Work

A real adapter remains blocked until:

- License status is clarified.
- A user explicitly requests live integration work.
- Runtime dependencies, services, secrets, data locality, and consent rules are
  specified.
- Local fixture tests prove fail-closed behavior before any external run path.
