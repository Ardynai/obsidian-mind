"""Loopback UDP (stdlib) CSI ingest. Optional pyserial behind extras.

Binds 127.0.0.1 only. Packets are parsed in memory, features derived, raw IQ
dropped. Nothing is forwarded off-box. Hardware validation is never claimed
from this software path.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import socket
import threading
import time
from typing import Any

from somatic.consent.ledger import ConsentLedger
from somatic.consent.scopes import ANALYSIS_INSIGHT, DATA_INGESTION
from somatic.evidence_bus.adapter import EvidenceCost, HypothesisSpec
from somatic.evidence_bus.records import EvidenceSource, MeasurementPlan, RawEvidence
from somatic.evidence_bus.sandbox_adapters import SensorHardwareDisabled
from somatic.safety.core import require_consent
from somatic.sensors.live_features import (
    ENVELOPE_HISTORY,
    derive_features,
    occupancy_from_amp,
    occupancy_from_iq,
    phase_row,
)
from somatic.sensors.live_store import append_csi_features, load_csi_features

DEFAULT_UDP_PORT = 53721
DEFAULT_BIND_HOST = "127.0.0.1"
MAX_PACKET_BYTES = 8192
CSI_UDP_PORT_ENV = "SOMATIC_CSI_UDP_PORT"
CSI_UDP_HOST_ENV = "SOMATIC_CSI_UDP_HOST"
_LOOPBACK_NAMES = frozenset({"127.0.0.1", "localhost"})


def is_loopback_bind(host: str) -> bool:
    return str(host or "").strip().lower() in _LOOPBACK_NAMES


class LoopbackBindError(ValueError):
    """Raised when a caller asks the CSI ingest to bind off loopback."""


def default_udp_port() -> int:
    raw = os.environ.get(CSI_UDP_PORT_ENV, "").strip()
    if not raw:
        return DEFAULT_UDP_PORT
    try:
        port = int(raw)
    except ValueError as exc:
        raise LoopbackBindError("SOMATIC_CSI_UDP_PORT must be an integer") from exc
    if port < 0 or port > 65535:
        raise LoopbackBindError("SOMATIC_CSI_UDP_PORT out of range")
    return port


def default_bind_host() -> str:
    host = os.environ.get(CSI_UDP_HOST_ENV, "").strip() or DEFAULT_BIND_HOST
    if not is_loopback_bind(host):
        raise LoopbackBindError("CSI UDP ingest binds 127.0.0.1 or localhost only")
    return host


def _split_csv_line(line: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    in_quotes = False
    for char in line:
        if char == '"':
            in_quotes = not in_quotes
            continue
        if char == "," and not in_quotes:
            parts.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    parts.append("".join(current).strip())
    return parts


def _parse_numeric_vector(value: object) -> list[float]:
    if isinstance(value, (list, tuple)):
        numbers: list[float] = []
        for item in value:
            try:
                number = float(item)
            except (TypeError, ValueError):
                continue
            if math.isfinite(number):
                numbers.append(number)
        return numbers
    text = str(value or "").strip().strip("[]")
    if not text:
        return []
    chunks = text.replace(",", " ").split()
    numbers = []
    for chunk in chunks:
        try:
            number = float(chunk)
        except ValueError:
            continue
        if math.isfinite(number):
            numbers.append(number)
    return numbers


def parse_csi_packet(line: str | bytes) -> dict[str, Any] | None:
    """Parse one UDP/serial line into an in-memory packet. Returns None if invalid."""

    if isinstance(line, bytes):
        try:
            text = line.decode("utf-8")
        except UnicodeDecodeError:
            return None
    else:
        text = line
    text = text.strip()
    if not text:
        return None
    if text.startswith("{"):
        try:
            payload = json.loads(text)
        except ValueError:
            return None
        if not isinstance(payload, dict):
            return None
        return _normalize_packet(payload)
    return _parse_csv_packet(text)


def _normalize_packet(payload: dict[str, Any]) -> dict[str, Any] | None:
    amp = payload.get("amp") or payload.get("occupancy") or payload.get("subcarriers")
    phase = payload.get("ph") or payload.get("phases")
    iq = payload.get("iq") or payload.get("csi") or payload.get("csi_data")
    occupancy: list[float] = []
    phase_values: list[float] = []
    if amp is not None:
        occupancy = occupancy_from_amp(_parse_numeric_vector(amp))
        if phase is not None:
            phase_values = phase_row(_parse_numeric_vector(phase))
    elif iq is not None:
        occupancy, phase_values = occupancy_from_iq(_parse_numeric_vector(iq))
    else:
        return None
    if not occupancy:
        return None
    ts = payload.get("ts") or payload.get("timestamp")
    try:
        timestamp = float(ts) if ts is not None else time.time()
    except (TypeError, ValueError):
        timestamp = time.time()
    rssi = payload.get("rssi")
    return {
        "timestamp": timestamp,
        "unit_id": str(payload.get("unit_id") or payload.get("unit") or "esp32"),
        "rssi": rssi,
        "occupancy": occupancy,
        "phase": phase_values,
    }


def _parse_csv_packet(text: str) -> dict[str, Any] | None:
    parts = _split_csv_line(text)
    if not parts:
        return None
    head = parts[0].upper()
    if head in {"CSI_DATA", "CSI"}:
        # ESP32-CSI-Tool-ish: type, frame_id, timestamp, source, rssi, csi_data, ...
        if len(parts) < 6:
            return None
        occupancy, phase_values = occupancy_from_iq(_parse_numeric_vector(parts[5]))
        if not occupancy:
            return None
        try:
            timestamp = float(parts[2])
        except ValueError:
            timestamp = time.time()
        try:
            rssi = float(parts[4])
        except ValueError:
            rssi = None
        return {
            "timestamp": timestamp,
            "unit_id": parts[3] or "esp32",
            "rssi": rssi,
            "occupancy": occupancy,
            "phase": phase_values,
        }
    # JSON-schema CSV: ts,unit_id,rssi,amp0,amp1,...
    if len(parts) < 4:
        return None
    try:
        timestamp = float(parts[0])
    except ValueError:
        return None
    unit_id = parts[1] or "esp32"
    try:
        rssi = float(parts[2])
    except ValueError:
        rssi = None
    occupancy = occupancy_from_amp(_parse_numeric_vector(parts[3:]))
    if not occupancy:
        return None
    return {
        "timestamp": timestamp,
        "unit_id": unit_id,
        "rssi": rssi,
        "occupancy": occupancy,
        "phase": [],
    }


class LiveCsiIngest:
    """Loopback UDP listener that stores derived features only."""

    def __init__(
        self,
        *,
        host: str = DEFAULT_BIND_HOST,
        port: int | None = None,
        persist: bool = True,
    ) -> None:
        if not is_loopback_bind(host):
            raise LoopbackBindError("CSI UDP ingest binds 127.0.0.1 or localhost only")
        self.host = host
        self.port = int(port) if port is not None else default_udp_port()
        self.persist = persist
        self._sock: socket.socket | None = None
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._latest: dict[str, Any] | None = None
        self._previous_occupancy: list[float] | None = None
        self._envelope: list[float] = []
        self._bound_port = self.port
        self.packets_accepted = 0
        self.packets_dropped = 0

    @property
    def bound_port(self) -> int:
        return self._bound_port

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> LiveCsiIngest:
        if self.running:
            return self
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((self.host, self.port))
        except OSError:
            sock.close()
            raise
        sock.settimeout(0.2)
        self._sock = sock
        self._bound_port = int(sock.getsockname()[1])
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="somatic-csi-udp", daemon=True)
        self._thread.start()
        return self

    def stop(self) -> None:
        self._stop.set()
        sock = self._sock
        if sock is not None:
            try:
                sock.close()
            except OSError:
                pass
        thread = self._thread
        if thread is not None:
            thread.join(timeout=2)
        self._sock = None
        self._thread = None

    def ingest_line(self, line: str | bytes) -> dict[str, Any] | None:
        """Parse one packet without the socket (tests + serial drain)."""

        packet = parse_csi_packet(line)
        if packet is None:
            self.packets_dropped += 1
            return None
        return self._accept(packet)

    def send_loopback(self, line: str | bytes) -> None:
        payload = line if isinstance(line, bytes) else line.encode("utf-8")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(payload[:MAX_PACKET_BYTES], (self.host, self._bound_port))

    def latest(self) -> dict[str, Any] | None:
        with self._lock:
            return dict(self._latest) if self._latest else None

    def _loop(self) -> None:
        while not self._stop.is_set():
            sock = self._sock
            if sock is None:
                break
            try:
                data, addr = sock.recvfrom(MAX_PACKET_BYTES + 1)
            except TimeoutError:
                continue
            except OSError:
                break
            self._handle_datagram(data, addr)

    def _handle_datagram(self, data: bytes, addr: tuple[object, ...]) -> None:
        if not addr or not is_loopback_bind(str(addr[0])):
            self.packets_dropped += 1
            return
        if len(data) > MAX_PACKET_BYTES:
            self.packets_dropped += 1
            return
        self.ingest_line(data)

    def _accept(self, packet: dict[str, Any]) -> dict[str, Any]:
        occupancy = list(packet["occupancy"])
        phase = list(packet.get("phase") or [])
        with self._lock:
            features = derive_features(
                occupancy=occupancy,
                phase=phase,
                envelope_history=self._envelope,
                previous_occupancy=self._previous_occupancy,
                rssi=packet.get("rssi"),
                unit_id=str(packet.get("unit_id") or ""),
                timestamp=packet.get("timestamp"),
            )
            envelope = features.get("envelope")
            if isinstance(envelope, list):
                self._envelope = list(envelope)[-ENVELOPE_HISTORY:]
            else:
                self._envelope = []
            self._previous_occupancy = occupancy
            persist_now = self.persist
        if persist_now:
            append_csi_features(features)
        with self._lock:
            self._latest = features
            self.packets_accepted += 1
        return features


class LiveCsiAdapter:
    """Evidence Bus adapter for loopback CSI features. Consent-gated; no pose."""

    tier = 1
    hardware_access = False

    def __init__(self, ingest: LiveCsiIngest | None = None) -> None:
        self.modality = "csi"
        self.adapter_id = "live-csi-udp"
        self._ingest = ingest

    def plan(self, hypothesis: HypothesisSpec, ledger: ConsentLedger) -> MeasurementPlan:
        require_consent(ledger, ANALYSIS_INSIGHT)
        source = EvidenceSource(
            id="src-csi-live-udp",
            modality="csi",
            provider_ref=self.adapter_id,
            description="Loopback UDP CSI ingest; derived features only.",
            metadata={
                "simulated": False,
                "tier": 1,
                "hardware_access": False,
                "network_calls": False,
                "raw_export": False,
                "local_first": True,
                "bind": "127.0.0.1",
            },
        )
        return MeasurementPlan(
            id=f"plan-csi-live-{hypothesis.id}",
            sources=[source],
            objective=hypothesis.statement,
            safety_profile="research-only",
            metadata={
                "simulated": False,
                "hypothesis_id": hypothesis.id,
                "domain": hypothesis.domain,
                "live_hardware": True,
                "transport": "udp-loopback",
            },
        )

    def acquire(self, plan: MeasurementPlan, ledger: ConsentLedger) -> tuple[RawEvidence, ...]:
        require_consent(ledger, ANALYSIS_INSIGHT)
        ingest = self._ingest or get_ingest()
        features = ingest.latest()
        if features is None:
            stored = load_csi_features()
            features = (
                dict(stored[-1])
                if stored
                else {
                    "record_type": "live-csi-features",
                    "simulated": False,
                    "waiting_for_packets": True,
                    "envelope": [],
                    "occupancy_row": [],
                    "amp_heatmap": [],
                    "phase_heatmap": [],
                    "breathing_rate_per_min": 0.0,
                    "motion_energy": 0.0,
                    "presence": False,
                    "pose3d_omitted": True,
                    "hardware_validation": "sandbox-verified; needs a real ESP32 to validate live",
                    "not_a_clinical_normal": True,
                }
            )
        digest = hashlib.sha256(
            json.dumps(features, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
        ).hexdigest()
        raw = RawEvidence(
            id=f"raw-csi-live-{digest[:12]}",
            source=plan.sources[0],
            payload_ref=f"live-csi://udp/{digest[:12]}",
            sha256=digest,
            metadata={
                "simulated": False,
                "offline": True,
                "hardware_access": False,
                "raw_frames_exported": False,
                "raw_audio_exported": False,
                "raw_csi_iq_exported": False,
                "features": features,
                "limitations": [
                    "Derived CSI features only.",
                    "Raw IQ was not stored or exported.",
                    "Needs a real ESP32 to validate live capture.",
                ],
            },
        )
        return (raw,)

    def cost(self, plan: MeasurementPlan) -> EvidenceCost:
        del plan
        return EvidenceCost(
            compute_units=1.2,
            privacy_risk="local-loopback",
            dollars=0.0,
            hardware_required=False,
        )

    def confidence(self, raw: RawEvidence) -> float:
        features = raw.metadata.get("features")
        if not isinstance(features, dict):
            return 0.2
        value = features.get("confidence")
        try:
            return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return 0.3


_INGEST: LiveCsiIngest | None = None
_INGEST_LOCK = threading.Lock()


def get_ingest() -> LiveCsiIngest:
    global _INGEST
    with _INGEST_LOCK:
        if _INGEST is None:
            _INGEST = LiveCsiIngest(host=default_bind_host(), port=default_udp_port())
        return _INGEST


def start_ingest(*, persist: bool = True) -> LiveCsiIngest:
    ingest = get_ingest()
    ingest.persist = persist
    return ingest.start()


def stop_ingest() -> None:
    replace_ingest(None)


def replace_ingest(ingest: LiveCsiIngest | None) -> None:
    """Test helper: swap the process-wide ingest. Stops the previous one."""

    global _INGEST
    with _INGEST_LOCK:
        if _INGEST is not None and _INGEST is not ingest:
            _INGEST.stop()
        _INGEST = ingest


def open_serial_transport(port: str, *, baudrate: int = 115200) -> Any:
    """Lazy pyserial opener. Extra-only; never imported by default."""

    try:
        import serial
    except ImportError as exc:
        raise SensorHardwareDisabled(
            "serial CSI ingest needs the csi/sensors extra (pyserial)"
        ) from exc
    return serial.Serial(port=port, baudrate=baudrate, timeout=0.2)


def drain_serial_lines(
    ingest: LiveCsiIngest,
    serial_port: Any,
    *,
    max_lines: int = 32,
) -> int:
    """Read up to ``max_lines`` from an already-opened serial port."""

    accepted = 0
    for _ in range(max_lines):
        raw = serial_port.readline()
        if not raw:
            break
        if ingest.ingest_line(raw) is not None:
            accepted += 1
    return accepted


def require_live_csi(ledger: ConsentLedger) -> None:
    """DATA_INGESTION + ANALYSIS_INSIGHT + explicit live-csi grant with subject consent."""

    from somatic.sensors.live_consent import load_live_consent

    require_consent(ledger, DATA_INGESTION)
    require_consent(ledger, ANALYSIS_INSIGHT)
    live = load_live_consent()
    if not live.is_granted("csi") or not live.subject_consent("csi"):
        raise SensorHardwareDisabled(
            "live CSI ingest is off by default; grant live-sensor CSI with subject consent first"
        )
