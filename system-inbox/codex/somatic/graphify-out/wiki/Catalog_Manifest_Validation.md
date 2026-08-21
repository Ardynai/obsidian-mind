# Catalog Manifest Validation

> 15 nodes · cohesion 0.20

## Key Concepts

- **validate_catalog_shape()** (13 connections) — `somatic/fabric/catalog.py`
- **catalog.py** (9 connections) — `somatic/fabric/catalog.py`
- **CatalogValidationResult** (5 connections) — `somatic/fabric/catalog.py`
- **.test_signed_catalog_verifies_against_keyring()** (4 connections) — `tests/test_fabric_catalog_signatures.py`
- **load_crypto_fixture()** (4 connections) — `tests/test_fabric_catalog_signatures.py`
- **_find_catalog_key()** (3 connections) — `somatic/fabric/catalog.py`
- **_publisher_key_active()** (3 connections) — `somatic/fabric/catalog.py`
- **FabricCatalogSignatureTests** (3 connections) — `tests/test_fabric_catalog_signatures.py`
- **.test_invalid_catalog_signature_fails_closed()** (3 connections) — `tests/test_fabric_catalog_signatures.py`
- **test_fabric_catalog_signatures.py** (3 connections) — `tests/test_fabric_catalog_signatures.py`
- **catalog_entry_from_manifest()** (2 connections) — `somatic/fabric/catalog.py`
- **_parse_utc()** (2 connections) — `somatic/fabric/catalog.py`
- **_validate_catalog_entry()** (2 connections) — `somatic/fabric/catalog.py`
- **FabricCatalogSignatureFixtureTests** (2 connections) — `tests/test_fabric_catalog_signatures.py`
- **.test_catalog_signature_fixtures_exist_and_parse()** (2 connections) — `tests/test_fabric_catalog_signatures.py`

## Relationships

- [Keyring Signature Verification](Keyring_Signature_Verification.md) (7 shared connections)
- [Fabric Cryptography Utilities](Fabric_Cryptography_Utilities.md) (4 shared connections)
- [Fabric Conformance Testing](Fabric_Conformance_Testing.md) (2 shared connections)
- [License Policy Evaluation](License_Policy_Evaluation.md) (1 shared connections)
- [Benchmarking and Scoring](Benchmarking_and_Scoring.md) (1 shared connections)
- [Fabric Environment Integration](Fabric_Environment_Integration.md) (1 shared connections)
- [Fabric Canonical JSON](Fabric_Canonical_JSON.md) (1 shared connections)
- [Shared Interop Fixtures](Shared_Interop_Fixtures.md) (1 shared connections)

## Source Files

- `somatic/fabric/catalog.py`
- `tests/test_fabric_catalog_signatures.py`

## Audit Trail

- EXTRACTED: 48 (80%)
- INFERRED: 12 (20%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*