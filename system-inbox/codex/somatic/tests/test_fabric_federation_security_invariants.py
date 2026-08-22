"""Regression tests that LOCK the fabric federation security invariants (I3-I7).

These tests are additive to ``tests/test_fabric_federation_connect.py`` and do
not duplicate its coverage.  They focus on the security invariants from the
retroactive review of PR #66:

  I3  allowlist reject both ways (send + receive)
  I4  tampered contentId / descriptor rejected before delivery
  I5  Secure Drop ciphertext preserved (never decrypted in-process)
  I6  fail-closed on missing config (URL / token / DID / allowlist)
  I7  no secrets (tokens / bearer values) in logs or exception messages

The test harness reuses the same local-HTTP-server pattern as the connect test
but is self-contained so it can evolve independently.
"""

from __future__ import annotations

import ast
import hashlib
import json
import threading
import tomllib
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib import parse as urllib_parse

from somatic.fabric.federation import (
    FabricAllowlistError,
    FabricConfigError,
    FabricFederationClient,
    FabricFederationConfig,
    FabricIntegrityError,
)
from tests.doctor_fixture import DOCTOR_RESULT

REPO_ROOT = Path(__file__).resolve().parents[1]

LOCAL_DID = (
    "did:multiverse:somatic#aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
)
SIBLING_DID = (
    "did:multiverse:kortex-audio#bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
)
OTHER_DID = "did:multiverse:other#cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
SIDECAR_AUTH_VALUE = "sidecar-secret-token-for-invariants"
REGISTRY_AUTH_VALUE = "registry-secret-token-for-invariants"


# ---------------------------------------------------------------------------
# I3 — allowlist reject both ways
# ---------------------------------------------------------------------------


class AllowlistRejectBothWaysTests(unittest.TestCase):
    """A non-allowlisted DID must be rejected on send AND receive."""

    def setUp(self):
        self.sidecar_state: dict = {"payloads": {}, "descriptors": {}}
        self.registry_state: dict = {"allowlist": [SIBLING_DID], "inbox": [], "deliveries": []}
        self.sidecar_server = _start_server(_make_sidecar_handler(self.sidecar_state))
        self.registry_server = _start_server(_make_registry_handler(self.registry_state))
        self.addCleanup(_stop_server, self.registry_server)
        self.addCleanup(_stop_server, self.sidecar_server)

    def _config(self, allowlist=(SIBLING_DID,)):
        return FabricFederationConfig(
            sidecar_base_url=_server_url(self.sidecar_server),
            sidecar_token=SIDECAR_AUTH_VALUE,
            registry_base_url=_server_url(self.registry_server),
            registry_token=REGISTRY_AUTH_VALUE,
            local_did=LOCAL_DID,
            allowlisted_sibling_dids=tuple(allowlist),
            timeout_seconds=5.0,
            max_payload_bytes=1024 * 1024,
        )

    def test_send_to_non_allowlisted_did_is_rejected(self):
        """I3 send direction — must raise before any sidecar PUT or delivery POST."""
        client = FabricFederationClient(self._config())
        with self.assertRaises(FabricAllowlistError):
            client.send(OTHER_DID, b"should never be sent")
        # No delivery should have been recorded.
        self.assertEqual(self.registry_state["deliveries"], [])
        # No payload should have been stored in the sidecar.
        self.assertEqual(self.sidecar_state["payloads"], {})

    def test_receive_from_non_allowlisted_did_is_rejected(self):
        """I3 receive direction — a non-allowlisted sender is rejected."""
        content_id, descriptor = _store_sidecar_payload(self.sidecar_state, b"blocked sender")
        self.registry_state["inbox"].append(
            {
                "fromDid": OTHER_DID,
                "toDid": LOCAL_DID,
                "contentId": content_id,
                "descriptor": descriptor,
            }
        )
        with self.assertRaises(FabricAllowlistError):
            FabricFederationClient(self._config()).receive_once()

    def test_send_to_self_is_rejected_when_not_in_allowlist(self):
        """I3 — local DID is discarded from the allowlist by fetch_allowlist."""
        self.registry_state["allowlist"] = [LOCAL_DID]
        # If the only allowlisted DID is the local DID, fetch_allowlist
        # discards it and raises because the result is empty.
        with self.assertRaises(FabricAllowlistError):
            FabricFederationClient(self._config(allowlist=(LOCAL_DID,))).send(
                SIBLING_DID,
                b"self send",
            )


# ---------------------------------------------------------------------------
# I4 — tampered contentId / descriptor rejected before delivery
# ---------------------------------------------------------------------------


class IntegrityReverifyTests(unittest.TestCase):
    """Inbound bytes must be re-verified against the descriptor contentId."""

    def setUp(self):
        self.sidecar_state: dict = {
            "payloads": {},
            "descriptors": {},
            "tamper_content_ids": set(),
        }
        self.registry_state: dict = {"allowlist": [SIBLING_DID], "inbox": [], "deliveries": []}
        self.sidecar_server = _start_server(_make_sidecar_handler(self.sidecar_state))
        self.registry_server = _start_server(_make_registry_handler(self.registry_state))
        self.addCleanup(_stop_server, self.registry_server)
        self.addCleanup(_stop_server, self.sidecar_server)

    def _config(self):
        return FabricFederationConfig(
            sidecar_base_url=_server_url(self.sidecar_server),
            sidecar_token=SIDECAR_AUTH_VALUE,
            registry_base_url=_server_url(self.registry_server),
            registry_token=REGISTRY_AUTH_VALUE,
            local_did=LOCAL_DID,
            allowlisted_sibling_dids=(SIBLING_DID,),
            timeout_seconds=5.0,
            max_payload_bytes=1024 * 1024,
        )

    def test_tampered_payload_byte_is_rejected(self):
        """I4 — a single flipped byte in the sidecar payload is caught."""
        content_id, descriptor = _store_sidecar_payload(self.sidecar_state, b"integrity target")
        self.sidecar_state["tamper_content_ids"].add(content_id)
        self.registry_state["inbox"].append(
            {
                "fromDid": SIBLING_DID,
                "toDid": LOCAL_DID,
                "contentId": content_id,
                "descriptor": descriptor,
            }
        )
        with self.assertRaises(FabricIntegrityError):
            FabricFederationClient(self._config()).receive_once()

    def test_mismatched_inbound_descriptor_contentId_is_rejected(self):
        """I4 — if the inbox descriptor contentId differs from the sidecar's, reject."""
        content_id, _ = _store_sidecar_payload(self.sidecar_state, b"real bytes")
        # Build a second descriptor for different bytes, then swap the contentId.
        other_id, other_descriptor = _store_sidecar_payload(self.sidecar_state, b"different bytes")
        forged_descriptor = dict(other_descriptor)
        forged_descriptor["contentId"] = content_id
        forged_descriptor["merkleRoot"] = content_id
        self.registry_state["inbox"].append(
            {
                "fromDid": SIBLING_DID,
                "toDid": LOCAL_DID,
                "contentId": content_id,
                "descriptor": forged_descriptor,
            }
        )
        with self.assertRaises((FabricIntegrityError, FabricAllowlistError)):
            FabricFederationClient(self._config()).receive_once()

    def test_empty_payload_descriptor_is_accepted(self):
        """I4 — an empty payload is represented by one zero-size piece and passes."""
        content_id, descriptor = _store_sidecar_payload(self.sidecar_state, b"")
        self.registry_state["inbox"].append(
            {
                "fromDid": SIBLING_DID,
                "toDid": LOCAL_DID,
                "contentId": content_id,
                "descriptor": descriptor,
            }
        )
        received = FabricFederationClient(self._config()).receive_once()
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].payload, b"")


# ---------------------------------------------------------------------------
# I5 — Secure Drop ciphertext preserved
# ---------------------------------------------------------------------------


class CiphertextPreservedTests(unittest.TestCase):
    """Encrypted payloads must never be decrypted in-process."""

    def setUp(self):
        self.sidecar_state: dict = {"payloads": {}, "descriptors": {}}
        self.registry_state: dict = {"allowlist": [SIBLING_DID], "inbox": [], "deliveries": []}
        self.sidecar_server = _start_server(_make_sidecar_handler(self.sidecar_state))
        self.registry_server = _start_server(_make_registry_handler(self.registry_state))
        self.addCleanup(_stop_server, self.registry_server)
        self.addCleanup(_stop_server, self.sidecar_server)

    def _config(self):
        return FabricFederationConfig(
            sidecar_base_url=_server_url(self.sidecar_server),
            sidecar_token=SIDECAR_AUTH_VALUE,
            registry_base_url=_server_url(self.registry_server),
            registry_token=REGISTRY_AUTH_VALUE,
            local_did=LOCAL_DID,
            allowlisted_sibling_dids=(SIBLING_DID,),
            timeout_seconds=5.0,
            max_payload_bytes=1024 * 1024,
        )

    def test_secure_send_preserves_ciphertext_in_sidecar(self):
        """I5 — sending with secure=True stores the raw ciphertext; no decryption."""
        ciphertext = b"\x00\x01\x02\x03\x04\x05ciphertext-bytes"
        result = FabricFederationClient(self._config()).send(SIBLING_DID, ciphertext, secure=True)
        self.assertTrue(result.secure)
        self.assertEqual(self.sidecar_state["payloads"][result.content_id], ciphertext)
        self.assertTrue(self.registry_state["deliveries"][0]["secure"])
        self.assertTrue(self.registry_state["deliveries"][0]["ciphertext"])

    def test_secure_receive_returns_ciphertext_unchanged(self):
        """I5 — receiving a secure payload returns the exact ciphertext bytes."""
        ciphertext = b"\xff\xfe\xfd\xfcencrypted-drop-payload"
        content_id, descriptor = _store_sidecar_payload(self.sidecar_state, ciphertext)
        self.registry_state["inbox"].append(
            {
                "fromDid": SIBLING_DID,
                "toDid": LOCAL_DID,
                "contentId": content_id,
                "descriptor": descriptor,
                "secure": True,
                "ciphertext": True,
            }
        )
        received = FabricFederationClient(self._config()).receive_once()
        self.assertEqual(len(received), 1)
        self.assertTrue(received[0].secure)
        self.assertEqual(received[0].payload, ciphertext)

    def test_no_decryption_function_exists_in_module(self):
        """I5 — the federation module must not contain any decrypt/decipher function."""
        source = (REPO_ROOT / "somatic" / "fabric" / "federation.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                name_lower = node.name.lower()
                self.assertNotIn(
                    "decrypt",
                    name_lower,
                    "federation.py must not implement a decryption function",
                )
                self.assertNotIn(
                    "decipher",
                    name_lower,
                    "federation.py must not implement a decipher function",
                )


# ---------------------------------------------------------------------------
# I6 — fail-closed on missing config
# ---------------------------------------------------------------------------


class FailClosedConfigTests(unittest.TestCase):
    """Missing sidecar URL / token / DID / allowlist => connector inert."""

    _VALID_ENV = {
        "SOMATIC_FABRIC_SIDECAR_URL": "http://127.0.0.1:37877",
        "SOMATIC_FABRIC_SIDECAR_TOKEN": "tok",  # nosec B105 — test fixture, not a real secret
        "SOMATIC_FABRIC_REGISTRY_URL": "http://127.0.0.1:37878",
        "SOMATIC_FABRIC_REGISTRY_TOKEN": "tok",  # nosec B105 — test fixture, not a real secret
        "SOMATIC_FABRIC_DID": LOCAL_DID,
        "SOMATIC_FABRIC_ALLOWLIST_DIDS": SIBLING_DID,
    }

    def test_blank_env_produces_inert_config(self):
        """I6 — an empty env dict must produce a config that fails validation."""
        config = FabricFederationConfig.from_env({})
        with self.assertRaises(FabricConfigError):
            config.validate()

    def test_missing_sidecar_url_raises(self):
        env = dict(self._VALID_ENV)
        del env["SOMATIC_FABRIC_SIDECAR_URL"]
        config = FabricFederationConfig.from_env(env)
        with self.assertRaises(FabricConfigError):
            config.validate()

    def test_empty_sidecar_url_raises(self):
        env = dict(self._VALID_ENV)
        env["SOMATIC_FABRIC_SIDECAR_URL"] = ""
        config = FabricFederationConfig.from_env(env)
        with self.assertRaises(FabricConfigError):
            config.validate()

    def test_missing_sidecar_token_raises(self):
        env = dict(self._VALID_ENV)
        del env["SOMATIC_FABRIC_SIDECAR_TOKEN"]
        env.pop("FABRIC_TRANSPORT_D_AUTH_TOKEN", None)
        config = FabricFederationConfig.from_env(env)
        with self.assertRaises(FabricConfigError):
            config.validate()

    def test_missing_registry_url_raises(self):
        env = dict(self._VALID_ENV)
        del env["SOMATIC_FABRIC_REGISTRY_URL"]
        config = FabricFederationConfig.from_env(env)
        with self.assertRaises(FabricConfigError):
            config.validate()

    def test_missing_registry_token_raises(self):
        env = dict(self._VALID_ENV)
        del env["SOMATIC_FABRIC_REGISTRY_TOKEN"]
        config = FabricFederationConfig.from_env(env)
        with self.assertRaises(FabricConfigError):
            config.validate()

    def test_missing_did_raises(self):
        env = dict(self._VALID_ENV)
        del env["SOMATIC_FABRIC_DID"]
        config = FabricFederationConfig.from_env(env)
        with self.assertRaises(FabricConfigError):
            config.validate()

    def test_non_loopback_sidecar_url_raises(self):
        env = dict(self._VALID_ENV)
        env["SOMATIC_FABRIC_SIDECAR_URL"] = "http://10.0.0.1:37877"
        config = FabricFederationConfig.from_env(env)
        with self.assertRaises(FabricConfigError):
            config.validate()

    def test_https_sidecar_url_raises(self):
        env = dict(self._VALID_ENV)
        env["SOMATIC_FABRIC_SIDECAR_URL"] = "https://127.0.0.1:37877"
        config = FabricFederationConfig.from_env(env)
        with self.assertRaises(FabricConfigError):
            config.validate()

    def test_credentials_in_sidecar_url_raises(self):
        env = dict(self._VALID_ENV)
        env["SOMATIC_FABRIC_SIDECAR_URL"] = "http://user:pass@127.0.0.1:37877"
        config = FabricFederationConfig.from_env(env)
        with self.assertRaises(FabricConfigError):
            config.validate()

    def test_client_constructor_validates(self):
        """I6 — FabricFederationClient constructor calls validate() and fails closed."""
        with self.assertRaises(FabricConfigError):
            FabricFederationClient(FabricFederationConfig.from_env({}))

    def test_blank_env_sends_nothing(self):
        """I6 — from_env({}) cannot produce a client that transmits anything."""
        config = FabricFederationConfig.from_env({})
        # Every field that would enable transport is empty.
        self.assertEqual(config.sidecar_base_url, "")
        self.assertEqual(config.sidecar_token, "")
        self.assertEqual(config.registry_base_url, "")
        self.assertEqual(config.registry_token, "")
        self.assertEqual(config.local_did, "")
        self.assertEqual(config.allowlisted_sibling_dids, ())


# ---------------------------------------------------------------------------
# I7 — no secrets in logs
# ---------------------------------------------------------------------------


class NoSecretsInLogsTests(unittest.TestCase):
    """Tokens, DID keys, and bearer values must never be printed or logged."""

    SECRET_VALUES = (
        SIDECAR_AUTH_VALUE,
        REGISTRY_AUTH_VALUE,
        "sidecar-secret-token-for-invariants",
        "registry-secret-token-for-invariants",
    )

    def test_no_print_or_logging_calls_in_federation_module(self):
        """I7 — federation.py must not contain print() or logging calls."""
        source = (REPO_ROOT / "somatic" / "fabric" / "federation.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "print":
                    self.fail("federation.py must not call print()")
                if isinstance(func, ast.Attribute) and func.attr == "print":
                    self.fail("federation.py must not call .print()")
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertNotEqual(
                        alias.name,
                        "logging",
                        "federation.py must not import the logging module",
                    )
            if isinstance(node, ast.ImportFrom):
                self.assertNotEqual(
                    node.module,
                    "logging",
                    "federation.py must not import from the logging module",
                )

    def test_token_not_in_exception_messages(self):
        """I7 — exception messages must not contain the raw token value."""
        config = FabricFederationConfig(
            sidecar_base_url="http://127.0.0.1:1",
            sidecar_token=SIDECAR_AUTH_VALUE,
            registry_base_url="http://127.0.0.1:2",
            registry_token=REGISTRY_AUTH_VALUE,
            local_did=LOCAL_DID,
            allowlisted_sibling_dids=(SIBLING_DID,),
            timeout_seconds=0.5,
        )
        client = FabricFederationClient(config)
        # Trigger an HTTP error by hitting a non-listening port.
        try:
            client.send(SIBLING_DID, b"trigger error")
        except Exception as exc:
            message = str(exc)
            for secret in self.SECRET_VALUES:
                self.assertNotIn(
                    secret,
                    message,
                    f"exception message must not contain token value: {secret}",
                )
        else:
            self.fail("expected an exception when connecting to a non-listening port")

    def test_token_not_in_exception_or_raise_fstrings(self):
        """I7 — f-strings used in raise/exception messages must not embed tokens.

        The Authorization header legitimately uses the token in an f-string, but
        that string is sent over HTTP, never logged.  Exception messages, however,
        could be logged by a caller, so they must not contain raw token values.
        """
        source = (REPO_ROOT / "somatic" / "fabric" / "federation.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        token_field_names = {"sidecar_token", "registry_token"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Raise):
                # Check the exception argument for f-strings embedding tokens.
                if node.exc is not None and isinstance(node.exc, ast.Call):
                    for arg in node.exc.args:
                        if isinstance(arg, ast.JoinedStr):
                            for value_node in arg.values:
                                if isinstance(value_node, ast.FormattedValue):
                                    fmt = ast.dump(value_node)
                                    for field in token_field_names:
                                        self.assertNotIn(
                                            field,
                                            fmt,
                                            f"exception f-string must not embed {field}",
                                        )


# ---------------------------------------------------------------------------
# I1/I2 — stdlib-only and out-of-process-only (complement existing test)
# ---------------------------------------------------------------------------


class StdlibAndOutOfProcessTests(unittest.TestCase):
    """Additional I1/I2 checks that complement the existing connect test."""

    def test_pyproject_dependencies_stay_empty(self):
        pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(pyproject["project"]["dependencies"], [])

    def test_no_socket_or_subprocess_import_in_federation(self):
        """I2 — no raw socket, subprocess, or third-party network imports."""
        source = (REPO_ROOT / "somatic" / "fabric" / "federation.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        forbidden_roots = {"socket", "subprocess", "ssl", "asyncio", "requests", "httpx", "aiohttp"}
        allowed_roots = {
            "__future__",
            "collections",
            "dataclasses",
            "hashlib",
            "json",
            "os",
            "pathlib",
            "typing",
            "urllib",
        }
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = {alias.name.split(".")[0] for alias in node.names}
                self.assertLessEqual(imported, allowed_roots)
                for root in imported:
                    self.assertNotIn(root, forbidden_roots)
            if isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".")[0]
                self.assertIn(root, allowed_roots)
                self.assertNotIn(root, forbidden_roots)

    def test_no_dht_swarm_or_chunking_reimplementation(self):
        """I2 — no DHT, swarm, bittorrent, or content-chunking implementation."""
        source = (REPO_ROOT / "somatic" / "fabric" / "federation.py").read_text(encoding="utf-8")
        source_lower = source.lower()
        forbidden_terms = (
            "dht",
            "swarm",
            "bittorrent",
            "webtorrent",
            "libp2p",
            "chunk_payload",
            "split_into_chunks",
            "create_descriptor",
            "build_descriptor",
            "@multiverse/fabric-core",
            "fabric_core",
        )
        for term in forbidden_terms:
            self.assertNotIn(term, source_lower, f"federation.py must not contain '{term}'")


# ---------------------------------------------------------------------------
# I8 — pre-runtime boundary (doctor output check)
# ---------------------------------------------------------------------------


class PreRuntimeBoundaryTests(unittest.TestCase):
    """I8 — somatic doctor must keep real-mode runtime blocked."""

    def test_doctor_reports_fabric_out_of_process(self):
        """I8 — doctor output mentions the out-of-process sidecar connector."""
        output = DOCTOR_RESULT[1]
        self.assertIn("out-of-process", output.lower() + output)
        self.assertIn("fabric federation", output.lower() + output)

    def test_doctor_reports_runtime_blocked(self):
        """I8 — doctor output confirms real-mode runtime is blocked/disabled."""
        output = DOCTOR_RESULT[1].lower()
        self.assertIn("disabled", output)
        # The fabric-specific lines must not claim real-mode runtime is enabled.
        for line in output.splitlines():
            if "fabric federation" in line:
                self.assertNotIn("real runtime enabled", line)
                self.assertNotIn("runtime execution: enabled", line)


# ---------------------------------------------------------------------------
# Local HTTP server helpers (same pattern as test_fabric_federation_connect)
# ---------------------------------------------------------------------------


def _start_server(handler_class):
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler_class)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    server.test_thread = thread
    thread.start()
    return server


def _stop_server(server):
    server.shutdown()
    server.server_close()
    server.test_thread.join(timeout=5)


def _server_url(server):
    host, port = server.server_address
    return f"http://{host}:{port}"


def _make_sidecar_handler(state):
    class SidecarHandler(BaseHTTPRequestHandler):
        def do_PUT(self):
            self._require_auth()
            if self.path != "/v1/content":
                self._send_json({"error": "not_found"}, status=404)
                return
            payload = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            content_id, descriptor = _store_sidecar_payload(state, payload)
            self._send_json({"contentId": content_id, "descriptor": descriptor})

        def do_GET(self):
            self._require_auth()
            path = urllib_parse.urlsplit(self.path).path
            prefix = "/v1/content/"
            if not path.startswith(prefix):
                self._send_json({"error": "not_found"}, status=404)
                return
            suffix = path[len(prefix) :]
            if suffix.endswith("/descriptor"):
                content_id = suffix.removesuffix("/descriptor")
                descriptor = state["descriptors"].get(content_id)
                if descriptor is None:
                    self._send_json({"error": "not_found"}, status=404)
                    return
                self._send_json({"contentId": content_id, "descriptor": descriptor})
                return
            content_id = suffix
            payload = state["payloads"].get(content_id)
            if payload is None:
                self._send_json({"error": "not_found"}, status=404)
                return
            if content_id in state.get("tamper_content_ids", set()):
                payload = _tamper(payload)
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def _require_auth(self):
            if self.headers.get("Authorization") != f"Bearer {SIDECAR_AUTH_VALUE}":
                self._send_json({"error": "unauthorized"}, status=401)
                raise ConnectionAbortedError("unauthorized")

        def _send_json(self, payload, status=200):
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            return None

    return SidecarHandler


def _make_registry_handler(state):
    class RegistryHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            self._require_auth()
            payload = self._read_json()
            if self.path == "/systems/register":
                state.setdefault("registers", []).append(payload)
                self._send_json({"ok": True, "id": payload.get("id"), "did": payload.get("did")})
                return
            if self.path == "/fabric/federation/deliveries":
                state["deliveries"].append(payload)
                self._send_json({"ok": True, "contentId": payload.get("contentId")})
                return
            self._send_json({"error": "not_found"}, status=404)

        def do_GET(self):
            self._require_auth()
            path = urllib_parse.urlsplit(self.path).path
            if path == "/fabric/federation/allowlist":
                self._send_json({"allowlistedDids": state["allowlist"]})
                return
            if path == "/fabric/federation/inbox":
                self._send_json({"items": state["inbox"]})
                return
            self._send_json({"error": "not_found"}, status=404)

        def _require_auth(self):
            if self.headers.get("Authorization") != f"Bearer {REGISTRY_AUTH_VALUE}":
                self._send_json({"error": "unauthorized"}, status=401)
                raise ConnectionAbortedError("unauthorized")

        def _read_json(self):
            body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            return json.loads(body.decode("utf-8"))

        def _send_json(self, payload, status=200):
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            return None

    return RegistryHandler


def _store_sidecar_payload(state, payload):
    descriptor = _descriptor_for_payload(payload)
    content_id = descriptor["contentId"]
    state["payloads"][content_id] = payload
    state["descriptors"][content_id] = descriptor
    return content_id, descriptor


def _descriptor_for_payload(payload, piece_size=5):
    chunks = [payload[index : index + piece_size] for index in range(0, len(payload), piece_size)]
    if not chunks:
        chunks = [b""]
    pieces = []
    offset = 0
    for index, chunk in enumerate(chunks):
        pieces.append(
            {
                "index": index,
                "offset": offset,
                "size": len(chunk),
                "sha256": hashlib.sha256(b"\x00" + chunk).hexdigest(),
            }
        )
        offset += len(chunk)
    merkle_root = _merkle_root([bytes.fromhex(piece["sha256"]) for piece in pieces])
    return {
        "schemaVersion": "1.0.0",
        "transport": "fabric-ca",
        "hash": "sha256",
        "merkle": "sha256-domain-separated-binary-pair-v1",
        "pieceSize": piece_size,
        "totalSize": len(payload),
        "pieces": pieces,
        "merkleRoot": merkle_root,
        "contentId": merkle_root,
    }


def _merkle_root(leaf_hashes):
    level = list(leaf_hashes)
    while len(level) > 1:
        next_level = []
        for index in range(0, len(level), 2):
            left = level[index]
            right = level[index + 1] if index + 1 < len(level) else left
            next_level.append(hashlib.sha256(b"\x01" + left + right).digest())
        level = next_level
    return level[0].hex()


def _tamper(payload):
    if not payload:
        return b"x"
    return bytes([payload[0] ^ 1]) + payload[1:]


if __name__ == "__main__":
    unittest.main()
