# Security

Somatic is a research harness that will eventually coordinate models, datasets, sensors, lab adapters, reports, and plugin packs. Security boundaries must be designed before runtime features are added.

## Reporting

Use GitHub private vulnerability reporting if it is enabled for this repository. If it is not enabled, contact the maintainers before disclosing exploit details publicly.

Do not include secrets, tokens, private health data, private lab data, proprietary datasets, or exploit payloads in public issues.

## Phase 0 Security Scope

This phase contains documentation and placeholder manifests only. There are no runtime services, package installs, external API calls, provider credentials, lab connections, or sensor integrations.

## Planned Security Boundaries

- Provider adapters must run with least privilege.
- Code packs must be quarantined until explicitly enabled.
- Data packs must be verified before indexing or execution-adjacent use.
- Fabric assets must use SHA-256 verification and signature checks before trust.
- Clinical and personal baseline data must be local-first by default.
- Real lab actions must require explicit human approval.
- Reports must separate generated claims from evidence, assumptions, and human review state.

## Secret Handling

Future code must not commit provider keys, lab credentials, signing keys, patient identifiers, private datasets, or local catalogs. Local secrets should live in ignored environment files or operating-system secret stores.

## Encryption At Rest (opt-in)

Local stores (consent ledger, readings, experiment tags, sensor features) are **plaintext JSON with `chmod 0600` by default**. The Python standard library has no AEAD cipher, so encryption is an **opt-in** feature backed by the optional [`cryptography`](https://cryptography.io) package — never hand-rolled crypto.

**Enable:**

```bash
pip install "somatic[fabric]"        # provides the optional `cryptography` package
set SOMATIC_ENCRYPT_STORES=1         # also accepted: true / on / yes
# optional explicit key material:
set SOMATIC_STORE_PASSPHRASE=<your passphrase>
```

**Design:**

- Cipher: AES-256-GCM; key derived per store file with scrypt (n=16384, r=8, p=1, 32-byte key), random 16-byte salt and 12-byte nonce per write.
- Envelope on disk: JSON object with `"format": "somatic-encrypted-v1"` plus kdf params, salt, nonce, ciphertext (hex).
- Key material: `SOMATIC_STORE_PASSPHRASE` when set; otherwise a random 32-byte key file is created beside each store (`<store>.key`, `chmod 0600`) on first encrypted write.
- Scope of the flag: writes only. Reads transparently decrypt envelopes and still read legacy plaintext files.
- The core package stays stdlib-only: without the flag nothing imports or requires `cryptography`.

**Failure policy (fail closed):** a corrupt, truncated, tampered-with, or undecryptable store file loads as all-OFF consent / empty data — exactly like any other invalid store file. If you lose the passphrase or delete the `.key` files, your encrypted stores are unreadable by design.

**Right-to-erasure:** erase functions delete both the ciphertext file and the store's key file.

**Known limitations (documented honestly):**

- The plaintext default remains until you opt in; anyone with file-system access to `~/.somatic/` can read unencrypted stores.
- With `SOMATIC_ENCRYPT_STORES=1` but `cryptography` missing, encrypted *writes* raise a clear error (a store is never silently written in plaintext believing it was encrypted).
- Key files live beside the stores under `~/.somatic/`; they protect against casual reading, not against malware running as your user. For stronger protection use an OS-level secret store or full-disk encryption alongside this feature.
