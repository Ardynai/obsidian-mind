# Install Modes

Somatic keeps the basic install lightweight. Advanced lanes are optional.

## Basic Install

The basic project has no runtime dependencies beyond Python 3.11 or newer.

```powershell
python -m somatic doctor
python -m somatic run fixtures/workflows/valid-literature-only.yaml
```

When installed as a package, the console script is:

```powershell
somatic doctor
somatic run fixtures/workflows/valid-literature-only.yaml
```

## Dev Install

The `dev` extra is for contributors:

```powershell
uv pip install -e ".[dev]"
```

It includes pytest, ruff, and mypy. Do not install it when you only need the standard-library mock runner.

## Lane-Specific Extras

Optional extras are declared for:

- `cli`
- `schemas`
- `agents`
- `robin`
- `finch`
- `biomodel`
- `sensors`
- `csi`
- `video`
- `audio`
- `fabric`
- `bench`

Install only the lane you need. Heavy scientific and sensor dependencies are not part of the basic install.

Phase 5A provider placeholders do not add install requirements. PaperQA2,
FutureHouse Robin, scientific-agent-skills, AutoScientists, Boltz-2, aviary, and
ldp are not part of the basic install and are not imported by the placeholder
provider modules. Future adapters must add explicit optional extras or install
notes before any external package is imported.

Phase 5B adds `somatic.providers.paperqa2` without changing the basic install.
It checks PaperQA2 availability with `importlib.util.find_spec`, exposes only
deterministic fake-backed behavior by default, and fails closed for real mode.
The optional `paperqa` package is not installed, required, or imported at module
import time.

Phase 5C adds `somatic.providers.scientific_agent_skills` without changing the
basic install. It reports the staged source path when present, exposes only a
deterministic metadata subset by default, and fails closed for real mode. The
upstream skills collection is not installed, imported, executed, or required.

Phase 5G adds `somatic.analysis.extras` and `somatic.analysis.provider` without
changing the basic install. Finch optional extras for pandas, scipy, numpy,
scanpy, and biopython are detected with `importlib.util.find_spec`, reported as
disabled status metadata, and never imported or executed by default.

Phase 6A adds `somatic.providers.boltz` without changing the basic install. It
detects optional `boltz` availability with `importlib.util.find_spec`, reports
the staged source path, and returns only deterministic fake-backed biomodel
plan/result metadata. It does not install or import Boltz, download model
weights or molecule data, call MSA servers, run predictions, or use GPU runtime.

The `fabric` extra enables optional local Ed25519 crypto checks for Fabric keyring and pack-signature verification:

```powershell
uv pip install -e ".[fabric]"
python -m somatic fabric check fixtures/fabric/crypto/signed-data-pack.json --keyring fixtures/fabric/crypto/keyring-signed.json
```

The basic install can still run Somatic workflows and Fabric shape checks without this extra. If `--keyring` is requested without the crypto backend, Fabric checks fail closed instead of treating signatures as verified.

## All-Extras / FutureCube Mode

The power-user mode is described as all-extras / FutureCube mode. The actual Python extra is named `all` and combines practical optional lanes:

```powershell
uv pip install -e ".[all]"
```

This may be large and should not be treated as the normal installation path.

## Why Heavy Integrations Are Optional

Scientific discovery workflows span agents, molecular modeling, sensors, video, audio, Fabric transport, and benchmarking. Forcing every dependency into the basic install would make Somatic harder to audit, slower to install, and less usable for simple offline research workflows.

## Runtime Defaults

No advanced lane runs unless explicitly configured. The current runtime does not implement real provider API calls, model downloads, Fabric transport, live sensors, or lab actions. Fabric crypto verification is local/offline and does not download, install, enable, or execute packs.

The Phase 5A external science placeholders are metadata and protocol scaffolds
only. They do not enable provider loading, network access, external API calls,
model downloads, live agent orchestration, or biomodel execution.

The Phase 5B PaperQA2 scaffold follows the same default. It does not fetch
literature, build PaperQA2 indexes, call metadata providers, or send private
health data to an external provider without explicit future configuration and
consent.

The Phase 6A Boltz scaffold follows the same default. It records Boltz source
inspection and mock plan/result metadata only. Future real mode must require
explicit opt-in, model/download/MSA consent gates, resource checks, provenance
hashes, and research-only safety review.

The Phase 5C scientific-agent-skills scaffold is metadata-only. It does not
execute skills, run scanner scripts, install skill dependencies, call public
databases, or send clinical/health data to external connectors without explicit
future configuration and consent.

The Phase 5G Finch optional-extras scaffold is also metadata-only. It does not
run pandas, scipy, numpy, scanpy, biopython, package-backed analysis, clinical
interpretation, genomic interpretation, external APIs, or network calls.
