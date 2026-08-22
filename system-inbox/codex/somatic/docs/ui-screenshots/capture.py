"""Refresh docs/ui-screenshots/*.png from the local loopback UI.

Requires Google Chrome or Microsoft Edge. Isolates stores so ~/.somatic is untouched.
Captures every surface in light and dark.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from somatic.bridge.server import start_background_server  # noqa: E402

OUT = Path(__file__).resolve().parent

PATHS = [
    ("01-status.png", "/"),
    ("02-consent.png", "/consent"),
    ("03-analyze-blocked.png", "/analyze"),
    ("04-privacy.png", "/privacy"),
    ("05-sensors.png", "/sensors"),
    ("06-share-blocked.png", "/share"),
    ("07-ingest-blocked.png", "/ingest"),
    ("08-experiments-blocked.png", "/experiments"),
    ("09-research-blocked.png", "/research"),
    ("10-remedy-blocked.png", "/remedy"),
    ("11-parasite-blocked.png", "/parasite"),
    ("12-science-blocked.png", "/science"),
    ("13-presence-blocked.png", "/presence"),
    ("14-bench-blocked.png", "/bench"),
    ("15-suggestions-blocked.png", "/suggestions"),
    ("16-tools.png", "/tools"),
    ("17-replay.png", "/replay"),
    ("18-field-blocked.png", "/field"),
]


def _browser() -> str:
    candidates = [
        Path(os.environ.get("PROGRAMFILES", r"C:\Program Files"))
        / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("PROGRAMFILES", r"C:\Program Files"))
        / "Microsoft/Edge/Application/msedge.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Google/Chrome/Application/chrome.exe",
    ]
    for path in candidates:
        if path.is_file():
            return str(path)
    raise SystemExit("Chrome or Edge not found")


def _shot(browser: str, dest: Path, url: str, scheme: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        browser,
        "--headless=new",
        "--hide-scrollbars",
        "--window-size=1600,1100",
        "--use-gl=angle",
        "--use-angle=swiftshader-webgl",
        "--enable-unsafe-swiftshader",
        "--enable-webgl",
        "--ignore-gpu-blocklist",
        f"--blink-settings=preferredColorScheme={scheme}",
        "--virtual-time-budget=12000",
        f"--screenshot={dest}",
        url,
    ]
    subprocess.run(cmd, check=True)
    if not dest.is_file() or dest.stat().st_size < 1000:
        raise SystemExit(f"screenshot missing or tiny: {dest}")
    print(dest.relative_to(OUT), dest.stat().st_size)


def main() -> int:
    browser = _browser()
    tmp = tempfile.TemporaryDirectory()
    os.environ["SOMATIC_CONSENT_PATH"] = str(Path(tmp.name) / "consent.json")
    os.environ["SOMATIC_INGEST_PATH"] = str(Path(tmp.name) / "readings.json")
    os.environ["SOMATIC_EXPERIMENT_PATH"] = str(Path(tmp.name) / "experiments.json")
    os.environ["SOMATIC_SENSOR_LIVE_PATH"] = str(Path(tmp.name) / "sensor-live.json")
    os.environ["SOMATIC_CSI_FEATURES_PATH"] = str(Path(tmp.name) / "csi-features.json")
    httpd, _thread, port = start_background_server(port=0)
    try:
        for name, path in PATHS:
            light = OUT / name
            dark = OUT / "dark" / name
            _shot(browser, light, f"http://127.0.0.1:{port}{path}?theme=light", "light")
            time.sleep(0.15)
            _shot(browser, dark, f"http://127.0.0.1:{port}{path}?theme=dark", "dark")
            time.sleep(0.15)
        from somatic.consent import (
            AI_ADVISORY,
            ANALYSIS_INSIGHT,
            DATA_INGESTION,
            load_ledger,
            save_ledger,
        )

        ledger = load_ledger()
        ledger.grant(DATA_INGESTION)
        ledger.grant(ANALYSIS_INSIGHT)
        save_ledger(ledger)
        _shot(
            browser,
            OUT / "19-field.png",
            f"http://127.0.0.1:{port}/field?theme=light&preview=1",
            "light",
        )
        _shot(
            browser,
            OUT / "dark" / "19-field.png",
            f"http://127.0.0.1:{port}/field?theme=dark&preview=1",
            "dark",
        )
        ledger.grant(AI_ADVISORY)
        save_ledger(ledger)
        _shot(
            browser,
            OUT / "20-presence.png",
            f"http://127.0.0.1:{port}/presence?theme=light",
            "light",
        )
        _shot(
            browser,
            OUT / "dark" / "20-presence.png",
            f"http://127.0.0.1:{port}/presence?theme=dark",
            "dark",
        )
        _shot(
            browser,
            OUT / "21-palette.png",
            f"http://127.0.0.1:{port}/?theme=light&palette=1",
            "light",
        )
        _shot(
            browser,
            OUT / "dark" / "21-palette.png",
            f"http://127.0.0.1:{port}/?theme=dark&palette=1",
            "dark",
        )
    finally:
        httpd.shutdown()
        tmp.cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
