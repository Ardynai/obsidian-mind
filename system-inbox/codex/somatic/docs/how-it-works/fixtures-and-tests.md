# Fixtures And Tests

## Owns

Offline proof material and behavior checks:

- `fixtures/`
- `tests/`
- `.github/workflows/ci.yml`
- `examples/`

## Main Flow

Most features in Somatic are fixture-first. A workflow fixture exercises code, generated artifacts land under `runs/`, and tests assert that public metadata stays deterministic, sanitized, and blocked from real runtime behavior.

CI runs:

```powershell
python -m unittest
python -m somatic doctor
python -m somatic run fixtures/workflows/valid-literature-only.yaml --run-id ci-mock-run
```

## Gotchas

- `runs/` is generated output and should not be committed.
- Some fixtures intentionally contain invalid cases. Do not "fix" them unless the related test contract changes.
- Many tests assert exact public strings. When changing docs or status text, check the CLI and release-summary tests.
- Keep fixture examples generic and sanitized: no secrets, raw health data, raw CSI, absolute paths, private source IDs, or credentials.

## Start Reading

Start with the test file matching the area you plan to touch. For a new workflow mode, inspect `tests/test_workflow_loader.py`, `tests/test_mock_runtime.py`, and the nearest mode-specific test.
