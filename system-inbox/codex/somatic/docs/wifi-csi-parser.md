# WiFi CSI Parser

Phase 8B added `somatic.sensors.csi_formats` and
`somatic.sensors.csi_parser` as a standard-library-only parser scaffold for
local fake/sample fixtures. Phase 8C freezes that scaffold as a small offline
parser contract with deterministic replay validation. Phase 8D adds a
fixture-backed sensor-provider replay mode that consumes the same parser
contract and emits sanitized metadata only. Phase 8E adds deterministic
sanitized evidence scoring over replay metadata only. Phase 8F adds batch
replay evaluation for tournament/readiness reports over sanitized fixture-group
metadata only. Phase 8G adds a deterministic sanitized evidence-pack export
contract for portable parser, replay, scoring, and batch readiness metadata.
Phase 8I hardens the evidence-pack reader with v1 compatibility classification,
fingerprint verification, sanitized failure metadata, and future-version
handling.

## Runtime Surface

- `parse_csi_file(path)` accepts an explicit local file path under
  the active repo's `fixtures/sensors/csi/` root and rejects other local paths.
- `parse_csi_fixture(ref, repo_root=...)` accepts a fixture filename or
  `fixture://sensors/csi/...` ref and rejects absolute paths or traversal.
- `build_csi_parser_artifacts(refs, repo_root=...)` returns two summary-only
  payloads: `csi_parser_report` and `csi_parsed_summary`.
- `SandboxSensorProvider.replay_csi_fixtures(refs, repo_root=...)` calls the
  parser through the sensor-provider seam and returns sanitized replay provider
  output plus the same report and summary payloads.
- `score_csi_replay_evidence(report, summary)` consumes sanitized aggregate
  report/summary payloads only and returns bounded `evidence_quality` and
  `replay_integrity` metadata.
- `evaluate_csi_replay_batch(groups, repo_root=...)` accepts configured local
  CSI fixture groups, routes each group through
  `SandboxSensorProvider.replay_csi_fixtures(...)`, and returns metadata-only
  group and aggregate readiness scores.
- `build_csi_evidence_pack(...)` exports deterministic portable JSON over
  sanitized parser, replay, scoring, or batch metadata only. It emits a stable
  SHA-256 fingerprint, sanitized counts/status counts, evidence-quality and
  replay-integrity scores, contract versions, and closed boundary flags.
- `compute_csi_evidence_pack_fingerprint(payload)` recomputes the v1 portable
  pack fingerprint over the whole sanitized JSON payload with `pack_id` and
  `pack_fingerprint` treated as null.
- `classify_csi_evidence_pack_compatibility(payload)` validates a portable pack
  without exposing private field names or values. It returns one of
  `compatible`, `incompatible`, `unsupported_version`, or `malformed`.
- `python -m somatic csi-parse <fixture> --repo-root <repo>` prints the same
  sanitized aggregate report and summary JSON for local fixture review.

The parser emits deterministic frame/sample counts, source format names,
malformed-row reports, and bounded metadata. It does not emit signal-processing
results or raw signal arrays in the parsed summary.

Public aggregate outputs redact local fixture refs or format labels that would
expose raw signal component names. The parser can retain exact format names in
in-memory records and direct parser reports for contract tests, but provider,
CLI, and n-of-1 artifacts use neutral fixture IDs and format classes.

## Contract

The stable contract version is `1`.

- Parsed records are in-memory `CsiParsedFile`, `CsiFrame`, and `CsiSample`
  dataclasses for local tests only.
- Parser reports are `CsiParserReport` dictionaries with repo-relative `path`,
  `status`, `rows_seen`, `frame_count`, `sample_count`, `malformed_rows`,
  sanitized `errors`, structured `parse_errors`, and count-only `warnings`.
- Parse errors are `CsiParseError` dictionaries with `row_number`,
  `line_number`, stable `code`, sanitized `message`, `source_format`, and
  `recoverable`.
- Sanitized summaries are aggregate metadata only. They exclude raw sample
  arrays, source IDs, absolute paths, and the signal-value keys listed in the
  contract constants.
- Evidence scoring payloads are additive metadata under `csi_evidence_scoring`.
  They include parser status, fixture status counts, fixture count, frame count,
  sample count, malformed-row count, error/warning counts, format coverage,
  parser contract version, count-based score basis, and closed boundary flags.
  They do not include fixture paths, source IDs, source records, per-row values,
  or frame/sample arrays.
- Batch evaluation payloads are additive metadata with contract version `1`.
  They include `group_count`, `evaluated_group_count`, group status counts,
  aggregate frame/sample/malformed/error/warning counts, public source format
  classes, `aggregate_evidence_quality`, `aggregate_replay_integrity`,
  `scorer_id`, `scoring_contract_version`, and sanitized per-group
  status/score summaries. They are bounded by explicit maximum group and
  per-group ref counts. They do not include fixture refs, fixture filenames,
  provider reports, parser summaries, parse rows, source IDs, absolute paths,
  unsafe refs, frame/sample arrays, or raw signal values.
- Evidence-pack payloads are additive metadata with contract version `1`.
  They include `evidence_pack_contract_version`, deterministic `pack_id` and
  `pack_fingerprint`, parser/scorer/batch contract versions, sanitized
  fixture/group/status counts, aggregate `evidence_quality` and
  `replay_integrity`, fail-closed readiness status, sanitized diagnostic
  counts/categories, and closed boundary flags. They do not include fixture
  refs, fixture filenames, provider reports, parser summaries, raw CSI arrays,
  source IDs, absolute paths, unsafe refs, or signal values.
- Evidence-pack compatibility results are sanitized metadata with contract
  version checks, fingerprint status, missing-field counts, unknown-field
  counts, privacy-violation counts, and generic error/warning categories only.
  They do not echo rejected field names, fixture refs, local paths, provider
  payload bodies, parser payload bodies, or signal terms.

Scoring values:

- `score`, `evidence_quality`, and `replay_integrity` are integers on a bounded
  0-100 scale.
- Parsed fixture replay with no warnings/errors starts at 100.
- Partial, rejected, parse-error, warning, and unsupported-format counts apply
  deterministic penalties.
- Replays with no parsed frames fail closed at score 0.
- The score is replay metadata quality only. It is not signal quality, vital-sign
  inference, monitoring, diagnosis, treatment advice, medical advice, or a
  clinical claim.

Status values:

- `parsed`: at least one frame parsed and no malformed rows.
- `partial`: at least one frame parsed and one or more malformed rows.
- `rejected`: no frames parsed, unsupported extension or format, missing file,
  unsafe path, oversized fixture, or all rows malformed.

Row-count semantics:

- CSV blank lines are ignored and do not count as `rows_seen`.
- CSV headers are not counted as rows.
- JSONL blank lines are ignored.
- `rows_seen` counts non-blank data rows or JSONL records reviewed.
- Unknown CSV columns are ignored and reported only as a count; names are not
  copied to report-facing artifacts.

## Evidence-Pack Compatibility

Phase 8I keeps the portable CSI evidence-pack contract at v1 and adds a
standard-library compatibility reader for future evolution.

- `compatible`: all required v1 fields are present, contract versions are v1,
  generated-from IDs and versions match the v1 exporter contract, boundary
  flags remain closed, scores/counts/status fields are bounded, the privacy
  scan passes, and `pack_fingerprint` matches the deterministic v1 fingerprint.
- `incompatible`: the pack is v1-shaped but violates a required semantic rule,
  privacy rule, artifact-ref rule, pack-id rule, score/count bound, or
  fingerprint check.
- `unsupported_version`: the payload declares a future or unknown
  evidence-pack, generated-from, or version field. The reader reports this
  explicitly and does not coerce the payload into v1.
- `malformed`: the payload is not a JSON object or is missing required v1
  fields. Missing fields fail closed and are reported as sanitized counts.

The v1 fingerprint is SHA-256 over JSON serialized with sorted keys, two-space
indentation, and a trailing newline after setting `pack_id` and
`pack_fingerprint` to null. This matches the pack's `fingerprint_scope` value
and keeps identical sanitized inputs stable across export and compatibility
checks.

Additive unknown top-level fields are ignored by the v1 reader only when their
values are simple safe scalar metadata. Unknown nested objects, arrays, or
numeric values fail closed because they can smuggle signal payloads. The whole
payload must still pass the strict portable privacy scan and the fingerprint
must still match. Because the fingerprint covers the full sanitized payload,
adding a field requires recomputing `pack_id` and `pack_fingerprint`; otherwise
the pack is `incompatible`.

Checked-in compatibility examples live at:

- `fixtures/reports/csi-evidence-pack-v1-parsed.json`
- `fixtures/reports/csi-evidence-pack-v1-partial-batch.json`

## N-of-1 Artifacts

When the n-of-1 workflow includes CSI parser fixture refs, the sandbox sensor
provider replays those fixtures through `replay_csi_fixtures(...)`. The mock
runtime writes:

- `artifacts/csi_parser_report.json`
- `artifacts/csi_parsed_summary.json`
- `artifacts/csi_evidence_pack.json`

The n-of-1 summary includes `csi_parser_metadata` with parser id, replay
provider metadata, fixture count, frame count, sample count, neutral source
format classes, artifact refs, and closed boundary flags. It does not repeat
fixture filenames or fixture refs in the summary surface.

Phase 8E copies the same `csi_evidence_scoring` object into:

- `artifacts/csi_parser_report.json`
- `artifacts/csi_parsed_summary.json`
- `sensor_evidence_record.metadata.csi.evidence_scoring`
- `sensor_evidence_record.raw_evidence.metadata.csi.evidence_scoring`
- `n_of_1_summary.csi_evidence_scoring_metadata`

Phase 8G exports `artifacts/csi_evidence_pack.json` and references it from
`n_of_1_summary.csi_evidence_pack_metadata`,
`artifacts/n_of_1_report_packet.json`, and the planning-only
`artifacts/n_of_1_fabric_pack_plan.json`. The Fabric plan references the
evidence pack by run-relative path and SHA-256 only; it does not become a
Content Fabric manifest and does not sign, publish, transport, seed, install,
or execute anything.

Phase 9B also exposes the same CSI evidence pack through generic
`sensor_evidence_artifact_refs` in the run manifest, n-of-1 summary, report
packet, tournament summary, and Fabric plan. Parser report and parsed-summary
artifacts are local diagnostics; Fabric planning marks them outside the future
candidate package surface.

Tournament-style workflows expose a readiness-only metadata object in
`team_orchestrator_summary.csi_evidence_scoring_readiness`. It says whether
sanitized CSI evidence scoring or batch replay metadata is configured for the
run and explicitly does not modify tournament score fields, Elo ratings, bracket
selection, winner selection, or final rankings.

When a tournament fixture provides `kind: csi-replay-evaluation-groups`, Phase
8F evaluates the groups through the sandbox provider and embeds batch readiness
metadata in the existing TeamOrchestrator summary. `aggregate_evidence_quality`
and `aggregate_replay_integrity` use the minimum group score so rejected groups
fail closed for readiness. `average_group_score` is informational only and is
not a ranking input.

Phase 8G also writes `artifacts/csi_evidence_pack.json` for CSI-configured
tournament runs and links a compact pack ref/fingerprint from
`team_orchestrator_summary.csi_evidence_pack`. The pack is readiness metadata
only and still does not modify `SCORE_FIELDS`, candidate scores, Elo, bracket
selection, winner selection, or rankings.

## Public Examples

Phase 8H documents public example manifests under `examples/wifi-csi-demo/`.
They cover parser CLI fixture review, n-of-1 replay with
`artifacts/csi_evidence_pack.json`, and tournament batch readiness metadata
with `artifacts/csi_evidence_pack.json`.

See `docs/wifi-csi-public-examples.md` for fresh-clone commands, artifact
inspection snippets, and the release-readiness checklist.

## Boundary

The parser is local fake/sample fixtures only. Report and summary artifacts must
not expose raw sample arrays, source IDs, absolute paths, or raw signal-value
keys such as `samples`, `raw_values`, `real`, `imag`, `amplitude`, `phase`, or
`rssi`.

Evidence packs apply the stricter portable-export boundary: no fixture refs,
private fixture filenames, source IDs, absolute paths, unsafe refs, provider
payload bodies, parser report bodies, parser summary bodies, raw CSI arrays, or
signal values are exported. Warnings and errors are represented only as counts
or sanitized parse-error category counts. Compatibility checks preserve the
same boundary: failure results expose counts and generic categories only, never
the rejected raw field names or values.

It uses no serial, MQTT, UDP, pcap, monitor mode, live capture, ESP32,
RTL8812AU, router, adapter, driver, packet capture, WiFi device probing,
network code, optional dependency, DSP package, sensor package, vital-sign
inference, clinical interpretation, diagnosis, treatment, monitoring, or
emergency triage.

Future real CSI parser support requires explicit consent, source-license
review, test fixtures, privacy review, safety review, hardware review, local
retention/export controls, and separate opt-in configuration.
