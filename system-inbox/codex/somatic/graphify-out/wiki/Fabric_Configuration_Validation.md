# Fabric Configuration Validation

> 23 nodes · cohesion 0.18

## Key Concepts

- **FabricConfigError** (30 connections) — `somatic/fabric/federation.py`
- **FailClosedConfigTests** (19 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.from_env()** (17 connections) — `somatic/fabric/federation.py`
- **.test_client_constructor_validates()** (5 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.test_blank_env_produces_inert_config()** (4 connections) — `tests/test_fabric_federation_security_invariants.py`
- **_float_env()** (3 connections) — `somatic/fabric/federation.py`
- **_int_env()** (3 connections) — `somatic/fabric/federation.py`
- **.test_blank_env_sends_nothing()** (3 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.test_credentials_in_sidecar_url_raises()** (3 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.test_empty_sidecar_url_raises()** (3 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.test_https_sidecar_url_raises()** (3 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.test_missing_did_raises()** (3 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.test_missing_registry_token_raises()** (3 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.test_missing_registry_url_raises()** (3 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.test_missing_sidecar_token_raises()** (3 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.test_missing_sidecar_url_raises()** (3 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.test_non_loopback_sidecar_url_raises()** (3 connections) — `tests/test_fabric_federation_security_invariants.py`
- **_split_csv()** (2 connections) — `somatic/fabric/federation.py`
- **Raised when required local configuration is absent or unsafe.** (1 connections) — `somatic/fabric/federation.py`
- **Missing sidecar URL / token / DID / allowlist => connector inert.** (1 connections) — `tests/test_fabric_federation_security_invariants.py`
- **I6 — an empty env dict must produce a config that fails validation.** (1 connections) — `tests/test_fabric_federation_security_invariants.py`
- **I6 — FabricFederationClient constructor calls validate() and fails closed.** (1 connections) — `tests/test_fabric_federation_security_invariants.py`
- **I6 — from_env({}) cannot produce a client that transmits anything.** (1 connections) — `tests/test_fabric_federation_security_invariants.py`

## Relationships

- [Fabric Communication Errors](Fabric_Communication_Errors.md) (10 shared connections)
- [Fabric Federation Configuration](Fabric_Federation_Configuration.md) (6 shared connections)
- [Fabric Registry Client](Fabric_Registry_Client.md) (4 shared connections)
- [Fabric Federation Client](Fabric_Federation_Client.md) (2 shared connections)
- [Log Secret Prevention](Log_Secret_Prevention.md) (1 shared connections)
- [Runtime Boundary Enforcement](Runtime_Boundary_Enforcement.md) (1 shared connections)
- [Network Isolation Checks](Network_Isolation_Checks.md) (1 shared connections)
- [Fabric Environment Integration](Fabric_Environment_Integration.md) (1 shared connections)

## Source Files

- `somatic/fabric/federation.py`
- `tests/test_fabric_federation_security_invariants.py`

## Audit Trail

- EXTRACTED: 83 (70%)
- INFERRED: 35 (30%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*