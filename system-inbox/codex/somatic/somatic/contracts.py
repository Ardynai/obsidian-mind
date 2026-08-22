SUPPORTED_WORKFLOW_MODES = {
    "literature-only",
    "hypothesis-tournament",
    "robin-loop",
    "in-silico-screening",
    "n-of-1",
    "wet-lab-manual",
    "sandbox-lab",
    "wifi-csi-observation",
    "hybrid-clinical",
    "fabric-pack-ingest",
}

REQUIRED_WORKFLOW_FIELDS = (
    "schema_version",
    "id",
    "title",
    "mode",
    "description",
    "version",
    "status",
    "stages",
    "inputs",
    "providers",
    "artifacts",
    "safety_profile",
    "evidence_requirements",
    "output_packet",
)

MOCK_PROVIDER_FILES = {
    "biomodel": "boltz2-provider-mock-config.json",
    "llm": "mock-llm-provider.json",
    "literature": "mock-literature-provider.json",
    "sensor": "mock-sensor-provider.json",
    "report": "mock-report-provider.json",
}
