# Agents And Analysis

## Owns

The deterministic mock reasoning shapes used by tournament and Robin workflows:

- `somatic/agents/`
- `somatic/analysis/`
- `fixtures/workflows/valid-hypothesis-tournament.yaml`
- `fixtures/workflows/valid-robin-loop.yaml`

## Main Flow

Hypothesis tournament mode builds fixed candidate hypotheses, reflection notes, local review scores, pairwise debates, Elo-style ratings, a team-orchestrator summary, and final ranked hypotheses. The main entry is `run_hypothesis_tournament`.

Robin mode maps the Crow/Falcon/Finch loop into local fixtures: Crow builds mock literature context, Falcon builds a measurement plan, the sandbox evidence source emits deterministic raw evidence, and Finch emits a structured verdict plus standard-library table/dose-response/provenance summaries.

## Gotchas

- These are not live LLM agents. They are deterministic scaffolds for artifact shape and review semantics.
- External systems such as FutureHouse Robin, AutoScientists, PaperQA2, and scientific-agent-skills are reference-only or disabled provider scaffolds unless a future reviewed runtime changes that.
- Analysis helpers are standard-library first. Optional package availability is reported as metadata, not used by the base runner.

## Start Reading

For tournament mode, start at `somatic/agents/tournament.py`. For Robin mode, start at `_run_robin_loop` in `somatic/mock_runtime.py`, then read `somatic/agents/crow.py`, `falcon.py`, `finch.py`, and `finch_toolbelt.py`.
