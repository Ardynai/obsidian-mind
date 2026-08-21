# Runtime Boundary Enforcement

> 6 nodes · cohesion 0.33

## Key Concepts

- **PreRuntimeBoundaryTests** (9 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.test_doctor_reports_fabric_out_of_process()** (2 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.test_doctor_reports_runtime_blocked()** (2 connections) — `tests/test_fabric_federation_security_invariants.py`
- **I8 — somatic doctor must keep real-mode runtime blocked.** (1 connections) — `tests/test_fabric_federation_security_invariants.py`
- **I8 — doctor output mentions the out-of-process sidecar connector.** (1 connections) — `tests/test_fabric_federation_security_invariants.py`
- **I8 — doctor output confirms real-mode runtime is blocked/disabled.** (1 connections) — `tests/test_fabric_federation_security_invariants.py`

## Relationships

- [Fabric Federation Configuration](Fabric_Federation_Configuration.md) (2 shared connections)
- [Fabric Configuration Validation](Fabric_Configuration_Validation.md) (1 shared connections)
- [Fabric Registry Client](Fabric_Registry_Client.md) (1 shared connections)
- [Fabric Communication Errors](Fabric_Communication_Errors.md) (1 shared connections)
- [Fabric Federation Client](Fabric_Federation_Client.md) (1 shared connections)

## Source Files

- `tests/test_fabric_federation_security_invariants.py`

## Audit Trail

- EXTRACTED: 11 (69%)
- INFERRED: 5 (31%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*