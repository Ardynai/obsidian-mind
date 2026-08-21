# CSI Packet Feature Extraction

> 19 nodes · cohesion 0.18

## Key Concepts

- **live_features.py** (10 connections) — `somatic/sensors/live_features.py`
- **_normalize_packet()** (6 connections) — `somatic/sensors/live_csi.py`
- **_parse_csv_packet()** (6 connections) — `somatic/sensors/live_csi.py`
- **occupancy_from_iq()** (6 connections) — `somatic/sensors/live_features.py`
- **parse_csi_packet()** (5 connections) — `somatic/sensors/live_csi.py`
- **derive_features()** (5 connections) — `somatic/sensors/live_features.py`
- **occupancy_from_amp()** (5 connections) — `somatic/sensors/live_features.py`
- **_as_floats()** (4 connections) — `somatic/sensors/live_features.py`
- **breathing_rate_per_min()** (4 connections) — `somatic/sensors/live_features.py`
- **_parse_numeric_vector()** (3 connections) — `somatic/sensors/live_csi.py`
- **phase_row()** (3 connections) — `somatic/sensors/live_features.py`
- **_split_csv_line()** (2 connections) — `somatic/sensors/live_csi.py`
- **link_strength()** (2 connections) — `somatic/sensors/live_features.py`
- **motion_energy()** (2 connections) — `somatic/sensors/live_features.py`
- **peak_rate_per_min()** (2 connections) — `somatic/sensors/live_features.py`
- **Parse one UDP/serial line into an in-memory packet. Returns None if invalid.** (1 connections) — `somatic/sensors/live_csi.py`
- **Stdlib CSI feature derivation. Optional numpy/scipy stay extra-only.  Raw IQ /** (1 connections) — `somatic/sensors/live_features.py`
- **Convert interleaved IQ pairs to occupancy + wrapped phase rows. Drops IQ.** (1 connections) — `somatic/sensors/live_features.py`
- **Peak-count fallback. FFT band estimate if numpy is installed (optional extra).** (1 connections) — `somatic/sensors/live_features.py`

## Relationships

- [Live CSI Adapter](Live_CSI_Adapter.md) (7 shared connections)

## Source Files

- `somatic/sensors/live_csi.py`
- `somatic/sensors/live_features.py`

## Audit Trail

- EXTRACTED: 58 (84%)
- INFERRED: 11 (16%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*