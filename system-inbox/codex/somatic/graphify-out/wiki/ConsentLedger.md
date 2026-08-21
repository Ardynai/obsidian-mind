# ConsentLedger

> God node · 147 connections · `somatic/consent/ledger.py`

**Community:** [Consent Ledger Management](Consent_Ledger_Management.md)

## Connections by Relation

### calls
- .test_live_scan_with_grant_is_features_only() `EXTRACTED`
- .test_erase_deletes_file_and_leaves_all_off() `INFERRED`
- .test_consent_erase_deletes_readings_store() `INFERRED`
- .test_live_scan_with_grant_reads_loopback_features() `INFERRED`
- .test_pose_model_stays_off() `INFERRED`
- .test_requires_analysis_insight_consent() `INFERRED`
- .test_render_includes_report_fields_when_granted() `INFERRED`
- .test_render_requires_professional_sharing_consent() `INFERRED`
- .test_adapter_waiting_features_have_empty_joints() `EXTRACTED`
- .test_analyze_requires_ai_advisory_consent_without_http() `INFERRED`
- .test_http_redirects_are_refused_and_do_not_follow_auth() `INFERRED`
- .test_save_round_trip_and_owner_only_mode() `INFERRED`
- .test_requires_analysis_insight() `INFERRED`
- .test_analyze_and_share_surface_observation_dates() `INFERRED`
- .test_requires_analysis_insight_consent() `INFERRED`
- .test_every_result_carries_informational_notice() `INFERRED`
- .test_live_scan_without_grant_is_refused() `EXTRACTED`
- .test_analyze_returns_informational_advisory_from_mock() `INFERRED`
- .test_authoritative_model_text_returns_safe_fallback() `INFERRED`
- .test_emergency_input_skips_endpoint() `INFERRED`

### contains
- ledger.py `EXTRACTED`

### imports
- test_video_pose.py `EXTRACTED`
- live_video.py `EXTRACTED`
- roster.py `EXTRACTED`
- loop.py `EXTRACTED`
- fusion.py `EXTRACTED`

### method
- .grant() `EXTRACTED`
- .revoke() `EXTRACTED`
- .is_granted() `EXTRACTED`
- .granted_scopes() `EXTRACTED`
- .purge_user_data() `EXTRACTED`
- .to_dict() `EXTRACTED`
- .__init__() `EXTRACTED`

### rationale_for
- In-memory consent ledger with JSON round-trip helpers.      All catalog scopes `EXTRACTED`

### references
- run_evidence_loop() `EXTRACTED`
- scan_sensor() `EXTRACTED`
- fuse_rf_vision() `EXTRACTED`
- _live_scan() `EXTRACTED`
- .from_dict() `EXTRACTED`
- fuse_csi_units() `EXTRACTED`
- require_live_video() `EXTRACTED`
- .acquire() `EXTRACTED`
- .plan() `EXTRACTED`
- ._from_dict_strict() `EXTRACTED`

### uses
- SensorHardwareDisabled `INFERRED`
- ConsentRequiredError `INFERRED`
- EvidenceGrade `INFERRED`
- LiveCsiIngest `INFERRED`
- LiveVideoIngest `INFERRED`
- LiveVideoAdapter `INFERRED`
- AdvisoryFramingError `INFERRED`
- HypothesisSpec `INFERRED`
- AdvisoryResult `INFERRED`
- AdvisoryModelClient `INFERRED`
- AdvisoryModelConfig `INFERRED`
- ReferenceRange `INFERRED`
- AnalysisReport `INFERRED`
- AdvisoryConfigError `INFERRED`
- LiveCsiAdapter `INFERRED`
- LoopbackBindError `INFERRED`
- InterventionTag `INFERRED`
- EvidenceLoopReport `INFERRED`
- SandboxModalityAdapter `INFERRED`
- AdvisoryHttpError `INFERRED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*