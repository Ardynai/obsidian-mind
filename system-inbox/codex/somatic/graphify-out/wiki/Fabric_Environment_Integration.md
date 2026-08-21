# Fabric Environment Integration

> 10 nodes · cohesion 0.31

## Key Concepts

- **_fabric()** (12 connections) — `somatic/cli/main.py`
- **.from_env()** (5 connections) — `somatic/fabric/federation.py`
- **_fabric_canonicalize()** (5 connections) — `somatic/cli/main.py`
- **_fabric_check_catalog()** (5 connections) — `somatic/cli/main.py`
- **_write_stdout_utf8_line()** (5 connections) — `somatic/cli/main.py`
- **_fabric_check_keyring_rotation()** (4 connections) — `somatic/cli/main.py`
- **_fabric_check_shared_fixtures()** (4 connections) — `somatic/cli/main.py`
- **_fabric_receive_once()** (4 connections) — `somatic/cli/main.py`
- **_fabric_register()** (4 connections) — `somatic/cli/main.py`
- **_fabric_send()** (4 connections) — `somatic/cli/main.py`

## Relationships

- [Benchmarking and Scoring](Benchmarking_and_Scoring.md) (10 shared connections)
- [Fabric Canonical JSON](Fabric_Canonical_JSON.md) (8 shared connections)
- [Keyring Signature Verification](Keyring_Signature_Verification.md) (3 shared connections)
- [Fabric Configuration Validation](Fabric_Configuration_Validation.md) (1 shared connections)
- [Fabric Federation Client](Fabric_Federation_Client.md) (1 shared connections)
- [Catalog Manifest Validation](Catalog_Manifest_Validation.md) (1 shared connections)

## Source Files

- `somatic/cli/main.py`
- `somatic/fabric/federation.py`

## Audit Trail

- EXTRACTED: 52 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*