# Evidence And Documents

## Owns

Sanitized evidence contracts and metadata-only document fixture handling:

- `somatic/evidence_bus/`
- `somatic/evidence/framework.py`
- `somatic/evidence/document_adapter.py`
- `somatic/evidence/document_evidence_pack.py`
- `fixtures/evidence/`

## Main Flow

Evidence Bus types provide the common `EvidenceSource`, `RawEvidence`, and `StructuredVerdict` shape. Document fixtures use a narrower metadata-only adapter boundary before building an evidence pack.

The document path validates that adapter output is count/status metadata only. Unsafe fields such as raw document bodies, paths, URLs, credentials, source IDs, and raw text are rejected before evidence-pack metadata is emitted.

## Gotchas

- The document adapter contract is narrower than the evidence-pack contract by design.
- Sanitization is part of the public API. Do not add raw fixture refs, paths, URLs, source IDs, or document bodies to public reports.
- Document evidence reuses the sensor-evidence artifact-ref pattern even though it is not a sensor.

## Start Reading

Start with the module comments in `somatic/evidence/document_adapter.py` and `somatic/evidence/document_evidence_pack.py`, then read `tests/test_document_adapter_contract.py` and `tests/test_document_evidence_pack.py`.
