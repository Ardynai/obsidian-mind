import csv
from pathlib import Path

from .statistics import (
    descriptive_stats,
    detect_numeric_columns,
    is_missing,
    numeric_values,
)


def read_csv_table(path):
    table_path = Path(path)
    with table_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [dict(row) for row in reader]


def profile_csv_table(path):
    table_path = Path(path)
    rows = read_csv_table(table_path)
    columns = list(rows[0]) if rows else _read_header(table_path)
    missing_values = {
        column: sum(1 for row in rows if is_missing(row.get(column))) for column in columns
    }
    numeric_columns = detect_numeric_columns(rows, columns)
    numeric_stats = {
        column: descriptive_stats(numeric_values(rows, column)) for column in numeric_columns
    }
    column_summary = {
        column: {
            "missing": missing_values[column],
            "non_missing": len(rows) - missing_values[column],
            "numeric": column in numeric_columns,
        }
        for column in columns
    }
    return {
        "schema_version": 1,
        "source_file": table_path.name,
        "columns": columns,
        "row_count": len(rows),
        "column_count": len(columns),
        "missing_values": missing_values,
        "numeric_columns": numeric_columns,
        "numeric_stats": numeric_stats,
        "column_summary": column_summary,
        "mock": True,
        "offline": True,
        "research_only": True,
    }


def _read_header(path):
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        return next(reader, [])
