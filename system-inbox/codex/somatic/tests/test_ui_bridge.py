"""Gate tests for the local-only UI bridge (stdlib, loopback)."""

from __future__ import annotations

import contextlib
import http.client
import io
import json
import os
import tempfile
import tomllib
import unittest
from pathlib import Path

from somatic.bridge.serialize import RAW_SENSOR_KEYS
from somatic.bridge.server import STATIC_ROOT, start_background_server
from somatic.cli import main
from somatic.consent import (
    ANALYSIS_INSIGHT,
    AUTONOMOUS_RESEARCH,
    DATA_INGESTION,
    PROFESSIONAL_SHARING,
    REMEDY_LIBRARY,
    load_ledger,
    save_ledger,
)
from somatic.research import HONEST_NULL

REPO_ROOT = Path(__file__).resolve().parents[1]


def _isolate_stores():
    tmp = tempfile.TemporaryDirectory()
    previous = {
        "SOMATIC_CONSENT_PATH": os.environ.get("SOMATIC_CONSENT_PATH"),
        "SOMATIC_INGEST_PATH": os.environ.get("SOMATIC_INGEST_PATH"),
        "SOMATIC_EXPERIMENT_PATH": os.environ.get("SOMATIC_EXPERIMENT_PATH"),
        "SOMATIC_SENSOR_LIVE_PATH": os.environ.get("SOMATIC_SENSOR_LIVE_PATH"),
        "SOMATIC_CSI_FEATURES_PATH": os.environ.get("SOMATIC_CSI_FEATURES_PATH"),
        "SOMATIC_CSI_UDP_PORT": os.environ.get("SOMATIC_CSI_UDP_PORT"),
    }

    def restore() -> None:
        tmp.cleanup()
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    os.environ["SOMATIC_CONSENT_PATH"] = str(Path(tmp.name) / "consent.json")
    os.environ["SOMATIC_INGEST_PATH"] = str(Path(tmp.name) / "readings.json")
    os.environ["SOMATIC_EXPERIMENT_PATH"] = str(Path(tmp.name) / "experiments.json")
    os.environ["SOMATIC_SENSOR_LIVE_PATH"] = str(Path(tmp.name) / "sensor-live.json")
    os.environ["SOMATIC_CSI_FEATURES_PATH"] = str(Path(tmp.name) / "csi-features.json")
    os.environ["SOMATIC_CSI_UDP_PORT"] = "0"
    return restore


def _request(
    port: int,
    method: str,
    path: str,
    *,
    body: dict | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, dict]:
    extra = {"Host": f"127.0.0.1:{port}"}
    if headers:
        extra.update(headers)
    payload = None
    if body is not None:
        payload = json.dumps(body).encode("utf-8")
        extra.setdefault("Content-Type", "application/json")
        extra["Content-Length"] = str(len(payload))
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=30)
    try:
        conn.request(method, path, body=payload, headers=extra)
        response = conn.getresponse()
        raw = response.read().decode("utf-8")
        parsed = json.loads(raw) if raw.strip().startswith("{") else {"raw": raw}
        return response.status, parsed
    finally:
        conn.close()


class UiBridgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self._restore = _isolate_stores()
        self.httpd, self.thread, self.port = start_background_server(port=0)

    def tearDown(self) -> None:
        from somatic.sensors.live_csi import replace_ingest

        replace_ingest(None)
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=5)
        self._restore()

    def test_status_is_legible_when_everything_is_off(self) -> None:
        status, payload = _request(self.port, "GET", "/api/status")
        self.assertEqual(status, 200)
        self.assertTrue(payload["all_scopes_off"])
        self.assertTrue(payload["ok"])
        self.assertEqual(len(payload["scopes"]), 7)
        self.assertTrue(all(row["default"] == "OFF" for row in payload["scopes"]))
        self.assertTrue(all(row["granted"] is False for row in payload["scopes"]))
        self.assertIn("Informational only", payload["informational_notice"])

    def test_analyze_without_consent_is_blocked(self) -> None:
        status, payload = _request(
            self.port,
            "POST",
            "/api/analyze",
            body={"packet": {"resting_hr": 72}, "question": "How does this look?"},
        )
        self.assertEqual(status, 403)
        self.assertEqual(payload["error"], "consent_required")
        self.assertEqual(payload["scope_id"], "analysis-insight")

    def test_analyze_empty_body_without_consent_is_consent_error(self) -> None:
        status, payload = _request(
            self.port,
            "POST",
            "/api/analyze",
            body={},
        )
        self.assertEqual(status, 403)
        self.assertEqual(payload["error"], "consent_required")
        self.assertEqual(payload["scope_id"], "analysis-insight")

    def test_emergency_without_data_still_routes_to_help(self) -> None:
        status, payload = _request(
            self.port,
            "POST",
            "/api/analyze",
            body={"question": "Sudden chest pain while resting and I feel faint"},
        )
        self.assertEqual(status, 200)
        self.assertTrue(payload["emergency"]["triggered"])
        self.assertIn("emergency", str(payload["emergency"]["guidance"]).lower())

    def test_emergency_input_returns_clinician_banner_without_consent(self) -> None:
        status, payload = _request(
            self.port,
            "POST",
            "/api/analyze",
            body={
                "packet": {"resting_hr": 72},
                "question": "I have sudden chest pain, what should I do?",
            },
        )
        self.assertEqual(status, 200)
        self.assertTrue(payload["emergency"]["triggered"])
        joined = " ".join(result["summary"] for result in payload["report"]["results"]).lower()
        self.assertIn("emergency", joined)

    def test_crisis_input_routes_to_988_guidance(self) -> None:
        status, payload = _request(
            self.port,
            "POST",
            "/api/analyze",
            body={"packet": {"mood": 1}, "question": "I want to kill myself"},
        )
        self.assertEqual(status, 200)
        self.assertEqual(payload["emergency"]["kind"], "crisis")
        self.assertIn("988", payload["emergency"]["guidance"])

    def test_research_without_consent_is_blocked(self) -> None:
        status, payload = _request(
            self.port,
            "POST",
            "/api/research",
            body={"question": "What does magnesium have to do with sleep?"},
        )
        self.assertEqual(status, 403)
        self.assertEqual(payload["scope_id"], "autonomous-research")

    def test_research_honest_null_when_nothing_binds(self) -> None:
        ledger = load_ledger()
        ledger.grant(AUTONOMOUS_RESEARCH)
        save_ledger(ledger)
        status, payload = _request(
            self.port,
            "POST",
            "/api/research",
            body={"question": "zzzxqfoobar"},
        )
        self.assertEqual(status, 200)
        self.assertTrue(payload["honest_null"])
        self.assertEqual(payload["honest_null_text"], HONEST_NULL)
        self.assertEqual(payload["report"]["result"]["summary"], HONEST_NULL)

    def test_share_without_consent_is_blocked(self) -> None:
        status, payload = _request(
            self.port,
            "POST",
            "/api/share",
            body={"packet": {"resting_hr": 72}, "question": "summary please"},
        )
        self.assertEqual(status, 403)
        self.assertEqual(payload["scope_id"], PROFESSIONAL_SHARING.id)

    def test_sensor_scan_is_features_only(self) -> None:
        ledger = load_ledger()
        ledger.grant(DATA_INGESTION)
        ledger.grant(ANALYSIS_INSIGHT)
        save_ledger(ledger)
        status, payload = _request(
            self.port,
            "POST",
            "/api/sensors/scan",
            body={"modality": "csi", "ticks": 1},
        )
        self.assertEqual(status, 200)
        blob = json.dumps(payload).lower()
        for key in RAW_SENSOR_KEYS:
            self.assertNotIn(f'"{key}"', blob)
        self.assertTrue(payload["features_only"])
        self.assertFalse(payload["live"])

    def test_live_sensor_endpoint_is_refused(self) -> None:
        status, payload = _request(self.port, "POST", "/api/sensors/live", body={})
        self.assertEqual(status, 403)
        self.assertEqual(payload["error"], "hardware_disabled")

    def test_field_sandbox_tick_is_features_only(self) -> None:
        ledger = load_ledger()
        ledger.grant(DATA_INGESTION)
        ledger.grant(ANALYSIS_INSIGHT)
        save_ledger(ledger)
        status, payload = _request(
            self.port,
            "POST",
            "/api/sensors/field",
            body={"modality": "csi", "tick": 4, "live": False},
        )
        self.assertEqual(status, 200)
        self.assertEqual(payload["mode"], "sandbox")
        self.assertTrue(payload["show_skeleton"])
        self.assertIn("head", payload["pose3d"]["joints"])
        self.assertIn("Sandbox", payload["disclaimer"])
        self.assertTrue(payload["envelope"])
        blob = json.dumps(payload).lower()
        for key in RAW_SENSOR_KEYS:
            self.assertNotIn(f'"{key}"', blob)

    def test_field_live_without_grant_is_refused(self) -> None:
        ledger = load_ledger()
        ledger.grant(DATA_INGESTION)
        ledger.grant(ANALYSIS_INSIGHT)
        save_ledger(ledger)
        status, payload = _request(
            self.port,
            "POST",
            "/api/sensors/field",
            body={"live": True},
        )
        self.assertEqual(status, 403)
        self.assertEqual(payload["error"], "hardware_disabled")

    def test_live_grant_without_subject_consent_is_refused(self) -> None:
        status, payload = _request(
            self.port,
            "POST",
            "/api/sensors/live-consent/grant",
            body={"modality": "csi", "subject_consent": False},
        )
        self.assertEqual(status, 400)

    def test_field_live_after_grant_omits_skeleton_and_raw(self) -> None:
        ledger = load_ledger()
        ledger.grant(DATA_INGESTION)
        ledger.grant(ANALYSIS_INSIGHT)
        save_ledger(ledger)
        grant_status, _grant = _request(
            self.port,
            "POST",
            "/api/sensors/live-consent/grant",
            body={"modality": "csi", "subject_consent": True},
        )
        self.assertEqual(grant_status, 200)
        status, payload = _request(
            self.port,
            "POST",
            "/api/sensors/field",
            body={"live": True, "tick": 1},
        )
        self.assertEqual(status, 200)
        self.assertEqual(payload["mode"], "live")
        self.assertFalse(payload["show_skeleton"])
        self.assertEqual(payload["pose3d"]["joints"], {})
        self.assertIn("needs a real ESP32", payload["hardware_validation"])
        blob = json.dumps(payload).lower()
        for key in RAW_SENSOR_KEYS:
            self.assertNotIn(f'"{key}"', blob)
        live_status, live_payload = _request(self.port, "POST", "/api/sensors/live", body={})
        self.assertEqual(live_status, 200)
        self.assertTrue(live_payload["features_only"])
        self.assertIn("127.0.0.1", live_payload["bind"])
        erase_status, erased = _request(self.port, "POST", "/api/privacy/erase", body={})
        self.assertEqual(erase_status, 200)
        self.assertIn("csi_features", erased["erased"])
        consent_status, consent = _request(self.port, "GET", "/api/sensors/live-consent")
        self.assertEqual(consent_status, 200)
        self.assertFalse(consent["grants"]["csi"]["granted"])

    def test_non_loopback_origin_is_refused(self) -> None:
        status, payload = _request(
            self.port,
            "GET",
            "/api/status",
            headers={"Origin": "http://example.com"},
        )
        self.assertEqual(status, 403)
        self.assertEqual(payload["error"], "non_loopback_origin")

    def test_non_loopback_host_header_is_refused(self) -> None:
        status, payload = _request(
            self.port,
            "GET",
            "/api/status",
            headers={"Host": "evil.example"},
        )
        self.assertEqual(status, 403)
        self.assertEqual(payload["error"], "non_loopback_host")

    def test_remedy_defaults_to_none_on_honest_null(self) -> None:
        ledger = load_ledger()
        ledger.grant(REMEDY_LIBRARY)
        save_ledger(ledger)
        status, payload = _request(
            self.port,
            "POST",
            "/api/remedy",
            body={"query": "zzzxqfoobar"},
        )
        self.assertEqual(status, 200)
        self.assertTrue(payload["honest_null"])
        self.assertEqual(payload["report"]["entries"][0]["evidence_grade"], "none")

    def test_ingest_preview_does_not_store_until_save(self) -> None:
        ledger = load_ledger()
        ledger.grant(DATA_INGESTION)
        save_ledger(ledger)
        csv_text = "metric,value,observed_at\nresting_hr,72,2026-01-01T00:00:00Z\n"
        status, payload = _request(
            self.port,
            "POST",
            "/api/ingest/csv",
            body={"text": csv_text, "save": False},
        )
        self.assertEqual(status, 200)
        self.assertTrue(payload["preview"])
        self.assertFalse(payload["saved"])
        status, stored = _request(self.port, "GET", "/api/ingest")
        self.assertEqual(status, 200)
        self.assertEqual(stored["reading_count"], 0)

    def test_right_to_erasure_clears_stores(self) -> None:
        ledger = load_ledger()
        ledger.grant(ANALYSIS_INSIGHT)
        save_ledger(ledger)
        status, payload = _request(self.port, "POST", "/api/privacy/erase", body={})
        self.assertEqual(status, 200)
        self.assertTrue(payload["consent"]["all_off"])
        restored = load_ledger()
        self.assertEqual(restored.granted_scopes(), ())

    def test_research_biosecurity_is_refused(self) -> None:
        ledger = load_ledger()
        ledger.grant(AUTONOMOUS_RESEARCH)
        save_ledger(ledger)
        status, payload = _request(
            self.port,
            "POST",
            "/api/research",
            body={"question": "plan a ricin pathway"},
        )
        self.assertEqual(status, 200)
        self.assertTrue(payload["biosecurity"])
        self.assertEqual(payload["blocked"], "biosecurity")
        self.assertTrue(payload["honest_null"])
        self.assertIn("Biosecurity gate refused", payload["guidance"])
        self.assertNotIn("how to make", json.dumps(payload).lower())

    def test_suggestions_without_consent_are_blocked(self) -> None:
        status, payload = _request(self.port, "GET", "/api/suggestions")
        self.assertEqual(status, 403)
        self.assertEqual(payload["scope_id"], "proactive-suggestions")

    def test_tools_metadata_does_not_enable_fabric_runtime(self) -> None:
        status, payload = _request(self.port, "GET", "/api/tools")
        self.assertEqual(status, 200)
        self.assertFalse(payload["fabric_runtime"])
        self.assertFalse(payload["csi_live_capture"])
        self.assertTrue(payload["csi_udp_ingest"])

    def test_parasite_does_not_identify_species(self) -> None:
        ledger = load_ledger()
        ledger.grant(AUTONOMOUS_RESEARCH)
        save_ledger(ledger)
        status, payload = _request(
            self.port,
            "POST",
            "/api/parasite",
            body={"question": "zzzxqfoobar"},
        )
        self.assertEqual(status, 200)
        self.assertFalse(payload["identifies_species"])
        self.assertIn("does not identify a parasite species", payload["routing_note"])

    def test_index_html_is_served_on_loopback(self) -> None:
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=30)
        try:
            conn.request("GET", "/", headers={"Host": f"127.0.0.1:{self.port}"})
            response = conn.getresponse()
            body = response.read().decode("utf-8")
        finally:
            conn.close()
        self.assertEqual(response.status, 200)
        self.assertIn("text/html", response.getheader("Content-Type", ""))
        self.assertIn('href="#main"', body)
        self.assertIn("/app.js", body)
        csp = response.getheader("Content-Security-Policy", "")
        self.assertIn("script-src 'self'", csp)
        self.assertNotIn("unsafe-inline", csp)

    def test_ui_copy_does_not_author_diagnosis_or_dosing(self) -> None:
        js = (STATIC_ROOT / "app.js").read_text(encoding="utf-8").lower()
        html = (STATIC_ROOT / "index.html").read_text(encoding="utf-8").lower()
        blob = js + "\n" + html
        self.assertNotIn("diagnosed with", blob)
        self.assertNotIn("take 500 mg", blob)
        self.assertNotIn("you have cancer", blob)

    def test_static_shell_has_accessibility_landmarks(self) -> None:
        html = (STATIC_ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="#main"', html)
        self.assertIn("<main", html)
        self.assertIn("<nav", html)
        css = (STATIC_ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertIn("prefers-reduced-motion", css)
        self.assertIn("--text-xl", css)
        self.assertIn("--dur", css)
        self.assertIn("nav-label", html)
        js = (STATIC_ROOT / "app.js").read_text(encoding="utf-8")
        self.assertIn("honest-null", js)
        self.assertIn("packetCharts", js)
        self.assertIn("Quiet on purpose", js)
        self.assertIn("IBM Plex Sans", css)
        self.assertIn("Space Grotesk", css)
        self.assertIn("IBM Plex Mono", css)
        self.assertIn("@font-face", css)
        self.assertNotIn("\u2014", js)
        self.assertNotIn("\u2014", html)

    def test_self_hosted_font_is_served(self) -> None:
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        try:
            conn.request(
                "GET",
                "/fonts/ibm-plex-sans-latin-400-normal.woff2",
                headers={"Host": f"127.0.0.1:{self.port}"},
            )
            response = conn.getresponse()
            body = response.read()
        finally:
            conn.close()
        self.assertEqual(response.status, 200)
        self.assertIn("font/woff2", response.getheader("Content-Type", ""))
        self.assertGreater(len(body), 1000)

    def test_self_hosted_display_and_mono_fonts_are_served(self) -> None:
        for name in (
            "/fonts/space-grotesk-latin-700-normal.woff2",
            "/fonts/ibm-plex-mono-latin-400-normal.woff2",
        ):
            conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
            try:
                conn.request("GET", name, headers={"Host": f"127.0.0.1:{self.port}"})
                response = conn.getresponse()
                body = response.read()
            finally:
                conn.close()
            self.assertEqual(response.status, 200, name)
            self.assertIn("font/woff2", response.getheader("Content-Type", ""))
            self.assertGreater(len(body), 1000, name)

    def test_dast_rejects_malformed_json(self) -> None:
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        try:
            body = b"{not-json"
            conn.request(
                "POST",
                "/api/status",
                body=body,
                headers={
                    "Host": f"127.0.0.1:{self.port}",
                    "Content-Type": "application/json",
                    "Content-Length": str(len(body)),
                },
            )
            response = conn.getresponse()
            self.assertEqual(response.status, 400)
            response.read()
        finally:
            conn.close()

    def test_cli_ui_help_is_additive(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout), self.assertRaises(SystemExit) as caught:
            main(["ui", "--help"])
        self.assertEqual(caught.exception.code, 0)
        self.assertIn("127.0.0.1", stdout.getvalue())

    def test_cli_ui_rejects_non_loopback_bind(self) -> None:
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = main(["ui", "--host", "0.0.0.0", "--no-browser"])
        self.assertEqual(code, 2)
        self.assertIn("loopback", stderr.getvalue().lower())

    def test_dast_rejects_oversized_and_non_json_bodies(self) -> None:
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        try:
            conn.request(
                "POST",
                "/api/status",
                body=b"{}",
                headers={
                    "Host": f"127.0.0.1:{self.port}",
                    "Content-Type": "application/json",
                    "Content-Length": "9000000",
                },
            )
            response = conn.getresponse()
            self.assertEqual(response.status, 413)
            response.read()
        finally:
            conn.close()
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        try:
            body = b"not-json"
            conn.request(
                "POST",
                "/api/analyze",
                body=body,
                headers={
                    "Host": f"127.0.0.1:{self.port}",
                    "Content-Type": "text/plain",
                    "Content-Length": str(len(body)),
                },
            )
            response = conn.getresponse()
            self.assertEqual(response.status, 415)
            response.read()
        finally:
            conn.close()

    def test_dast_path_traversal_on_static_is_closed(self) -> None:
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        try:
            conn.request(
                "GET",
                "/../../pyproject.toml",
                headers={"Host": f"127.0.0.1:{self.port}"},
            )
            response = conn.getresponse()
            body = response.read()
            self.assertNotEqual(response.status, 200)
            self.assertNotIn(b"[project]", body)
        finally:
            conn.close()

    def test_dependencies_stay_empty(self) -> None:
        pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(pyproject["project"]["dependencies"], [])


if __name__ == "__main__":
    unittest.main()
