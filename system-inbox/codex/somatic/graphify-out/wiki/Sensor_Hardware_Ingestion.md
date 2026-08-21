# Sensor Hardware Ingestion

> 126 nodes · cohesion 0.04

## Key Concepts

- **SensorHardwareDisabled** (47 connections) — `somatic/evidence_bus/sandbox_adapters.py`
- **test_video_pose.py** (38 connections) — `tests/test_video_pose.py`
- **LiveVideoIngest** (28 connections) — `somatic/sensors/live_video.py`
- **LiveVideoAdapter** (27 connections) — `somatic/sensors/live_video.py`
- **LiveSensorConsent** (25 connections) — `somatic/sensors/live_consent.py`
- **live_video.py** (25 connections) — `somatic/sensors/live_video.py`
- **roster.py** (23 connections) — `somatic/sensors/roster.py`
- **scan_sensor()** (20 connections) — `somatic/sensors/roster.py`
- **MediaPipePoseExtractor** (20 connections) — `somatic/sensors/video_pose.py`
- **RawEvidence** (19 connections) — `somatic/evidence_bus/records.py`
- **VideoProcessor** (19 connections) — `somatic/sensors/video_processor.py`
- **video_pose.py** (17 connections) — `somatic/sensors/video_pose.py`
- **_sensor_roster()** (14 connections) — `somatic/cli/main.py`
- **EvidenceLoopReport** (13 connections) — `somatic/evidence_bus/loop.py`
- **_live_scan()** (13 connections) — `somatic/sensors/roster.py`
- **LiveVideoConsentTests** (13 connections) — `tests/test_video_pose.py`
- **strip_frame_payload()** (12 connections) — `somatic/sensors/video_processor.py`
- **require_live_csi()** (11 connections) — `somatic/sensors/live_csi.py`
- **video_processor.py** (11 connections) — `somatic/sensors/video_processor.py`
- **_FakePoseExtractor** (11 connections) — `tests/test_video_pose.py`
- **FieldAndFusionVideoTests** (11 connections) — `tests/test_video_pose.py`
- **start_ingest()** (10 connections) — `somatic/sensors/live_csi.py`
- **require_live_video()** (10 connections) — `somatic/sensors/live_video.py`
- **list_sensor_lanes()** (10 connections) — `somatic/sensors/roster.py`
- **VideoProcessorTests** (10 connections) — `tests/test_video_pose.py`
- *... and 101 more nodes in this community*

## Relationships

- [Consent and Experiment Storage](Consent_and_Experiment_Storage.md) (42 shared connections)
- [Evidence Measurement Planning](Evidence_Measurement_Planning.md) (38 shared connections)
- [Live CSI Adapter](Live_CSI_Adapter.md) (33 shared connections)
- [Consent Ledger Management](Consent_Ledger_Management.md) (20 shared connections)
- [Benchmarking and Scoring](Benchmarking_and_Scoring.md) (9 shared connections)
- [Presence and Research Rendering](Presence_and_Research_Rendering.md) (7 shared connections)
- [Biomodel Evidence Processing](Biomodel_Evidence_Processing.md) (1 shared connections)
- [Sensor Evidence Records](Sensor_Evidence_Records.md) (1 shared connections)
- [Evidence Bus Sandbox](Evidence_Bus_Sandbox.md) (1 shared connections)
- [Phase 12 Closeout Summary](Phase_12_Closeout_Summary.md) (1 shared connections)

## Source Files

- `somatic/cli/main.py`
- `somatic/evidence_bus/loop.py`
- `somatic/evidence_bus/records.py`
- `somatic/evidence_bus/sandbox_adapters.py`
- `somatic/sensors/live_consent.py`
- `somatic/sensors/live_csi.py`
- `somatic/sensors/live_video.py`
- `somatic/sensors/roster.py`
- `somatic/sensors/video_pose.py`
- `somatic/sensors/video_processor.py`
- `tests/test_sensor_roster.py`
- `tests/test_video_pose.py`

## Audit Trail

- EXTRACTED: 598 (78%)
- INFERRED: 169 (22%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*