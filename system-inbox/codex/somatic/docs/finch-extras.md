# Finch Optional Extras

Phase 5G adds a disabled Finch optional-extras provider scaffold for future
package-backed local analysis. The basic Finch path remains the Phase 5D
standard-library toolbelt.

## Scope

The scaffold tracks availability for:

- `pandas`
- `scipy`
- `numpy`
- `scanpy`
- `biopython` through the `Bio` import name

Availability is detected lazily with `importlib.util.find_spec`. Somatic does
not import those packages, install them, call their APIs, or require them for
the basic install.

## Runtime Boundary

`somatic.analysis.provider.FinchExtrasProvider` returns deterministic
fake-backed metadata:

- provider status is `scaffolded`
- runtime execution is disabled by default
- the standard-library Finch fallback remains active
- network and external runtime surfaces are disabled
- clinical and genomic interpretation are not enabled

Real package-backed analysis is future work. The scaffold fails closed when a
real optional package path is requested before an explicit reviewed runtime path
exists.

## Robin Integration

Robin-loop runs still use Somatic's local Crow/Falcon/Finch shape. Finch writes
the existing standard-library artifacts and adds optional provider status under
`artifacts/finch_toolbelt_summary.json` at `optional_extras`.

This metadata helps future package-backed work see which optional packages are
present locally without changing current behavior.

## Fixtures

Provider metadata lives in:

- `fixtures/providers/finch-extras-provider-placeholder.json`
- `fixtures/providers/finch-extras-provider-mock-config.json`

Both fixtures stay fake-backed, disabled by default, network-free, and
non-clinical.
