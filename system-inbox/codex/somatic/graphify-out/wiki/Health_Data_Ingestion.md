# Health Data Ingestion

> 60 nodes · cohesion 0.06

## Key Concepts

- **IngestPacketTests** (23 connections) — `tests/test_ingest.py`
- **ingest_csv_text()** (19 connections) — `somatic/ingest/csv.py`
- **load_readings()** (15 connections) — `somatic/ingest/store.py`
- **packet.py** (11 connections) — `somatic/ingest/packet.py`
- **_ingest()** (10 connections) — `somatic/cli/main.py`
- **ingest_apple_health()** (9 connections) — `somatic/ingest/apple_health.py`
- **Reading** (9 connections) — `somatic/ingest/packet.py`
- **append_readings()** (9 connections) — `somatic/ingest/store.py`
- **default_ingest_path()** (9 connections) — `somatic/ingest/store.py`
- **erase_stored_readings()** (9 connections) — `somatic/ingest/store.py`
- **apple_health.py** (8 connections) — `somatic/ingest/apple_health.py`
- **store.py** (8 connections) — `somatic/ingest/store.py`
- **ingest_csv()** (7 connections) — `somatic/ingest/csv.py`
- **reading_from_dict()** (7 connections) — `somatic/ingest/packet.py`
- **_isolate_ingest_env()** (7 connections) — `tests/test_ingest.py`
- **csv.py** (6 connections) — `somatic/ingest/csv.py`
- **.test_consent_erase_deletes_readings_store()** (6 connections) — `tests/test_ingest.py`
- **__init__.py** (5 connections) — `somatic/ingest/__init__.py`
- **notes_for_mixed_units()** (5 connections) — `somatic/ingest/packet.py`
- **parse_finite_value()** (5 connections) — `somatic/ingest/packet.py`
- **.test_analyze_and_share_surface_observation_dates()** (5 connections) — `tests/test_ingest.py`
- **test_ingest.py** (4 connections) — `tests/test_ingest.py`
- **_readings_for_metric()** (3 connections) — `somatic/experiments/n_of_1.py`
- **_metric_for_hk_type()** (3 connections) — `somatic/ingest/apple_health.py`
- **save_readings()** (3 connections) — `somatic/ingest/store.py`
- *... and 35 more nodes in this community*

## Relationships

- [Consent and Experiment Storage](Consent_and_Experiment_Storage.md) (34 shared connections)
- [Consent Ledger Management](Consent_Ledger_Management.md) (16 shared connections)
- [Benchmarking and Scoring](Benchmarking_and_Scoring.md) (9 shared connections)
- [N-of-1 Experiment Design](N-of-1_Experiment_Design.md) (3 shared connections)
- [User Data Analysis](User_Data_Analysis.md) (2 shared connections)

## Source Files

- `somatic/cli/main.py`
- `somatic/experiments/n_of_1.py`
- `somatic/ingest/__init__.py`
- `somatic/ingest/apple_health.py`
- `somatic/ingest/csv.py`
- `somatic/ingest/packet.py`
- `somatic/ingest/store.py`
- `tests/test_ingest.py`

## Audit Trail

- EXTRACTED: 214 (78%)
- INFERRED: 60 (22%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*