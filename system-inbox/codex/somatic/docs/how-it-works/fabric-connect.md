# Fabric Connect

Somatic connects to the closed Multiverse fabric federation out of process. The
canonical producer and transport implementation remain in `Ardynai/multiverse`:

- `packages/fabric-core`
- `fabric-transport-d`

Somatic does not import private JavaScript packages, does not add JavaScript
dependencies, and does not reimplement chunking, hashing, Merkle construction,
peer transport, DHT, swarm behavior, or decryption. The Python connector uses
only the standard library and calls the sidecar and registry over HTTP.

## Runtime Boundary

Somatic owns these checks:

- call the loopback `fabric-transport-d` sidecar with a bearer token
- register its DID and reachability with the Multiverse registry
- obtain an authenticated sibling DID allowlist from the registry or config
- reject senders and recipients outside the allowlist
- fetch inbound content by `contentId`
- re-verify the received bytes against the descriptor before delivery
- keep encrypted Secure Drop payloads as ciphertext

The sidecar owns these behaviors:

- content-addressed chunking
- descriptor creation
- peer adapters
- piece storage
- identity custody and signing where stdlib Python cannot provide the primitive
- transport pulls and sidecar-to-sidecar routing

The registry owns:

- system registration
- DID/reachability records
- federation addressing
- authenticated sibling allowlist publication

## Configuration

Use secret/config storage or environment variables. Do not commit DID private
keys, bearer tokens, or sidecar registry secrets.

```powershell
SOMATIC_FABRIC_SIDECAR_URL=http://127.0.0.1:37877
SOMATIC_FABRIC_SIDECAR_TOKEN=<secret>
SOMATIC_FABRIC_REGISTRY_URL=<registry-url>
SOMATIC_FABRIC_REGISTRY_TOKEN=<secret>
SOMATIC_FABRIC_DID=<somatic-did>
SOMATIC_FABRIC_REACHABILITY_URL=<optional-registry-reachability-url>
SOMATIC_FABRIC_ALLOWLIST_DIDS=<comma-separated-fallback-sibling-dids>
```

The sidecar URL must be loopback HTTP: `localhost`, `127.0.0.1`, or `::1`.
Registry URLs may be `http` or `https`, but credentials must be carried by the
bearer token header rather than embedded in the URL.

Optional path overrides exist for deployments whose registry exposes the
federation routes under a different prefix:

```powershell
SOMATIC_FABRIC_REGISTRY_REGISTER_PATH=/systems/register
SOMATIC_FABRIC_REGISTRY_ALLOWLIST_PATH=/fabric/federation/allowlist
SOMATIC_FABRIC_REGISTRY_DELIVERY_PATH=/fabric/federation/deliveries
SOMATIC_FABRIC_REGISTRY_INBOX_PATH=/fabric/federation/inbox
```

## Commands

Register Somatic and refresh the allowlist:

```powershell
python -m somatic fabric register
```

Send a file to an allowlisted sibling DID:

```powershell
python -m somatic fabric send --to-did did:multiverse:kortex-audio#... --path .\payload.bin
```

Mark a payload as encrypted ciphertext without decrypting it in Somatic:

```powershell
python -m somatic fabric send --to-did did:multiverse:ardyn#... --path .\drop.bin --secure
```

Poll one inbound batch and re-verify every content ID before local delivery:

```powershell
python -m somatic fabric receive-once
```

## Integrity Check

For each received descriptor, Somatic recomputes the content ID using the Fabric
CA Merkle contract:

- leaf hash: `sha256(b"\x00" + piece)`
- node hash: `sha256(b"\x01" + left + right)`
- ordered pieces from the descriptor
- only the final piece may be shorter than `pieceSize`
- empty payloads are represented by one zero-size piece
- `merkleRoot` and `contentId` must match

If any byte is tampered, if a piece hash is wrong, if the descriptor is malformed,
or if the sender is not allowlisted, Somatic fails closed.

## Non-Goals

This connector does not add:

- public DHT or swarm behavior
- P2P dependencies
- private `@multiverse/fabric-core` imports
- JavaScript dependencies
- chunked transport implementation
- Merkle transport implementation
- content-addressed payload movement outside the sidecar
- shell or process execution
- database writes or query runtime
- decryption of Secure Drop ciphertext

## Security Invariants (reviewed)

A retroactive security review of the federation connector was completed on 2026-07-06.
The full audit record lives at `docs/reviews/fabric-federation-security-review.md`.
Regression tests that lock these invariants are in
`tests/test_fabric_federation_security_invariants.py`.

| # | Invariant | Verdict | Enforcement |
|---|-----------|---------|-------------|
| I1 | stdlib-only; `pyproject dependencies == []` | PASS | AST import scan + pyproject check |
| I2 | out-of-process only; no peer sockets, DHT, swarm, or chunking reimplementation | PASS | HTTP-only via `urllib.request`; no socket/subprocess imports |
| I3 | allowlist reject both ways (send + receive) | PASS | `_require_allowlisted` called before any I/O in `send()` and `receive_once()` |
| I4 | inbound bytes re-verified against descriptor contentId (domain-separated SHA-256 Merkle) before delivery | PASS | `verify_payload_against_descriptor` recomputes leaf/node hashes and compares to `contentId` |
| I5 | Secure Drop stays ciphertext; no in-process decryption | PASS | no decrypt function exists; `secure` flag is metadata only |
| I6 | fail-closed config; missing URL/token/DID/allowlist makes connector inert | PASS | `validate()` raises on any empty required field; constructors call it |
| I7 | no secrets in logs; tokens/bearer values never printed or logged | PASS | no `print()` or `logging` in module; no f-string embeds tokens |
| I8 | pre-runtime boundary intact; `somatic doctor` keeps real-mode runtime blocked | PASS | doctor output says "out-of-process sidecar ready when configured"; all runtime execution "disabled" |

No code changes were required — all invariants were already enforced by the implementation.
The review added regression tests and documentation only.
