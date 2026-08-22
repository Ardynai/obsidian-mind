# Sensor Roadmap

Somatic sensors are local-first and private by default. Phase 7A defines the
first standard-library sensor provider boundary and a fake-backed sandbox
provider for n-of-1 planning. Phase 7B adds a fake-backed WiFi CSI planning
scaffold and reference inventory. Phase 8A stages WiFi CSI reference sources
outside the Somatic checkout for read-only source review only.

## Scaffolded Modalities

- WiFi CSI.
- Video.
- 3D video.
- Thermal.
- Audio.
- Wearable.
- Environmental.

## Current Status

No live sensor integration is implemented. The Phase 7A runner emits
deterministic sandbox artifacts only:

- `sensor_stream_plan.json`
- `sensor_observations.json`
- `sensor_feature_set.json`
- `sensor_evidence_record.json`
- `n_of_1_baseline_placeholder.json`
- `n_of_1_summary.json`

The sandbox provider does not access hardware, run WiFi CSI capture, use
camera/microphone/audio/wearable/BLE/WiFi/thermal/environmental devices, call
networks, export personal data, perform real monitoring, or make clinical
claims.

The Phase 7B CSI scaffold is disabled by default and metadata-only. It does not
access ESP32, RTL8812AU, routers, WiFi adapters, drivers, monitor mode, packet
capture, WiFi device probing, raw RF/CSI data, DSP packages, sensor packages,
or network code. Raw RF/CSI data is local-first and private by default; none is
collected, retained, or exported.

Phase 8A source staging records exact paths, commits, license status, hardware
assumptions, capture paths, data formats, dependencies, safe-use notes, and
non-adoption rules for `NTUMARS/Awesome-WiFi-CSI-Sensing`,
`thu4n/ESP32-WiFi-Sensing`, and `MaliosDark/wifi-3d-fusion`.
`ruvnet/RuView` is conditional reference-only for reassessment. No staged source
is adopted, imported, copied, executed, installed, or depended on. Phase 10G
adds booth-first WiFi CSI planning metadata for a future single-subject
controlled booth, not live sensing. Phase 10H adds the shared real-mode
readiness gate for CSI and document adapters. Phase 10I adds shared public
surface invariants, and Phase 10J records the checkpoint and next safe lanes.
Live sensing remains disabled.

## Future Sequence

1. Define modality-specific schemas.
2. Add offline sample pack validators.
3. Add local-only parser fixtures.
4. Add privacy and consent checks.
5. Add optional lane extras.
6. Consider live capture adapters only after explicit configuration and safety review.

## Safety Defaults

- No hidden surveillance use cases.
- No sensor access without explicit configuration.
- No remote upload by default.
- Personal data stays local unless explicitly exported.
- Camera, microphone, CSI, wearable, thermal, environmental, and baseline data
  must not leave the machine without explicit configuration and consent.
- Future real WiFi CSI requires explicit consent from the operator, intended
  subject, and all potentially affected people in the sensing area. Do not use
  it in shared, public, workplace, household, or care environments unless
  bystanders are informed and consent is practical.
- Future real-mode adapters must also pass license review, privacy review,
  hardware review, model artifact review, dependency review, and network policy
  review before runtime behavior can be considered.
- WiFi CSI, RSSI, pcap, serial CSI logs, SD-card CSVs, raw RF/CSI, derived
  features, embeddings, ReID sequences, pose outputs, skeleton outputs, and
  activity labels are sensitive by default.
- No diagnosis, treatment, emergency triage, clinician replacement, or real
  monitoring from sandbox artifacts.
