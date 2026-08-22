import hashlib
import json

from somatic.evidence_bus import MeasurementPlan, RawEvidence


class SandboxEvidenceSource:
    """Deterministic offline EvidenceSource for the Robin-shaped loop."""

    supported_modalities = ("literature", "sim", "wetlab")

    def acquire(self, measurement_plan: MeasurementPlan):
        records = []
        for index, source in enumerate(measurement_plan.sources, start=1):
            if source.modality not in self.supported_modalities:
                raise ValueError(f"Unsupported sandbox modality: {source.modality}")
            payload = _payload_for_modality(source.modality, measurement_plan.objective)
            digest = _stable_hash(
                {
                    "plan_id": measurement_plan.id,
                    "source_id": source.id,
                    "modality": source.modality,
                    "payload": payload,
                }
            )
            records.append(
                RawEvidence(
                    id=f"raw-robin-{index:03d}-{source.modality}",
                    source=source,
                    payload_ref=f"sandbox://{measurement_plan.id}/{source.modality}",
                    sha256=digest,
                    metadata={
                        "mock": True,
                        "offline": True,
                        "boundary": "mock/offline/research-only",
                        "payload": payload,
                    },
                )
            )
        return records


def _payload_for_modality(modality, objective):
    payloads = {
        "literature": {
            "record_type": "mock-literature-context",
            "context_count": 2,
            "objective_echo": objective,
            "observations": [
                "Local fixture records describe provenance and safety constraints.",
                "No external literature search, PaperQA2, or FutureHouse Robin runtime was used.",
            ],
        },
        "sim": {
            "record_type": "mock-simulation-measurement",
            "sample_count": 12,
            "mock_signal_mean": 0.42,
            "mock_signal_units": "sandbox-score",
            "interpretation_boundary": "Signal is synthetic and only checks pipeline wiring.",
            "table_refs": [
                {
                    "path": "fixtures/evidence/tables/dose-response.csv",
                    "role": "dose-response",
                }
            ],
        },
        "wetlab": {
            "record_type": "mock-wetlab-observation",
            "sample_count": 3,
            "real_wetlab_action_performed": False,
            "mock_observation": "Fixture-only wetlab placeholder retained for Evidence Bus shape.",
            "table_refs": [
                {
                    "path": "fixtures/evidence/tables/simple-lab-results.csv",
                    "role": "table-profile",
                }
            ],
        },
    }
    return payloads[modality]


def _stable_hash(payload):
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
