# Consent and Experiment Storage

> 88 nodes · cohesion 0.08

## Key Concepts

- **api.py** (103 connections) — `somatic/bridge/api.py`
- **require_consent()** (62 connections) — `somatic/safety/core.py`
- **load_ledger()** (47 connections) — `somatic/consent/store.py`
- **Any** (40 connections)
- **dispatch()** (38 connections) — `somatic/bridge/api.py`
- **BridgeError** (21 connections) — `somatic/bridge/api.py`
- **load_live_consent()** (21 connections) — `somatic/sensors/live_consent.py`
- **InterventionTag** (13 connections) — `somatic/experiments/n_of_1.py`
- **_privacy()** (13 connections) — `somatic/bridge/api.py`
- **load_tags()** (12 connections) — `somatic/experiments/store.py`
- **ingest_apple_health_xml()** (12 connections) — `somatic/ingest/apple_health.py`
- **normalize_observed_at()** (12 connections) — `somatic/ingest/packet.py`
- **_sensors_field()** (12 connections) — `somatic/bridge/api.py`
- **_consent()** (12 connections) — `somatic/cli/main.py`
- **_experiment()** (12 connections) — `somatic/cli/main.py`
- **save_live_consent()** (12 connections) — `somatic/sensors/live_consent.py`
- **default_consent_path()** (11 connections) — `somatic/consent/store.py`
- **_sensors_scan()** (11 connections) — `somatic/bridge/api.py`
- **_analyze()** (10 connections) — `somatic/bridge/api.py`
- **_erase_all()** (10 connections) — `somatic/bridge/api.py`
- **_experiment_tag()** (10 connections) — `somatic/bridge/api.py`
- **_share()** (10 connections) — `somatic/bridge/api.py`
- **live_consent.py** (10 connections) — `somatic/sensors/live_consent.py`
- **default_experiment_path()** (9 connections) — `somatic/experiments/store.py`
- **store.py** (9 connections) — `somatic/experiments/store.py`
- *... and 63 more nodes in this community*

## Relationships

- [Sensor Hardware Ingestion](Sensor_Hardware_Ingestion.md) (42 shared connections)
- [Health Data Ingestion](Health_Data_Ingestion.md) (34 shared connections)
- [Benchmarking and Scoring](Benchmarking_and_Scoring.md) (28 shared connections)
- [Consent Ledger Management](Consent_Ledger_Management.md) (25 shared connections)
- [Presence and Research Rendering](Presence_and_Research_Rendering.md) (22 shared connections)
- [Live CSI Adapter](Live_CSI_Adapter.md) (17 shared connections)
- [UI Bridge Security Tests](UI_Bridge_Security_Tests.md) (15 shared connections)
- [Evidence Measurement Planning](Evidence_Measurement_Planning.md) (15 shared connections)
- [User Data Analysis](User_Data_Analysis.md) (12 shared connections)
- [N-of-1 Experiment Design](N-of-1_Experiment_Design.md) (11 shared connections)
- [Consent Ledger Operations](Consent_Ledger_Operations.md) (7 shared connections)
- [Advisory Model Client](Advisory_Model_Client.md) (5 shared connections)

## Source Files

- `somatic/bridge/api.py`
- `somatic/cli/main.py`
- `somatic/consent/store.py`
- `somatic/experiments/n_of_1.py`
- `somatic/experiments/store.py`
- `somatic/ingest/apple_health.py`
- `somatic/ingest/packet.py`
- `somatic/safety/core.py`
- `somatic/sensors/live_consent.py`
- `somatic/sensors/live_csi.py`
- `somatic/sensors/live_video.py`
- `tests/test_consent_store.py`

## Audit Trail

- EXTRACTED: 750 (89%)
- INFERRED: 92 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*