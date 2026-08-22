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
    FabricFederationClient,
    FabricFederationConfig,
    FabricIntegrityError,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
LOCAL_DID = (
    "did:multiverse:somatic#aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
)
SIBLING_DID = (
    "did:multiverse:kortex-audio#bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
)
OTHER_DID = "did:multiverse:other#cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
SIDECAR_AUTH_VALUE = "sidecar-test-auth"
REGISTRY_AUTH_VALUE = "registry-test-auth"


class FabricFederationConnectTests(unittest.TestCase):
    def setUp(self):
        self.sidecar_state = {
            "payloads": {},
            "descriptors": {},
            "auth_headers": [],
            "tamper_content_ids": set(),
        }
        self.registry_state = {
            "allowlist": [SIBLING_DID],
            "inbox": [],
            "deliveries": [],
            "registers": [],
            "auth_headers": [],
        }
        self.sidecar_server = _start_server(_make_sidecar_handler(self.sidecar_state))
        self.registry_server = _start_server(_make_registry_handler(self.registry_state))
        self.addCleanup(_stop_server, self.registry_server)
        self.addCleanup(_stop_server, self.sidecar_server)

    def config(self, allowlist=(SIBLING_DID,)):
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

    def test_register_authenticates_via_registry(self):
        result = FabricFederationClient(self.config()).connect()

        self.assertTrue(result["registered"])
        self.assertEqual(result["localDid"], LOCAL_DID)
        self.assertEqual(self.registry_state["auth_headers"][0], f"Bearer {REGISTRY_AUTH_VALUE}")
        self.assertEqual(self.registry_state["registers"][0]["did"], LOCAL_DID)

    def test_send_reaches_allowlisted_sibling(self):
        result = FabricFederationClient(self.config()).send(SIBLING_DID, b"fabric bytes")

        self.assertEqual(result.to_did, SIBLING_DID)
        self.assertIn(result.content_id, self.sidecar_state["payloads"])
        self.assertEqual(self.registry_state["deliveries"][0]["toDid"], SIBLING_DID)
        self.assertEqual(self.registry_state["deliveries"][0]["contentId"], result.content_id)
        self.assertFalse(self.registry_state["deliveries"][0]["secure"])

    def test_receive_from_allowlisted_sibling_reverifies_content(self):
        content_id, descriptor = _store_sidecar_payload(self.sidecar_state, b"trusted inbound")
        self.registry_state["inbox"].append(
            {
                "fromDid": SIBLING_DID,
                "toDid": LOCAL_DID,
                "contentId": content_id,
                "descriptor": descriptor,
            }
        )

        received = FabricFederationClient(self.config()).receive_once()

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].from_did, SIBLING_DID)
        self.assertEqual(received[0].payload, b"trusted inbound")
        self.assertEqual(received[0].content_id, content_id)

    def test_receive_rejects_non_allowlisted_sibling_did(self):
        content_id, descriptor = _store_sidecar_payload(self.sidecar_state, b"blocked inbound")
        self.registry_state["inbox"].append(
            {
                "fromDid": OTHER_DID,
                "toDid": LOCAL_DID,
                "contentId": content_id,
                "descriptor": descriptor,
            }
        )

        with self.assertRaises(FabricAllowlistError):
            FabricFederationClient(self.config()).receive_once()

    def test_content_id_reverify_catches_tampered_byte(self):
        content_id, descriptor = _store_sidecar_payload(self.sidecar_state, b"tamper target")
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
            FabricFederationClient(self.config()).receive_once()

    def test_encrypted_transfers_stay_ciphertext(self):
        ciphertext = b"ciphertext-not-plaintext"
        send_result = FabricFederationClient(self.config()).send(
            SIBLING_DID,
            ciphertext,
            secure=True,
        )
        self.assertTrue(self.registry_state["deliveries"][0]["secure"])
        self.assertEqual(self.sidecar_state["payloads"][send_result.content_id], ciphertext)

        self.registry_state["inbox"].append(
            {
                "fromDid": SIBLING_DID,
                "toDid": LOCAL_DID,
                "contentId": send_result.content_id,
                "secure": True,
            }
        )
        received = FabricFederationClient(self.config()).receive_once()

        self.assertTrue(received[0].secure)
        self.assertEqual(received[0].payload, ciphertext)

    def test_dependencies_stay_empty_and_connector_avoids_private_js_imports(self):
        pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(pyproject["project"]["dependencies"], [])

        checked_files = [
            REPO_ROOT / "somatic" / "fabric" / "federation.py",
            REPO_ROOT / "somatic" / "cli" / "main.py",
        ]
        forbidden_fragments = (
            "@multiverse/fabric-core",
            "fabric_core",
            "from fabric_core",
            "import fabric_core",
            "requests",
            "aiohttp",
            "websocket",
            "bittorrent",
            "webtorrent",
        )
        for path in checked_files:
            text = path.read_text(encoding="utf-8").lower()
            for fragment in forbidden_fragments:
                with self.subTest(path=path.name, fragment=fragment):
                    self.assertNotIn(fragment, text)

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
        tree = ast.parse((REPO_ROOT / "somatic" / "fabric" / "federation.py").read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = {alias.name.split(".")[0] for alias in node.names}
                self.assertLessEqual(imported, allowed_roots)
            if isinstance(node, ast.ImportFrom) and node.module:
                self.assertIn(node.module.split(".")[0], allowed_roots)


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
            if content_id in state["tamper_content_ids"]:
                payload = _tamper(payload)
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("X-Fabric-Content-Id", content_id)
            self.end_headers()
            self.wfile.write(payload)

        def _require_auth(self):
            state["auth_headers"].append(self.headers.get("Authorization", ""))
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
                state["registers"].append(payload)
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
            state["auth_headers"].append(self.headers.get("Authorization", ""))
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
