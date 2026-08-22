# WiFi CSI Data Formats

Phase 8B recorded a narrow data-format scaffold for local fake/sample WiFi CSI
fixtures. Phase 8C keeps those formats offline and fixture-only while adding
deterministic replay and malformed-row contract tests. Phase 8D routes n-of-1
fixture replay through the sandbox sensor provider and redacts public fixture
identifiers where needed. Phase 8F batches configured fixture groups for
tournament readiness metadata but adds no new file format. The source hints come
from read-only inspection of the staged Phase 8A references. Somatic does not
copy vendor parsers, run staged code, install dependencies, or depend on
upstream sample datasets.

## Supported Fixture Shapes

The standard-library parser supports only tiny files under
`fixtures/sensors/csi/`:

- ESP32-style CSV with `CSI_DATA` rows and a bracketed numeric CSI vector, as in
  `sample-esp32-csi.csv`.
- Amplitude/phase CSV with `frame_id`, `subcarrier`, `amplitude`, and `phase`
  columns, as in `sample-amplitude-phase.csv`. N-of-1 replay uses the neutral
  `csi-tabular-fixture.csv` ref for the same shape.
- Generic JSON-lines records with `type`, `frame_id`, optional `rssi`, and
  `samples`, as in `sample-csi-jsonl.jsonl`.

The parser also includes `invalid-csi-malformed.csv` for deterministic malformed
row reporting and `csi-parser-report-placeholder.json` as a static placeholder
boundary fixture.

Phase 8C adds edge-case fixtures for replay validation:

- `edge-blank-lines-unknown-columns.csv`: blank CSV lines are ignored; unknown
  columns are ignored and reported only as a count.
- `invalid-esp32-short-vector.csv`: short or odd local fixture vectors are
  rejected with `invalid_vector_length`.
- `invalid-csi-jsonl.jsonl`: invalid JSONL rows and rows without a usable local
  record payload are reported while valid rows still parse.
- `mixed-valid-invalid-csi.csv`: mixed valid/invalid CSV rows produce `partial`.
- `unsupported-csi.npz` and `unsupported-csi.pcap`: unsupported extensions are
  rejected before format detection.

CSV `rows_seen` counts non-blank data rows after the header. JSONL `rows_seen`
counts non-blank records. Supported parser status values are `parsed`,
`partial`, and `rejected`.

## Excluded Formats

Phase 8B does not parse pcap, Nexmon, radiotap, monitor-mode captures, `.npz`,
serial streams, MQTT messages, UDP packets, SD-card dumps, router exports, or
hardware-adapter output. Phase 8C keeps `.npz` and `.pcap` as explicit rejected
fixtures. Phase 8D and Phase 8F do not add any new file format or live provider.
`.npz` support would require non-standard dependencies, so future sequence
fixtures must be represented as Somatic-owned CSV or JSON samples unless a later
review approves otherwise.

## Boundary

These are local fake/sample fixtures only. There is no serial, no MQTT, no UDP,
no pcap, no monitor mode, no live capture, no hardware access, no WiFi device
probing, no network code, no DSP package, no sensor package, no vital-sign
inference, and no medical claim.

Future real parser support requires explicit consent, source-license review,
test fixtures owned or cleared for use, privacy review, safety review, hardware
review, retention/export controls, and separate opt-in configuration.
