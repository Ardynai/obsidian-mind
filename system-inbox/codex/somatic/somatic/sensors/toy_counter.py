"""Fixture-only toy counter evidence provider."""

import csv
from pathlib import Path

from .evidence import sensor_evidence_result_code, sensor_evidence_score_int
from .toy_counter_evidence_pack import build_toy_counter_evidence_pack

TOY_COUNTER_FIXTURE_PROVIDER_ID = "somatic-toy-counter-fixture-provider-v1"
TOY_COUNTER_FIXTURE_PROVIDER_CONTRACT_VERSION = 1
TOY_COUNTER_FIXTURE_INPUT_KIND = "toy-counter-fixture-rows"
TOY_COUNTER_FIXTURE_INPUT_KINDS = (
    TOY_COUNTER_FIXTURE_INPUT_KIND,
    "toy-counter-tabular-fixtures",
)
TOY_COUNTER_FIXTURE_BASE = Path("fixtures") / "sensors" / "toy-counter"
DEFAULT_TOY_COUNTER_FIXTURE_REFS = ("toy-counter-parsed.csv",)
MAX_TOY_COUNTER_FIXTURE_REFS = 3
MAX_TOY_COUNTER_ROWS = 32


class ToyCounterFixtureSensorProvider:
    """Reads local toy CSV fixtures and returns sanitized pack metadata."""

    provider_id = TOY_COUNTER_FIXTURE_PROVIDER_ID

    def status(self) -> dict[str, object]:
        return {
            "provider_id": self.provider_id,
            "contract_version": TOY_COUNTER_FIXTURE_PROVIDER_CONTRACT_VERSION,
            "mode": "fixture-only",
            "metadata_only": True,
            "fixture_only": True,
            "offline": True,
            "mock": True,
            "hardware_access": False,
            "network_calls": False,
            "live_capture": False,
        }

    def evidence_pack(
        self,
        fixture_refs,
        *,
        repo_root: str | Path,
        artifact_refs: dict[str, object] | None = None,
        artifact_hashes: dict[str, object] | None = None,
    ) -> dict[str, object]:
        evaluation = evaluate_toy_counter_fixture_refs(
            fixture_refs,
            repo_root=repo_root,
        )
        return build_toy_counter_evidence_pack(
            fixture_evaluation=evaluation,
            artifact_refs=artifact_refs,
            artifact_hashes=artifact_hashes,
        )


def evaluate_toy_counter_fixture_refs(
    fixture_refs,
    *,
    repo_root: str | Path,
) -> dict[str, object]:
    refs = _fixture_ref_tuple(fixture_refs)
    if not refs:
        refs = DEFAULT_TOY_COUNTER_FIXTURE_REFS
    refs = refs[:MAX_TOY_COUNTER_FIXTURE_REFS]
    status_counts = {"parsed": 0, "partial": 0, "rejected": 0}
    categories: dict[str, int] = {}
    quality_total = 0
    row_count = 0
    accepted_refs = 0

    for ref in refs:
        safe_name = _safe_fixture_name(ref)
        if not safe_name:
            status_counts["rejected"] += 1
            _increment(categories, "unsafe-ref")
            continue
        path = Path(repo_root) / TOY_COUNTER_FIXTURE_BASE / safe_name
        try:
            path.resolve().relative_to((Path(repo_root) / TOY_COUNTER_FIXTURE_BASE).resolve())
        except ValueError:
            status_counts["rejected"] += 1
            _increment(categories, "unsafe-ref")
            continue
        if not path.exists():
            status_counts["rejected"] += 1
            _increment(categories, "missing-ref")
            continue
        accepted_refs += 1
        parsed = _read_fixture_rows(path)
        row_count += parsed["row_count"]
        quality_total += parsed["quality_total"]
        for status, count in parsed["status_counts"].items():
            status_counts[status] += count
        for category, count in parsed["parse_error_categories"].items():
            _increment(categories, category, count)

    status = _aggregate_status(status_counts, row_count)
    evidence_quality = quality_total // row_count if row_count else 0
    if status == "rejected":
        evidence_quality = 0
    return {
        "status": status,
        "fixture_count": accepted_refs,
        "row_count": row_count,
        "category_count": len([key for key, value in categories.items() if value]),
        "status_counts": status_counts,
        "parse_error_categories": dict(sorted(categories.items())),
        "error_count": status_counts["rejected"],
        "warning_count": status_counts["partial"],
        "evidence_quality": evidence_quality,
        "replay_integrity": 100 if status == "parsed" else evidence_quality,
    }


def _read_fixture_rows(path: Path) -> dict[str, object]:
    status_counts = {"parsed": 0, "partial": 0, "rejected": 0}
    categories: dict[str, int] = {}
    row_count = 0
    quality_total = 0
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or "status" not in reader.fieldnames:
                _increment(categories, "missing-status-column")
                return {
                    "row_count": 0,
                    "quality_total": 0,
                    "status_counts": dict(status_counts, rejected=1),
                    "parse_error_categories": categories,
                }
            for row in reader:
                if row_count >= MAX_TOY_COUNTER_ROWS:
                    _increment(categories, "row-limit")
                    break
                row_count += 1
                status = str(row.get("status") or "rejected").strip().lower()
                if status not in status_counts:
                    status = "rejected"
                    _increment(categories, "invalid-status")
                status_counts[status] += 1
                quality_total += _quality_score(row.get("quality_bucket"), status)
                code = sensor_evidence_result_code(row.get("diagnostic_code") or "none")
                if code not in {"none", "ok"}:
                    _increment(categories, code)
    except UnicodeDecodeError:
        status_counts["rejected"] += 1
        _increment(categories, "decode-error")
    return {
        "row_count": row_count,
        "quality_total": quality_total,
        "status_counts": status_counts,
        "parse_error_categories": categories,
    }


def _safe_fixture_name(ref: object) -> str:
    text = str(ref or "").strip()
    if not text or "://" in text:
        return ""
    normalized = text.replace("\\", "/")
    path = Path(normalized)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        return ""
    if len(path.parts) != 1 or path.suffix.lower() != ".csv":
        return ""
    safe = path.name
    if safe != normalized:
        return ""
    return safe


def _fixture_ref_tuple(value) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, (list, tuple)):
        return tuple(str(item) for item in value)
    return ()


def _quality_score(value: object, status: str) -> int:
    if status == "rejected":
        return 0
    text = str(value or "").strip().lower()
    scores = {
        "high": 100,
        "medium": 80,
        "low": 50,
        "none": 0,
    }
    return sensor_evidence_score_int(scores.get(text, 50))


def _aggregate_status(status_counts: dict[str, int], row_count: int) -> str:
    if row_count <= 0 or status_counts["parsed"] + status_counts["partial"] == 0:
        return "rejected"
    if status_counts["partial"] or status_counts["rejected"]:
        return "partial"
    return "parsed"


def _increment(target: dict[str, int], key: str, count: int = 1) -> None:
    safe_key = sensor_evidence_result_code(key).replace("_", "-")
    target[safe_key] = target.get(safe_key, 0) + count


__all__ = [
    "DEFAULT_TOY_COUNTER_FIXTURE_REFS",
    "MAX_TOY_COUNTER_FIXTURE_REFS",
    "TOY_COUNTER_FIXTURE_BASE",
    "TOY_COUNTER_FIXTURE_INPUT_KIND",
    "TOY_COUNTER_FIXTURE_INPUT_KINDS",
    "TOY_COUNTER_FIXTURE_PROVIDER_CONTRACT_VERSION",
    "TOY_COUNTER_FIXTURE_PROVIDER_ID",
    "ToyCounterFixtureSensorProvider",
    "evaluate_toy_counter_fixture_refs",
]
