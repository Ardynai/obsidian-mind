import math
import statistics as statistics_lib

MISSING_MARKERS = {"", "na", "n/a", "nan", "none", "null"}


def is_missing(value):
    if value is None:
        return True
    return str(value).strip().lower() in MISSING_MARKERS


def to_float(value):
    if is_missing(value):
        return None
    try:
        parsed = float(str(value).strip())
    except ValueError:
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def numeric_values(rows, column):
    values = []
    for row in rows:
        parsed = to_float(row.get(column))
        if parsed is not None:
            values.append(parsed)
    return values


def detect_numeric_columns(rows, columns=None):
    if columns is None:
        columns = list(rows[0]) if rows else []
    numeric = []
    for column in columns:
        non_missing = [row.get(column) for row in rows if not is_missing(row.get(column))]
        if non_missing and all(to_float(value) is not None for value in non_missing):
            numeric.append(column)
    return numeric


def descriptive_stats(values):
    clean = [float(value) for value in values if value is not None and math.isfinite(float(value))]
    if not clean:
        return {
            "count": 0,
            "min": None,
            "max": None,
            "mean": None,
            "median": None,
            "stdev": None,
        }
    return {
        "count": len(clean),
        "min": _round(clean[0] if len(clean) == 1 else min(clean)),
        "max": _round(clean[0] if len(clean) == 1 else max(clean)),
        "mean": _round(statistics_lib.fmean(clean)),
        "median": _round(statistics_lib.median(clean)),
        "stdev": _round(statistics_lib.stdev(clean)) if len(clean) > 1 else None,
    }


def group_by_summary(rows, group_column, value_column=None):
    groups = {}
    for row in rows:
        group = row.get(group_column)
        key = "(missing)" if is_missing(group) else str(group)
        groups.setdefault(key, []).append(row)

    summarized = {}
    for key in sorted(groups):
        group_rows = groups[key]
        entry = {"row_count": len(group_rows)}
        if value_column:
            entry["numeric_stats"] = descriptive_stats(numeric_values(group_rows, value_column))
        summarized[key] = entry

    return {
        "schema_version": 1,
        "group_column": group_column,
        "value_column": value_column,
        "groups": summarized,
    }


def _round(value):
    if value is None:
        return None
    rounded = round(float(value), 6)
    if rounded == 0:
        return 0.0
    return rounded
