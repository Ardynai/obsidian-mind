# Fabric Conformance Testing

> 30 nodes · cohesion 0.10

## Key Concepts

- **load_conformance_fixture()** (23 connections) — `somatic/fabric/fixtures.py`
- **FabricConformanceScaffoldTests** (8 connections) — `tests/test_fabric_conformance_scaffold.py`
- **FabricManifestTests** (8 connections) — `tests/test_fabric_manifest.py`
- **basic_conformance_precheck()** (6 connections) — `somatic/fabric/conformance.py`
- **FabricKeyringCatalogTests** (5 connections) — `tests/test_fabric_keyring_catalog.py`
- **integer_only_json_errors()** (4 connections) — `somatic/fabric/conformance.py`
- **code_signature_threshold_errors()** (4 connections) — `somatic/fabric/signing.py`
- **.test_invalid_float_fixture_is_detected_by_integer_only_walk()** (4 connections) — `tests/test_fabric_conformance_scaffold.py`
- **FabricPrecheckResult** (3 connections) — `somatic/fabric/conformance.py`
- **conformance.py** (3 connections) — `somatic/fabric/conformance.py`
- **.test_invalid_license_fixture_fails_license_gate_precheck()** (3 connections) — `tests/test_fabric_conformance_scaffold.py`
- **.test_invalid_path_fixture_is_detected_by_path_precheck()** (3 connections) — `tests/test_fabric_conformance_scaffold.py`
- **.test_unsigned_code_pack_fails_signature_threshold_precheck()** (3 connections) — `tests/test_fabric_conformance_scaffold.py`
- **.test_catalog_rejects_duplicate_pack_entries()** (3 connections) — `tests/test_fabric_keyring_catalog.py`
- **.test_keyring_rejects_invalid_threshold_and_status()** (3 connections) — `tests/test_fabric_keyring_catalog.py`
- **.test_sample_catalog_passes_shape_validation()** (3 connections) — `tests/test_fabric_keyring_catalog.py`
- **.test_sample_keyring_passes_shape_validation()** (3 connections) — `tests/test_fabric_keyring_catalog.py`
- **.test_invalid_license_pack_fails_validation()** (3 connections) — `tests/test_fabric_manifest.py`
- **.test_invalid_path_pack_fails_validation()** (3 connections) — `tests/test_fabric_manifest.py`
- **.test_license_policy_distinguishes_public_private_and_install()** (3 connections) — `tests/test_fabric_manifest.py`
- **.test_manifest_rejects_class_type_mismatch_and_unsorted_files()** (3 connections) — `tests/test_fabric_manifest.py`
- **.test_unsigned_code_pack_fails_validation()** (3 connections) — `tests/test_fabric_manifest.py`
- **.test_valid_sample_pack_passes_current_shape_validators()** (3 connections) — `tests/test_fabric_manifest.py`
- **conformance_fixture_root()** (2 connections) — `somatic/fabric/fixtures.py`
- **fixtures.py** (2 connections) — `somatic/fabric/fixtures.py`
- *... and 5 more nodes in this community*

## Relationships

- [License Policy Evaluation](License_Policy_Evaluation.md) (9 shared connections)
- [Fabric Canonical JSON](Fabric_Canonical_JSON.md) (9 shared connections)
- [Path Confinement Validation](Path_Confinement_Validation.md) (3 shared connections)
- [Fabric Cryptography Utilities](Fabric_Cryptography_Utilities.md) (2 shared connections)
- [Catalog Manifest Validation](Catalog_Manifest_Validation.md) (2 shared connections)
- [Keyring Signature Verification](Keyring_Signature_Verification.md) (2 shared connections)
- [Fabric Signing Cryptography](Fabric_Signing_Cryptography.md) (1 shared connections)

## Source Files

- `somatic/fabric/conformance.py`
- `somatic/fabric/fixtures.py`
- `somatic/fabric/signing.py`
- `tests/test_fabric_conformance_scaffold.py`
- `tests/test_fabric_keyring_catalog.py`
- `tests/test_fabric_manifest.py`

## Audit Trail

- EXTRACTED: 56 (48%)
- INFERRED: 60 (52%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*