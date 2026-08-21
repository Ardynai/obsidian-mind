# UI Bridge Security Tests

> 38 nodes · cohesion 0.10

## Key Concepts

- **UiBridgeTests** (36 connections) — `tests/test_ui_bridge.py`
- **_request()** (23 connections) — `tests/test_ui_bridge.py`
- **save_ledger()** (20 connections) — `somatic/consent/store.py`
- **.test_field_live_after_grant_omits_skeleton_and_raw()** (4 connections) — `tests/test_ui_bridge.py`
- **.test_field_live_without_grant_is_refused()** (4 connections) — `tests/test_ui_bridge.py`
- **.test_field_sandbox_tick_is_features_only()** (4 connections) — `tests/test_ui_bridge.py`
- **.test_ingest_preview_does_not_store_until_save()** (4 connections) — `tests/test_ui_bridge.py`
- **.test_parasite_does_not_identify_species()** (4 connections) — `tests/test_ui_bridge.py`
- **.test_remedy_defaults_to_none_on_honest_null()** (4 connections) — `tests/test_ui_bridge.py`
- **.test_research_biosecurity_is_refused()** (4 connections) — `tests/test_ui_bridge.py`
- **.test_research_honest_null_when_nothing_binds()** (4 connections) — `tests/test_ui_bridge.py`
- **.test_right_to_erasure_clears_stores()** (4 connections) — `tests/test_ui_bridge.py`
- **.test_sensor_scan_is_features_only()** (4 connections) — `tests/test_ui_bridge.py`
- **.tearDown()** (2 connections) — `tests/test_ui_bridge.py`
- **.test_analyze_without_consent_is_blocked()** (2 connections) — `tests/test_ui_bridge.py`
- **.test_crisis_input_routes_to_988_guidance()** (2 connections) — `tests/test_ui_bridge.py`
- **.test_emergency_input_returns_clinician_banner_without_consent()** (2 connections) — `tests/test_ui_bridge.py`
- **.test_live_grant_without_subject_consent_is_refused()** (2 connections) — `tests/test_ui_bridge.py`
- **.test_live_sensor_endpoint_is_refused()** (2 connections) — `tests/test_ui_bridge.py`
- **.test_non_loopback_host_header_is_refused()** (2 connections) — `tests/test_ui_bridge.py`
- **.test_non_loopback_origin_is_refused()** (2 connections) — `tests/test_ui_bridge.py`
- **.test_research_without_consent_is_blocked()** (2 connections) — `tests/test_ui_bridge.py`
- **.test_share_without_consent_is_blocked()** (2 connections) — `tests/test_ui_bridge.py`
- **.test_status_is_legible_when_everything_is_off()** (2 connections) — `tests/test_ui_bridge.py`
- **.test_suggestions_without_consent_are_blocked()** (2 connections) — `tests/test_ui_bridge.py`
- *... and 13 more nodes in this community*

## Relationships

- [Consent and Experiment Storage](Consent_and_Experiment_Storage.md) (15 shared connections)
- [UI Bridge Isolation](UI_Bridge_Isolation.md) (3 shared connections)
- [UI Screenshot Capture](UI_Screenshot_Capture.md) (1 shared connections)
- [Benchmarking and Scoring](Benchmarking_and_Scoring.md) (1 shared connections)
- [Consent Ledger Operations](Consent_Ledger_Operations.md) (1 shared connections)
- [Consent Ledger Management](Consent_Ledger_Management.md) (1 shared connections)
- [Live CSI Adapter](Live_CSI_Adapter.md) (1 shared connections)

## Source Files

- `somatic/consent/store.py`
- `tests/test_ui_bridge.py`

## Audit Trail

- EXTRACTED: 123 (78%)
- INFERRED: 34 (22%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*