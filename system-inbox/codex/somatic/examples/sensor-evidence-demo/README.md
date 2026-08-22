# Sensor Evidence Extension Demo

This example shows the public extension pattern for a sanitized fixture-only
sensor-evidence provider. The toy provider is intentionally boring: it reads a
small checked-in CSV fixture and exports only count/status metadata.

Run from the repository root:

```powershell
python -m somatic sensor-evidence providers
python -m somatic sensor-evidence validate --workflow examples/sensor-evidence-demo/toy-counter-fixture-workflow.yaml
python -m somatic run examples/sensor-evidence-demo/toy-counter-fixture-workflow.yaml --runs-dir runs/examples --run-id run-toy-counter-provider-example
```

Use `--format json` with either `sensor-evidence` command for deterministic
machine-readable preflight output.

`python -m somatic sensor-evidence providers --format json` renders the Phase
9G provider manifest contract. Compare it with
`fixtures/providers/sensor-evidence-provider-manifest-v1.json` when changing
registry metadata intentionally.

Inspect the portable evidence pack and generic refs:

```powershell
python -c "import json, pathlib; p=json.loads(pathlib.Path('runs/examples/run-toy-counter-provider-example/artifacts/toy_counter_evidence_pack.json').read_text()); print(p['status']); print(p['pack_fingerprint'])"
python -c "import json, pathlib; m=json.loads(pathlib.Path('runs/examples/run-toy-counter-provider-example/manifest.json').read_text()); print(m['sensor_evidence_artifact_refs']['toy_counter_evidence_pack']['artifact_ref']); print(m['sensor_evidence_artifact_refs']['toy_counter_evidence_pack']['sha256'])"
```

The example does not add live capture, hardware access, network listeners,
credentials, provider payload export, value export, ranking input, or Fabric
publishing.
