import json
import unittest
from pathlib import Path

from somatic.sensors.csi_parser import build_csi_parser_artifacts
from somatic.sensors.csi_scoring import (
    CSI_EVIDENCE_SCORER_ID,
    CSI_EVIDENCE_SCORING_CONTRACT_VERSION,
    build_csi_tournament_readiness,
    score_csi_replay_evidence,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
VALID_REFS = (
    "sample-esp32-csi.csv",
    "sample-amplitude-phase.csv",
    "sample-csi-jsonl.jsonl",
)
FORBIDDEN_CSI_SCORING_KEYS = {
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
FORBIDDEN_CSI_SCORING_WORDS = (
    "raw_values",
    "samples",
    "imag",
    "amplitude",
    "rssi",
    "source_id",
    "source_ids",
)


class WifiCsiEvidenceScoringTests(unittest.TestCase):
    def test_valid_replay_produces_deterministic_bounded_scores(self):
        left_report, left_summary = build_csi_parser_artifacts(
            VALID_REFS,
            repo_root=REPO_ROOT,
        )
        right_report, right_summary = build_csi_parser_artifacts(
            VALID_REFS,
            repo_root=REPO_ROOT,
        )

        left_score = left_report["csi_evidence_scoring"]
        right_score = right_report["csi_evidence_scoring"]

        self.assertEqual(left_score, right_score)
        self.assertEqual(left_summary["csi_evidence_scoring"], left_score)
        self.assertEqual(left_score["contract_version"], CSI_EVIDENCE_SCORING_CONTRACT_VERSION)
        self.assertEqual(left_score["scorer_id"], CSI_EVIDENCE_SCORER_ID)
        self.assertEqual(left_score["status"], "parsed")
        self.assertEqual(left_score["score"], 100)
        self.assertEqual(left_score["evidence_quality"], 100)
        self.assertEqual(left_score["replay_integrity"], 100)
        self.assertEqual(left_score["score_scale"], "0-100")
        self.assertEqual(left_score["status_counts"], {"parsed": 3, "partial": 0, "rejected": 0})
        self.assertEqual(left_score["fixture_count"], 3)
        self.assertEqual(left_score["frame_count"], 6)
        self.assertEqual(left_score["sample_count"], 14)
        self.assertEqual(left_score["format_coverage_ratio"], 1.0)
        self.assertTrue(left_score["bounded"])
        self.assertTrue(left_score["explainable"])
        self._assert_scoring_payload_is_sanitized(left_score)

    def test_partial_mixed_replay_scores_lower_without_failing(self):
        valid_report, valid_summary = build_csi_parser_artifacts(
            VALID_REFS,
            repo_root=REPO_ROOT,
        )
        partial_report, partial_summary = build_csi_parser_artifacts(
            ("sample-esp32-csi.csv", "mixed-valid-invalid-csi.csv"),
            repo_root=REPO_ROOT,
        )

        valid_score = valid_report["csi_evidence_scoring"]
        partial_score = partial_report["csi_evidence_scoring"]

        self.assertEqual(partial_summary["csi_evidence_scoring"], partial_score)
        self.assertEqual(partial_score["status"], "partial")
        self.assertGreater(partial_score["score"], 0)
        self.assertLess(partial_score["score"], valid_score["score"])
        self.assertEqual(partial_score["parsed_count"], 1)
        self.assertEqual(partial_score["partial_count"], 1)
        self.assertEqual(partial_score["rejected_count"], 0)
        self.assertGreater(partial_score["parse_error_count"], 0)
        self._assert_scoring_payload_is_sanitized(partial_score)

    def test_rejected_and_invalid_utf8_replay_scores_fail_closed(self):
        for fixture_name in ("unsupported-csi.npz", "invalid-utf8-csi.csv"):
            with self.subTest(fixture_name=fixture_name):
                report, summary = build_csi_parser_artifacts(
                    (fixture_name,),
                    repo_root=REPO_ROOT,
                )
                score = report["csi_evidence_scoring"]

                self.assertEqual(summary["csi_evidence_scoring"], score)
                self.assertEqual(score["status"], "rejected")
                self.assertEqual(score["score"], 0)
                self.assertEqual(score["evidence_quality"], 0)
                self.assertEqual(score["replay_integrity"], 0)
                self.assertEqual(score["rejected_count"], 1)
                self.assertEqual(score["frame_count"], 0)
                self._assert_scoring_payload_is_sanitized(score)

    def test_unsafe_refs_do_not_appear_in_scoring_metadata(self):
        unsafe_refs = (
            str(REPO_ROOT / "fixtures" / "sensors" / "csi" / "sample-esp32-csi.csv"),
            "https://example.invalid/csi-fixture.csv",
        )

        report, summary = build_csi_parser_artifacts(unsafe_refs, repo_root=REPO_ROOT)
        score = report["csi_evidence_scoring"]
        encoded = json.dumps({"report": report, "summary": summary}, sort_keys=True)

        self.assertEqual(score["status"], "rejected")
        self.assertEqual(score["score"], 0)
        self.assertNotIn("example.invalid", encoded)
        self.assertNotIn(str(REPO_ROOT).replace("\\", "/"), encoded.replace("\\", "/"))
        self._assert_scoring_payload_is_sanitized(score)

    def test_tournament_readiness_is_metadata_only_and_not_a_ranking_input(self):
        readiness = build_csi_tournament_readiness()

        self.assertEqual(readiness["status"], "not-configured")
        self.assertFalse(readiness["core_tournament_scores_modified"])
        self.assertFalse(readiness["ranking_input"])
        self.assertTrue(readiness["requires_sanitized_replay_metadata"])
        self.assertTrue(readiness["summary_output_only"])
        self.assertFalse(readiness["raw_signal_values_exported"])
        self._assert_scoring_payload_is_sanitized(readiness)

    def test_tournament_readiness_clamps_optional_score_metadata(self):
        readiness = build_csi_tournament_readiness(
            {
                "status": "parsed",
                "evidence_quality": 120,
                "replay_integrity": "-5",
                "parser_status": "parsed",
            }
        )

        self.assertEqual(readiness["status"], "parsed")
        self.assertEqual(readiness["evidence_quality"], 100)
        self.assertEqual(readiness["replay_integrity"], 0)
        self.assertFalse(readiness["ranking_input"])
        self._assert_scoring_payload_is_sanitized(readiness)

    def test_direct_scorer_accepts_sanitized_payloads_only(self):
        report, summary = build_csi_parser_artifacts(VALID_REFS, repo_root=REPO_ROOT)
        direct_score = score_csi_replay_evidence(report, summary)

        self.assertEqual(direct_score, report["csi_evidence_scoring"])
        self._assert_scoring_payload_is_sanitized(direct_score)

    def _assert_scoring_payload_is_sanitized(self, payload):
        self._assert_no_forbidden_csi_scoring_keys(payload)
        self._assert_no_forbidden_csi_scoring_words(payload)
        self._assert_no_absolute_paths(payload)

    def _assert_no_forbidden_csi_scoring_keys(self, payload):
        if isinstance(payload, dict):
            for key, value in payload.items():
                with self.subTest(csi_scoring_key=key):
                    self.assertNotIn(str(key).lower(), FORBIDDEN_CSI_SCORING_KEYS)
                self._assert_no_forbidden_csi_scoring_keys(value)
        elif isinstance(payload, list):
            for item in payload:
                self._assert_no_forbidden_csi_scoring_keys(item)

    def _assert_no_forbidden_csi_scoring_words(self, payload):
        if isinstance(payload, dict):
            for value in payload.values():
                self._assert_no_forbidden_csi_scoring_words(value)
        elif isinstance(payload, list):
            for item in payload:
                self._assert_no_forbidden_csi_scoring_words(item)
        elif isinstance(payload, str):
            lowered = payload.lower()
            for word in FORBIDDEN_CSI_SCORING_WORDS:
                with self.subTest(csi_scoring_forbidden_word=word):
                    self.assertNotIn(word, lowered)

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


if __name__ == "__main__":
    unittest.main()
