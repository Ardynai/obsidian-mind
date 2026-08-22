import json
import unittest
from pathlib import Path

from somatic.sensors.csi_batch import (
    CSI_BATCH_EVALUATION_CONTRACT_VERSION,
    CSI_BATCH_EVALUATOR_ID,
    CSI_BATCH_MAX_GROUPS,
    CSI_BATCH_MAX_REFS_PER_GROUP,
    build_csi_batch_tournament_readiness,
    evaluate_csi_replay_batch,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
VALID_GROUPS = (
    {
        "refs": (
            "sample-esp32-csi.csv",
            "sample-amplitude-phase.csv",
            "sample-csi-jsonl.jsonl",
        ),
    },
    {
        "refs": (
            "sample-esp32-csi.csv",
            "sample-csi-jsonl.jsonl",
        ),
    },
)
MIXED_GROUPS = (
    VALID_GROUPS[0],
    {
        "refs": (
            "sample-esp32-csi.csv",
            "mixed-valid-invalid-csi.csv",
        ),
    },
    {"refs": ("unsupported-csi.npz",)},
)
FORBIDDEN_CSI_BATCH_KEYS = {
    "samples",
    "raw_values",
    "real",
    "imag",
    "amplitude",
    "phase",
    "rssi",
    "source_id",
    "source_ids",
    "report",
    "summary",
    "files",
    "fixtures",
    "fixture_refs",
    "parse_errors",
}
FORBIDDEN_CSI_BATCH_WORDS = (
    "raw_values",
    "amplitude",
    "phase",
    "rssi",
    "source_id",
    "source_ids",
    "example.invalid",
    "sample-esp32-csi",
    "mixed-valid-invalid-csi",
    "unsupported-csi",
    "invalid-utf8-csi",
)


class WifiCsiBatchReplayTests(unittest.TestCase):
    def test_multiple_fixture_groups_evaluate_deterministically(self):
        left = evaluate_csi_replay_batch(VALID_GROUPS, repo_root=REPO_ROOT)
        right = evaluate_csi_replay_batch(VALID_GROUPS, repo_root=REPO_ROOT)

        self.assertEqual(self._stable_json(left), self._stable_json(right))
        self.assertEqual(left["contract_version"], CSI_BATCH_EVALUATION_CONTRACT_VERSION)
        self.assertEqual(left["evaluator_id"], CSI_BATCH_EVALUATOR_ID)
        self.assertEqual(left["status"], "parsed")
        self.assertEqual(left["group_count"], 2)
        self.assertEqual(left["evaluated_group_count"], 2)
        self.assertEqual(left["rejected_group_count"], 0)
        self.assertEqual(left["group_status_counts"], {"parsed": 2, "partial": 0, "rejected": 0})
        self.assertEqual(left["score"], 100)
        self.assertEqual(left["aggregate_evidence_quality"], 100)
        self.assertEqual(left["aggregate_replay_integrity"], 100)
        self.assertEqual(left["minimum_group_score"], 100)
        self.assertEqual(left["average_group_score"], 100.0)
        self.assertFalse(left["core_tournament_scores_modified"])
        self.assertFalse(left["ranking_input"])
        self._assert_batch_payload_is_sanitized(left)

    def test_valid_partial_and_rejected_groups_aggregate_fail_closed(self):
        payload = evaluate_csi_replay_batch(MIXED_GROUPS, repo_root=REPO_ROOT)

        self.assertEqual(payload["status"], "partial")
        self.assertEqual(payload["group_count"], 3)
        self.assertEqual(payload["evaluated_group_count"], 3)
        self.assertEqual(payload["group_status_counts"], {"parsed": 1, "partial": 1, "rejected": 1})
        self.assertEqual(payload["status_counts"], {"parsed": 4, "partial": 1, "rejected": 1})
        self.assertEqual(payload["fixture_count"], 6)
        self.assertEqual(payload["minimum_group_score"], 0)
        self.assertEqual(payload["score"], 0)
        self.assertEqual(payload["evidence_quality"], 0)
        self.assertEqual(payload["replay_integrity"], 0)
        self.assertEqual(payload["aggregate_evidence_quality"], 0)
        self.assertEqual(payload["aggregate_replay_integrity"], 0)
        self.assertEqual(payload["average_group_score"], 59.333)
        self.assertEqual(
            [group["status"] for group in payload["groups"]],
            ["parsed", "partial", "rejected"],
        )
        self.assertEqual(
            [group["score"] for group in payload["groups"]],
            [100, 78, 0],
        )
        self._assert_batch_payload_is_sanitized(payload)

    def test_unsafe_refs_and_invalid_utf8_fail_closed_with_redacted_metadata(self):
        unsafe_ref = str(REPO_ROOT / "fixtures" / "sensors" / "csi" / "sample-esp32-csi.csv")
        payload = evaluate_csi_replay_batch(
            (
                {"refs": (unsafe_ref, "https://example.invalid/csi-fixture.csv")},
                {"refs": ("invalid-utf8-csi.csv",)},
            ),
            repo_root=REPO_ROOT,
        )
        encoded = self._stable_json(payload)

        self.assertEqual(payload["status"], "rejected")
        self.assertEqual(payload["group_status_counts"], {"parsed": 0, "partial": 0, "rejected": 2})
        self.assertEqual(payload["score"], 0)
        self.assertNotIn("example.invalid", encoded)
        self.assertNotIn(str(REPO_ROOT).replace("\\", "/"), encoded.replace("\\", "/"))
        self.assertNotIn("fixture_refs", payload["groups"][0])
        self._assert_batch_payload_is_sanitized(payload)

    def test_over_limit_groups_fail_closed_without_group_expansion(self):
        payload = evaluate_csi_replay_batch(
            [{"refs": ("sample-esp32-csi.csv",)}] * (CSI_BATCH_MAX_GROUPS + 1),
            repo_root=REPO_ROOT,
        )

        self.assertEqual(payload["status"], "rejected")
        self.assertEqual(payload["group_count"], CSI_BATCH_MAX_GROUPS + 1)
        self.assertEqual(payload["evaluated_group_count"], 0)
        self.assertEqual(payload["rejected_group_count"], CSI_BATCH_MAX_GROUPS + 1)
        self.assertTrue(payload["group_limit_exceeded"])
        self.assertFalse(payload["ref_limit_exceeded"])
        self.assertEqual(payload["groups"], [])
        self.assertEqual(payload["score"], 0)
        self._assert_batch_payload_is_sanitized(payload)

    def test_over_limit_group_refs_fail_closed_without_ref_export(self):
        payload = evaluate_csi_replay_batch(
            [
                {
                    "refs": tuple(
                        "sample-esp32-csi.csv" for _ in range(CSI_BATCH_MAX_REFS_PER_GROUP + 1)
                    ),
                }
            ],
            repo_root=REPO_ROOT,
        )

        self.assertEqual(payload["status"], "rejected")
        self.assertEqual(payload["group_count"], 1)
        self.assertEqual(payload["evaluated_group_count"], 1)
        self.assertEqual(payload["rejected_group_count"], 1)
        self.assertFalse(payload["group_limit_exceeded"])
        self.assertTrue(payload["ref_limit_exceeded"])
        self.assertEqual(payload["fixture_count"], CSI_BATCH_MAX_REFS_PER_GROUP + 1)
        self.assertEqual(payload["groups"][0]["fixture_count"], CSI_BATCH_MAX_REFS_PER_GROUP + 1)
        self.assertTrue(payload["groups"][0]["ref_limit_exceeded"])
        self.assertNotIn("fixture_refs", payload["groups"][0])
        self.assertEqual(payload["score"], 0)
        self._assert_batch_payload_is_sanitized(payload)

    def test_empty_batch_rejects_without_provider_group_output(self):
        payload = evaluate_csi_replay_batch([], repo_root=REPO_ROOT)

        self.assertEqual(payload["status"], "rejected")
        self.assertEqual(payload["group_count"], 0)
        self.assertEqual(payload["evaluated_group_count"], 0)
        self.assertEqual(payload["fixture_count"], 0)
        self.assertEqual(payload["score"], 0)
        self.assertEqual(payload["groups"], [])
        self._assert_batch_payload_is_sanitized(payload)

    def test_batch_readiness_is_metadata_only_and_not_ranking_input(self):
        batch = evaluate_csi_replay_batch(MIXED_GROUPS, repo_root=REPO_ROOT)
        readiness = build_csi_batch_tournament_readiness(batch)

        self.assertEqual(readiness["status"], "partial")
        self.assertEqual(readiness["group_count"], 3)
        self.assertEqual(readiness["evaluated_group_count"], 3)
        self.assertEqual(readiness["rejected_group_count"], 1)
        self.assertEqual(readiness["aggregate_evidence_quality"], 0)
        self.assertEqual(readiness["aggregate_replay_integrity"], 0)
        self.assertTrue(readiness["metadata_only"])
        self.assertFalse(readiness["core_tournament_scores_modified"])
        self.assertFalse(readiness["tournament_rankings_modified"])
        self.assertFalse(readiness["ranking_input"])
        self.assertEqual(len(readiness["group_summaries"]), 3)
        self._assert_batch_payload_is_sanitized(readiness)

    def _assert_batch_payload_is_sanitized(self, payload):
        self._assert_no_forbidden_batch_keys(payload)
        self._assert_no_forbidden_batch_words(payload)
        self._assert_no_absolute_paths(payload)

    def _assert_no_forbidden_batch_keys(self, payload):
        if isinstance(payload, dict):
            for key, value in payload.items():
                with self.subTest(csi_batch_key=key):
                    self.assertNotIn(str(key).lower(), FORBIDDEN_CSI_BATCH_KEYS)
                self._assert_no_forbidden_batch_keys(value)
        elif isinstance(payload, list):
            for item in payload:
                self._assert_no_forbidden_batch_keys(item)

    def _assert_no_forbidden_batch_words(self, payload):
        if isinstance(payload, dict):
            for value in payload.values():
                self._assert_no_forbidden_batch_words(value)
        elif isinstance(payload, list):
            for item in payload:
                self._assert_no_forbidden_batch_words(item)
        elif isinstance(payload, str):
            lowered = payload.lower()
            for word in FORBIDDEN_CSI_BATCH_WORDS:
                with self.subTest(csi_batch_forbidden_word=word):
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

    @staticmethod
    def _stable_json(payload):
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))


if __name__ == "__main__":
    unittest.main()
