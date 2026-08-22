# Fabric JCS Local Vectors

These fixtures are local Somatic Phase 4G.1 vectors for RFC 8785/JCS behavior in the Fabric-supported JSON domain.

Scope:

- JSON objects, arrays, strings, booleans, null, and non-negative safe integers only.
- Object member names sort by UTF-16 code units.
- Arrays preserve source order.
- Canonical output has no insignificant whitespace and is encoded as UTF-8.
- Signing payloads keep the top-level `signatures` key present and set to `[]`.

These are not Locus mutual-certification fixtures. Shared Locus/Somatic certification remains deferred to Phase 4G.3.
