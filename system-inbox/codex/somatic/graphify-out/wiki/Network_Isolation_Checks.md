# Network Isolation Checks

> 7 nodes · cohesion 0.29

## Key Concepts

- **StdlibAndOutOfProcessTests** (10 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.test_no_dht_swarm_or_chunking_reimplementation()** (2 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.test_no_socket_or_subprocess_import_in_federation()** (2 connections) — `tests/test_fabric_federation_security_invariants.py`
- **Additional I1/I2 checks that complement the existing connect test.** (1 connections) — `tests/test_fabric_federation_security_invariants.py`
- **I2 — no raw socket, subprocess, or third-party network imports.** (1 connections) — `tests/test_fabric_federation_security_invariants.py`
- **I2 — no DHT, swarm, bittorrent, or content-chunking implementation.** (1 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.test_pyproject_dependencies_stay_empty()** (1 connections) — `tests/test_fabric_federation_security_invariants.py`

## Relationships

- [Fabric Federation Configuration](Fabric_Federation_Configuration.md) (2 shared connections)
- [Fabric Configuration Validation](Fabric_Configuration_Validation.md) (1 shared connections)
- [Fabric Registry Client](Fabric_Registry_Client.md) (1 shared connections)
- [Fabric Communication Errors](Fabric_Communication_Errors.md) (1 shared connections)
- [Fabric Federation Client](Fabric_Federation_Client.md) (1 shared connections)

## Source Files

- `tests/test_fabric_federation_security_invariants.py`

## Audit Trail

- EXTRACTED: 13 (72%)
- INFERRED: 5 (28%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*