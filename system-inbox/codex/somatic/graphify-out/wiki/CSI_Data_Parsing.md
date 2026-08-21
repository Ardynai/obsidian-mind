# CSI Data Parsing

> 104 nodes · cohesion 0.05

## Key Concepts

- **csi_parser.py** (38 connections) — `somatic/sensors/csi_parser.py`
- **WifiCsiParserTests** (28 connections) — `tests/test_wifi_csi_parser.py`
- **build_csi_parser_artifacts()** (24 connections) — `somatic/sensors/csi_parser.py`
- **parse_csi_file()** (17 connections) — `somatic/sensors/csi_parser.py`
- **parse_csi_fixture()** (17 connections) — `somatic/sensors/csi_parser.py`
- **_parse_esp32_csv()** (15 connections) — `somatic/sensors/csi_parser.py`
- **CsiParsedFile** (14 connections) — `somatic/sensors/csi_formats.py`
- **CsiParserReport** (12 connections) — `somatic/sensors/csi_formats.py`
- **csi_formats.py** (12 connections) — `somatic/sensors/csi_formats.py`
- **_parse_amplitude_phase_csv()** (12 connections) — `somatic/sensors/csi_parser.py`
- **csi_scoring.py** (12 connections) — `somatic/sensors/csi_scoring.py`
- **WifiCsiEvidenceScoringTests** (12 connections) — `tests/test_wifi_csi_evidence_scoring.py`
- **CsiFrame** (11 connections) — `somatic/sensors/csi_formats.py`
- **._assert_scoring_payload_is_sanitized()** (11 connections) — `tests/test_wifi_csi_evidence_scoring.py`
- **._assert_messages_are_report_safe()** (11 connections) — `tests/test_wifi_csi_parser.py`
- **score_csi_replay_evidence()** (10 connections) — `somatic/sensors/csi_scoring.py`
- **CsiSample** (9 connections) — `somatic/sensors/csi_formats.py`
- **_parse_jsonl()** (9 connections) — `somatic/sensors/csi_parser.py`
- **_parsed_with_report()** (9 connections) — `somatic/sensors/csi_parser.py`
- **CsiParseError** (8 connections) — `somatic/sensors/csi_formats.py`
- **._assert_no_forbidden_report_keys()** (8 connections) — `tests/test_wifi_csi_parser.py`
- **_public_parse_error()** (7 connections) — `somatic/sensors/csi_parser.py`
- **_public_parsed_summary()** (7 connections) — `somatic/sensors/csi_parser.py`
- **_public_report_payload()** (7 connections) — `somatic/sensors/csi_parser.py`
- **_rejected_file()** (7 connections) — `somatic/sensors/csi_parser.py`
- *... and 79 more nodes in this community*

## Relationships

- [Sensor Evidence Provider Validation](Sensor_Evidence_Provider_Validation.md) (12 shared connections)
- [CSI Evidence Pack Construction](CSI_Evidence_Pack_Construction.md) (3 shared connections)
- [CSI Batch Readiness](CSI_Batch_Readiness.md) (2 shared connections)
- [Benchmarking and Scoring](Benchmarking_and_Scoring.md) (2 shared connections)
- [CSI Capture Planning](CSI_Capture_Planning.md) (1 shared connections)
- [Sandbox Sensor Provider](Sandbox_Sensor_Provider.md) (1 shared connections)
- [CSI Evidence Pack Validation](CSI_Evidence_Pack_Validation.md) (1 shared connections)
- [CSI Evidence Pack Tests](CSI_Evidence_Pack_Tests.md) (1 shared connections)
- [Blackboard Build Logic](Blackboard_Build_Logic.md) (1 shared connections)

## Source Files

- `somatic/sensors/csi_formats.py`
- `somatic/sensors/csi_parser.py`
- `somatic/sensors/csi_scoring.py`
- `tests/test_wifi_csi_evidence_scoring.py`
- `tests/test_wifi_csi_parser.py`

## Audit Trail

- EXTRACTED: 503 (89%)
- INFERRED: 61 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*