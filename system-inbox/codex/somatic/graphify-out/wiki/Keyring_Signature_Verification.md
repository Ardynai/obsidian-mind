# Keyring Signature Verification

> 32 nodes · cohesion 0.16

## Key Concepts

- **verify_pack_publisher_threshold()** (18 connections) — `somatic/fabric/keyring.py`
- **validate_keyring_shape()** (17 connections) — `somatic/fabric/keyring.py`
- **keyring.py** (16 connections) — `somatic/fabric/keyring.py`
- **verify_catalog_signature_threshold()** (15 connections) — `somatic/fabric/catalog.py`
- **verify_keyring_root_threshold()** (15 connections) — `somatic/fabric/keyring.py`
- **verify_keyring_replacement()** (12 connections) — `somatic/fabric/keyring.py`
- **SignatureVerificationResult** (8 connections) — `somatic/fabric/keyring.py`
- **_verify_signature_entry()** (8 connections) — `somatic/fabric/keyring.py`
- **load_crypto_fixture()** (7 connections) — `tests/test_fabric_keyring_crypto.py`
- **_fabric_check()** (7 connections) — `somatic/cli/main.py`
- **FabricKeyringCryptoTests** (6 connections) — `tests/test_fabric_keyring_crypto.py`
- **.test_invalid_shared_fixtures_fail_closed()** (6 connections) — `tests/test_fabric_shared_interop_fixtures.py`
- **.test_shared_keyring_pack_and_catalog_self_certify()** (5 connections) — `tests/test_fabric_shared_interop_fixtures.py`
- **_find_key()** (4 connections) — `somatic/fabric/keyring.py`
- **KeyringValidationResult** (4 connections) — `somatic/fabric/keyring.py`
- **_parse_utc()** (4 connections) — `somatic/fabric/keyring.py`
- **_root_key_active()** (4 connections) — `somatic/fabric/keyring.py`
- **_timestamp_is_expired()** (4 connections) — `somatic/fabric/keyring.py`
- **.test_signed_code_pack_verifies_and_unsigned_code_still_fails()** (4 connections) — `tests/test_fabric_keyring_crypto.py`
- **.test_signed_keyring_passes_shape_and_root_threshold()** (4 connections) — `tests/test_fabric_keyring_crypto.py`
- **.test_signed_pack_verifies_publisher_threshold()** (4 connections) — `tests/test_fabric_keyring_crypto.py`
- **_key_usable_for_manifest()** (3 connections) — `somatic/fabric/keyring.py`
- **_validate_keys()** (3 connections) — `somatic/fabric/keyring.py`
- **_validate_publisher()** (3 connections) — `somatic/fabric/keyring.py`
- **.test_invalid_signature_fails_publisher_threshold()** (3 connections) — `tests/test_fabric_keyring_crypto.py`
- *... and 7 more nodes in this community*

## Relationships

- [Fabric Cryptography Utilities](Fabric_Cryptography_Utilities.md) (10 shared connections)
- [Catalog Manifest Validation](Catalog_Manifest_Validation.md) (7 shared connections)
- [Benchmarking and Scoring](Benchmarking_and_Scoring.md) (6 shared connections)
- [Fabric Canonical JSON](Fabric_Canonical_JSON.md) (5 shared connections)
- [Shared Interop Fixtures](Shared_Interop_Fixtures.md) (4 shared connections)
- [License Policy Evaluation](License_Policy_Evaluation.md) (4 shared connections)
- [Fabric Environment Integration](Fabric_Environment_Integration.md) (3 shared connections)
- [Fabric Conformance Testing](Fabric_Conformance_Testing.md) (2 shared connections)
- [Keyring Rotation Fixtures](Keyring_Rotation_Fixtures.md) (2 shared connections)

## Source Files

- `somatic/cli/main.py`
- `somatic/fabric/catalog.py`
- `somatic/fabric/keyring.py`
- `tests/test_fabric_keyring_crypto.py`
- `tests/test_fabric_shared_interop_fixtures.py`

## Audit Trail

- EXTRACTED: 149 (74%)
- INFERRED: 52 (26%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*