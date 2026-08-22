import json
import unittest
from pathlib import Path

from somatic.fabric.canonical import signing_payload
from somatic.fabric.digests import manifest_digest, sha256_hex

REPO_ROOT = Path(__file__).resolve().parents[1]
INTEROP_ROOT = REPO_ROOT / "fixtures" / "fabric" / "interop"
LOCUS_PHASE_4G3_COMMIT = "5f81ee360834dc6451c4ea35d7509325813d9d10"


class FabricInteropMetadataTests(unittest.TestCase):
    def test_mutual_verification_report_records_attempt_and_boundaries(self):
        report_path = REPO_ROOT / "docs" / "fabric-mutual-verification-report.md"

        self.assertTrue(report_path.exists(), report_path)

        report = report_path.read_text(encoding="utf-8")
        required_fragments = (
            "C:\\AI\\locus\\electron\\content-fabric\\",
            "79f480d592ec82e879b7588a25bad6b4ea2536ca",
            "npm run test:connectivity",
            "Somatic-generated fixtures -> Locus",
            "Locus-owned fixtures -> Somatic",
            "not certified",
            "No Locus files were copied",
            "catalog signature",
        )
        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, report)

    def test_somatic_generated_metadata_records_phase4f_results(self):
        metadata = json.loads(
            (INTEROP_ROOT / "somatic-generated-metadata.json").read_text(encoding="utf-8")
        )

        self.assertEqual(metadata["status"], "mutual-verification-attempted-not-certified")
        self.assertEqual(metadata["generatedBy"], "somatic")
        self.assertTrue(metadata["testOnlyKeys"])
        self.assertRegex(metadata["sourceSomaticCommit"], r"^[a-f0-9]{40}$")

        fixture_files = metadata["fixtureFiles"]
        self.assertEqual(
            set(fixture_files),
            {
                "somatic-generated-pack.json",
                "somatic-generated-keyring.json",
                "somatic-generated-catalog.json",
            },
        )

        locus = metadata["locusVerification"]
        self.assertEqual(locus["path"], "C:\\AI\\locus\\electron\\content-fabric\\")
        self.assertEqual(locus["commit"], "79f480d592ec82e879b7588a25bad6b4ea2536ca")
        self.assertEqual(locus["overallResult"], "verified-partial-not-certified")
        self.assertEqual(locus["somaticPackVerification"], "verified")
        self.assertEqual(locus["somaticKeyringVerification"], "verified")
        self.assertEqual(locus["somaticCatalogValidation"], "verified-shape")
        self.assertEqual(
            locus["somaticCatalogSignatureVerification"],
            "verified-with-locus-ed25519-primitive-no-high-level-catalog-verifier",
        )
        self.assertIn("npm run test:content", locus["commandsAttempted"])

    def test_mutual_verification_report_records_phase4g3_shared_fixture_result(self):
        report = (REPO_ROOT / "docs" / "fabric-mutual-verification-report.md").read_text(
            encoding="utf-8"
        )
        expected_fragments = (
            "Phase 4G.3",
            LOCUS_PHASE_4G3_COMMIT,
            "shared-pack.json",
            "shared-keyring.json",
            "shared-catalog.json",
            "shared fixture certification achieved",
            "verified-with-locus-ed25519-primitive-no-high-level-catalog-verifier",
            "invalid shared signature pack",
            "invalid shared keyring threshold",
        )
        for fragment in expected_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, report)

    def test_metadata_digests_match_current_somatic_fixtures(self):
        metadata = json.loads(
            (INTEROP_ROOT / "somatic-generated-metadata.json").read_text(encoding="utf-8")
        )
        pack = json.loads(
            (INTEROP_ROOT / "somatic-generated-pack.json").read_text(encoding="utf-8")
        )
        catalog = json.loads(
            (INTEROP_ROOT / "somatic-generated-catalog.json").read_text(encoding="utf-8")
        )

        self.assertEqual(
            metadata["digests"]["signedCodePackSigningPayloadSha256"],
            sha256_hex(signing_payload(pack)),
        )
        self.assertEqual(
            metadata["digests"]["signedCodePackManifestDigest"],
            manifest_digest(pack),
        )
        self.assertEqual(
            metadata["digests"]["signedCatalogSigningPayloadSha256"],
            sha256_hex(signing_payload(catalog)),
        )


if __name__ == "__main__":
    unittest.main()
