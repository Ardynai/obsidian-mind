"""Host-side CSI line forwarder: stdin/serial/demo -> UDP 127.0.0.1.

The ESP32 cannot send to the PC's 127.0.0.1, and Somatic refuses to bind a LAN
address. Flash firmware that prints one JSON or CSV line per CSI frame on USB
serial, then run this on the same machine.

  python examples/hardware/csi_udp_forward.py --demo
  python examples/hardware/csi_udp_forward.py
  python examples/hardware/csi_udp_forward.py --serial COM5 --unit-id esp32-a

--demo emits synthetic packets. That is not a live ESP32 scan.
"""

from __future__ import annotations

import argparse
import json
import math
import socket
import sys
import time
from collections.abc import Iterator

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 53721


def _bind_host(host: str) -> str:
    if host.strip().lower() not in {"127.0.0.1", "localhost"}:
        raise SystemExit("forwarder destination must be 127.0.0.1 or localhost")
    return host


def send_line(sock: socket.socket, host: str, port: int, line: str) -> None:
    payload = line.strip()
    if not payload:
        return
    sock.sendto(payload.encode("utf-8")[:8192], (host, port))


def demo_lines(unit_id: str, count: int) -> Iterator[str]:
    for index in range(count):
        t = index / 10.0
        amp = [round(0.35 + 0.25 * math.sin(t + k * 0.4), 4) for k in range(16)]
        phase = [round(0.2 * math.sin(t * 0.7 + k * 0.2), 4) for k in range(16)]
        yield json.dumps(
            {
                "v": 1,
                "ts": time.time(),
                "unit_id": unit_id,
                "rssi": -50,
                "amp": amp,
                "phase": phase,
            }
        )
        time.sleep(0.1)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--unit-id", default="esp32-a")
    parser.add_argument("--demo", action="store_true", help="synthetic packets; not a real ESP32")
    parser.add_argument("--demo-count", type=int, default=80)
    parser.add_argument("--serial", default="", help="optional pyserial port (csi extra)")
    parser.add_argument("--baud", type=int, default=115200)
    args = parser.parse_args(argv)
    host = _bind_host(args.host)
    if args.port < 0 or args.port > 65535:
        raise SystemExit("port out of range")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        if args.demo:
            print(
                f"Sending synthetic CSI feature lines to {host}:{args.port} (not a real ESP32)",
                file=sys.stderr,
            )
            for line in demo_lines(args.unit_id, max(1, args.demo_count)):
                send_line(sock, host, args.port, line)
            return 0
        if args.serial:
            try:
                import serial
            except ImportError:
                raise SystemExit(
                    "serial forwarder needs pyserial (pip install 'somatic[csi]')"
                ) from None
            try:
                with serial.Serial(args.serial, args.baud, timeout=0.2) as port:
                    print(f"Reading {args.serial} -> {host}:{args.port}", file=sys.stderr)
                    while True:
                        raw = port.readline()
                        if not raw:
                            continue
                        try:
                            line = raw.decode("utf-8")
                        except UnicodeDecodeError:
                            continue
                        send_line(sock, host, args.port, line)
            except KeyboardInterrupt:
                return 0
            return 0
        print(f"Reading stdin -> {host}:{args.port}", file=sys.stderr)
        try:
            for line in sys.stdin:
                send_line(sock, host, args.port, line)
        except KeyboardInterrupt:
            return 0
        return 0
    finally:
        sock.close()


if __name__ == "__main__":
    raise SystemExit(main())
