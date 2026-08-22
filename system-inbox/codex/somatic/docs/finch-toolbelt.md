# Finch Toolbelt

Phase 5D expands Finch from a mock analyzer into a deterministic local analysis
toolbelt for sandbox evidence. Phase 5G adds disabled optional-extras status
metadata for future package-backed analysis. The active toolbelt still uses
only the Python standard library and keeps all outputs mock, offline,
research-only, and unsuitable for clinical or scientific conclusions.

## Scope

The toolbelt currently supports:

- CSV parsing with `csv`.
- Table schema and column summaries.
- Missing value counts.
- Numeric column detection.
- Descriptive statistics: count, min, max, mean, median, and sample standard
  deviation when enough values exist.
- Simple categorical group summaries.
- Preliminary dose-response table summaries.
- Deterministic artifact and file hashing with SHA-256.
- Analysis provenance records.
- Optional package availability metadata for future Finch extras.

It does not import or execute pandas, scipy, numpy, scanpy, biopython, RDKit, or
any other third-party analysis package. Those remain future optional extras and
must not become required for the basic install.

## Modules

- `somatic.analysis.tables`: CSV loading and table profiling.
- `somatic.analysis.statistics`: numeric parsing, descriptive stats, and
  group-by summaries.
- `somatic.analysis.dose_response`: preliminary sorted dose/response summary.
- `somatic.analysis.provenance`: deterministic SHA-256 provenance helpers.
- `somatic.analysis.extras`: lazy optional package availability metadata.
- `somatic.analysis.provider`: disabled fake-backed Finch extras provider.
- `somatic.agents.finch_toolbelt`: Robin-loop adapter over local table refs in
  sandbox raw evidence.

## Robin Outputs

When `robin-loop` sandbox evidence includes local table references, Finch writes:

- `artifacts/finch_toolbelt_summary.json`
- `artifacts/table_profile.json`
- `artifacts/dose_response_summary.json`
- `artifacts/analysis_provenance.json`

These artifacts are deterministic research artifacts. They summarize local
fixtures only. They are not medical advice, not clinical evidence, and not real
scientific conclusions.

`artifacts/finch_toolbelt_summary.json` also includes an `optional_extras`
object with lazy availability status for pandas, scipy, numpy, scanpy, and
biopython. This is status metadata only. It does not enable package-backed
analysis.

## Dose-Response Boundary

The dose-response helper sorts rows by numeric dose, records numeric response
points, computes a trend direction, computes the baseline-vs-highest-dose delta,
and emits a short interpretation string. It does not fit curves, estimate
confidence intervals, calculate potency, make efficacy claims, or validate a
lab result.

Real lab/scientific validation, richer statistics, and package-backed analysis
remain future work behind explicit optional extras, safety review, provenance
records, and user configuration.

See [finch-extras.md](finch-extras.md) for the Phase 5G provider scaffold.
