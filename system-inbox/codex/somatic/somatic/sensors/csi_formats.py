from dataclasses import asdict, dataclass, field

CSI_PARSER_ID = "somatic-csi-fixture-parser-v1"
CSI_PARSER_CONTRACT_VERSION = 1
MAX_CSI_FIXTURE_BYTES = 64 * 1024

CSI_PARSER_SUPPORTED_FORMATS = (
    "esp32-csi-csv",
    "amplitude-phase-csv",
    "generic-csi-jsonl",
)

CSI_PARSER_SANITIZED_FORBIDDEN_KEYS = (
    "samples",
    "raw_values",
    "real",
    "imag",
    "amplitude",
    "phase",
    "rssi",
    "source_id",
    "source_ids",
)

CSI_PARSER_CONTRACT = {
    "schema_version": 1,
    "contract_version": CSI_PARSER_CONTRACT_VERSION,
    "parser_id": CSI_PARSER_ID,
    "records": {
        "parsed_file": "in-memory CsiParsedFile with frames retained for local tests",
        "frame": "in-memory CsiFrame with parsed sample tuple",
        "sample": "in-memory CsiSample with parsed numeric values",
        "parse_error": "sanitized CsiParseError with stable code and row metadata",
    },
    "report_fields": [
        "schema_version",
        "contract_version",
        "parser_id",
        "status",
        "path",
        "source_format",
        "rows_seen",
        "frame_count",
        "sample_count",
        "malformed_rows",
        "errors",
        "parse_errors",
        "warnings",
        "truncated",
        "file_size_bytes",
    ],
    "artifacts": {
        "report": "sanitized parser report metadata only",
        "sanitized_summary": "aggregate summary metadata only",
        "evidence_scoring": "deterministic sanitized replay metadata score only",
        "batch_evaluation": "deterministic sanitized fixture-group replay readiness metadata only",
    },
    "status_vocabulary": ["parsed", "partial", "rejected"],
    "privacy": {
        "fixture_only": True,
        "local_file_only": True,
        "summary_output_only": True,
        "forbidden_summary_keys": list(CSI_PARSER_SANITIZED_FORBIDDEN_KEYS),
    },
}

CSI_PARSER_CAPABILITIES = {
    "schema_version": 1,
    "contract_version": CSI_PARSER_CONTRACT_VERSION,
    "parser_id": CSI_PARSER_ID,
    "status": "stable-offline-fixture-parser",
    "dependency_profile": "python-standard-library",
    "supported_formats": list(CSI_PARSER_SUPPORTED_FORMATS),
    "max_fixture_file_size_bytes": MAX_CSI_FIXTURE_BYTES,
    "fixture_only": True,
    "local_file_only": True,
    "summary_output_only": True,
    "raw_signal_processing": False,
    "vital_sign_inference": False,
    "medical_or_clinical_claims": False,
    "no_live_capture": True,
    "no_serial_access": True,
    "no_network_calls": True,
    "no_mqtt_udp_listener": True,
    "no_packet_capture": True,
    "no_monitor_mode": True,
    "no_hardware_access": True,
    "no_medical_or_clinical_claims": True,
}

CSI_PARSER_BOUNDARY_FALSE_FLAGS = {
    "hardware_access": False,
    "network_calls": False,
    "serial_access": False,
    "mqtt_udp_listener": False,
    "packet_capture": False,
    "monitor_mode": False,
    "wifi_network_probing": False,
    "live_capture": False,
    "raw_csi_data_collected": False,
    "raw_csi_data_exported": False,
    "clinical_interpretation": False,
    "medical_or_clinical_claim": False,
}

CSI_PARSER_BOUNDARY_TRUE_FLAGS = {
    "mock": True,
    "offline": True,
    "research_only": True,
    "local_only": True,
    "fixture_only": True,
    "summary_output_only": True,
}


@dataclass(frozen=True)
class CsiParseError:
    row_number: int | None
    line_number: int | None
    code: str
    message: str
    source_format: str
    recoverable: bool = True

    def to_dict(self) -> dict[str, object]:
        return _json_ready(asdict(self))


@dataclass(frozen=True)
class CsiSample:
    sample_index: int
    subcarrier: int | None = None
    amplitude: float | None = None
    phase: float | None = None
    real: float | None = None
    imag: float | None = None
    rssi: float | None = None
    raw_values: tuple[float, ...] = ()
    label: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return _json_ready(asdict(self))

    def to_summary_dict(self) -> dict[str, object]:
        return {
            "sample_index": self.sample_index,
            "subcarrier_present": self.subcarrier is not None,
            "numeric_signal_present": any(
                value is not None for value in (self.amplitude, self.phase, self.real, self.imag)
            )
            or bool(self.raw_values),
            "numeric_component_count": len(self.raw_values),
            "label_present": self.label is not None,
        }


@dataclass(frozen=True)
class CsiFrame:
    frame_id: str
    source_format: str
    timestamp: float | None
    source_id: str
    samples: tuple[CsiSample, ...]
    rssi: float | None = None
    label: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)

    @property
    def sample_count(self) -> int:
        return len(self.samples)

    def to_dict(self) -> dict[str, object]:
        return _json_ready(asdict(self))

    def to_summary_dict(self) -> dict[str, object]:
        return {
            "source_format": self.source_format,
            "timestamp_present": self.timestamp is not None,
            "source_present": bool(self.source_id),
            "sample_count": self.sample_count,
            "label_present": self.label is not None,
            "metadata_key_count": len(self.metadata),
        }


@dataclass(frozen=True)
class CsiParsedFile:
    path: str
    parser_id: str
    source_format: str
    frames: tuple[CsiFrame, ...]
    row_count: int
    malformed_rows: int
    truncated: bool
    max_file_size_bytes: int
    file_size_bytes: int
    errors: tuple[str, ...] = ()
    parse_errors: tuple[CsiParseError, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def frame_count(self) -> int:
        return len(self.frames)

    @property
    def sample_count(self) -> int:
        return sum(frame.sample_count for frame in self.frames)

    def to_dict(self) -> dict[str, object]:
        payload = _json_ready(asdict(self))
        payload["frame_count"] = self.frame_count
        payload["sample_count"] = self.sample_count
        payload.update(CSI_PARSER_BOUNDARY_TRUE_FLAGS)
        payload.update(CSI_PARSER_BOUNDARY_FALSE_FLAGS)
        return payload

    def to_summary_dict(self) -> dict[str, object]:
        payload = {
            "schema_version": 1,
            "contract_version": CSI_PARSER_CONTRACT_VERSION,
            "path": self.path,
            "parser_id": self.parser_id,
            "source_format": self.source_format,
            "row_count": self.row_count,
            "malformed_rows": self.malformed_rows,
            "frame_count": self.frame_count,
            "sample_count": self.sample_count,
            "truncated": self.truncated,
            "max_file_size_bytes": self.max_file_size_bytes,
            "file_size_bytes": self.file_size_bytes,
            "errors": list(self.errors),
            "parse_errors": [error.to_dict() for error in self.parse_errors],
            "warnings": list(self.warnings),
            "source_count": len({frame.source_id for frame in self.frames}),
        }
        payload.update(CSI_PARSER_BOUNDARY_TRUE_FLAGS)
        payload.update(CSI_PARSER_BOUNDARY_FALSE_FLAGS)
        return payload


@dataclass(frozen=True)
class CsiParserReport:
    parser_id: str
    status: str
    path: str
    source_format: str
    rows_seen: int
    frame_count: int
    sample_count: int
    malformed_rows: int
    errors: tuple[str, ...] = ()
    parse_errors: tuple[CsiParseError, ...] = ()
    warnings: tuple[str, ...] = ()
    truncated: bool = False
    max_file_size_bytes: int = MAX_CSI_FIXTURE_BYTES
    file_size_bytes: int = 0
    fixture_count: int = 1

    def to_dict(self) -> dict[str, object]:
        payload = _json_ready(asdict(self))
        payload["schema_version"] = 1
        payload["contract_version"] = CSI_PARSER_CONTRACT_VERSION
        payload.update(CSI_PARSER_BOUNDARY_TRUE_FLAGS)
        payload.update(CSI_PARSER_BOUNDARY_FALSE_FLAGS)
        return payload


def csi_parser_boundary_payload() -> dict[str, object]:
    payload = dict(CSI_PARSER_BOUNDARY_TRUE_FLAGS)
    payload.update(CSI_PARSER_BOUNDARY_FALSE_FLAGS)
    return payload


def _json_ready(value):
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    return value


__all__ = [
    "CSI_PARSER_BOUNDARY_FALSE_FLAGS",
    "CSI_PARSER_BOUNDARY_TRUE_FLAGS",
    "CSI_PARSER_CAPABILITIES",
    "CSI_PARSER_CONTRACT",
    "CSI_PARSER_CONTRACT_VERSION",
    "CSI_PARSER_ID",
    "CSI_PARSER_SANITIZED_FORBIDDEN_KEYS",
    "CSI_PARSER_SUPPORTED_FORMATS",
    "MAX_CSI_FIXTURE_BYTES",
    "CsiFrame",
    "CsiParseError",
    "CsiParsedFile",
    "CsiParserReport",
    "CsiSample",
    "csi_parser_boundary_payload",
]
