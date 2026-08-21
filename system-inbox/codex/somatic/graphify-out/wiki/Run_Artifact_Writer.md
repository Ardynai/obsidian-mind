# Run Artifact Writer

> 9 nodes · cohesion 0.39

## Key Concepts

- **run_writer.py** (9 connections) — `somatic/run_writer.py`
- **write_run_artifacts()** (7 connections) — `somatic/run_writer.py`
- **_sensor_evidence_artifact_refs()** (4 connections) — `somatic/run_writer.py`
- **_artifact_hashes()** (3 connections) — `somatic/run_writer.py`
- **make_run_id()** (2 connections) — `somatic/run_writer.py`
- **_sha256()** (2 connections) — `somatic/run_writer.py`
- **_utc_now()** (2 connections) — `somatic/run_writer.py`
- **_write_json()** (2 connections) — `somatic/run_writer.py`
- **_write_text()** (2 connections) — `somatic/run_writer.py`

## Relationships

- [Workflow Evidence Analysis](Workflow_Evidence_Analysis.md) (4 shared connections)
- [Sensor Evidence Framework](Sensor_Evidence_Framework.md) (1 shared connections)

## Source Files

- `somatic/run_writer.py`

## Audit Trail

- EXTRACTED: 31 (94%)
- INFERRED: 2 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*