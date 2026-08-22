# WiFi CSI Public Examples

Phase 8H exposes the existing offline, fixture-only CSI parser, replay,
scoring, batch, and evidence-pack path through small public example manifests.
Phase 8I adds v1 compatibility examples and fingerprint checks for the portable
evidence-pack artifact. Phase 9A keeps CSI as the first implementation of the
generic sanitized sensor-evidence contract foundation. The examples are safe
from a fresh clone because they use only committed fixture files, the
standard-library Somatic CLI, and temporary run directories created by the local
mock runner.

## Example Manifests

- `examples/wifi-csi-demo/csi-parser-cli-example.json` runs the parser CLI on
  one local fixture and prints sanitized parser-contract metadata to stdout.
  This local report may include neutral fixture identifiers for replay
  debugging; use `csi_evidence_pack.json` for portable public export.
- `examples/wifi-csi-demo/n-of-1-csi-replay-example.json` runs the existing
  n-of-1 fixture and writes `artifacts/csi_evidence_pack.json` alongside the
  existing n-of-1 report and Fabric planning artifacts.
- `examples/wifi-csi-demo/tournament-csi-readiness-example.json` runs the
  existing hypothesis tournament fixture and writes CSI batch readiness
  metadata plus `artifacts/csi_evidence_pack.json`.

The JSON files are example manifests, not a new runtime schema. They point at
the existing CLI and workflow fixtures so a new developer can copy commands
without learning the full test suite first.

## Quick Verification

From the repository root:

```powershell
python -m somatic csi-parse sample-esp32-csi.csv --repo-root .
```

Generate the n-of-1 CSI evidence pack:

```powershell
python -m somatic run fixtures/workflows/valid-n-of-1.yaml --runs-dir runs/examples --run-id run-csi-n-of-1-example
python -c "import json, pathlib; p=json.loads(pathlib.Path('runs/examples/run-csi-n-of-1-example/artifacts/csi_evidence_pack.json').read_text()); print(p['status']); print(p['pack_fingerprint']); print(p['scores'])"
```

Generate the tournament CSI readiness pack:

```powershell
python -m somatic run fixtures/workflows/valid-hypothesis-tournament.yaml --runs-dir runs/examples --run-id run-csi-tournament-example
python -c "import json, pathlib; p=json.loads(pathlib.Path('runs/examples/run-csi-tournament-example/artifacts/csi_evidence_pack.json').read_text()); print(p['status']); print(p['pack_fingerprint']); print(p['counts'])"
```

Inspect the tournament readiness metadata without treating it as a ranking
input:

```powershell
python -c "import json, pathlib; s=json.loads(pathlib.Path('runs/examples/run-csi-tournament-example/artifacts/team_orchestrator_summary.json').read_text()); print(s['csi_evidence_scoring_readiness']['status']); print(s['csi_evidence_pack']['artifact_ref']); print(s['csi_evidence_pack']['pack_fingerprint'])"
```

Check the portable evidence-pack compatibility result:

```powershell
python -c "import json, pathlib; from somatic.sensors.csi_evidence_pack import classify_csi_evidence_pack_compatibility; p=json.loads(pathlib.Path('runs/examples/run-csi-n-of-1-example/artifacts/csi_evidence_pack.json').read_text()); print(classify_csi_evidence_pack_compatibility(p).classification)"
```

The run directories above are local generated output and are intentionally not
committed. Re-running the same command against the same sanitized inputs should
preserve the CSI evidence-pack fingerprint.

## Release-Readiness Checklist

- Supported parser fixtures: tiny local ESP32-style CSV, aggregate tabular CSV,
  JSONL CSI-like records, mixed valid/invalid fixture rows, malformed fixtures,
  invalid UTF-8 fixtures, and unsupported-extension negative fixtures under
  `fixtures/sensors/csi/`.
- Generated CSI artifact names: `artifacts/csi_parser_report.json`,
  `artifacts/csi_parsed_summary.json`, `artifacts/csi_evidence_pack.json`, and
  tournament readiness metadata in
  `artifacts/team_orchestrator_summary.json`.
- Evidence-pack fingerprint: `pack_fingerprint` is deterministic for the same
  sanitized parser/replay/scoring/batch metadata and is paired with a
  deterministic `pack_id`. The fingerprint covers the full sanitized payload
  with `pack_id` and `pack_fingerprint` treated as null.
- Evidence-pack compatibility: v1 reader results are `compatible`,
  `incompatible`, `unsupported_version`, or `malformed`. Missing required
  fields fail closed; future versions are explicitly unsupported until a new
  reader is added; generated-from IDs/versions must match v1; additive unknown
  fields are allowed only as simple safe scalar metadata when the full payload
  remains privacy-safe and the fingerprint is recomputed.
- Generic sensor-evidence foundation: `somatic.sensors.evidence` provides the
  reusable contract primitives for future sanitized providers: identity,
  provider/evidence kind, compatibility classification, deterministic
  fingerprinting, readiness status, run-artifact refs/hashes, sanitized
  diagnostics/counts, and closed privacy boundary flags. CSI v1 continues to
  own the public `csi_evidence_pack.json` shape and fingerprint anchors.
- Checked-in compatibility examples:
  `fixtures/reports/csi-evidence-pack-v1-parsed.json` and
  `fixtures/reports/csi-evidence-pack-v1-partial-batch.json`.
- Privacy boundary: portable CSI evidence packs export only metadata counts,
  statuses, score summaries, contract versions, closed boundary flags, artifact
  hashes, and generic artifact refs. They do not export fixture names, unsafe
  refs, private local paths, source IDs, provider payloads, parser payload
  bodies, sample arrays, or signal values.
- Parser CLI boundary: `csi-parse` stdout is a local parser-contract report, not
  a portable public export. It remains sanitized against raw signal values,
  unsafe refs, source IDs, and absolute paths, but can include local fixture
  identifiers needed by parser replay tests.
- Tournament boundary: CSI metadata is readiness-only. It does not modify
  `SCORE_FIELDS`, candidate scores, Elo ratings, brackets, winner selection,
  final rankings, or report conclusions.
- Non-goals: no live capture, hardware access, packet capture, monitor mode,
  serial, MQTT, UDP, router tooling, credentials, network listeners, heavy
  dependencies, vital-sign inference, fall detection, diagnosis, treatment
  advice, medical advice, or clinical claims.
