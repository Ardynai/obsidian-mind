# Fabric Canonical JSON

> 48 nodes · cohesion 0.10

## Key Concepts

- **loads_fabric_json()** (18 connections) — `somatic/fabric/canonical.py`
- **FabricJsonError** (16 connections) — `somatic/fabric/canonical.py`
- **canonical.py** (14 connections) — `somatic/fabric/canonical.py`
- **signing_payload()** (14 connections) — `somatic/fabric/canonical.py`
- **FabricIntegerError** (13 connections) — `somatic/fabric/canonical.py`
- **_shared_fixture_errors()** (12 connections) — `somatic/cli/main.py`
- **canonical_dumps()** (11 connections) — `somatic/fabric/canonical.py`
- **canonical_bytes()** (10 connections) — `somatic/fabric/canonical.py`
- **manifest_digest()** (10 connections) — `somatic/fabric/digests.py`
- **sha256_hex()** (10 connections) — `somatic/fabric/digests.py`
- **validate_integer_only_json()** (9 connections) — `somatic/fabric/canonical.py`
- **FabricRawJsonTests** (9 connections) — `tests/test_fabric_raw_json.py`
- **FabricCanonicalTests** (7 connections) — `tests/test_fabric_canonical.py`
- **validate_raw_json_numbers()** (6 connections) — `somatic/fabric/canonical.py`
- **FabricJcsVectorTests** (6 connections) — `tests/test_fabric_jcs_vectors.py`
- **.test_shared_expected_digests_match_generated_values()** (6 connections) — `tests/test_fabric_shared_interop_fixtures.py`
- **_fabric_digest()** (6 connections) — `somatic/cli/main.py`
- **_serialize_canonical()** (5 connections) — `somatic/fabric/canonical.py`
- **.test_digest_helpers_are_deterministic()** (5 connections) — `tests/test_fabric_canonical.py`
- **.test_expected_digest_fixture_matches_current_scaffold()** (5 connections) — `tests/test_fabric_canonical.py`
- **_fabric_payload()** (5 connections) — `somatic/cli/main.py`
- **.test_integer_only_validation_rejects_float_fixture()** (4 connections) — `tests/test_fabric_canonical.py`
- **.test_metadata_digests_match_current_somatic_fixtures()** (4 connections) — `tests/test_fabric_interop_metadata.py`
- **_reject_duplicate_object_pairs()** (3 connections) — `somatic/fabric/canonical.py`
- **_validate_json_string()** (3 connections) — `somatic/fabric/canonical.py`
- *... and 23 more nodes in this community*

## Relationships

- [Benchmarking and Scoring](Benchmarking_and_Scoring.md) (9 shared connections)
- [Fabric Conformance Testing](Fabric_Conformance_Testing.md) (9 shared connections)
- [Fabric Environment Integration](Fabric_Environment_Integration.md) (8 shared connections)
- [Keyring Signature Verification](Keyring_Signature_Verification.md) (5 shared connections)
- [License Policy Evaluation](License_Policy_Evaluation.md) (3 shared connections)
- [Fabric Cryptography Utilities](Fabric_Cryptography_Utilities.md) (2 shared connections)
- [Shared Interop Fixtures](Shared_Interop_Fixtures.md) (2 shared connections)
- [Fabric Signing Cryptography](Fabric_Signing_Cryptography.md) (1 shared connections)
- [Fabric Interop Metadata](Fabric_Interop_Metadata.md) (1 shared connections)
- [Catalog Manifest Validation](Catalog_Manifest_Validation.md) (1 shared connections)

## Source Files

- `somatic/cli/main.py`
- `somatic/fabric/canonical.py`
- `somatic/fabric/digests.py`
- `tests/test_fabric_canonical.py`
- `tests/test_fabric_interop_metadata.py`
- `tests/test_fabric_jcs_vectors.py`
- `tests/test_fabric_raw_json.py`
- `tests/test_fabric_shared_interop_fixtures.py`

## Audit Trail

- EXTRACTED: 165 (63%)
- INFERRED: 96 (37%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*