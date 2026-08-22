# AutoScientists Source Inspection

Phase 5E inspected the staged AutoScientists source as reference material only.
No AutoScientists code was copied, vendored, imported, executed, or installed.
No package manager, network service, ClawInstitute runtime, Claude Code runtime,
Fabric runtime, provider API, biomodel, sensor, lab, or clinical workflow was
used.

## Source

- Repository: `mims-harvard/AutoScientists`
- Local path: `C:\AI\external-sources\somatic\AutoScientists`
- Inspected commit: `c71a92343b9a488ed10134be805845b9473ad18f`
- Inspection mode: static, read-only file review
- Current Somatic status: reference-only concept mapping

## License Status

No `LICENSE`, `LICENCE`, `COPYING`, or `NOTICE` file was found in the staged
source during Phase 5E inspection. Until license status is clarified,
AutoScientists is not an implementation dependency and its code cannot be
copied, vendored, imported, or executed by Somatic.

Allowed current use:

- Read-only source inspection.
- Concept-level mapping into Somatic-owned interfaces.
- Documentation of architecture, dependencies, and non-adoption boundaries.

Blocked current use:

- Source copy or vendoring.
- Runtime imports.
- Dependency installation.
- ClawInstitute, AnonAPI, Claude Code, or other live orchestration execution.
- Networked agents or external evidence spend.

## Observed Structure

Top-level files and folders include:

- `README.md`
- `launch.py`
- `requirements.txt`
- `runbook.md`
- `system/`
- `task-autoresearch/`
- `task-biomlbench/`
- `task-protein-gym/`

`requirements.txt` lists `requests>=2.31` and `pyyaml>=6.0`. `launch.py`
contains launcher logic around local run directories, copied task material, and
service calls. Somatic did not execute it.

The README describes AutoScientists as a decentralized team of AI agents for
long-running computational scientific experimentation. The implementation
material is organized around teams, workshops, workspaces, message board posts,
runbook instructions, and task-specific profiles.

## Architecture Findings

Useful reference concepts:

- Hypothesis-centered team formation rather than static axis ownership.
- A lifecycle with bootstrap, discussion, execution, and adaptation stages.
- Critique and team discussion before spending experimental compute.
- Shared blackboard style state through posts, files, results, champions, and
  dead-end records.
- Monitor-style stagnation detection and reorganization when teams stop making
  useful progress.
- Separation between an orchestrator that coordinates and agents or task
  workers that perform experiments.

Runtime concepts Somatic does not adopt in Phase 5E:

- Claude Code subagents.
- ClawInstitute or AnonAPI service calls.
- `requests`-based orchestration.
- Node, Python package installation, or benchmark task execution.
- GPU agents, live training, live experiment launch, or leaderboard submission.
- AutoScientists file templates as copied runtime assets.

## Somatic Mapping Boundary

Phase 5E maps only the architecture ideas into Somatic-owned deterministic
artifacts:

- `team_roster.json` records lifecycle, confidence estimate, critique gate,
  stall status, blackboard contribution, evidence spend decision,
  reorganization trigger, next action, and future provider hook metadata.
- `team_critiques.json` preserves critique-before-budget ordering.
- `shared_blackboard.json` records team contribution events.
- `evidence_budget.json` remains mock points only and blocks external spend.
- `reorganization_log.json` records no-stall and no-reorganization rationale.
- `team_orchestrator_summary.json` aggregates the Phase 5E fields.

The optional provider scaffold remains disabled, fake-backed, and
reference-only until license and runtime boundaries are explicitly revisited.
