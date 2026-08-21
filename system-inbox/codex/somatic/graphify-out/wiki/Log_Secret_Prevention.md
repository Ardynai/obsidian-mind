# Log Secret Prevention

> 8 nodes · cohesion 0.25

## Key Concepts

- **NoSecretsInLogsTests** (10 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.test_token_not_in_exception_messages()** (4 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.test_no_print_or_logging_calls_in_federation_module()** (2 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.test_token_not_in_exception_or_raise_fstrings()** (2 connections) — `tests/test_fabric_federation_security_invariants.py`
- **Tokens, DID keys, and bearer values must never be printed or logged.** (1 connections) — `tests/test_fabric_federation_security_invariants.py`
- **I7 — federation.py must not contain print() or logging calls.** (1 connections) — `tests/test_fabric_federation_security_invariants.py`
- **I7 — exception messages must not contain the raw token value.** (1 connections) — `tests/test_fabric_federation_security_invariants.py`
- **I7 — f-strings used in raise/exception messages must not embed tokens.** (1 connections) — `tests/test_fabric_federation_security_invariants.py`

## Relationships

- [Fabric Federation Configuration](Fabric_Federation_Configuration.md) (3 shared connections)
- [Fabric Federation Client](Fabric_Federation_Client.md) (2 shared connections)
- [Fabric Configuration Validation](Fabric_Configuration_Validation.md) (1 shared connections)
- [Fabric Registry Client](Fabric_Registry_Client.md) (1 shared connections)
- [Fabric Communication Errors](Fabric_Communication_Errors.md) (1 shared connections)

## Source Files

- `tests/test_fabric_federation_security_invariants.py`

## Audit Trail

- EXTRACTED: 15 (68%)
- INFERRED: 7 (32%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*