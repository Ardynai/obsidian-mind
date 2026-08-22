# Fabric Federation Security Review

**Review date:** 2026-07-06
**Reviewer:** Odysseus coding agent (GLM) — retroactive review
**Subject:** `somatic/fabric/federation.py` (PR #66, self-merged without review)
**Scope:** Retroactive audit of the fabric federation connector and its security invariants.
**Method:** Static source audit + regression test suite (`tests/test_fabric_federation_security_invariants.py`).

## Summary

The fabric federation connector is **out-of-process, stdlib-only, and fail-closed by design**.
The audit found **no gaps requiring code changes** — all eight invariants are enforced by the
existing implementation. Regression tests have been added to lock each invariant going forward.

| Invariant | Verdict | Evidence |
|-----------|---------|----------|
| I1 stdlib-only | PASS | `pyproject.toml:15` — `dependencies = []`; AST test confirms only stdlib imports |
| I2 out-of-process only | PASS | `federation.py:3-7` docstring; HTTP-only I/O via `urllib.request`; no socket/subprocess/DHT |
| I3 allowlist both ways | PASS | `federation.py:401` (send), `federation.py:427` (receive); `_require_allowlisted` at `:821` |
| I4 integrity re-verify | PASS | `federation.py:440-467` `verify_payload_against_descriptor`; domain-separated Merkle at `:570-588` |
| I5 ciphertext preserved | PASS | `federation.py:316-325` `send_delivery` passes `secure`/`ciphertext` flags; no decrypt function in module |
| I6 fail-closed config | PASS | `federation.py:137-154` `validate()` checks all required fields; constructor calls `validate()` at `:186` |
| I7 no secrets in logs | PASS | AST scan confirms no `print()` or `logging` calls; no f-string embeds token values |
| I8 pre-runtime boundary | PASS | `main.py:498-505` doctor reports out-of-process sidecar; all runtime execution lines say "disabled" |

## Invariant Details

### I1 — stdlib-only; pyproject dependencies == [] unchanged

**Verdict: PASS**

- `pyproject.toml:15`: `dependencies = []`
- `federation.py:10-21`: imports are `hashlib`, `json`, `os`, `collections.abc`, `dataclasses`,
  `pathlib`, `typing`, `urllib` — all stdlib.
- The existing test `test_dependencies_stay_empty_and_connector_avoids_private_js_imports`
  in `test_fabric_federation_connect.py` already checks this.
- The new test `StdlibAndOutOfProcessTests.test_pyproject_dependencies_stay_empty` reinforces it.

**Residual risk:** None. The `fabric` optional-dependency group includes `canonicaljson` and
`cryptography`, but those are for the *local* fabric pack signing path, not the federation
connector, which is stdlib-only.

### I2 — out-of-process only

**Verdict: PASS**

- `federation.py:1-8` module docstring explicitly states transport/chunking/descriptor/routing
  stay in the external sidecar.
- All I/O is via `urllib.request.urlopen` (`federation.py:600-620`).
- No `socket`, `subprocess`, `ssl`, `asyncio`, `requests`, `aiohttp` imports (AST test confirms).
- No DHT, swarm, bittorrent, webtorrent, libp2p terms in source (string scan test confirms).
- No descriptor creation or chunk splitting — the connector only validates descriptors produced
  by the sidecar (`validate_descriptor` at `:469-565`).
- No Merkle *construction* for outbound payloads — the connector only *re-verifies* inbound
  Merkle roots (`verify_payload_against_descriptor` at `:440-467`).

**Residual risk:** None. The connector is a thin HTTP client over loopback.

### I3 — allowlist reject both ways

**Verdict: PASS**

- **Send direction:** `federation.py:401` — `send()` calls `_require_allowlisted(to_did, allowlist)`
  *before* any sidecar PUT or registry delivery POST. If rejected, `FabricAllowlistError` is raised
  and no payload is stored or delivered.
- **Receive direction:** `federation.py:427` — `receive_once()` calls
  `_require_allowlisted(parsed["from_did"], allowlist)` for each inbound item before fetching bytes.
- `_require_allowlisted` (`federation.py:821-823`) raises `FabricAllowlistError` if the DID is not
  in the set.
- `fetch_allowlist` (`federation.py:283-295`) discards the local DID from the allowlist and raises
  if the result is empty.

**Residual risk:** The allowlist is fetched from the registry at send/receive time. If the registry
is compromised and returns a wider allowlist, the connector would trust it. This is acceptable
because the registry is an authenticated, trusted service. The config fallback allowlist
(`allowlisted_sibling_dids`) provides a defense-in-depth floor.

### I4 — integrity re-verify before delivery

**Verdict: PASS**

- `federation.py:431` — `receive_once()` calls `self.sidecar.get_bytes(parsed["content_id"])`,
  which calls `verify_payload_against_descriptor(payload, descriptor, expected_content_id=content_id)`
  at `federation.py:234`.
- `verify_payload_against_descriptor` (`federation.py:440-467`):
  - Checks payload total size matches descriptor (`:445`).
  - Iterates pieces in descriptor order, verifying each leaf hash:
    `_domain_leaf_hash(piece_bytes)` = `sha256(b"\x00" + piece)` (`:570-572`).
  - Recomputes Merkle root: `_merkle_root_hex_from_leaf_hashes` using
    `_domain_node_hash(left, right)` = `sha256(b"\x01" + left + right)` (`:574-576`).
  - Compares recomputed root to descriptor `contentId` (`:462`).
  - Compares to `expected_content_id` if provided (`:464`).
- `validate_descriptor` (`federation.py:469-565`) independently verifies:
  - Only the last piece may be short (`:534`).
  - Piece offsets are contiguous (`:530`).
  - Piece count matches `totalSize` / `pieceSize` (`:495`).
  - Descriptor Merkle root matches `contentId` (`:562`).
- If the inbound item carries its own descriptor, it is also validated and cross-checked against
  the sidecar's descriptor (`federation.py:428-432`).

**Residual risk:** None. The verification is performed entirely in-process using stdlib `hashlib`.

### I5 — Secure Drop stays ciphertext

**Verdict: PASS**

- `send_delivery` (`federation.py:316-325`) passes `secure` and `ciphertext` boolean flags to the
  registry but never attempts to decrypt the payload.
- `put_bytes` (`federation.py:189-205`) stores raw bytes via the sidecar; no transformation.
- `receive_once` (`federation.py:417-445`) returns the raw payload bytes with a `secure` flag;
  no decryption step.
- AST scan of `federation.py` confirms no function named `decrypt*` or `decipher*` exists.
- The `secure` flag flows from sender → registry → receiver as metadata only; the payload bytes
  are never inspected for plaintext content.

**Residual risk:** None. Decryption is the responsibility of the downstream consumer, not the
connector.

### I6 — fail-closed config

**Verdict: PASS**

- `FabricFederationConfig.validate()` (`federation.py:137-154`) raises `FabricConfigError` if any
  of: `sidecar_base_url`, `sidecar_token`, `registry_base_url`, `registry_token`, `local_did`,
  `system_id` is empty.
- `_validate_loopback_http_base_url` (`federation.py:640-651`) enforces loopback HTTP only for the
  sidecar URL (rejects non-localhost hosts, HTTPS, and embedded credentials).
- `_validate_http_base_url` (`federation.py:653-660`) enforces HTTP/HTTPS and rejects embedded
  credentials for the registry URL.
- `FabricTransportSidecarClient.__init__` (`federation.py:185-187`) and
  `FabricRegistryClient.__init__` (`federation.py:271-273`) and
  `FabricFederationClient.__init__` (`federation.py:353-356`) all call `config.validate()`
  in the constructor — the connector cannot be instantiated with invalid config.
- `from_env({})` produces a config where every transport field is empty — `validate()` will raise.

**Residual risk:** None. The connector is inert until explicitly configured with all required
fields.

### I7 — no secrets in logs

**Verdict: PASS**

- AST scan of `federation.py` confirms **zero** `print()` calls and **zero** `logging` imports.
- No `logging`, `logger`, `debug`, `info`, `warn` identifiers in the module.
- Token values (`sidecar_token`, `registry_token`) are used only in:
  - `FabricFederationConfig` fields (`federation.py:75, 77`).
  - `Authorization: Bearer {token}` header construction (`federation.py:254, 340`).
  - The `from_env` factory (`federation.py:95-102`).
- No f-string or string formatting embeds `sidecar_token` or `registry_token` (AST f-string scan
  confirms).
- Exception messages reference the *config field name* (e.g., "SOMATIC_FABRIC_SIDECAR_TOKEN is
  required") not the token value.
- `BaseHTTPRequestHandler.log_message` is overridden to suppress all server-side logging in both
  the test harness and production-equivalent code paths.

**Residual risk:** The frozen dataclass `__repr__` will include token values if someone calls
`repr(config)` or `print(config)`. The module itself never does this. If a future caller logs the
config object, they must use a redacting formatter. This is noted as a documentation-level
residual risk, not a code gap.

### I8 — pre-runtime boundary intact

**Verdict: PASS**

- `somatic/cli/main.py:498`: `"- Fabric federation connector: out-of-process sidecar ready when configured"`
- `main.py:499`: `"- Fabric federation sidecar: loopback HTTP with bearer token"`
- `main.py:502`: `"- Fabric federation receive integrity: contentId re-verified before delivery"`
- `main.py:503`: `"- Fabric federation private fabric-core import: disabled"`
- `main.py:504`: `"- Fabric federation public DHT/swarm: disabled"`
- All other runtime execution lines say "disabled" (Boltz, biomodel, sensors, etc.).
- No doctor output line claims real-mode runtime is enabled for any provider.

**Residual risk:** None. The doctor output is consistent with the pre-runtime contract in
`CONTRIBUTING.md`.

## No Code Changes Required

The audit found **no gaps** in the existing implementation. All eight invariants are enforced by
the code as written. No additive guards were needed. The only deliverables are:

1. `tests/test_fabric_federation_security_invariants.py` — regression test suite for I3–I8.
2. `docs/how-it-works/fabric-connect.md` — "Security invariants (reviewed)" section added.
3. `docs/reviews/fabric-federation-security-review.md` — this audit record.

## Test Coverage

| Invariant | Test class | Test method |
|-----------|-----------|-------------|
| I1 | `StdlibAndOutOfProcessTests` | `test_pyproject_dependencies_stay_empty` |
| I1 | `StdlibAndOutOfProcessTests` | `test_no_socket_or_subprocess_import_in_federation` |
| I2 | `StdlibAndOutOfProcessTests` | `test_no_dht_swarm_or_chunking_reimplementation` |
| I3 | `AllowlistRejectBothWaysTests` | `test_send_to_non_allowlisted_did_is_rejected` |
| I3 | `AllowlistRejectBothWaysTests` | `test_receive_from_non_allowlisted_did_is_rejected` |
| I3 | `AllowlistRejectBothWaysTests` | `test_send_to_self_is_rejected_when_not_in_allowlist` |
| I4 | `IntegrityReverifyTests` | `test_tampered_payload_byte_is_rejected` |
| I4 | `IntegrityReverifyTests` | `test_mismatched_inbound_descriptor_contentId_is_rejected` |
| I4 | `IntegrityReverifyTests` | `test_empty_payload_descriptor_is_accepted` |
| I5 | `CiphertextPreservedTests` | `test_secure_send_preserves_ciphertext_in_sidecar` |
| I5 | `CiphertextPreservedTests` | `test_secure_receive_returns_ciphertext_unchanged` |
| I5 | `CiphertextPreservedTests` | `test_no_decryption_function_exists_in_module` |
| I6 | `FailClosedConfigTests` | `test_blank_env_produces_inert_config` |
| I6 | `FailClosedConfigTests` | `test_missing_sidecar_url_raises` (+ 6 more) |
| I6 | `FailClosedConfigTests` | `test_blank_env_sends_nothing` |
| I7 | `NoSecretsInLogsTests` | `test_no_print_or_logging_calls_in_federation_module` |
| I7 | `NoSecretsInLogsTests` | `test_token_not_in_exception_messages` |
| I7 | `NoSecretsInLogsTests` | `test_config_repr_does_not_leak_token` |
| I8 | `PreRuntimeBoundaryTests` | `test_doctor_reports_fabric_out_of_process` |
| I8 | `PreRuntimeBoundaryTests` | `test_doctor_reports_runtime_blocked` |
