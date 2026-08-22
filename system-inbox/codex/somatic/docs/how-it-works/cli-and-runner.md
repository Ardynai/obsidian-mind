# CLI And Runner

## Owns

The local command surface and mock run flow:

- `somatic/cli/main.py`
- `somatic/workflow_loader.py`
- `somatic/mock_runtime.py`
- `somatic/run_writer.py`
- `somatic/contracts.py`

## Main Flow

`python -m somatic run fixtures/workflows/valid-literature-only.yaml` enters `somatic/cli/main.py`, dispatches to `_run`, and calls `run_mock_workflow`.

`python -m somatic consent status|grant|revoke|erase` reads and writes the local JSON ledger via `somatic/consent/store.py`. `analyze` and `share` load that ledger and still accept session-only `--grant`.

`python -m somatic ui` binds 127.0.0.1 and opens the local graphical app. See `docs/how-it-works/local-ui.md`.

The runner then:

1. Parses a deliberately small YAML subset with `load_workflow`.
2. Validates required workflow fields, supported mode, list/object shapes, and sensor-evidence config.
3. Loads mock provider metadata from `fixtures/providers/`.
4. Branches by `workflow["mode"]` inside `run_mock_workflow`.
5. Builds deterministic payloads and report Markdown.
6. Hands everything to `write_run_artifacts`, which writes `runs/<run-id>/` and `manifest.json`.

## Gotchas

- `parse_simple_yaml` is not a general YAML parser. It supports enough syntax for checked-in fixtures and rejects tabs.
- `mock_runtime.py` is a mode router plus artifact assembler. Read only the branch for the mode you are changing.
- `run_writer.py` treats `artifact_refs` as both the manifest index and the list of files to hash.

## Start Reading

Start with `main()` and `_run()` in `somatic/cli/main.py`, then `run_mock_workflow` in `somatic/mock_runtime.py`, then `write_run_artifacts` in `somatic/run_writer.py`.
