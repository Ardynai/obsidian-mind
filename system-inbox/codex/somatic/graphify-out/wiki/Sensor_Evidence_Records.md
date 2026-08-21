# Sensor Evidence Records

> 33 nodes · cohesion 0.10

## Key Concepts

- **SensorStreamPlan** (16 connections) — `somatic/providers/sensors.py`
- **SensorObservation** (12 connections) — `somatic/providers/sensors.py`
- **SensorFeatureSet** (10 connections) — `somatic/providers/sensors.py`
- **SensorPrivacyPolicy** (9 connections) — `somatic/providers/sensors.py`
- **.evidence_record()** (9 connections) — `somatic/sensors/sandbox.py`
- **sensors.py** (8 connections) — `somatic/providers/sensors.py`
- **SensorProvider** (7 connections) — `somatic/providers/sensors.py`
- **SensorEvidenceRecord** (5 connections) — `somatic/providers/sensors.py`
- **.evidence_record()** (5 connections) — `somatic/providers/sensors.py`
- **.features()** (5 connections) — `somatic/providers/sensors.py`
- **.features()** (5 connections) — `somatic/sensors/sandbox.py`
- **.test_dataclasses_preserve_privacy_and_modality_boundaries()** (5 connections) — `tests/test_sensor_provider_scaffold.py`
- **.observations()** (4 connections) — `somatic/providers/sensors.py`
- **sandbox.py** (4 connections) — `somatic/sensors/sandbox.py`
- **.test_rejects_unknown_sensor_modality()** (4 connections) — `tests/test_sensor_provider_scaffold.py`
- **.plan_stream()** (3 connections) — `somatic/providers/sensors.py`
- **.privacy_policy()** (3 connections) — `somatic/providers/sensors.py`
- **.observations()** (3 connections) — `somatic/sensors/sandbox.py`
- **.replay_csi_fixtures()** (2 connections) — `somatic/providers/sensors.py`
- **_payload_sha256()** (2 connections) — `somatic/sensors/sandbox.py`
- **Return the local-first privacy policy before planning any stream.** (1 connections) — `somatic/providers/sensors.py`
- **Describe a sensor stream without touching hardware.** (1 connections) — `somatic/providers/sensors.py`
- **Return deterministic observations from fixtures or sandbox data.** (1 connections) — `somatic/providers/sensors.py`
- **Return deterministic feature metadata derived from observations.** (1 connections) — `somatic/providers/sensors.py`
- **Map feature metadata into Evidence Bus records.** (1 connections) — `somatic/providers/sensors.py`
- *... and 8 more nodes in this community*

## Relationships

- [Sandbox Sensor Provider](Sandbox_Sensor_Provider.md) (17 shared connections)
- [CSI Capture Planning](CSI_Capture_Planning.md) (6 shared connections)
- [Evidence Bus Sandbox](Evidence_Bus_Sandbox.md) (2 shared connections)
- [Evidence Measurement Planning](Evidence_Measurement_Planning.md) (2 shared connections)
- [Literature Evidence Providers](Literature_Evidence_Providers.md) (1 shared connections)
- [Workflow Evidence Analysis](Workflow_Evidence_Analysis.md) (1 shared connections)
- [Sensor Hardware Ingestion](Sensor_Hardware_Ingestion.md) (1 shared connections)

## Source Files

- `somatic/providers/sensors.py`
- `somatic/sensors/sandbox.py`
- `tests/test_sensor_provider_scaffold.py`

## Audit Trail

- EXTRACTED: 120 (90%)
- INFERRED: 14 (10%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*