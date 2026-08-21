# Fabric Federation Configuration

> 44 nodes · cohesion 0.08

## Key Concepts

- **FabricFederationConfig** (20 connections) — `somatic/fabric/federation.py`
- **test_fabric_federation_security_invariants.py** (17 connections) — `tests/test_fabric_federation_security_invariants.py`
- **AllowlistRejectBothWaysTests** (12 connections) — `tests/test_fabric_federation_security_invariants.py`
- **CiphertextPreservedTests** (12 connections) — `tests/test_fabric_federation_security_invariants.py`
- **IntegrityReverifyTests** (12 connections) — `tests/test_fabric_federation_security_invariants.py`
- **._config()** (11 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.test_mismatched_inbound_descriptor_contentId_is_rejected()** (7 connections) — `tests/test_fabric_federation_security_invariants.py`
- **_store_sidecar_payload()** (7 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.test_receive_from_non_allowlisted_did_is_rejected()** (6 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.test_tampered_payload_byte_is_rejected()** (6 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.setUp()** (5 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.test_send_to_non_allowlisted_did_is_rejected()** (5 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.test_send_to_self_is_rejected_when_not_in_allowlist()** (5 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.setUp()** (5 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.test_secure_receive_returns_ciphertext_unchanged()** (5 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.setUp()** (5 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.test_empty_payload_descriptor_is_accepted()** (5 connections) — `tests/test_fabric_federation_security_invariants.py`
- **_start_server()** (5 connections) — `tests/test_fabric_federation_security_invariants.py`
- **.test_secure_send_preserves_ciphertext_in_sidecar()** (4 connections) — `tests/test_fabric_federation_security_invariants.py`
- **_make_registry_handler()** (4 connections) — `tests/test_fabric_federation_security_invariants.py`
- **_make_sidecar_handler()** (4 connections) — `tests/test_fabric_federation_security_invariants.py`
- **_server_url()** (4 connections) — `tests/test_fabric_federation_security_invariants.py`
- **_stop_server()** (4 connections) — `tests/test_fabric_federation_security_invariants.py`
- **ThreadingHTTPServer** (4 connections)
- **._config()** (3 connections) — `tests/test_fabric_federation_security_invariants.py`
- *... and 19 more nodes in this community*

## Relationships

- [Fabric Federation Client](Fabric_Federation_Client.md) (14 shared connections)
- [Fabric Registry Client](Fabric_Registry_Client.md) (10 shared connections)
- [Fabric Communication Errors](Fabric_Communication_Errors.md) (7 shared connections)
- [Fabric Configuration Validation](Fabric_Configuration_Validation.md) (6 shared connections)
- [Log Secret Prevention](Log_Secret_Prevention.md) (3 shared connections)
- [Runtime Boundary Enforcement](Runtime_Boundary_Enforcement.md) (2 shared connections)
- [Network Isolation Checks](Network_Isolation_Checks.md) (2 shared connections)
- [Local UI HTTP Server](Local_UI_HTTP_Server.md) (1 shared connections)
- [Advisory Model Client](Advisory_Model_Client.md) (1 shared connections)

## Source Files

- `somatic/fabric/federation.py`
- `tests/test_fabric_federation_security_invariants.py`

## Audit Trail

- EXTRACTED: 147 (73%)
- INFERRED: 55 (27%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*