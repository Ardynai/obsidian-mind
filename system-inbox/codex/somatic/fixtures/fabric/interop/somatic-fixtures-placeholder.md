# Somatic Fixture Placeholder

Somatic Fabric source fixtures currently live in:

```text
fixtures/fabric/crypto/
```

Phase 4E/4F Somatic-origin exports:

- `somatic-generated-pack.json`
- `somatic-generated-keyring.json`
- `somatic-generated-catalog.json`
- `somatic-generated-metadata.json`

Source fixtures remain in `fixtures/fabric/crypto/` and `fixtures/fabric/crypto/rotation/`.

These are deterministic test vectors with test-only private key material in adjacent key files. Phase 4F records local partial verification for the pack, keyring, and catalog signature path, but these are not production signing material and are not a certification vector until Locus and Somatic mutually verify the full set of byte-identical canonical payloads, manifest digests, key ids, signatures, keyrings, catalogs, and rejection cases.
