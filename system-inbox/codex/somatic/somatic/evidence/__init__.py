"""Non-sensor evidence domain modules.

Phase 10A introduces the first non-sensor evidence domain using the same
sanitized artifact-ref pattern as the sensor-evidence subsystem.  Each
domain lives in its own sub-module under ``somatic.evidence`` and reuses
``somatic.evidence.framework`` primitives for deterministic fingerprinting,
compatibility classification, and run-relative SHA-256 artifact refs.
Phase 10F adds a metadata-only document adapter boundary in
``somatic.evidence.document_adapter`` before document evidence packs are built.
"""
