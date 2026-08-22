# Contributing

## Local Checks

Run the standard no-dependency checks before opening a PR:

```powershell
python -m unittest
python -m somatic doctor
python -m somatic run fixtures/workflows/valid-literature-only.yaml --run-id local-smoke
```

Optional checks are welcome when the tools are installed:

```powershell
python -m pytest
python -m ruff check .
python -m mypy somatic
npx fallow --format json
```

## Docs Upkeep

Every feature PR must update the relevant `docs/how-it-works/*.md` file when it changes ownership, flow, artifacts, safety boundaries, public commands, or where a human should start reading.

Run a full readability pass after roughly every five merged feature batches. That pass should refresh `docs/ARCHITECTURE.md`, `docs/ONBOARDING.md`, and the affected how-it-works docs, then make only behavior-preserving naming or comment updates where the code is genuinely hard to read.

## Safety Boundary

Somatic is still pre-runtime for real providers. Do not imply that review metadata authorizes execution. Public status should keep real-mode runtime blocked unless a future explicitly reviewed runtime phase changes that contract.
