import ast
import contextlib
import io
import json
import unittest
from pathlib import Path

from somatic.cli import main
from somatic.fabric.crypto import CRYPTO_AVAILABLE

REPO_ROOT = Path(__file__).resolve().parents[1]


class FabricCliTests(unittest.TestCase):
    def test_fabric_check_accepts_valid_sample_pack(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "fabric",
                    "check",
                    str(
                        REPO_ROOT
                        / "fixtures"
                        / "fabric"
                        / "conformance"
                        / "sample-pack-signed.json"
                    ),
                ]
            )

        self.assertEqual(exit_code, 0)
        output = stdout.getvalue()
        self.assertIn("Fabric check: valid", output)
        self.assertIn("sample-pack-signed.json", output)

    def test_fabric_check_rejects_invalid_license_fixture(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "fabric",
                    "check",
                    str(
                        REPO_ROOT
                        / "fixtures"
                        / "fabric"
                        / "conformance"
                        / "invalid-license-pack.json"
                    ),
                ]
            )

        self.assertEqual(exit_code, 1)
        output = stdout.getvalue()
        self.assertIn("Fabric check: invalid", output)
        self.assertIn("license", output.lower())

    def test_fabric_check_with_keyring_verifies_signed_pack_when_crypto_available(self):
        stdout = io.StringIO()
        expected = 0 if CRYPTO_AVAILABLE else 1

        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "fabric",
                    "check",
                    str(REPO_ROOT / "fixtures" / "fabric" / "crypto" / "signed-code-pack.json"),
                    "--keyring",
                    str(REPO_ROOT / "fixtures" / "fabric" / "crypto" / "keyring-signed.json"),
                ]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, expected)
        if CRYPTO_AVAILABLE:
            self.assertIn("crypto: publisher threshold verified", output)
        else:
            self.assertIn("cryptographic verification unavailable", output.lower())

    def test_fabric_check_with_keyring_rejects_invalid_signature(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "fabric",
                    "check",
                    str(
                        REPO_ROOT / "fixtures" / "fabric" / "crypto" / "invalid-signature-pack.json"
                    ),
                    "--keyring",
                    str(REPO_ROOT / "fixtures" / "fabric" / "crypto" / "keyring-signed.json"),
                ]
            )

        self.assertEqual(exit_code, 1)
        output = stdout.getvalue()
        self.assertIn("Fabric check: invalid", output)
        self.assertIn("signature", output.lower())

    def test_fabric_check_with_keyring_verifies_signed_catalog_when_crypto_available(self):
        stdout = io.StringIO()
        expected = 0 if CRYPTO_AVAILABLE else 1

        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "fabric",
                    "check",
                    str(REPO_ROOT / "fixtures" / "fabric" / "crypto" / "signed-catalog.json"),
                    "--keyring",
                    str(REPO_ROOT / "fixtures" / "fabric" / "crypto" / "keyring-signed.json"),
                ]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, expected)
        if CRYPTO_AVAILABLE:
            self.assertIn("catalog signature threshold verified", output)
        else:
            self.assertIn("cryptographic verification unavailable", output.lower())

    def test_fabric_check_with_keyring_rejects_invalid_catalog_signature(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "fabric",
                    "check",
                    str(
                        REPO_ROOT
                        / "fixtures"
                        / "fabric"
                        / "crypto"
                        / "invalid-catalog-signature.json"
                    ),
                    "--keyring",
                    str(REPO_ROOT / "fixtures" / "fabric" / "crypto" / "keyring-signed.json"),
                ]
            )

        self.assertEqual(exit_code, 1)
        output = stdout.getvalue()
        self.assertIn("Fabric check: invalid", output)
        self.assertIn("catalog signature", output.lower())

    def test_fabric_payload_prints_signing_payload_digest(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "fabric",
                    "payload",
                    str(REPO_ROOT / "fixtures" / "fabric" / "crypto" / "signed-code-pack.json"),
                ]
            )

        self.assertEqual(exit_code, 0)
        output = stdout.getvalue()
        self.assertIn("Fabric signing payload", output)
        self.assertIn("sha256:", output)
        self.assertIn("signatures key set to []", output)

    def test_fabric_payload_prints_exact_jcs_digest(self):
        expected = json.loads(
            (REPO_ROOT / "fixtures" / "fabric" / "jcs" / "expected-payload-digests.json").read_text(
                encoding="utf-8"
            )
        )
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "fabric",
                    "payload",
                    str(REPO_ROOT / "fixtures" / "fabric" / "jcs" / "signatures-field.json"),
                ]
            )

        self.assertEqual(exit_code, 0)
        self.assertIn(
            f"- sha256:{expected['signatures-field.json']}",
            stdout.getvalue(),
        )

    def test_fabric_canonicalize_prints_canonical_json(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "fabric",
                    "canonicalize",
                    str(REPO_ROOT / "fixtures" / "fabric" / "jcs" / "basic-object.json"),
                ]
            )

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), '{"a":1,"m":true,"n":null,"z":"last"}\n')

    def test_fabric_digest_prints_manifest_digest(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "fabric",
                    "digest",
                    str(
                        REPO_ROOT
                        / "fixtures"
                        / "fabric"
                        / "interop"
                        / "shared"
                        / "shared-pack.json"
                    ),
                ]
            )

        self.assertEqual(exit_code, 0)
        self.assertIn("Fabric digest: shared-pack.json", stdout.getvalue())
        self.assertIn("manifestDigest: sha256:", stdout.getvalue())

    def test_fabric_check_catalog_verifies_shared_catalog_when_crypto_available(self):
        stdout = io.StringIO()
        expected = 0 if CRYPTO_AVAILABLE else 1

        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "fabric",
                    "check-catalog",
                    str(
                        REPO_ROOT
                        / "fixtures"
                        / "fabric"
                        / "interop"
                        / "shared"
                        / "shared-catalog.json"
                    ),
                    "--keyring",
                    str(
                        REPO_ROOT
                        / "fixtures"
                        / "fabric"
                        / "interop"
                        / "shared"
                        / "shared-keyring.json"
                    ),
                ]
            )

        self.assertEqual(exit_code, expected)
        output = stdout.getvalue()
        if CRYPTO_AVAILABLE:
            self.assertIn("Fabric catalog check: valid", output)
            self.assertIn("catalog signature threshold verified", output)
        else:
            self.assertIn("cryptographic verification unavailable", output.lower())

    def test_fabric_check_shared_fixtures_self_certifies_when_crypto_available(self):
        stdout = io.StringIO()
        expected = 0 if CRYPTO_AVAILABLE else 1

        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "fabric",
                    "check-shared-fixtures",
                    str(REPO_ROOT / "fixtures" / "fabric" / "interop" / "shared"),
                ]
            )

        self.assertEqual(exit_code, expected)
        output = stdout.getvalue()
        if CRYPTO_AVAILABLE:
            self.assertIn("Fabric shared fixtures: valid", output)
            self.assertIn("invalid fixtures rejected", output)
            self.assertIn("Locus verification recorded for Phase 4G.3", output)
        else:
            self.assertIn("cryptographic verification unavailable", output.lower())

    def test_fabric_check_keyring_rotation_accepts_valid_rotation(self):
        stdout = io.StringIO()
        expected = 0 if CRYPTO_AVAILABLE else 1

        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "fabric",
                    "check-keyring-rotation",
                    str(
                        REPO_ROOT
                        / "fixtures"
                        / "fabric"
                        / "crypto"
                        / "rotation"
                        / "previous-keyring.json"
                    ),
                    str(
                        REPO_ROOT
                        / "fixtures"
                        / "fabric"
                        / "crypto"
                        / "rotation"
                        / "valid-rotated-keyring.json"
                    ),
                ]
            )

        self.assertEqual(exit_code, expected)
        output = stdout.getvalue()
        self.assertIn("keyring rotation", output.lower())
        if CRYPTO_AVAILABLE:
            self.assertIn("valid", output.lower())
        else:
            self.assertIn("unavailable", output.lower())

    def test_no_network_or_external_api_surfaces_in_fabric_runtime(self):
        forbidden_import_roots = (
            "requests",
            "urllib",
            "http",
            "socket",
            "openai",
            "webtorrent",
            "bittorrent",
        )
        forbidden_call_names = ("urlopen", "request", "create_connection")
        runtime_files = [
            REPO_ROOT / "somatic" / "fabric" / "canonical.py",
            REPO_ROOT / "somatic" / "fabric" / "crypto.py",
            REPO_ROOT / "somatic" / "fabric" / "digests.py",
            REPO_ROOT / "somatic" / "fabric" / "signing.py",
            REPO_ROOT / "somatic" / "fabric" / "keyring.py",
            REPO_ROOT / "somatic" / "fabric" / "manifest.py",
            REPO_ROOT / "somatic" / "fabric" / "catalog.py",
            REPO_ROOT / "somatic" / "fabric" / "pathing.py",
            REPO_ROOT / "somatic" / "fabric" / "conformance.py",
            REPO_ROOT / "somatic" / "fabric" / "interop.py",
            REPO_ROOT / "somatic" / "cli" / "main.py",
        ]

        for path in runtime_files:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported = [alias.name.split(".")[0] for alias in node.names]
                    for module in imported:
                        with self.subTest(path=path.name, module=module):
                            self.assertNotIn(module, forbidden_import_roots)
                if isinstance(node, ast.ImportFrom) and node.module:
                    module = node.module.split(".")[0]
                    with self.subTest(path=path.name, module=module):
                        self.assertNotIn(module, forbidden_import_roots)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    with self.subTest(path=path.name, call=node.func.id):
                        self.assertNotIn(node.func.id, forbidden_call_names)


if __name__ == "__main__":
    unittest.main()
