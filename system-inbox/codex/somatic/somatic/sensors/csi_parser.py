import csv
import json
import math
import re
from pathlib import Path

from .csi_formats import (
    CSI_PARSER_BOUNDARY_FALSE_FLAGS,
    CSI_PARSER_BOUNDARY_TRUE_FLAGS,
    CSI_PARSER_CAPABILITIES,
    CSI_PARSER_CONTRACT_VERSION,
    CSI_PARSER_ID,
    CSI_PARSER_SUPPORTED_FORMATS,
    MAX_CSI_FIXTURE_BYTES,
    CsiFrame,
    CsiParsedFile,
    CsiParseError,
    CsiParserReport,
    CsiSample,
)
from .csi_scoring import score_csi_replay_evidence

CSI_FIXTURE_ROOT = Path("fixtures") / "sensors" / "csi"
SUPPORTED_CSI_FIXTURE_EXTENSIONS = (".csv", ".jsonl")
DEFAULT_N_OF_1_CSI_FIXTURE_REFS = (
    "fixture://sensors/csi/sample-esp32-csi.csv",
    "fixture://sensors/csi/csi-tabular-fixture.csv",
    "fixture://sensors/csi/sample-csi-jsonl.jsonl",
)
CSI_PUBLIC_SOURCE_FORMAT_LABELS = {
    "esp32-csi-csv": "csi-csv-fixture",
    "amplitude-phase-csv": "csi-tabular-fixture",
    "generic-csi-jsonl": "csi-jsonl-fixture",
    "unsupported-extension": "unsupported-fixture-extension",
    "unknown": "unknown-fixture-format",
}
CSI_PUBLIC_IDENTIFIER_FORBIDDEN_TERMS = (
    "raw_values",
    "real",
    "imag",
    "amplitude",
    "phase",
    "rssi",
    "source_id",
    "source_ids",
)


def resolve_csi_fixture_path(ref: str, repo_root: str | Path | None = None) -> Path:
    raw_ref = str(ref)
    if Path(raw_ref).is_absolute():
        raise ValueError("absolute CSI fixture refs are not allowed")
    if "://" in raw_ref and not raw_ref.startswith("fixture://"):
        raise ValueError("unsafe CSI fixture ref scheme")
    if raw_ref.startswith("fixture://"):
        raw_ref = raw_ref.removeprefix("fixture://")
        prefix = "sensors/csi/"
        if not raw_ref.startswith(prefix):
            raise ValueError("unsafe CSI fixture ref outside sensors/csi")
        raw_ref = raw_ref.removeprefix(prefix)
    relative = Path(raw_ref)
    if any(part in ("", ".", "..") for part in relative.parts):
        raise ValueError("unsafe CSI fixture ref path")
    if len(relative.parts) != 1:
        raise ValueError("unsafe CSI fixture ref path")
    root = Path(repo_root) if repo_root else Path.cwd()
    fixture_root = (root / CSI_FIXTURE_ROOT).resolve()
    resolved = (fixture_root / relative).resolve()
    try:
        resolved.relative_to(fixture_root)
    except ValueError as exc:
        raise ValueError("unsafe CSI fixture ref path") from exc
    return resolved


def parse_csi_fixture(
    ref: str,
    repo_root: str | Path | None = None,
    max_file_size_bytes: int = MAX_CSI_FIXTURE_BYTES,
) -> tuple[CsiParsedFile, CsiParserReport]:
    path = resolve_csi_fixture_path(ref, repo_root=repo_root)
    return parse_csi_file(
        path,
        repo_root=repo_root,
        max_file_size_bytes=max_file_size_bytes,
    )


def parse_csi_file(
    path: str | Path,
    source_format: str | None = None,
    repo_root: str | Path | None = None,
    max_file_size_bytes: int = MAX_CSI_FIXTURE_BYTES,
) -> tuple[CsiParsedFile, CsiParserReport]:
    raw_path = str(path)
    root = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()
    fixture_root = (root / CSI_FIXTURE_ROOT).resolve()
    if _looks_remote(raw_path):
        return _rejected_file(
            path="<remote-csi-path>",
            source_format=source_format or "unknown",
            error="remote CSI paths are not allowed",
            error_code="remote_path_rejected",
            max_file_size_bytes=max_file_size_bytes,
        )
    resolved = Path(path).resolve()
    if not _is_csi_fixture_path(resolved, fixture_root):
        return _rejected_file(
            path=_safe_path(resolved, root),
            source_format=source_format or "unknown",
            error="CSI parser only accepts fixtures/sensors/csi files",
            error_code="outside_fixture_root",
            max_file_size_bytes=max_file_size_bytes,
        )
    if not resolved.exists() or not resolved.is_file():
        return _rejected_file(
            path=_safe_path(resolved, root),
            source_format=source_format or "unknown",
            error="CSI fixture file does not exist",
            error_code="fixture_missing",
            max_file_size_bytes=max_file_size_bytes,
        )
    raw_file_size = resolved.stat().st_size
    if raw_file_size > max_file_size_bytes:
        return _rejected_file(
            path=_safe_path(resolved, root),
            source_format=source_format or "unknown",
            error="CSI fixture file exceeds maximum size",
            error_code="fixture_too_large",
            max_file_size_bytes=max_file_size_bytes,
            file_size_bytes=raw_file_size,
            truncated=True,
        )
    if resolved.suffix.lower() not in SUPPORTED_CSI_FIXTURE_EXTENSIONS:
        return _rejected_file(
            path=_safe_path(resolved, root),
            source_format="unsupported-extension",
            error="unsupported CSI fixture file extension",
            error_code="unsupported_extension",
            max_file_size_bytes=max_file_size_bytes,
            file_size_bytes=raw_file_size,
        )
    try:
        text = resolved.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return _rejected_file(
            path=_safe_path(resolved, root),
            source_format=source_format or "unknown",
            error="CSI fixture file could not be read as UTF-8 text",
            error_code="fixture_read_failed",
            max_file_size_bytes=max_file_size_bytes,
            file_size_bytes=raw_file_size,
        )
    file_size = _normalized_text_size_bytes(text)
    detected_format = source_format or _detect_source_format(resolved, text)
    if detected_format == "esp32-csi-csv":
        parsed, report = _parse_esp32_csv(
            resolved,
            text,
            repo_root=root,
            max_file_size_bytes=max_file_size_bytes,
            file_size_bytes=file_size,
        )
    elif detected_format == "amplitude-phase-csv":
        parsed, report = _parse_amplitude_phase_csv(
            resolved,
            text,
            repo_root=root,
            max_file_size_bytes=max_file_size_bytes,
            file_size_bytes=file_size,
        )
    elif detected_format == "generic-csi-jsonl":
        parsed, report = _parse_jsonl(
            resolved,
            text,
            repo_root=root,
            max_file_size_bytes=max_file_size_bytes,
            file_size_bytes=file_size,
        )
    else:
        parsed, report = _rejected_file(
            path=_safe_path(resolved, root),
            source_format=detected_format,
            error="unsupported CSI fixture format",
            error_code="unsupported_format",
            max_file_size_bytes=max_file_size_bytes,
            file_size_bytes=file_size,
        )
    return parsed, report


def _normalized_text_size_bytes(text: str) -> int:
    return len(text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8"))


def build_csi_parser_artifacts(
    fixture_refs: tuple[str, ...] | list[str],
    repo_root: str | Path | None = None,
    max_file_size_bytes: int = MAX_CSI_FIXTURE_BYTES,
) -> tuple[dict[str, object], dict[str, object]]:
    parsed_files = []
    reports = []
    for ref in fixture_refs:
        try:
            parsed, report = parse_csi_fixture(
                ref,
                repo_root=repo_root,
                max_file_size_bytes=max_file_size_bytes,
            )
        except ValueError as exc:
            parsed, report = _rejected_file(
                path="<unsafe-csi-fixture-ref>",
                source_format="unknown",
                error=str(exc),
                error_code="unsafe_fixture_ref",
                max_file_size_bytes=max_file_size_bytes,
            )
        parsed_files.append(parsed)
        reports.append(report)

    source_formats = sorted(
        {_public_source_format_label(parsed.source_format) for parsed in parsed_files}
    )
    total_malformed = sum(report.malformed_rows for report in reports)
    total_frames = sum(parsed.frame_count for parsed in parsed_files)
    total_samples = sum(parsed.sample_count for parsed in parsed_files)
    status = "parsed"
    if total_malformed and total_frames:
        status = "partial"
    elif total_malformed or not total_frames:
        status = "rejected"
    errors = [_public_message(error) for report in reports for error in report.errors]
    parse_errors = [
        _public_parse_error(error) for report in reports for error in report.parse_errors
    ]
    warnings = [_public_message(warning) for report in reports for warning in report.warnings]
    status_counts = _aggregate_status_counts(reports)
    report_payload = {
        "schema_version": 1,
        "contract_version": CSI_PARSER_CONTRACT_VERSION,
        "id": "csi-parser-report",
        "parser_id": CSI_PARSER_ID,
        "status": status,
        "fixture_count": len(parsed_files),
        "fixture_refs": [
            _public_fixture_ref(ref, index) for index, ref in enumerate(fixture_refs, start=1)
        ],
        "source_formats": source_formats,
        "rows_seen": sum(report.rows_seen for report in reports),
        "frame_count": total_frames,
        "sample_count": total_samples,
        "malformed_rows": total_malformed,
        "status_counts": dict(status_counts),
        "errors": errors,
        "parse_errors": parse_errors,
        "warnings": warnings,
        "capabilities": _public_capabilities(max_file_size_bytes),
        "fixtures": [
            _public_report_payload(report, index) for index, report in enumerate(reports, start=1)
        ],
        "scope": "local fake/sample fixtures only",
    }
    report_payload.update(CSI_PARSER_BOUNDARY_TRUE_FLAGS)
    report_payload.update(CSI_PARSER_BOUNDARY_FALSE_FLAGS)

    summary_payload = {
        "schema_version": 1,
        "contract_version": CSI_PARSER_CONTRACT_VERSION,
        "id": "csi-parsed-summary",
        "parser_id": CSI_PARSER_ID,
        "status": status,
        "fixture_count": len(parsed_files),
        "fixture_refs": [
            _public_fixture_ref(ref, index) for index, ref in enumerate(fixture_refs, start=1)
        ],
        "source_formats": source_formats,
        "frame_count": total_frames,
        "sample_count": total_samples,
        "malformed_rows": total_malformed,
        "status_counts": dict(status_counts),
        "files": [
            _public_parsed_summary(parsed, index)
            for index, parsed in enumerate(parsed_files, start=1)
        ],
        "scope": "summary-only parser metadata; no signal processing output",
    }
    summary_payload.update(CSI_PARSER_BOUNDARY_TRUE_FLAGS)
    summary_payload.update(CSI_PARSER_BOUNDARY_FALSE_FLAGS)
    scoring_payload = score_csi_replay_evidence(report_payload, summary_payload)
    report_payload["csi_evidence_scoring"] = dict(scoring_payload)
    summary_payload["csi_evidence_scoring"] = dict(scoring_payload)
    return report_payload, summary_payload


def _parse_esp32_csv(
    path: Path,
    text: str,
    *,
    repo_root: Path,
    max_file_size_bytes: int,
    file_size_bytes: int,
) -> tuple[CsiParsedFile, CsiParserReport]:
    rows = [row for row in csv.reader(text.splitlines()) if any(cell.strip() for cell in row)]
    if not rows:
        return _rejected_file(
            path=_safe_path(path, repo_root),
            source_format="esp32-csi-csv",
            error="empty CSI fixture",
            error_code="empty_fixture",
            max_file_size_bytes=max_file_size_bytes,
            file_size_bytes=file_size_bytes,
        )
    header = None
    data_rows = rows
    first = [cell.strip().lower() for cell in rows[0]]
    if "csi_data" in first or "csi" in first or "type" in first:
        header = first
        data_rows = rows[1:]
    warnings = _unknown_column_warnings(
        header,
        {
            "type",
            "frame_id",
            "id",
            "timestamp",
            "source",
            "mac",
            "rssi",
            "csi_data",
            "csi",
            "data",
            "label",
        },
    )
    frames = []
    errors = []
    for offset, row in enumerate(data_rows, start=2 if header else 1):
        row_map = _row_map(header, row)
        row_type = (row_map.get("type") or (row[0] if row else "")).strip()
        if row_type != "CSI_DATA":
            errors.append(
                _parse_error(
                    row_number=offset,
                    line_number=offset,
                    code="record_marker_missing",
                    message=f"row {offset} malformed: expected fixture record marker",
                    source_format="esp32-csi-csv",
                )
            )
            continue
        vector_text = (
            row_map.get("csi_data")
            or row_map.get("csi")
            or row_map.get("data")
            or _first_bracketed_cell(row)
        )
        values = _parse_numeric_vector(vector_text)
        if len(values) < 2 or len(values) % 2:
            errors.append(
                _parse_error(
                    row_number=offset,
                    line_number=offset,
                    code="invalid_vector_length",
                    message=f"row {offset} malformed: fixture vector length is invalid",
                    source_format="esp32-csi-csv",
                )
            )
            continue
        frame_id = row_map.get("frame_id") or row_map.get("id") or str(len(frames) + 1)
        timestamp = _optional_float(row_map.get("timestamp"))
        source_id = row_map.get("source") or row_map.get("mac") or "esp32-fixture"
        rssi = _optional_float(row_map.get("rssi"))
        label = row_map.get("label") or None
        samples = []
        for sample_index, index in enumerate(range(0, len(values), 2)):
            real = float(values[index])
            imag = float(values[index + 1])
            samples.append(
                CsiSample(
                    sample_index=sample_index,
                    real=real,
                    imag=imag,
                    amplitude=round(math.hypot(real, imag), 6),
                    phase=round(math.atan2(imag, real), 6),
                    rssi=rssi,
                    raw_values=(real, imag),
                    label=label,
                    metadata={"pair_order": "real-imag"},
                )
            )
        frames.append(
            CsiFrame(
                frame_id=str(frame_id),
                source_format="esp32-csi-csv",
                timestamp=timestamp,
                source_id=str(source_id),
                rssi=rssi,
                label=label,
                samples=tuple(samples),
                metadata={"row_number": offset, "row_marker": "CSI_DATA"},
            )
        )
    return _parsed_with_report(
        path=path,
        source_format="esp32-csi-csv",
        frames=tuple(frames),
        row_count=len(data_rows),
        parse_errors=tuple(errors),
        warnings=warnings,
        repo_root=repo_root,
        max_file_size_bytes=max_file_size_bytes,
        file_size_bytes=file_size_bytes,
    )


def _parse_amplitude_phase_csv(
    path: Path,
    text: str,
    *,
    repo_root: Path,
    max_file_size_bytes: int,
    file_size_bytes: int,
) -> tuple[CsiParsedFile, CsiParserReport]:
    reader = csv.DictReader(line for line in text.splitlines() if line.strip())
    rows = list(reader)
    frames_by_id = {}
    frame_order = []
    errors = []
    warnings = _unknown_column_warnings(
        reader.fieldnames,
        {
            "frame_id",
            "id",
            "timestamp",
            "source",
            "label",
            "subcarrier",
            "amplitude",
            "phase",
        },
    )
    for offset, row in enumerate(rows, start=2):
        frame_id = (row.get("frame_id") or "").strip()
        amplitude = _required_float(row.get("amplitude"))
        phase = _required_float(row.get("phase"))
        if not frame_id or amplitude is None or phase is None:
            errors.append(
                _parse_error(
                    row_number=offset,
                    line_number=offset,
                    code="required_fields_missing",
                    message=f"row {offset} malformed: required fixture fields missing",
                    source_format="amplitude-phase-csv",
                )
            )
            continue
        timestamp = _optional_float(row.get("timestamp"))
        source_id = row.get("source") or "amplitude-phase-fixture"
        label = row.get("label") or None
        subcarrier = _optional_int(row.get("subcarrier"))
        sample = CsiSample(
            sample_index=len(frames_by_id.get(frame_id, [])),
            subcarrier=subcarrier,
            amplitude=amplitude,
            phase=phase,
            label=label,
        )
        if frame_id not in frames_by_id:
            frame_order.append((frame_id, timestamp, source_id, label))
            frames_by_id[frame_id] = []
        frames_by_id[frame_id].append(sample)
    frames = tuple(
        CsiFrame(
            frame_id=str(frame_id),
            source_format="amplitude-phase-csv",
            timestamp=timestamp,
            source_id=str(source_id),
            label=label,
            samples=tuple(frames_by_id[frame_id]),
            metadata={"amplitude_phase_rows": len(frames_by_id[frame_id])},
        )
        for frame_id, timestamp, source_id, label in frame_order
    )
    return _parsed_with_report(
        path=path,
        source_format="amplitude-phase-csv",
        frames=frames,
        row_count=len(rows),
        parse_errors=tuple(errors),
        warnings=warnings,
        repo_root=repo_root,
        max_file_size_bytes=max_file_size_bytes,
        file_size_bytes=file_size_bytes,
    )


def _parse_jsonl(
    path: Path,
    text: str,
    *,
    repo_root: Path,
    max_file_size_bytes: int,
    file_size_bytes: int,
) -> tuple[CsiParsedFile, CsiParserReport]:
    frames = []
    errors = []
    lines = [line for line in text.splitlines() if line.strip()]
    for offset, line in enumerate(lines, start=1):
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            errors.append(
                _parse_error(
                    row_number=offset,
                    line_number=offset,
                    code="json_object_required",
                    message=f"row {offset} malformed: JSON object required",
                    source_format="generic-csi-jsonl",
                )
            )
            continue
        if not isinstance(item, dict):
            errors.append(
                _parse_error(
                    row_number=offset,
                    line_number=offset,
                    code="json_object_required",
                    message=f"row {offset} malformed: JSON object required",
                    source_format="generic-csi-jsonl",
                )
            )
            continue
        frame_id = item.get("frame_id") or item.get("id") or str(len(frames) + 1)
        timestamp = _optional_float(item.get("timestamp"))
        source_id = item.get("source") or item.get("mac") or "jsonl-fixture"
        rssi = _optional_float(item.get("rssi"))
        label = item.get("label") if isinstance(item.get("label"), str) else None
        samples = _json_samples(item, rssi=rssi, label=label)
        if not samples:
            errors.append(
                _parse_error(
                    row_number=offset,
                    line_number=offset,
                    code="record_payload_missing",
                    message=f"row {offset} malformed: record payload required",
                    source_format="generic-csi-jsonl",
                )
            )
            continue
        metadata = {
            "row_number": offset,
            "record_type": item.get("type", "CSI_DATA"),
        }
        if isinstance(item.get("activity_label"), str):
            metadata["activity_label"] = item["activity_label"]
        frames.append(
            CsiFrame(
                frame_id=str(frame_id),
                source_format="generic-csi-jsonl",
                timestamp=timestamp,
                source_id=str(source_id),
                rssi=rssi,
                label=label,
                samples=tuple(samples),
                metadata=metadata,
            )
        )
    return _parsed_with_report(
        path=path,
        source_format="generic-csi-jsonl",
        frames=tuple(frames),
        row_count=len(lines),
        parse_errors=tuple(errors),
        warnings=(),
        repo_root=repo_root,
        max_file_size_bytes=max_file_size_bytes,
        file_size_bytes=file_size_bytes,
    )


def _json_samples(
    item: dict[str, object],
    *,
    rssi: float | None,
    label: str | None,
) -> tuple[CsiSample, ...]:
    raw_samples = item.get("samples")
    if isinstance(raw_samples, list):
        samples = []
        for index, sample in enumerate(raw_samples):
            if not isinstance(sample, dict):
                continue
            real = _optional_float(sample.get("real"))
            imag = _optional_float(sample.get("imag"))
            amplitude = _optional_float(sample.get("amplitude"))
            phase = _optional_float(sample.get("phase"))
            if amplitude is None and real is not None and imag is not None:
                amplitude = round(math.hypot(real, imag), 6)
            if phase is None and real is not None and imag is not None:
                phase = round(math.atan2(imag, real), 6)
            if amplitude is None and phase is None and real is None and imag is None:
                continue
            samples.append(
                CsiSample(
                    sample_index=index,
                    subcarrier=_optional_int(sample.get("subcarrier")),
                    amplitude=amplitude,
                    phase=phase,
                    real=real,
                    imag=imag,
                    rssi=rssi,
                    raw_values=tuple(value for value in (real, imag) if value is not None),
                    label=label,
                )
            )
        return tuple(samples)
    vector = item.get("csi") or item.get("csi_data") or item.get("data")
    if isinstance(vector, list):
        values = [_required_float(value) for value in vector]
        if any(value is None for value in values) or len(values) < 2 or len(values) % 2:
            return ()
        samples = []
        for sample_index, index in enumerate(range(0, len(values), 2)):
            real = float(values[index])
            imag = float(values[index + 1])
            samples.append(
                CsiSample(
                    sample_index=sample_index,
                    real=real,
                    imag=imag,
                    amplitude=round(math.hypot(real, imag), 6),
                    phase=round(math.atan2(imag, real), 6),
                    rssi=rssi,
                    raw_values=(real, imag),
                    label=label,
                    metadata={"pair_order": "real-imag"},
                )
            )
        return tuple(samples)
    return ()


def _parsed_with_report(
    *,
    path: Path,
    source_format: str,
    frames: tuple[CsiFrame, ...],
    row_count: int,
    parse_errors: tuple[CsiParseError, ...],
    warnings: tuple[str, ...],
    repo_root: Path,
    max_file_size_bytes: int,
    file_size_bytes: int,
) -> tuple[CsiParsedFile, CsiParserReport]:
    errors = tuple(error.message for error in parse_errors)
    status = "parsed"
    if errors and frames:
        status = "partial"
    elif errors or not frames:
        status = "rejected"
    parsed = CsiParsedFile(
        path=_safe_path(path, repo_root),
        parser_id=CSI_PARSER_ID,
        source_format=source_format,
        frames=frames,
        row_count=row_count,
        malformed_rows=len(errors),
        truncated=False,
        max_file_size_bytes=max_file_size_bytes,
        file_size_bytes=file_size_bytes,
        errors=errors,
        parse_errors=parse_errors,
        warnings=warnings,
    )
    report = CsiParserReport(
        parser_id=CSI_PARSER_ID,
        status=status,
        path=_safe_path(path, repo_root),
        source_format=source_format,
        rows_seen=row_count,
        frame_count=parsed.frame_count,
        sample_count=parsed.sample_count,
        malformed_rows=len(errors),
        errors=errors,
        parse_errors=parse_errors,
        warnings=warnings,
        max_file_size_bytes=max_file_size_bytes,
        file_size_bytes=file_size_bytes,
    )
    return parsed, report


def _rejected_file(
    *,
    path: str,
    source_format: str,
    error: str,
    error_code: str,
    max_file_size_bytes: int,
    file_size_bytes: int = 0,
    truncated: bool = False,
) -> tuple[CsiParsedFile, CsiParserReport]:
    parse_error = _parse_error(
        row_number=None,
        line_number=None,
        code=error_code,
        message=error,
        source_format=source_format,
        recoverable=False,
    )
    parsed = CsiParsedFile(
        path=path,
        parser_id=CSI_PARSER_ID,
        source_format=source_format,
        frames=(),
        row_count=0,
        malformed_rows=1,
        truncated=truncated,
        max_file_size_bytes=max_file_size_bytes,
        file_size_bytes=file_size_bytes,
        errors=(error,),
        parse_errors=(parse_error,),
    )
    report = CsiParserReport(
        parser_id=CSI_PARSER_ID,
        status="rejected",
        path=path,
        source_format=source_format,
        rows_seen=0,
        frame_count=0,
        sample_count=0,
        malformed_rows=1,
        errors=(error,),
        parse_errors=(parse_error,),
        truncated=truncated,
        max_file_size_bytes=max_file_size_bytes,
        file_size_bytes=file_size_bytes,
    )
    return parsed, report


def _detect_source_format(path: Path, text: str) -> str:
    if path.suffix.lower() == ".jsonl":
        return "generic-csi-jsonl"
    first_line = text.splitlines()[0].lower() if text.splitlines() else ""
    if "csi_data" in first_line or first_line.startswith("csi_data"):
        return "esp32-csi-csv"
    if "amplitude" in first_line and "phase" in first_line:
        return "amplitude-phase-csv"
    return "unknown"


def _parse_error(
    *,
    row_number: int | None,
    line_number: int | None,
    code: str,
    message: str,
    source_format: str,
    recoverable: bool = True,
) -> CsiParseError:
    return CsiParseError(
        row_number=row_number,
        line_number=line_number,
        code=code,
        message=message,
        source_format=source_format,
        recoverable=recoverable,
    )


def _public_source_format_label(source_format: str) -> str:
    return CSI_PUBLIC_SOURCE_FORMAT_LABELS.get(source_format, "unknown-fixture-format")


def _public_fixture_ref(ref: object, index: int) -> str:
    text = str(ref)
    if _unsafe_public_ref(text) or _contains_public_forbidden_term(text):
        return f"csi-fixture-{index:03d}{_public_suffix(text)}"
    return text


def _public_fixture_path(path: object, index: int) -> str:
    text = str(path)
    if _unsafe_public_ref(text) or _contains_public_forbidden_term(text):
        return f"fixtures/sensors/csi/csi-fixture-{index:03d}{_public_suffix(text)}"
    return text


def _public_suffix(value: str) -> str:
    suffix = Path(value).suffix.lower()
    if suffix in SUPPORTED_CSI_FIXTURE_EXTENSIONS or suffix in {".npz", ".pcap"}:
        return suffix
    return ""


def _contains_public_forbidden_term(value: str) -> bool:
    lowered = value.lower()
    return any(term in lowered for term in CSI_PUBLIC_IDENTIFIER_FORBIDDEN_TERMS)


def _unsafe_public_ref(value: str) -> bool:
    if _looks_remote(value):
        return True
    if Path(value).is_absolute():
        return True
    if "://" in value and not value.startswith("fixture://"):
        return True
    return any(part in ("", ".", "..") for part in Path(value).parts)


def _public_message(message: str) -> str:
    if _contains_public_forbidden_term(str(message)):
        return "CSI fixture parser reviewed a malformed local fixture row"
    return str(message)


def _public_parse_error(error: CsiParseError) -> dict[str, object]:
    payload = error.to_dict()
    payload["message"] = _public_message(str(payload.get("message", "")))
    payload["source_format"] = _public_source_format_label(
        str(payload.get("source_format", "unknown"))
    )
    return payload


def _public_report_payload(report: CsiParserReport, index: int) -> dict[str, object]:
    payload = report.to_dict()
    payload["path"] = _public_fixture_path(payload.get("path", ""), index)
    payload["source_format"] = _public_source_format_label(report.source_format)
    payload["errors"] = [_public_message(error) for error in report.errors]
    payload["parse_errors"] = [_public_parse_error(error) for error in report.parse_errors]
    payload["warnings"] = [_public_message(warning) for warning in report.warnings]
    return payload


def _public_parsed_summary(parsed: CsiParsedFile, index: int) -> dict[str, object]:
    payload = parsed.to_summary_dict()
    payload["path"] = _public_fixture_path(payload.get("path", ""), index)
    payload["source_format"] = _public_source_format_label(parsed.source_format)
    payload["errors"] = [_public_message(error) for error in parsed.errors]
    payload["parse_errors"] = [_public_parse_error(error) for error in parsed.parse_errors]
    payload["warnings"] = [_public_message(warning) for warning in parsed.warnings]
    return payload


def _public_capabilities(max_file_size_bytes: int) -> dict[str, object]:
    payload = dict(CSI_PARSER_CAPABILITIES)
    payload["supported_formats"] = [
        _public_source_format_label(source_format) for source_format in CSI_PARSER_SUPPORTED_FORMATS
    ]
    payload["max_fixture_file_size_bytes"] = max_file_size_bytes
    return payload


def _aggregate_status_counts(reports: list[CsiParserReport]) -> dict[str, int]:
    counts = {"parsed": 0, "partial": 0, "rejected": 0}
    for report in reports:
        status = report.status if report.status in counts else "rejected"
        counts[status] += 1
    return counts


def _unknown_column_warnings(
    header: list[str] | None,
    allowed_columns: set[str],
) -> tuple[str, ...]:
    if not header:
        return ()
    unknown_count = sum(
        1 for column in header if column and column.strip().lower() not in allowed_columns
    )
    if not unknown_count:
        return ()
    return (f"ignored {unknown_count} unknown fixture columns",)


def _row_map(header: list[str] | None, row: list[str]) -> dict[str, str]:
    if not header:
        return {}
    return {header[index]: row[index].strip() for index in range(min(len(header), len(row)))}


def _first_bracketed_cell(row: list[str]) -> str:
    for cell in row:
        if "[" in cell and "]" in cell:
            return cell
    return ""


def _parse_numeric_vector(value: object) -> tuple[float, ...]:
    if not isinstance(value, str):
        return ()
    return tuple(float(item) for item in re.findall(r"-?\d+(?:\.\d+)?", value))


def _required_float(value: object) -> float | None:
    try:
        if value is None or str(value).strip() == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _optional_float(value: object) -> float | None:
    return _required_float(value)


def _optional_int(value: object) -> int | None:
    try:
        if value is None or str(value).strip() == "":
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _looks_remote(value: str) -> bool:
    lowered = value.lower()
    return lowered.startswith(("http://", "https://", "ftp://", "ws://", "wss://"))


def _is_csi_fixture_path(path: Path, fixture_root: Path) -> bool:
    try:
        path.relative_to(fixture_root)
    except ValueError:
        return False
    return True


def _safe_path(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root).as_posix()
    except ValueError:
        return "<outside-csi-fixture-root>"


__all__ = [
    "CSI_FIXTURE_ROOT",
    "DEFAULT_N_OF_1_CSI_FIXTURE_REFS",
    "SUPPORTED_CSI_FIXTURE_EXTENSIONS",
    "build_csi_parser_artifacts",
    "parse_csi_file",
    "parse_csi_fixture",
    "resolve_csi_fixture_path",
]
