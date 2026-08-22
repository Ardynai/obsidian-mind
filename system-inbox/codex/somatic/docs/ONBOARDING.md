# Onboarding

This guide is for a human contributor opening Somatic without an AI assistant.

## What Somatic Is Today

Somatic is a Python research-workflow scaffold. It can run deterministic local fixtures and produce mock run artifacts, but real provider runtimes are still blocked. Assume outputs are research-only planning artifacts unless a future PR explicitly changes that boundary.

Do not describe the repo as production-ready, clinically validated, sensor-enabled, lab-enabled, or runtime-authorized.

## Requirements

- Python 3.11 or newer.
- No required runtime dependencies for the standard local path.
- Optional developer tools, if installed locally: `pytest`, `ruff`, `mypy`, `fallow`.

## First Commands

From the repo root:

```powershell
python -m somatic ui
python -m somatic doctor
python -m somatic run fixtures/workflows/valid-literature-only.yaml --run-id local-smoke
python -m unittest
```

The run command writes local artifacts under `runs/local-smoke/`. `runs/` is generated output and should not be committed.

Useful optional checks:

```powershell
python -m pytest
python -m ruff check .
python -m mypy somatic
npx fallow --format json
```

## Layout

- `somatic/`: live Python package.
- `somatic/cli/main.py`: command entrypoint.
- `somatic/mock_runtime.py`: local fixture mode router.
- `somatic/run_writer.py`: run artifact writer.
- `somatic/safety/`: blocked-runtime and planning-contract surfaces.
- `somatic/fabric/`: Content Fabric fixture validation and signing helpers.
- `fixtures/`: local JSON/YAML/CSV fixtures.
- `tests/`: standard-library `unittest` tests.
- `docs/`: human contracts, phase notes, and how-it-works docs.
- `packages/`: placeholder package-boundary READMEs, not the active runtime package.

## Conventions

- Keep the base runtime standard-library only unless a task explicitly changes install policy.
- Keep public surfaces sanitized: no raw document text, raw CSI, URLs, absolute paths, credentials, secrets, or private identifiers in public fixtures/reports.
- Preserve blocked-runtime wording: `runtime_stage: not-implemented`, `execution_permitted: false`, and `real_mode_runtime_enabled: false`.
- Use fixture-backed examples for behavior changes.
- Update the relevant `docs/how-it-works/*.md` file when a feature changes ownership, flow, artifacts, or safety boundaries.

## Safe First Change

1. Pick a narrow fixture-backed area, such as a README wording fix or a new validation test for an existing helper.
2. Read the relevant area guide under `docs/how-it-works/`.
3. Find the owning test file in `tests/`.
4. Make the smallest change that proves the behavior.
5. Run the targeted test first, then `python -m unittest`.

Avoid starting with `somatic/mock_runtime.py`, `somatic/safety/phase12_contracts.py`, or the Fabric crypto/keyring helpers unless you are specifically working in those areas. They are important and dense.
