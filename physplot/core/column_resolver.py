"""Column-name and 1-based column-number resolution."""

from __future__ import annotations

import re
from typing import Any

MODULE_ID = "physplot.core.column_resolver"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-05-30-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"

_COLUMN_NUMBER_RE = re.compile(r"^\s*(?:column\s*|col\s*|c\s*|#)?(?P<number>\d+)\s*$", re.IGNORECASE)


def resolve_column(dataset: Any, column_reference) -> str:
    """Resolve a user column reference to the actual dataframe column name."""
    if column_reference is None:
        raise ValueError("Column reference cannot be None.")
    if isinstance(column_reference, str) and not column_reference.strip():
        raise ValueError("Column reference cannot be empty.")

    columns = [str(column) for column in dataset.dataframe.columns]

    if isinstance(column_reference, str) and column_reference in columns:
        return column_reference

    number = _extract_column_number(column_reference)
    if number is not None:
        if number < 1 or number > len(columns):
            raise ValueError(
                f"Column number {number} is out of range. Dataset has {len(columns)} columns."
            )
        return columns[number - 1]

    reference = str(column_reference)
    if reference in columns:
        return reference
    raise ValueError(f"Unknown column '{reference}'. Available columns: {', '.join(columns)}")


def get_column_number(dataset: Any, column_name: str) -> int:
    """Return the 1-based column number for an existing column name."""
    resolved = resolve_column(dataset, column_name)
    return list(dataset.dataframe.columns).index(resolved) + 1


def resolve_columns(dataset: Any, references: list) -> list[str]:
    """Resolve a list of column references to column names."""
    return [resolve_column(dataset, reference) for reference in references]


def _extract_column_number(column_reference) -> int | None:
    if isinstance(column_reference, bool):
        return None
    if isinstance(column_reference, int):
        return column_reference
    if isinstance(column_reference, str):
        match = _COLUMN_NUMBER_RE.match(column_reference)
        if match:
            return int(match.group("number"))
    return None
