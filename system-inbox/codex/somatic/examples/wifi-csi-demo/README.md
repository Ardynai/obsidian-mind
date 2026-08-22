# WiFi CSI Demo

Public examples for the offline, fixture-only WiFi CSI lane.

## Example Manifests

- `csi-parser-cli-example.json`: local parser CLI fixture review. This stdout
  report is not a portable public export; inspect `csi_evidence_pack.json` for
  the stricter no-fixture-ref artifact boundary.
- `n-of-1-csi-replay-example.json`: n-of-1 workflow with CSI replay and
  `artifacts/csi_evidence_pack.json`.
- `tournament-csi-readiness-example.json`: hypothesis tournament with CSI batch
  readiness metadata and `artifacts/csi_evidence_pack.json`.

These manifests are small public command descriptors. They reuse committed
fixtures and the existing CLI; they are not a new workflow schema.

## Quick Verify

From the repository root:

```powershell
python -m somatic doctor
python -m somatic csi-parse sample-esp32-csi.csv --repo-root .
python -m somatic csi-parse fixture://sensors/csi/sample-csi-jsonl.jsonl --repo-root .
python -m somatic run fixtures/workflows/valid-n-of-1.yaml --runs-dir runs/examples --run-id run-csi-n-of-1-example
python -m somatic run fixtures/workflows/valid-hypothesis-tournament.yaml --runs-dir runs/examples --run-id run-csi-tournament-example
```

Inspect the portable evidence packs:

```powershell
python -c "import json, pathlib; p=json.loads(pathlib.Path('runs/examples/run-csi-n-of-1-example/artifacts/csi_evidence_pack.json').read_text()); print(p['status']); print(p['pack_fingerprint'])"
python -c "import json, pathlib; p=json.loads(pathlib.Path('runs/examples/run-csi-tournament-example/artifacts/csi_evidence_pack.json').read_text()); print(p['status']); print(p['counts'])"
```

The generated `runs/examples/` directory is local output and is not committed.

## Boundary

This demo is fake-backed metadata only. It does not run CSI capture, access
WiFi hardware, use ESP32 or RTL8812AU devices, use routers or drivers, enter
monitor mode, perform packet capture, probe WiFi devices, collect raw RF/CSI
data, call networks, or make clinical claims.

See `docs/wifi-csi-public-examples.md` for the release-readiness checklist.
