import ast
import importlib
import json
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CSI_FIXTURE_DIR = REPO_ROOT / "fixtures" / "sensors" / "csi"
FORBIDDEN_CSI_REPORT_KEYS = {
    "samples",
    "raw_values",
    "real",
    "imag",
    "amplitude",
    "phase",
    "rssi",
    "source_id",
    "source_ids",
}
FORBIDDEN_CSI_REPORT_WORDS = tuple(sorted(FORBIDDEN_CSI_REPORT_KEYS))


class WifiCsiParserTests(unittest.TestCase):
    def test_parser_modules_import_without_optional_dependencies(self):
        formats = importlib.import_module("somatic.sensors.csi_formats")
        parser = importlib.import_module("somatic.sensors.csi_parser")
        batch = importlib.import_module("somatic.sensors.csi_batch")

        self.assertTrue(hasattr(formats, "CsiSample"))
        self.assertTrue(hasattr(formats, "CsiParsedFile"))
        self.assertTrue(hasattr(formats, "CsiParserReport"))
        self.assertTrue(hasattr(formats, "CsiParseError"))
        self.assertTrue(hasattr(parser, "parse_csi_file"))
        self.assertTrue(hasattr(parser, "parse_csi_fixture"))
        self.assertTrue(hasattr(batch, "evaluate_csi_replay_batch"))

    def test_parser_contract_is_explicit_and_report_safe(self):
        from somatic.sensors.csi_formats import (
            CSI_PARSER_CONTRACT,
            CSI_PARSER_CONTRACT_VERSION,
            CSI_PARSER_SANITIZED_FORBIDDEN_KEYS,
            CsiFrame,
            CsiParseError,
            CsiSample,
        )

        self.assertEqual(CSI_PARSER_CONTRACT_VERSION, 1)
        self.assertEqual(
            set(CSI_PARSER_SANITIZED_FORBIDDEN_KEYS),
            FORBIDDEN_CSI_REPORT_KEYS,
        )
        self.assertIn("parsed_file", CSI_PARSER_CONTRACT["records"])
        self.assertIn("parse_error", CSI_PARSER_CONTRACT["records"])
        self.assertIn("sanitized_summary", CSI_PARSER_CONTRACT["artifacts"])
        self.assertIn("evidence_scoring", CSI_PARSER_CONTRACT["artifacts"])
        self.assertIn("parse_errors", CSI_PARSER_CONTRACT["report_fields"])
        self.assertTrue(CSI_PARSER_CONTRACT["privacy"]["summary_output_only"])
        self.assertTrue(CSI_PARSER_CONTRACT["privacy"]["fixture_only"])

        error = CsiParseError(
            row_number=2,
            line_number=2,
            code="required_fields_missing",
            message="row 2 malformed: required fixture fields missing",
            source_format="amplitude-phase-csv",
            recoverable=True,
        )
        self.assertEqual(
            set(error.to_dict()),
            {
                "row_number",
                "line_number",
                "code",
                "message",
                "source_format",
                "recoverable",
            },
        )
        self._assert_messages_are_report_safe(error.to_dict())

        sample_summary = CsiSample(
            sample_index=1,
            amplitude=1.0,
            phase=0.5,
        ).to_summary_dict()
        self._assert_no_forbidden_report_keys(sample_summary)
        self.assertNotIn("label", sample_summary)
        self.assertEqual(sample_summary["label_present"], False)

        frame_summary = CsiFrame(
            frame_id="frame-1",
            source_format="generic-csi-jsonl",
            timestamp=0.0,
            source_id="mac-like-source-id",
            samples=(),
            label="fixture-label",
        ).to_summary_dict()
        self.assertNotIn("frame_id", frame_summary)
        self.assertNotIn("source_id", frame_summary)
        self.assertEqual(frame_summary["source_present"], True)
        self.assertNotIn("label", frame_summary)
        self.assertEqual(frame_summary["label_present"], True)

    def test_parser_capabilities_are_fixture_only_and_standard_library(self):
        from somatic.sensors.csi_formats import CSI_PARSER_CAPABILITIES

        self.assertEqual(
            CSI_PARSER_CAPABILITIES["parser_id"],
            "somatic-csi-fixture-parser-v1",
        )
        self.assertEqual(
            CSI_PARSER_CAPABILITIES["dependency_profile"],
            "python-standard-library",
        )
        self.assertIn("esp32-csi-csv", CSI_PARSER_CAPABILITIES["supported_formats"])
        self.assertIn(
            "amplitude-phase-csv",
            CSI_PARSER_CAPABILITIES["supported_formats"],
        )
        self.assertIn(
            "generic-csi-jsonl",
            CSI_PARSER_CAPABILITIES["supported_formats"],
        )
        for key in (
            "fixture_only",
            "local_file_only",
            "no_live_capture",
            "no_serial_access",
            "no_network_calls",
            "no_mqtt_udp_listener",
            "no_packet_capture",
            "no_monitor_mode",
            "no_medical_or_clinical_claims",
        ):
            with self.subTest(key=key):
                self.assertTrue(CSI_PARSER_CAPABILITIES[key])

    def test_replay_parses_every_local_csi_fixture_with_stable_sanitized_outputs(self):
        from somatic.sensors.csi_parser import parse_csi_fixture

        fixture_names = sorted(path.name for path in CSI_FIXTURE_DIR.iterdir() if path.is_file())
        self.assertIn("sample-esp32-csi.csv", fixture_names)
        self.assertIn("csi-parser-report-placeholder.json", fixture_names)

        for fixture_name in fixture_names:
            with self.subTest(fixture_name=fixture_name):
                left_parsed, left_report = parse_csi_fixture(fixture_name, repo_root=REPO_ROOT)
                right_parsed, right_report = parse_csi_fixture(fixture_name, repo_root=REPO_ROOT)

                left_summary = left_parsed.to_summary_dict()
                right_summary = right_parsed.to_summary_dict()
                left_report_payload = left_report.to_dict()
                right_report_payload = right_report.to_dict()

                self.assertEqual(
                    self._stable_json(left_summary),
                    self._stable_json(right_summary),
                )
                self.assertEqual(
                    self._stable_json(left_report_payload),
                    self._stable_json(right_report_payload),
                )
                for payload in (
                    left_summary,
                    right_summary,
                    left_report_payload,
                    right_report_payload,
                ):
                    self._assert_no_forbidden_report_keys(payload)
                    self._assert_messages_are_report_safe(payload)
                    self._assert_no_absolute_paths(payload)

    def test_parses_esp32_style_csv_fixture_deterministically(self):
        from somatic.sensors.csi_parser import parse_csi_fixture

        parsed, report = parse_csi_fixture(
            "sample-esp32-csi.csv",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(report.status, "parsed")
        self.assertEqual(report.source_format, "esp32-csi-csv")
        self.assertEqual(
            report.file_size_bytes,
            self._normalized_fixture_text_size("sample-esp32-csi.csv"),
        )
        self.assertEqual(report.rows_seen, 2)
        self.assertEqual(report.malformed_rows, 0)
        self.assertEqual(parsed.source_format, "esp32-csi-csv")
        self.assertEqual(parsed.frame_count, 2)
        self.assertEqual(parsed.sample_count, 8)
        self.assertEqual(parsed.frames[0].source_id, "esp32-fixture")
        self.assertEqual(parsed.frames[0].samples[0].real, 1.0)
        self.assertEqual(parsed.frames[0].samples[0].imag, 0.0)
        self.assertAlmostEqual(parsed.frames[0].samples[0].amplitude, 1.0)
        self.assertAlmostEqual(parsed.frames[0].samples[0].phase, 0.0)
        summary = parsed.to_summary_dict()
        self.assertEqual(summary["sample_count"], 8)
        self.assertEqual(summary["source_count"], 1)
        self.assertNotIn("source_ids", summary)
        self.assertNotIn("frame_count_by_source", summary)
        self.assertNotIn("sample_count_by_source", summary)
        self.assertFalse(summary["hardware_access"])
        self.assertFalse(summary["network_calls"])
        self.assertFalse(summary["medical_or_clinical_claim"])
        encoded_summary = json.dumps(summary, sort_keys=True)
        for forbidden_key in (
            "raw_values",
            "samples",
            "real",
            "imag",
            "amplitude",
            "phase",
            "rssi",
        ):
            with self.subTest(forbidden_key=forbidden_key):
                self.assertNotIn(f'"{forbidden_key}":', encoded_summary)
        self._assert_no_forbidden_report_keys(report.to_dict())
        self._assert_messages_are_report_safe(report.to_dict())

    def test_parses_amplitude_phase_csv_fixture_deterministically(self):
        from somatic.sensors.csi_parser import parse_csi_fixture

        parsed, report = parse_csi_fixture(
            "sample-amplitude-phase.csv",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(report.status, "parsed")
        self.assertEqual(parsed.source_format, "amplitude-phase-csv")
        self.assertEqual(parsed.frame_count, 2)
        self.assertEqual(parsed.sample_count, 3)
        self.assertEqual(parsed.frames[0].samples[1].subcarrier, 2)
        self.assertAlmostEqual(parsed.frames[0].samples[1].amplitude, 0.8)
        self.assertAlmostEqual(parsed.frames[0].samples[1].phase, -0.5)

    def test_parses_generic_jsonl_fixture_deterministically(self):
        from somatic.sensors.csi_parser import parse_csi_fixture

        parsed, report = parse_csi_fixture(
            "sample-csi-jsonl.jsonl",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(report.status, "parsed")
        self.assertEqual(parsed.source_format, "generic-csi-jsonl")
        self.assertEqual(parsed.frame_count, 2)
        self.assertEqual(parsed.sample_count, 3)
        self.assertEqual(parsed.frames[1].metadata["activity_label"], "fixture-motion")
        self.assertAlmostEqual(parsed.frames[1].samples[0].amplitude, 1.4)

    def test_malformed_fixture_returns_deterministic_rejection_report(self):
        from somatic.sensors.csi_parser import parse_csi_fixture

        parsed, report = parse_csi_fixture(
            "invalid-csi-malformed.csv",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(report.status, "rejected")
        self.assertEqual(report.source_format, "amplitude-phase-csv")
        self.assertEqual(report.rows_seen, 2)
        self.assertEqual(report.malformed_rows, 2)
        self.assertEqual(parsed.frame_count, 0)
        self.assertEqual(parsed.sample_count, 0)
        self.assertIn("row 2", report.errors[0])
        self.assertIn("malformed", report.errors[0])
        self.assertEqual(report.parse_errors[0].code, "required_fields_missing")
        self.assertFalse(report.to_dict()["hardware_access"])
        self.assertFalse(report.to_dict()["network_calls"])
        self.assertFalse(report.to_dict()["medical_or_clinical_claim"])
        self._assert_no_forbidden_report_keys(report.to_dict())
        self._assert_messages_are_report_safe(report.to_dict())

    def test_blank_lines_and_unknown_columns_parse_without_leaking_column_names(self):
        from somatic.sensors.csi_parser import parse_csi_fixture

        parsed, report = parse_csi_fixture(
            "edge-blank-lines-unknown-columns.csv",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(report.status, "parsed")
        self.assertEqual(report.rows_seen, 2)
        self.assertEqual(report.malformed_rows, 0)
        self.assertEqual(parsed.frame_count, 2)
        self.assertEqual(parsed.sample_count, 2)
        self.assertTrue(report.warnings)
        self.assertIn("unknown fixture columns", report.warnings[0])
        self._assert_no_forbidden_report_keys(parsed.to_summary_dict())
        self._assert_no_forbidden_report_keys(report.to_dict())
        self._assert_messages_are_report_safe(report.to_dict())

    def test_short_esp32_vector_is_rejected_with_structured_error(self):
        from somatic.sensors.csi_parser import parse_csi_fixture

        parsed, report = parse_csi_fixture(
            "invalid-esp32-short-vector.csv",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(report.status, "rejected")
        self.assertEqual(report.rows_seen, 1)
        self.assertEqual(report.malformed_rows, 1)
        self.assertEqual(parsed.frame_count, 0)
        self.assertEqual(report.parse_errors[0].code, "invalid_vector_length")
        self._assert_messages_are_report_safe(report.to_dict())

    def test_invalid_jsonl_rows_are_partial_and_deterministic(self):
        from somatic.sensors.csi_parser import parse_csi_fixture

        parsed, report = parse_csi_fixture(
            "invalid-csi-jsonl.jsonl",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(report.status, "partial")
        self.assertEqual(report.source_format, "generic-csi-jsonl")
        self.assertEqual(report.rows_seen, 3)
        self.assertEqual(report.frame_count, 1)
        self.assertEqual(report.malformed_rows, 2)
        self.assertEqual(
            [error.code for error in report.parse_errors],
            ["json_object_required", "record_payload_missing"],
        )
        self.assertEqual(parsed.sample_count, 1)
        self._assert_no_forbidden_report_keys(parsed.to_summary_dict())
        self._assert_messages_are_report_safe(report.to_dict())

    def test_mixed_valid_invalid_csv_rows_are_partial_and_deterministic(self):
        from somatic.sensors.csi_parser import parse_csi_fixture

        parsed, report = parse_csi_fixture(
            "mixed-valid-invalid-csi.csv",
            repo_root=REPO_ROOT,
        )

        self.assertEqual(report.status, "partial")
        self.assertEqual(report.rows_seen, 2)
        self.assertEqual(report.frame_count, 1)
        self.assertEqual(report.malformed_rows, 1)
        self.assertEqual(parsed.sample_count, 1)
        self.assertEqual(report.parse_errors[0].code, "required_fields_missing")
        self._assert_no_forbidden_report_keys(report.to_dict())
        self._assert_messages_are_report_safe(report.to_dict())

    def test_unsupported_fixture_extensions_are_rejected_before_format_detection(self):
        from somatic.sensors.csi_parser import parse_csi_fixture

        for fixture_name in ("unsupported-csi.npz", "unsupported-csi.pcap"):
            with self.subTest(fixture_name=fixture_name):
                parsed, report = parse_csi_fixture(fixture_name, repo_root=REPO_ROOT)

                self.assertEqual(report.status, "rejected")
                self.assertEqual(report.source_format, "unsupported-extension")
                self.assertEqual(report.rows_seen, 0)
                self.assertEqual(parsed.frame_count, 0)
                self.assertEqual(report.parse_errors[0].code, "unsupported_extension")
                self.assertFalse(report.to_dict()["network_calls"])
                self.assertFalse(report.to_dict()["hardware_access"])
                self._assert_messages_are_report_safe(report.to_dict())

    def test_fixture_loader_rejects_absolute_or_unsafe_refs(self):
        from somatic.sensors.csi_parser import resolve_csi_fixture_path

        resolved = resolve_csi_fixture_path(
            "fixture://sensors/csi/sample-esp32-csi.csv",
            repo_root=REPO_ROOT,
        )
        self.assertEqual(resolved, CSI_FIXTURE_DIR / "sample-esp32-csi.csv")

        with self.assertRaisesRegex(ValueError, "absolute"):
            resolve_csi_fixture_path(
                str(CSI_FIXTURE_DIR / "sample-esp32-csi.csv"),
                repo_root=REPO_ROOT,
            )
        with self.assertRaisesRegex(ValueError, "unsafe"):
            resolve_csi_fixture_path("../sample-esp32-csi.csv", repo_root=REPO_ROOT)
        with self.assertRaisesRegex(ValueError, "unsafe"):
            resolve_csi_fixture_path(
                "fixture://sensors/csi/../secret.csv",
                repo_root=REPO_ROOT,
            )

    def test_parse_file_rejects_url_like_paths_before_path_normalization(self):
        from somatic.sensors.csi_parser import parse_csi_file

        parsed, report = parse_csi_file("http://example.invalid/csi.csv")

        self.assertEqual(report.status, "rejected")
        self.assertEqual(parsed.frame_count, 0)
        self.assertIn("remote CSI paths are not allowed", report.errors)
        self.assertEqual(report.path, "<remote-csi-path>")
        self.assertEqual(parsed.path, "<remote-csi-path>")
        self.assertFalse(report.to_dict()["network_calls"])
        self._assert_no_absolute_paths(report.to_dict())

    def test_parse_file_rejects_local_paths_outside_csi_fixture_root(self):
        from somatic.sensors.csi_parser import parse_csi_file

        parsed, report = parse_csi_file(REPO_ROOT / "README.md")

        self.assertEqual(report.status, "rejected")
        self.assertEqual(parsed.frame_count, 0)
        self.assertIn("CSI parser only accepts fixtures/sensors/csi files", report.errors)
        self.assertFalse(report.to_dict()["hardware_access"])

    def test_parse_file_rejects_lookalike_fixture_root_outside_repo(self):
        from somatic.sensors.csi_parser import parse_csi_file

        with tempfile.TemporaryDirectory() as tmp:
            lookalike_root = Path(tmp) / "fixtures" / "sensors" / "csi"
            lookalike_root.mkdir(parents=True)
            lookalike_fixture = lookalike_root / "sample-esp32-csi.csv"
            lookalike_fixture.write_text(
                'type,frame_id,timestamp,source,csi_data\nCSI_DATA,1,0,tmp,"[1 0]"\n',
                encoding="utf-8",
            )

            parsed, report = parse_csi_file(lookalike_fixture, repo_root=REPO_ROOT)

        self.assertEqual(report.status, "rejected")
        self.assertEqual(parsed.frame_count, 0)
        self.assertIn("CSI parser only accepts fixtures/sensors/csi files", report.errors)
        self._assert_no_absolute_paths(report.to_dict())

    def test_parser_adds_no_network_hardware_or_optional_import_surfaces(self):
        forbidden_import_roots = {
            "requests",
            "urllib",
            "http",
            "socket",
            "websocket",
            "aiohttp",
            "httpx",
            "scapy",
            "pyshark",
            "pcapy",
            "dpkt",
            "wifi",
            "serial",
            "usb",
            "pyusb",
            "numpy",
            "scipy",
            "pandas",
            "neurokit2",
        }
        forbidden_call_names = {
            "urlopen",
            "urlretrieve",
            "request",
            "create_connection",
            "sniff",
            "pcap",
            "set_monitor_mode",
            "scan",
            "connect",
            "download",
        }
        for path in (
            REPO_ROOT / "somatic" / "sensors" / "csi_formats.py",
            REPO_ROOT / "somatic" / "sensors" / "csi_parser.py",
            REPO_ROOT / "somatic" / "sensors" / "csi_batch.py",
            REPO_ROOT / "somatic" / "sensors" / "csi_scoring.py",
        ):
            with self.subTest(path=path.name):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imported = {alias.name.split(".")[0] for alias in node.names}
                        self.assertTrue(imported.isdisjoint(forbidden_import_roots))
                    if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                        module = node.module.split(".")[0]
                        self.assertNotIn(module, forbidden_import_roots)
                    if isinstance(node, ast.Call):
                        name = (
                            node.func.id
                            if isinstance(node.func, ast.Name)
                            else getattr(node.func, "attr", None)
                        )
                        self.assertNotIn(name, forbidden_call_names)

    def _assert_no_forbidden_report_keys(self, payload):
        if isinstance(payload, dict):
            for key, value in payload.items():
                with self.subTest(report_key=key):
                    self.assertNotIn(str(key).lower(), FORBIDDEN_CSI_REPORT_KEYS)
                self._assert_no_forbidden_report_keys(value)
        elif isinstance(payload, list):
            for item in payload:
                self._assert_no_forbidden_report_keys(item)

    def _assert_messages_are_report_safe(self, payload):
        if isinstance(payload, dict):
            for key, value in payload.items():
                if key in {"errors", "warnings"} and isinstance(value, list):
                    for message in value:
                        self._assert_report_message_safe(str(message))
                elif key == "message":
                    self._assert_report_message_safe(str(value))
                else:
                    self._assert_messages_are_report_safe(value)
        elif isinstance(payload, list):
            for item in payload:
                self._assert_messages_are_report_safe(item)

    def _assert_report_message_safe(self, message):
        lowered = message.lower()
        for forbidden in FORBIDDEN_CSI_REPORT_WORDS:
            with self.subTest(forbidden_message_word=forbidden):
                self.assertNotIn(forbidden, lowered)

    def _assert_no_absolute_paths(self, payload):
        if isinstance(payload, dict):
            for value in payload.values():
                self._assert_no_absolute_paths(value)
        elif isinstance(payload, list):
            for item in payload:
                self._assert_no_absolute_paths(item)
        elif isinstance(payload, str):
            normalized = payload.replace("\\", "/")
            self.assertNotIn(str(REPO_ROOT).replace("\\", "/"), normalized)
            self.assertNotRegex(normalized, r"^[A-Za-z]:/")

    def _normalized_fixture_text_size(self, fixture_name):
        text = (CSI_FIXTURE_DIR / fixture_name).read_text(encoding="utf-8")
        return len(text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8"))

    @staticmethod
    def _stable_json(payload):
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))


if __name__ == "__main__":
    unittest.main()
