"""Report lane scaffold for safety-gated research outputs."""

from .n_of_1_fabric_plan import (
    NOf1FabricFilePlan,
    NOf1FabricPackPlan,
    build_n_of_1_fabric_pack_plan,
)
from .n_of_1_packet import (
    EXPECTED_N_OF_1_PACKET_ARTIFACTS,
    NOf1ArtifactRef,
    NOf1ReportPacket,
    artifact_payload_sha256,
    build_n_of_1_report_packet,
    collect_n_of_1_artifact_refs,
    collect_n_of_1_optional_artifact_refs,
    collect_n_of_1_sensor_evidence_artifact_refs,
)

STATUS = "scaffolded"

__all__ = [
    "EXPECTED_N_OF_1_PACKET_ARTIFACTS",
    "NOf1ArtifactRef",
    "NOf1FabricFilePlan",
    "NOf1FabricPackPlan",
    "NOf1ReportPacket",
    "STATUS",
    "artifact_payload_sha256",
    "build_n_of_1_fabric_pack_plan",
    "build_n_of_1_report_packet",
    "collect_n_of_1_artifact_refs",
    "collect_n_of_1_optional_artifact_refs",
    "collect_n_of_1_sensor_evidence_artifact_refs",
]
