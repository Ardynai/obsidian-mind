# Agents and Systems

This folder defines the roles of agents and systems that participate in Locus Evolution Lab workflows.

These are role definitions, not live agents.

## Initial roles

| Role | Purpose |
| --- | --- |
| OpenClaw | Conductor, scheduler, dispatcher, documenter, and local workflow memory owner. |
| GitNexus | Mandatory repo-intelligence system before mutation or hardening. |
| Codex | Narrow implementation, tests, and documentation updates. |
| KimiClaw | Implementation and integration work with OpenClaw/Kimi context. |
| Hermes | Optimization, DSPy/GEPA-style evolution, prompt/program improvement. |
| Evolver/OpenEvolve | Artificial-selection and induced-evolution experiment runners. |
| Agent Zero | Browser/UI validation, screenshots, behavior checks. |
| DeerFlow | Research and synthesis. |
| Security Lab | Isolated red/blue-team, eval, and adversarial testing only. |

## Rules

- No agent role grants permission by itself.
- Every side-effectful action must be gated and audited.
- Repo intelligence comes before code mutation.
- Claude is not part of the active evolution/hardening loop for this repo.
- Security/red-team tools stay isolated unless Josh explicitly starts a lab phase.
