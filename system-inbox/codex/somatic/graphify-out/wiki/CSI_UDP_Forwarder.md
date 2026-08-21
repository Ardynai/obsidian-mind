# CSI UDP Forwarder

> 7 nodes · cohesion 0.52

## Key Concepts

- **csi_udp_forward.py** (6 connections) — `examples/hardware/csi_udp_forward.py`
- **main()** (5 connections) — `examples/hardware/csi_udp_forward.py`
- **socket** (5 connections)
- **send_line()** (3 connections) — `examples/hardware/csi_udp_forward.py`
- **_bind_host()** (2 connections) — `examples/hardware/csi_udp_forward.py`
- **demo_lines()** (2 connections) — `examples/hardware/csi_udp_forward.py`
- **Host-side CSI line forwarder: stdin/serial/demo -> UDP 127.0.0.1.  The ESP32 c** (1 connections) — `examples/hardware/csi_udp_forward.py`

## Relationships

- [Network Safety and SSRF](Network_Safety_and_SSRF.md) (1 shared connections)
- [Live CSI Adapter](Live_CSI_Adapter.md) (1 shared connections)

## Source Files

- `examples/hardware/csi_udp_forward.py`

## Audit Trail

- EXTRACTED: 24 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*