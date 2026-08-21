# Advisory Model Client

> 53 nodes · cohesion 0.07

## Key Concepts

- **AdvisoryModelClient** (21 connections) — `somatic/advisory/adapter.py`
- **AdvisoryModelConfig** (20 connections) — `somatic/advisory/adapter.py`
- **AiAdvisoryAdapterTests** (17 connections) — `tests/test_ai_advisory_adapter.py`
- **AdvisoryConfigError** (15 connections) — `somatic/advisory/adapter.py`
- **adapter.py** (12 connections) — `somatic/advisory/adapter.py`
- **AdvisoryHttpError** (11 connections) — `somatic/advisory/adapter.py`
- **._config()** (9 connections) — `tests/test_ai_advisory_adapter.py`
- **_NoRedirectHandler** (8 connections) — `somatic/advisory/adapter.py`
- **test_ai_advisory_adapter.py** (8 connections) — `tests/test_ai_advisory_adapter.py`
- **.analyze()** (7 connections) — `somatic/advisory/adapter.py`
- **.from_env()** (7 connections) — `somatic/advisory/adapter.py`
- **._post_chat()** (6 connections) — `somatic/advisory/adapter.py`
- **_model_config_from_args()** (6 connections) — `somatic/cli/main.py`
- **models.py** (5 connections) — `somatic/advisory/models.py`
- **.test_analyze_requires_ai_advisory_consent_without_http()** (5 connections) — `tests/test_ai_advisory_adapter.py`
- **.test_http_redirects_are_refused_and_do_not_follow_auth()** (5 connections) — `tests/test_ai_advisory_adapter.py`
- **.test_v1_base_url_is_not_doubled()** (5 connections) — `tests/test_ai_advisory_adapter.py`
- **.validate()** (4 connections) — `somatic/advisory/adapter.py`
- **get_model_option()** (4 connections) — `somatic/advisory/models.py`
- **.setUp()** (4 connections) — `tests/test_ai_advisory_adapter.py`
- **.test_analyze_returns_informational_advisory_from_mock()** (4 connections) — `tests/test_ai_advisory_adapter.py`
- **.test_authoritative_model_text_returns_safe_fallback()** (4 connections) — `tests/test_ai_advisory_adapter.py`
- **.test_emergency_input_skips_endpoint()** (4 connections) — `tests/test_ai_advisory_adapter.py`
- **.test_https_or_loopback_required_when_key_set()** (4 connections) — `tests/test_ai_advisory_adapter.py`
- **.test_metadata_ip_encodings_rejected_when_key_set()** (4 connections) — `tests/test_ai_advisory_adapter.py`
- *... and 28 more nodes in this community*

## Relationships

- [Presence and Research Rendering](Presence_and_Research_Rendering.md) (19 shared connections)
- [Consent Ledger Management](Consent_Ledger_Management.md) (15 shared connections)
- [User Data Analysis](User_Data_Analysis.md) (9 shared connections)
- [Consent and Experiment Storage](Consent_and_Experiment_Storage.md) (5 shared connections)
- [Network Safety and SSRF](Network_Safety_and_SSRF.md) (3 shared connections)
- [Benchmarking and Scoring](Benchmarking_and_Scoring.md) (3 shared connections)
- [Fabric Federation Configuration](Fabric_Federation_Configuration.md) (1 shared connections)

## Source Files

- `somatic/advisory/__init__.py`
- `somatic/advisory/adapter.py`
- `somatic/advisory/models.py`
- `somatic/cli/main.py`
- `tests/test_ai_advisory_adapter.py`

## Audit Trail

- EXTRACTED: 164 (66%)
- INFERRED: 85 (34%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*