# Fabric Federation Client

> 23 nodes · cohesion 0.17

## Key Concepts

- **FabricFederationClient** (33 connections) — `somatic/fabric/federation.py`
- **FabricFederationConnectTests** (14 connections) — `tests/test_fabric_federation_connect.py`
- **test_fabric_federation_connect.py** (10 connections) — `tests/test_fabric_federation_connect.py`
- **.config()** (9 connections) — `tests/test_fabric_federation_connect.py`
- **.setUp()** (5 connections) — `tests/test_fabric_federation_connect.py`
- **.test_content_id_reverify_catches_tampered_byte()** (5 connections) — `tests/test_fabric_federation_connect.py`
- **.test_receive_rejects_non_allowlisted_sibling_did()** (5 connections) — `tests/test_fabric_federation_connect.py`
- **_store_sidecar_payload()** (5 connections) — `tests/test_fabric_federation_connect.py`
- **.test_receive_from_allowlisted_sibling_reverifies_content()** (4 connections) — `tests/test_fabric_federation_connect.py`
- **_descriptor_for_payload()** (3 connections) — `tests/test_fabric_federation_connect.py`
- **.test_encrypted_transfers_stay_ciphertext()** (3 connections) — `tests/test_fabric_federation_connect.py`
- **.test_register_authenticates_via_registry()** (3 connections) — `tests/test_fabric_federation_connect.py`
- **.test_send_reaches_allowlisted_sibling()** (3 connections) — `tests/test_fabric_federation_connect.py`
- **_start_server()** (3 connections) — `tests/test_fabric_federation_connect.py`
- **_make_registry_handler()** (2 connections) — `tests/test_fabric_federation_connect.py`
- **_make_sidecar_handler()** (2 connections) — `tests/test_fabric_federation_connect.py`
- **_merkle_root()** (2 connections) — `tests/test_fabric_federation_connect.py`
- **_server_url()** (2 connections) — `tests/test_fabric_federation_connect.py`
- **_stop_server()** (2 connections) — `tests/test_fabric_federation_connect.py`
- **.keepalive()** (1 connections) — `somatic/fabric/federation.py`
- **High-level send and receive facade for Somatic fabric federation.** (1 connections) — `somatic/fabric/federation.py`
- **.test_dependencies_stay_empty_and_connector_avoids_private_js_imports()** (1 connections) — `tests/test_fabric_federation_connect.py`
- **_tamper()** (1 connections) — `tests/test_fabric_federation_connect.py`

## Relationships

- [Fabric Federation Configuration](Fabric_Federation_Configuration.md) (14 shared connections)
- [Fabric Communication Errors](Fabric_Communication_Errors.md) (5 shared connections)
- [Fabric Registry Client](Fabric_Registry_Client.md) (4 shared connections)
- [Fabric Configuration Validation](Fabric_Configuration_Validation.md) (2 shared connections)
- [Log Secret Prevention](Log_Secret_Prevention.md) (2 shared connections)
- [Benchmarking and Scoring](Benchmarking_and_Scoring.md) (1 shared connections)
- [Fabric Environment Integration](Fabric_Environment_Integration.md) (1 shared connections)
- [Runtime Boundary Enforcement](Runtime_Boundary_Enforcement.md) (1 shared connections)
- [Network Isolation Checks](Network_Isolation_Checks.md) (1 shared connections)

## Source Files

- `somatic/fabric/federation.py`
- `tests/test_fabric_federation_connect.py`

## Audit Trail

- EXTRACTED: 79 (66%)
- INFERRED: 40 (34%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*