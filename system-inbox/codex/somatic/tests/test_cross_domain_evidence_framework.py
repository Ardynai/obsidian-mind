import copy
import json
import unittest
from pathlib import Path

from somatic.evidence.document_evidence_pack import (
    DOCUMENT_EVIDENCE_PACK_ARTIFACT_REF,
    DOCUMENT_EVIDENCE_PACK_CONTRACT,
    DOCUMENT_EVIDENCE_PROVIDER_KIND,
    classify_document_evidence_pack_compatibility,
    document_evidence_pack_artifact_metadata,
)
from somatic.evidence.document_fixture import DocumentFixtureEvidenceProvider
from somatic.evidence.framework import (
    classify_evidence_pack_contract,
    finalize_evidence_pack_identity,
)
from somatic.sensors.csi_evidence_pack import (
    CSI_EVIDENCE_PACK_CONTRACT,
    classify_csi_evidence_pack_compatibility,
    csi_evidence_pack_artifact_metadata,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CSI_FIXTURE = REPO_ROOT / "fixtures" / "reports" / "csi-evidence-pack-v1-parsed.json"


class CrossDomainEvidenceFrameworkTests(unittest.TestCase):
    def test_csi_and_document_use_shared_contract_classifier(self):
        for domain in self._domains():
            with self.subTest(domain=domain["name"]):
                pack = domain["pack"]()

                shared = classify_evidence_pack_contract(
                    pack,
                    contract=domain["contract"],
                )
                domain_result = domain["classify"](pack)

                self.assertEqual(domain_result.classification, "compatible")
                self.assertEqual(shared.classification, domain_result.classification)
                self.assertEqual(shared.errors, domain_result.errors)
                self.assertEqual(shared.fingerprint_verified, domain_result.fingerprint_verified)
                self.assertEqual(
                    shared.evidence_contract_version,
                    self._contract_version(domain_result),
                )

                stale = copy.deepcopy(pack)
                self._increment_first_count(stale)
                result = domain["classify"](stale)

                self.assertEqual(result.classification, "incompatible")
                self.assertIn("invalid_fingerprint_or_pack_id", result.errors)
                self._assert_private_strings_not_echoed(result.to_dict())

    def test_shared_contract_rejects_unsafe_artifact_refs_fail_closed(self):
        unsafe_refs = (
            "../private.json",
            "artifacts/../private.json",
            "C:/AI/somatic/private.json",
            "/home/runner/work/somatic/private.json",
            "https://example.invalid/private.json",
            "fixture://sensors/private.json",
        )

        for domain in self._domains():
            for ref in unsafe_refs:
                with self.subTest(domain=domain["name"], ref=ref):
                    pack = domain["pack"]()
                    pack["artifact_refs"] = {"pack": ref}
                    self._refresh(pack, domain["pack_id_prefix"])

                    result = domain["classify"](pack)

                    self.assertEqual(result.classification, "incompatible")
                    self.assertIn("invalid_artifact_refs", result.errors)
                    if ref.startswith(("C:/", "/", "http", "fixture://")):
                        self.assertGreater(result.privacy_violation_count, 0)
                    self._assert_private_strings_not_echoed(result.to_dict())

    def test_shared_contract_rejects_private_payloads_and_fixture_leakage(self):
        for domain in self._domains():
            cases = (
                (
                    "private_payload",
                    {
                        "provider_payload_body": {
                            "raw_values": [1, 2, 3],
                            "source_id": "private-source",
                            "credentials": "secret-token",
                        }
                    },
                ),
                ("fixture_name_leak", {"producer_build": domain["fixture_leak"]}),
                ("raw_content_leak", {"future_raw_content": domain["raw_content_leak"]}),
            )
            for case_name, mutation in cases:
                with self.subTest(domain=domain["name"], case=case_name):
                    pack = domain["pack"]()
                    pack.update(copy.deepcopy(mutation))
                    self._refresh(pack, domain["pack_id_prefix"])

                    result = domain["classify"](pack)

                    self.assertEqual(result.classification, "incompatible")
                    self.assertIn("privacy_boundary_violation", result.errors)
                    self.assertGreater(result.privacy_violation_count, 0)
                    self._assert_private_strings_not_echoed(result.to_dict())

    def test_shared_artifact_metadata_ref_contract_for_csi_and_document(self):
        csi_pack = self._csi_pack()
        csi_metadata = csi_evidence_pack_artifact_metadata(
            csi_pack,
            artifact_sha256="a" * 64,
        )
        self.assertEqual(csi_metadata["artifact_ref"], "artifacts/csi_evidence_pack.json")
        self.assertEqual(csi_metadata["pack_fingerprint"], csi_pack["pack_fingerprint"])
        self._assert_private_strings_not_echoed(csi_metadata)

        document_pack = self._document_pack()
        document_metadata = document_evidence_pack_artifact_metadata(
            document_pack,
            artifact_sha256="b" * 64,
        )
        self.assertEqual(document_metadata["artifact_ref"], DOCUMENT_EVIDENCE_PACK_ARTIFACT_REF)
        self.assertEqual(document_metadata["provider_kind"], DOCUMENT_EVIDENCE_PROVIDER_KIND)
        self.assertEqual(document_metadata["pack_fingerprint"], document_pack["pack_fingerprint"])
        self._assert_private_strings_not_echoed(document_metadata)

    def _domains(self):
        return (
            {
                "name": "csi",
                "pack": self._csi_pack,
                "classify": classify_csi_evidence_pack_compatibility,
                "contract": CSI_EVIDENCE_PACK_CONTRACT,
                "pack_id_prefix": "csi-evidence-pack-",
                "fixture_leak": "sample-esp32-csi.csv",
                "raw_content_leak": "raw_csi values would expose signal payloads",
            },
            {
                "name": "document",
                "pack": self._document_pack,
                "classify": classify_document_evidence_pack_compatibility,
                "contract": DOCUMENT_EVIDENCE_PACK_CONTRACT,
                "pack_id_prefix": "document-evidence-pack-",
                "fixture_leak": "document-parsed.json",
                "raw_content_leak": "raw document text would expose private content",
            },
        )

    def _csi_pack(self):
        return self._read_json(CSI_FIXTURE)

    def _document_pack(self):
        return DocumentFixtureEvidenceProvider().evidence_pack(
            ("document-parsed.json",),
            repo_root=REPO_ROOT,
        )

    @staticmethod
    def _refresh(pack, pack_id_prefix):
        pack["pack_id"] = None
        pack["pack_fingerprint"] = None
        finalize_evidence_pack_identity(pack, pack_id_prefix=pack_id_prefix)

    @staticmethod
    def _contract_version(result):
        return getattr(
            result,
            "evidence_pack_contract_version",
            getattr(result, "evidence_contract_version", None),
        )

    @staticmethod
    def _increment_first_count(pack):
        counts = pack.get("counts")
        if not isinstance(counts, dict):
            return
        for key, value in counts.items():
            if isinstance(value, int) and not isinstance(value, bool):
                counts[key] = value + 1
                return

    def _assert_private_strings_not_echoed(self, payload):
        strings = list(self._strings(payload))
        encoded = "\n".join(strings).lower()
        for forbidden in (
            "sample-esp32-csi",
            "document-parsed",
            "private-source",
            "secret-token",
            "raw_csi values",
            "raw document text",
            "https://example.invalid/private",
            "c:/ai/somatic/private",
            "/home/runner/work/somatic/private",
            "fixture://sensors/private",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)

    def _strings(self, payload):
        if isinstance(payload, dict):
            for value in payload.values():
                yield from self._strings(value)
        elif isinstance(payload, list):
            for item in payload:
                yield from self._strings(item)
        elif isinstance(payload, str):
            yield payload

    @staticmethod
    def _read_json(path):
        return json.loads(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
