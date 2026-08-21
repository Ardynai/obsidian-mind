# User Data Analysis

> 77 nodes · cohesion 0.05

## Key Concepts

- **analyze_user_data()** (29 connections) — `somatic/flows/analyze.py`
- **grade_metric()** (19 connections) — `somatic/insights/engine.py`
- **ReferenceRange** (18 connections) — `somatic/insights/engine.py`
- **AnalysisReport** (17 connections) — `somatic/flows/analyze.py`
- **render_professional_summary()** (14 connections) — `somatic/flows/share.py`
- **AnalyzeFlowTests** (13 connections) — `tests/test_analyze_flow.py`
- **render_fhir_bundle()** (12 connections) — `somatic/flows/share.py`
- **engine.py** (12 connections) — `somatic/insights/engine.py`
- **summarize_series()** (12 connections) — `somatic/insights/engine.py`
- **PersonalInsightsEngineTests** (12 connections) — `tests/test_personal_insights.py`
- **analyze.py** (11 connections) — `somatic/flows/analyze.py`
- **share.py** (10 connections) — `somatic/flows/share.py`
- **_share()** (9 connections) — `somatic/cli/main.py`
- **_run_insights()** (8 connections) — `somatic/flows/analyze.py`
- **ShareFlowTests** (7 connections) — `tests/test_share_flow.py`
- **_render_result_block()** (6 connections) — `somatic/flows/share.py`
- **.test_requires_analysis_insight_consent()** (6 connections) — `tests/test_personal_insights.py`
- **.test_render_includes_report_fields_when_granted()** (6 connections) — `tests/test_share_flow.py`
- **.test_render_requires_professional_sharing_consent()** (6 connections) — `tests/test_share_flow.py`
- **_safe_markdown_field()** (5 connections) — `somatic/flows/share.py`
- **_frame_insight()** (5 connections) — `somatic/insights/engine.py`
- **.test_every_result_carries_informational_notice()** (5 connections) — `tests/test_personal_insights.py`
- **_as_numeric_series()** (4 connections) — `somatic/flows/analyze.py`
- **_clean_series()** (4 connections) — `somatic/insights/engine.py`
- **.test_emergency_input_short_circuits()** (4 connections) — `tests/test_analyze_flow.py`
- *... and 52 more nodes in this community*

## Relationships

- [Consent Ledger Management](Consent_Ledger_Management.md) (23 shared connections)
- [Consent and Experiment Storage](Consent_and_Experiment_Storage.md) (12 shared connections)
- [Presence and Research Rendering](Presence_and_Research_Rendering.md) (10 shared connections)
- [Advisory Model Client](Advisory_Model_Client.md) (9 shared connections)
- [Benchmarking and Scoring](Benchmarking_and_Scoring.md) (8 shared connections)
- [Table Statistics and Profiling](Table_Statistics_and_Profiling.md) (6 shared connections)
- [Health Data Ingestion](Health_Data_Ingestion.md) (2 shared connections)
- [N-of-1 Experiment Design](N-of-1_Experiment_Design.md) (1 shared connections)

## Source Files

- `somatic/cli/main.py`
- `somatic/flows/__init__.py`
- `somatic/flows/analyze.py`
- `somatic/flows/share.py`
- `somatic/insights/__init__.py`
- `somatic/insights/engine.py`
- `tests/test_analyze_flow.py`
- `tests/test_personal_insights.py`
- `tests/test_share_flow.py`

## Audit Trail

- EXTRACTED: 239 (68%)
- INFERRED: 112 (32%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*