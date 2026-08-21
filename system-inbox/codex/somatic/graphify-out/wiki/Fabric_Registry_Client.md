# Fabric Registry Client

> 14 nodes · cohesion 0.19

## Key Concepts

- **FabricAllowlistError** (20 connections) — `somatic/fabric/federation.py`
- **FabricRegistryClient** (10 connections) — `somatic/fabric/federation.py`
- **.validate()** (8 connections) — `somatic/fabric/federation.py`
- **.fetch_allowlist()** (7 connections) — `somatic/fabric/federation.py`
- **.__init__()** (5 connections) — `somatic/fabric/federation.py`
- **_allowlist_dids_from_response()** (4 connections) — `somatic/fabric/federation.py`
- **.register()** (4 connections) — `somatic/fabric/federation.py`
- **.connect()** (3 connections) — `somatic/fabric/federation.py`
- **.__init__()** (3 connections) — `somatic/fabric/federation.py`
- **_validate_http_base_url()** (3 connections) — `somatic/fabric/federation.py`
- **_validate_loopback_http_base_url()** (3 connections) — `somatic/fabric/federation.py`
- **.keepalive()** (2 connections) — `somatic/fabric/federation.py`
- **Client for the Multiverse registry HTTP API.** (1 connections) — `somatic/fabric/federation.py`
- **Raised when a DID is not authenticated through the sibling allowlist.** (1 connections) — `somatic/fabric/federation.py`

## Relationships

- [Fabric Communication Errors](Fabric_Communication_Errors.md) (19 shared connections)
- [Fabric Federation Configuration](Fabric_Federation_Configuration.md) (10 shared connections)
- [Fabric Federation Client](Fabric_Federation_Client.md) (4 shared connections)
- [Fabric Configuration Validation](Fabric_Configuration_Validation.md) (4 shared connections)
- [Log Secret Prevention](Log_Secret_Prevention.md) (1 shared connections)
- [Runtime Boundary Enforcement](Runtime_Boundary_Enforcement.md) (1 shared connections)
- [Network Isolation Checks](Network_Isolation_Checks.md) (1 shared connections)

## Source Files

- `somatic/fabric/federation.py`

## Audit Trail

- EXTRACTED: 61 (82%)
- INFERRED: 13 (18%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*