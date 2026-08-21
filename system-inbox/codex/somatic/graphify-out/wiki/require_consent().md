# require_consent()

> God node · 62 connections · `somatic/safety/core.py`

**Community:** [Consent and Experiment Storage](Consent_and_Experiment_Storage.md)

## Connections by Relation

### calls
- ConsentRequiredError `EXTRACTED`
- run_research_loop() `INFERRED`
- run_evidence_loop() `EXTRACTED`
- evaluate_n_of_1() `INFERRED`
- run_science_loop() `INFERRED`
- scan_sensor() `EXTRACTED`
- ingest_csv_text() `INFERRED`
- grade_metric() `INFERRED`
- fuse_rf_vision() `EXTRACTED`
- _sensor_roster() `EXTRACTED`
- render_professional_summary() `INFERRED`
- render_presence() `INFERRED`
- _sensors_field() `EXTRACTED`
- _experiment() `EXTRACTED`
- render_fhir_bundle() `INFERRED`
- ingest_apple_health_xml() `INFERRED`
- summarize_series() `INFERRED`
- _sensors_scan() `EXTRACTED`
- require_live_csi() `INFERRED`
- _share() `EXTRACTED`

### contains
- core.py `EXTRACTED`

### imports
- main.py `EXTRACTED`
- api.py `EXTRACTED`
- live_video.py `EXTRACTED`
- roster.py `EXTRACTED`
- loop.py `EXTRACTED`
- fusion.py `EXTRACTED`

### rationale_for
- Return None when ``scope`` is granted; otherwise raise :class:`ConsentRequiredEr `EXTRACTED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*