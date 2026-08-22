# Fabric Conformance Fixtures

These fixtures exercise Somatic's Phase 3B Content Fabric conformance scaffold.

They are intentionally non-runtime fixtures:

- no real signing keys
- no real Ed25519 signatures
- no real JCS implementation
- no BitTorrent networking
- no install, quarantine, sandbox, or enablement runtime

The signature and digest values are non-cryptographic placeholders unless a later runtime explicitly regenerates them with RFC 8785 JCS and Ed25519.
