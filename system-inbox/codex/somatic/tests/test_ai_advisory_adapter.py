"""Tests for the consent-gated OpenAI-compatible AI advisory adapter."""

from __future__ import annotations

import json
import threading
import tomllib
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from somatic.advisory import (
    AGENTS_A1,
    OPENAI_COMPATIBLE,
    AdvisoryConfigError,
    AdvisoryHttpError,
    AdvisoryModelClient,
    AdvisoryModelConfig,
)
from somatic.advisory.adapter import SAFE_FALLBACK_SUMMARY
from somatic.consent import AI_ADVISORY, ConsentLedger
from somatic.safety.core import (
    INFORMATIONAL_NOTICE,
    ConsentRequiredError,
    EvidenceGrade,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


class AiAdvisoryAdapterTests(unittest.TestCase):
    def setUp(self):
        self.state = {
            "requests": [],
            "response_text": (
                "Your data suggests sleep duration may relate to next-day energy. "
                "Evidence grade: moderate. It may be worth discussing this pattern "
                "with a licensed professional."
            ),
            "status": 200,
        }
        self.server = _start_server(_make_chat_handler(self.state))
        self.addCleanup(_stop_server, self.server)

    def _config(self, **overrides):
        values = {
            "model_url": _server_url(self.server),
            "model": "test-model",
            "model_key": "",
            "timeout_seconds": 5.0,
            "option_id": OPENAI_COMPATIBLE.id,
            "chat_path": "/v1/chat/completions",
        }
        values.update(overrides)
        return AdvisoryModelConfig(**values)

    def test_analyze_requires_ai_advisory_consent_without_http(self):
        ledger = ConsentLedger()
        client = AdvisoryModelClient(self._config())
        with self.assertRaises(ConsentRequiredError):
            client.analyze(ledger, {"hrv": [50, 52]}, "Any patterns?")
        self.assertEqual(self.state["requests"], [])

    def test_analyze_returns_informational_advisory_from_mock(self):
        ledger = ConsentLedger()
        ledger.grant(AI_ADVISORY)
        client = AdvisoryModelClient(self._config(model_key="test-key"))
        result = client.analyze(
            ledger,
            {"sleep_hours": [6.5, 7.0, 6.0]},
            "What does my sleep log suggest?",
        )
        self.assertEqual(result.informational_notice, INFORMATIONAL_NOTICE)
        self.assertEqual(result.evidence_grade, EvidenceGrade.MODERATE)
        self.assertEqual(result.consent_scope, AI_ADVISORY.id)
        self.assertIn("licensed professional", result.summary.lower())
        self.assertEqual(len(self.state["requests"]), 1)
        request = self.state["requests"][0]
        self.assertEqual(request["authorization"], "Bearer test-key")
        self.assertEqual(request["body"]["model"], "test-model")
        self.assertEqual(request["body"]["messages"][0]["role"], "system")

    def test_emergency_input_skips_endpoint(self):
        ledger = ConsentLedger()
        ledger.grant(AI_ADVISORY)
        client = AdvisoryModelClient(self._config())
        result = client.analyze(
            ledger,
            {"notes": ["felt odd"]},
            "I have sudden chest pain — what should I do?",
        )
        self.assertEqual(result.evidence_grade, EvidenceGrade.NONE)
        self.assertIn("emergency", result.summary.lower())
        self.assertEqual(self.state["requests"], [])

    def test_authoritative_model_text_returns_safe_fallback(self):
        self.state["response_text"] = (
            "You have hypertension. Take 500 mg of medication twice daily."
        )
        ledger = ConsentLedger()
        ledger.grant(AI_ADVISORY)
        client = AdvisoryModelClient(self._config())
        result = client.analyze(
            ledger,
            {"bp": [150, 95]},
            "Interpret my blood pressure readings.",
        )
        self.assertEqual(result.evidence_grade, EvidenceGrade.NONE)
        self.assertEqual(result.summary, SAFE_FALLBACK_SUMMARY)
        self.assertNotIn("You have hypertension", result.summary)
        self.assertNotIn("500 mg", result.summary)
        self.assertEqual(len(self.state["requests"]), 1)

    def test_model_output_emergency_is_re_screened(self):
        self.state["response_text"] = (
            "Your notes mention crushing pressure in my chest; go to the ER."
        )
        ledger = ConsentLedger()
        ledger.grant(AI_ADVISORY)
        client = AdvisoryModelClient(self._config())
        result = client.analyze(
            ledger,
            {"notes": ["felt odd"]},
            "What stands out in my notes?",
        )
        self.assertEqual(result.evidence_grade, EvidenceGrade.NONE)
        self.assertIn("emergency", result.summary.lower())
        self.assertEqual(len(self.state["requests"]), 1)
        self.assertNotIn("go to the ER", result.summary)

    def test_https_or_loopback_required_when_key_set(self):
        with self.assertRaises(AdvisoryConfigError):
            AdvisoryModelClient(
                AdvisoryModelConfig(
                    model_url="http://example.invalid/v1",
                    model="test-model",
                    model_key="secret",
                )
            )
        client = AdvisoryModelClient(
            AdvisoryModelConfig(
                model_url="http://127.0.0.1:9",
                model="test-model",
                model_key="secret",
            )
        )
        self.assertIsNotNone(client)

    def test_metadata_ip_encodings_rejected_when_key_set(self):
        urls = (
            "http://169.254.169.254/",
            "https://169.254.169.254/latest/meta-data/",
            "http://2852039166/",
            "https://0xa9fea9fe/",
            "http://0251.0376.0251.0376/",
            "http://[::ffff:169.254.169.254]/",
            "https://[::ffff:a9fe:a9fe]/",
            "https://[2002:a9fe:a9fe::]/",
            "https://metadata.google.internal/",
            "https://192.168.1.10/",
            "https://10.1.2.3/",
            "https://[fd12:3456:789a::1]/",
            "https://169.254.1.1/",
        )
        for url in urls:
            with self.subTest(url=url):
                with self.assertRaises(AdvisoryConfigError):
                    AdvisoryModelClient(
                        AdvisoryModelConfig(
                            model_url=url,
                            model="test-model",
                            model_key="secret",
                        )
                    )

    def test_private_lan_rejected_even_without_model_key(self):
        with self.assertRaises(AdvisoryConfigError):
            AdvisoryModelClient(
                AdvisoryModelConfig(
                    model_url="https://192.168.1.10/v1",
                    model="test-model",
                )
            )

    def test_http_redirects_are_refused_and_do_not_follow_auth(self):
        self.state["status"] = 302
        self.state["location"] = "http://169.254.169.254/latest/meta-data/"
        ledger = ConsentLedger()
        ledger.grant(AI_ADVISORY)
        client = AdvisoryModelClient(self._config(model_key="test-key"))
        with self.assertRaises(AdvisoryHttpError) as raised:
            client.analyze(ledger, {"hrv": [50]}, "Any patterns?")
        self.assertIn("redirects are not followed", str(raised.exception))
        self.assertEqual(len(self.state["requests"]), 1)
        self.assertEqual(self.state["requests"][0]["authorization"], "Bearer test-key")

    def test_v1_base_url_is_not_doubled(self):
        from somatic.advisory.adapter import _join_base_url

        self.assertEqual(
            _join_base_url("http://localhost:11434/v1", "/v1/chat/completions"),
            "http://localhost:11434/v1/chat/completions",
        )
        self.assertEqual(
            _join_base_url("http://localhost:11434", "/v1/chat/completions"),
            "http://localhost:11434/v1/chat/completions",
        )
        with self.assertRaises(AdvisoryConfigError):
            AdvisoryModelConfig.from_env({}).validate()
        with self.assertRaises(AdvisoryConfigError):
            AdvisoryModelClient(AdvisoryModelConfig(model_url="", model="test-model"))
        with self.assertRaises(AdvisoryConfigError):
            AdvisoryModelClient(AdvisoryModelConfig(model_url="http://127.0.0.1:9", model=""))

    def test_model_registry_includes_agents_a1_and_generic(self):
        self.assertEqual(AGENTS_A1.model, "InternScience/Agents-A1")
        self.assertEqual(AGENTS_A1.endpoint_style, "openai-chat")
        self.assertEqual(AGENTS_A1.default_path, "/v1/chat/completions")
        self.assertEqual(OPENAI_COMPATIBLE.endpoint_style, "openai-chat")
        self.assertEqual(OPENAI_COMPATIBLE.default_path, "/v1/chat/completions")

    def test_dependencies_stay_empty(self):
        pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(pyproject["project"]["dependencies"], [])


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


def _make_chat_handler(state):
    class ChatHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            try:
                body = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                body = {}
            state["requests"].append(
                {
                    "path": self.path,
                    "authorization": self.headers.get("Authorization"),
                    "body": body,
                }
            )
            if self.path != "/v1/chat/completions":
                self._send_json({"error": "not_found"}, status=404)
                return
            payload = {
                "id": "chatcmpl-test",
                "object": "chat.completion",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": state["response_text"],
                        },
                        "finish_reason": "stop",
                    }
                ],
            }
            self._send_json(payload, status=int(state.get("status", 200)))

        def log_message(self, format, *args):  # noqa: A003
            return

        def _send_json(self, payload, status=200):
            if status in {301, 302, 303, 307, 308}:
                self.send_response(status)
                self.send_header("Location", str(state.get("location") or "/elsewhere"))
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return ChatHandler


if __name__ == "__main__":
    unittest.main()
