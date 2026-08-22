"""Stdlib loopback HTTP server for the local Somatic UI."""

from __future__ import annotations

import json
import mimetypes
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from somatic.bridge.api import BridgeError, dispatch
from somatic.bridge.origin import (
    bind_host_is_allowed,
    hostname_from_host_header,
    is_loopback_hostname,
    origin_is_loopback,
)

STATIC_ROOT = Path(__file__).resolve().parent / "static"
MAX_BODY_BYTES = 8_000_000
DEFAULT_PORT = 8765
BIND_HOST = "127.0.0.1"


class BridgeHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class BridgeHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args: object) -> None:
        sys.stderr.write(f"{self.address_string()} - {format % args}\n")

    def do_OPTIONS(self) -> None:
        if not self._gate_request():
            return
        self._send_bytes(204, b"", extra_headers=self._cors_headers())

    def do_GET(self) -> None:
        self._handle("GET")

    def do_POST(self) -> None:
        self._handle("POST")

    def _handle(self, method: str) -> None:
        if not self._gate_request():
            return
        parsed = urlparse(self.path)
        path = parsed.path or "/"
        query = _query_dict(parsed.query)
        if path.startswith("/api/"):
            try:
                body = self._read_json_body() if method == "POST" else None
                payload = dispatch(method, path, body, query=query)
            except BridgeError as exc:
                self._send_json(
                    exc.status,
                    {"error": exc.code, "message": exc.message, **exc.extra},
                )
                return
            except Exception:
                self._send_json(500, {"error": "internal", "message": "bridge error"})
                return
            self._send_json(200, payload)
            return
        if method != "GET":
            self._send_json(405, {"error": "method_not_allowed", "message": "use GET for pages"})
            return
        self._serve_static(path)

    def _gate_request(self) -> bool:
        host = hostname_from_host_header(self.headers.get("Host", ""))
        origin = self.headers.get("Origin", "")
        if not is_loopback_hostname(host):
            self._send_json(
                403,
                {
                    "error": "non_loopback_host",
                    "message": "Somatic UI only accepts Host: 127.0.0.1 or localhost",
                },
            )
            return False
        if not origin_is_loopback(origin):
            self._send_json(
                403,
                {
                    "error": "non_loopback_origin",
                    "message": "Somatic UI refuses non-loopback Origin headers",
                },
            )
            return False
        return True

    def _read_json_body(self) -> dict[str, Any]:
        length_raw = self.headers.get("Content-Length", "0")
        try:
            length = int(length_raw)
        except ValueError as exc:
            raise BridgeError(400, "invalid_request", "invalid Content-Length") from exc
        if length < 0 or length > MAX_BODY_BYTES:
            raise BridgeError(413, "too_large", "request body exceeds 8 MiB")
        content_type = self.headers.get("Content-Type", "")
        if length > 0 and content_type and "json" not in content_type.lower():
            raise BridgeError(
                415,
                "unsupported_media_type",
                "JSON endpoints accept application/json only",
            )
        raw = self.rfile.read(length) if length else b""
        if not raw:
            return {}
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise BridgeError(400, "invalid_json", "body must be JSON") from exc
        if not isinstance(payload, dict):
            raise BridgeError(400, "invalid_json", "JSON body must be an object")
        return payload

    def _serve_static(self, url_path: str) -> None:
        target = _safe_static_file(url_path)
        if target is None:
            self._send_json(404, {"error": "not_found", "message": "asset not found"})
            return
        data = target.read_bytes()
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if target.suffix == ".js":
            content_type = "application/javascript; charset=utf-8"
        elif target.suffix == ".css":
            content_type = "text/css; charset=utf-8"
        elif target.suffix == ".html":
            content_type = "text/html; charset=utf-8"
        elif target.suffix == ".json":
            content_type = "application/json; charset=utf-8"
        elif target.suffix == ".webmanifest":
            content_type = "application/manifest+json; charset=utf-8"
        elif target.suffix == ".woff2":
            content_type = "font/woff2"
        self._send_bytes(
            200,
            data,
            content_type=content_type,
            extra_headers={
                "Cache-Control": "no-store",
                "Content-Security-Policy": (
                    "default-src 'self'; connect-src 'self'; img-src 'self' data:; "
                    "font-src 'self'; style-src 'self'; script-src 'self'; "
                    "base-uri 'self'; form-action 'self'"
                ),
                "X-Content-Type-Options": "nosniff",
                "Referrer-Policy": "no-referrer",
            },
        )

    def _cors_headers(self) -> dict[str, str]:
        origin = self.headers.get("Origin", "").strip()
        headers = {
            "Vary": "Origin",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }
        if origin and origin_is_loopback(origin):
            headers["Access-Control-Allow-Origin"] = origin
        return headers

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8") + b"\n"
        headers = {
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "no-referrer",
            **self._cors_headers(),
        }
        self._send_bytes(
            status,
            body,
            content_type="application/json; charset=utf-8",
            extra_headers=headers,
        )

    def _send_bytes(
        self,
        status: int,
        body: bytes,
        *,
        content_type: str = "text/plain; charset=utf-8",
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for key, value in (extra_headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if body and self.command != "HEAD":
            self.wfile.write(body)


def _query_dict(query: str) -> dict[str, Any]:
    parsed = parse_qs(query, keep_blank_values=False)
    return {key: values[-1] for key, values in parsed.items() if values}


def _safe_static_file(url_path: str) -> Path | None:
    root = STATIC_ROOT.resolve()
    relative = str(url_path or "/").lstrip("/")
    if not relative:
        relative = "index.html"
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    if candidate.is_file():
        return candidate
    nested = candidate / "index.html"
    if nested.is_file():
        try:
            nested.relative_to(root)
        except ValueError:
            return None
        return nested
    if "." not in Path(relative).name:
        index = root / "index.html"
        if index.is_file():
            return index
    return None


def make_server(host: str = BIND_HOST, port: int = DEFAULT_PORT) -> BridgeHTTPServer:
    if not bind_host_is_allowed(host):
        raise ValueError("ui bind address must be 127.0.0.1 or localhost")
    return BridgeHTTPServer((BIND_HOST, int(port)), BridgeHandler)


def serve_ui(
    *,
    host: str = BIND_HOST,
    port: int = DEFAULT_PORT,
    open_browser: bool = True,
) -> int:
    """Bind 127.0.0.1 and serve the local UI until interrupted."""

    if not bind_host_is_allowed(host):
        print("ui: bind address must be loopback (127.0.0.1)", file=sys.stderr)
        return 2
    httpd = make_server(BIND_HOST, port)
    actual_port = int(httpd.server_address[1])
    url = f"http://127.0.0.1:{actual_port}/"
    print(f"Somatic UI (local-only) at {url}")
    print("Nothing leaves this machine. Press Ctrl+C to stop.")
    if open_browser:
        webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nSomatic UI stopped")
    finally:
        httpd.shutdown()
        httpd.server_close()
    return 0


def start_background_server(*, port: int = 0) -> tuple[BridgeHTTPServer, threading.Thread, int]:
    """Start a daemon server for tests. Caller must shutdown."""

    httpd = make_server(BIND_HOST, port)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd, thread, int(httpd.server_address[1])
