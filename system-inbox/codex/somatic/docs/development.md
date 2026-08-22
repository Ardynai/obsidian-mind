# Development

## Requirements

- Python 3.11 or newer.
- No package install is required for the standard-library test path.

## Standard Checks

```powershell
python -m unittest
python -m somatic doctor
python -m somatic run fixtures/workflows/valid-literature-only.yaml
```

## Optional Checks

If optional tooling is installed:

```powershell
python -m pytest
python -m ruff check .
python -m mypy somatic
```

Do not add mandatory dependencies to the basic runner without updating `docs/install-modes.md`.

## Project Layout

- `somatic/`: Python package.
- `tests/`: standard-library `unittest` tests.
- `fixtures/`: offline JSON/YAML fixtures.
- `docs/`: architecture and contract docs.
- `runs/`: generated local run artifacts, ignored by Git.

## Contribution Boundary

Keep Somatic standalone. Do not add OpenClaw, Locus, Multiverse, or private harness dependencies.
