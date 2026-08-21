# Live CSI Adapter

> 80 nodes · cohesion 0.04

## Key Concepts

- **LiveCsiIngest** (28 connections) — `somatic/sensors/live_csi.py`
- **live_csi.py** (20 connections) — `somatic/sensors/live_csi.py`
- **LiveCsiIngestTests** (20 connections) — `tests/test_live_csi.py`
- **LiveCsiAdapter** (15 connections) — `somatic/sensors/live_csi.py`
- **LoopbackBindError** (14 connections) — `somatic/sensors/live_csi.py`
- **test_live_csi.py** (13 connections) — `tests/test_live_csi.py`
- **field_snapshot()** (13 connections) — `somatic/sensors/field.py`
- **field.py** (10 connections) — `somatic/sensors/field.py`
- **load_csi_features()** (9 connections) — `somatic/sensors/live_store.py`
- **_assert_no_raw()** (9 connections) — `tests/test_live_csi.py`
- **LiveCsiConsentFuseTests** (9 connections) — `tests/test_live_csi.py`
- **FieldSnapshotTests** (8 connections) — `tests/test_live_csi.py`
- **replace_ingest()** (7 connections) — `somatic/sensors/live_csi.py`
- **erase_csi_features()** (7 connections) — `somatic/sensors/live_store.py`
- **live_store.py** (7 connections) — `somatic/sensors/live_store.py`
- **get_ingest()** (6 connections) — `somatic/sensors/live_csi.py`
- **.ingest_line()** (6 connections) — `somatic/sensors/live_csi.py`
- **default_csi_features_path()** (6 connections) — `somatic/sensors/live_store.py`
- **.test_live_scan_with_grant_reads_loopback_features()** (6 connections) — `tests/test_live_csi.py`
- **default_bind_host()** (5 connections) — `somatic/sensors/live_csi.py`
- **default_udp_port()** (5 connections) — `somatic/sensors/live_csi.py`
- **is_loopback_bind()** (5 connections) — `somatic/sensors/live_csi.py`
- **.acquire()** (5 connections) — `somatic/sensors/live_csi.py`
- **append_csi_features()** (5 connections) — `somatic/sensors/live_store.py`
- **drain_serial_lines()** (4 connections) — `somatic/sensors/live_csi.py`
- *... and 55 more nodes in this community*

## Relationships

- [Sensor Hardware Ingestion](Sensor_Hardware_Ingestion.md) (33 shared connections)
- [Consent and Experiment Storage](Consent_and_Experiment_Storage.md) (17 shared connections)
- [Evidence Measurement Planning](Evidence_Measurement_Planning.md) (12 shared connections)
- [Consent Ledger Management](Consent_Ledger_Management.md) (11 shared connections)
- [CSI Packet Feature Extraction](CSI_Packet_Feature_Extraction.md) (7 shared connections)
- [CSI UDP Forwarder](CSI_UDP_Forwarder.md) (1 shared connections)
- [UI Bridge Security Tests](UI_Bridge_Security_Tests.md) (1 shared connections)
- [Benchmarking and Scoring](Benchmarking_and_Scoring.md) (1 shared connections)
- [Presence and Research Rendering](Presence_and_Research_Rendering.md) (1 shared connections)

## Source Files

- `somatic/sensors/field.py`
- `somatic/sensors/live_csi.py`
- `somatic/sensors/live_store.py`
- `tests/test_live_csi.py`
- `tests/test_video_pose.py`

## Audit Trail

- EXTRACTED: 288 (79%)
- INFERRED: 76 (21%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*