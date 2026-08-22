# Evidence Model

Evidence records link Somatic outputs to sources, methods, provenance, limitations, and custody. The evidence model is shared by literature review, hypothesis tournaments, Robin-style loops, in-silico screening, lab planning, sensor observation, fabric ingest, and report packets.

Phase 1A defines the record contract only. It does not implement storage, indexing, retrieval, ranking, or citation formatting.

## Evidence Source Types

Initial `source_type` values:

- `paper`
- `dataset`
- `lab-result`
- `csi-stream`
- `model-output`
- `code-artifact`
- `notebook-artifact`
- `user-note`
- `fabric-pack`

## Required Fields

Every evidence record should include:

- `id`: stable evidence id.
- `schema_version`
- `source_type`
- `title`
- `summary`
- `created_at`
- `observed_at`: when the source observation or result occurred, if known.
- `provenance`
- `confidence`
- `limitations`
- `hashes`
- `chain_of_custody`
- `review_state`

## Provenance

The `provenance` object should include:

- `origin`: source system, publisher, user, instrument, provider, or pack id.
- `retrieved_at`
- `retrieved_by`: provider id or user id reference.
- `workflow_id`
- `run_id`
- `stage_id`
- `source_uri`: optional URI, path, DOI, catalog id, or magnet reference.
- `license`: license or usage terms when known.
- `permissions`: any consent, license, or access constraints.

## Citation Metadata

Papers, datasets, and packs should include `citation` when available:

- `authors`
- `title`
- `venue`
- `year`
- `doi`
- `url`
- `publisher`
- `version`

Citation metadata is descriptive. It is not a trust guarantee.

## Confidence

The `confidence` object should include:

- `level`: `low`, `medium`, `high`, or `unknown`.
- `score`: optional number between `0` and `1`.
- `rationale`: short explanation.
- `method`: human review, model estimate, instrument calibration, peer review, replication, or fixture.

Confidence must not be presented as clinical certainty.

## Limitations

The `limitations` array should list known weaknesses, assumptions, missing data, conflicts, and applicability boundaries. Report packets should preserve these limitations.

## Hashes and Digests

Evidence records should include digests when content is file-backed or pack-backed:

- `sha256`: hex digest for the canonical file or payload.
- `content_hash`: optional higher-level digest for normalized content.
- `signature_ref`: optional signature or pack signature reference.
- `hash_scope`: `file`, `payload`, `manifest`, `directory`, or `unknown`.

## Chain of Custody

The `chain_of_custody` array should record custody events:

- `event`: `created`, `retrieved`, `verified`, `transformed`, `reviewed`, `exported`, or `archived`.
- `at`: timestamp.
- `actor`: user, provider, instrument, or system reference.
- `input_hash`
- `output_hash`
- `notes`

Custody records should be append-only in future implementations.

## Review State

Evidence review state should be one of:

- `unreviewed`
- `machine-reviewed`
- `human-reviewed`
- `rejected`
- `superseded`

Health-related and lab-facing reports should clearly identify which evidence has been reviewed by qualified humans.
