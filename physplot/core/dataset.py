"""Dataset container with column roles and metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

import pandas as pd

from .metadata import infer_suggested_role, parse_column_label

MODULE_ID = "physplot.core.dataset"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-05-30-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"

VALID_ROLES = {
    "Ignore",
    "X",
    "Y",
    "X Error",
    "Y Error",
    "Group",
    "Label",
    "Batch Key",
    "Fit Weight",
}
SINGLETON_ROLES = {"X", "Y", "X Error", "Y Error", "Fit Weight"}


@dataclass
class Dataset:
    name: str
    dataframe: pd.DataFrame
    source_path: Path | None = None
    loader_name: str = "manual"
    loader_id: str = "manual"
    column_roles: dict[str, str] = field(default_factory=dict)
    column_metadata: dict[str, dict] = field(default_factory=dict)
    derived_columns: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.dataframe = self.dataframe.copy()
        self.dataframe.columns = [str(column) for column in self.dataframe.columns]
        self.source_path = Path(self.source_path) if self.source_path is not None else None
        self.loader_id = self.metadata.get("loader_id", self.loader_id)
        self.loader_name = self.metadata.get("loader_name", self.loader_name)
        self._normalize_roles()
        self._normalize_metadata()
        self.update_column_numbers()

    def get_column_number(self, column: str) -> int:
        from .column_resolver import get_column_number

        return get_column_number(self, column)

    def resolve_column(self, column_reference) -> str:
        from .column_resolver import resolve_column

        return resolve_column(self, column_reference)

    def get_column_metadata(self, column_reference) -> dict:
        column = self.resolve_column(column_reference)
        return dict(self.column_metadata[column])

    def update_column_numbers(self) -> None:
        for index, column in enumerate(self.dataframe.columns, start=1):
            metadata = self.column_metadata.setdefault(column, {})
            metadata["column_number"] = index
            metadata.setdefault("title", column)
            metadata.setdefault("source_label", column)
            metadata["dtype"] = str(self.dataframe[column].dtype)
            metadata.setdefault("unit", None)
            metadata.setdefault("suggested_role", infer_suggested_role(column, metadata.get("unit")))
            metadata.setdefault("derived", column in self.derived_columns)

    def describe_columns(self) -> pd.DataFrame:
        rows = []
        for column in self.dataframe.columns:
            metadata = self.column_metadata[column]
            rows.append(
                {
                    "column_number": metadata.get("column_number"),
                    "column_name": column,
                    "role": self.column_roles.get(column, "Ignore"),
                    "dtype": metadata.get("dtype"),
                    "unit": metadata.get("unit"),
                    "derived": metadata.get("derived", False),
                    "suggested_role": metadata.get("suggested_role", "Ignore"),
                    "source_label": metadata.get("source_label", column),
                }
            )
        return pd.DataFrame(rows)

    def set_role(self, column_reference, role: str) -> None:
        role = _normalize_role(role)
        column = self.resolve_column(column_reference)
        if role in SINGLETON_ROLES:
            for existing_column, existing_role in list(self.column_roles.items()):
                if existing_role == role:
                    self.column_roles[existing_column] = "Ignore"
        self.column_roles[column] = role

    def apply_suggested_roles(self) -> None:
        for column in self.dataframe.columns:
            suggested = self.column_metadata[column].get("suggested_role", "Ignore")
            if suggested != "Ignore":
                self.set_role(column, suggested)

    def add_column(self, name: str, values, metadata: dict) -> None:
        self.dataframe[name] = values
        if metadata.get("derived") and name not in self.derived_columns:
            self.derived_columns.append(name)
        self.column_roles[name] = self.column_roles.get(name, "Ignore")
        self.column_metadata[name] = dict(metadata)
        self.update_column_numbers()

    def rename_column(self, old_reference, new_name: str) -> str:
        self._ensure_column_reference_exists(old_reference)
        old_name = self.resolve_column(old_reference)
        new_name = str(new_name).strip()
        if not new_name:
            raise ValueError("Column name cannot be empty.")
        if new_name != old_name and new_name in self.dataframe.columns:
            raise ValueError(f"Column '{new_name}' already exists.")
        if new_name == old_name:
            return old_name
        self.dataframe = self.dataframe.rename(columns={old_name: new_name})
        if old_name in self.column_roles:
            self.column_roles[new_name] = self.column_roles.pop(old_name)
        if old_name in self.column_metadata:
            metadata = self.column_metadata.pop(old_name)
            metadata["title"] = new_name
            metadata.setdefault("source_label", old_name)
            self.column_metadata[new_name] = metadata
        self.derived_columns = [new_name if column == old_name else column for column in self.derived_columns]
        self.update_column_numbers()
        return new_name

    def set_cell_value(self, row_index: int, column_reference, value) -> None:
        self._ensure_column_reference_exists(column_reference, create_named=True)
        column = self.resolve_column(column_reference)
        if row_index < 1:
            raise ValueError("Row index is 1-based and must be at least 1.")
        while row_index > len(self.dataframe.index):
            self.dataframe.loc[len(self.dataframe.index)] = [""] * len(self.dataframe.columns)
        self.dataframe.at[row_index - 1, column] = value
        self.update_column_numbers()

    def delete_rows(self, row_indices) -> None:
        rows = sorted({int(row) for row in row_indices if int(row) >= 1}, reverse=True)
        drop_indices = [row - 1 for row in rows if row - 1 in self.dataframe.index]
        if drop_indices:
            self.dataframe = self.dataframe.drop(index=drop_indices).reset_index(drop=True)
            self.update_column_numbers()

    def delete_columns(self, column_references) -> None:
        columns_to_drop = []
        for reference in column_references:
            self._ensure_column_reference_exists(reference)
            column = self.resolve_column(reference)
            if column not in columns_to_drop:
                columns_to_drop.append(column)
        if not columns_to_drop:
            return
        self.dataframe = self.dataframe.drop(columns=columns_to_drop)
        for column in columns_to_drop:
            self.column_roles.pop(column, None)
            self.column_metadata.pop(column, None)
        self.derived_columns = [column for column in self.derived_columns if column not in columns_to_drop]
        self.update_column_numbers()

    def _ensure_column_reference_exists(self, column_reference, create_named: bool = False) -> None:
        """Create blank spreadsheet columns needed to replay GUI edits headlessly.

        The GUI always shows extra Excel-like columns such as ``Column 12``. When
        a saved sequence edits or renames one of those columns, headless replay
        has to create the same blank columns before resolving the reference.
        """
        if isinstance(column_reference, bool):
            return
        if isinstance(column_reference, str) and column_reference in self.dataframe.columns:
            return
        target_number = _extract_column_number(column_reference)
        if target_number is not None:
            if target_number < 1:
                return
            while len(self.dataframe.columns) < target_number:
                next_number = len(self.dataframe.columns) + 1
                name = f"Column {next_number}"
                self.add_column(name, [""] * len(self.dataframe.index), {"title": name, "derived": False})
            return
        if create_named and isinstance(column_reference, str):
            name = str(column_reference).strip()
            if name and name not in self.dataframe.columns:
                self.add_column(name, [""] * len(self.dataframe.index), {"title": name, "derived": False})

    def _normalize_roles(self) -> None:
        self.column_roles = {str(column): _normalize_role(role) for column, role in self.column_roles.items()}
        for column in self.dataframe.columns:
            self.column_roles.setdefault(column, "Ignore")

    def _normalize_metadata(self) -> None:
        normalized = {}
        for column in self.dataframe.columns:
            incoming = dict(self.column_metadata.get(column, {}))
            parsed = parse_column_label(incoming.get("source_label", column))
            unit = incoming.get("unit", parsed["unit"])
            metadata = {
                "title": incoming.get("title", parsed["title"]),
                "source_label": incoming.get("source_label", parsed["source_label"]),
                "column_number": incoming.get("column_number"),
                "dtype": str(self.dataframe[column].dtype),
                "unit": unit,
                "suggested_role": incoming.get("suggested_role", infer_suggested_role(column, unit)),
                "derived": incoming.get("derived", column in self.derived_columns),
            }
            metadata.update(incoming)
            normalized[column] = metadata
        self.column_metadata = normalized


def _normalize_role(role: str) -> str:
    mapping = {
        "x": "X",
        "y": "Y",
        "xerr": "X Error",
        "x_error": "X Error",
        "yerr": "Y Error",
        "y_error": "Y Error",
        "error": "Y Error",
        "group": "Group",
        "label": "Label",
        "batch_key": "Batch Key",
        "batch": "Batch Key",
        "fit_weight": "Fit Weight",
        "weight": "Fit Weight",
        "ignore": "Ignore",
    }
    normalized = mapping.get(str(role).strip().lower(), str(role).strip())
    if normalized not in VALID_ROLES:
        raise ValueError(f"Unknown column role '{role}'.")
    return normalized


def _extract_column_number(column_reference) -> int | None:
    if isinstance(column_reference, int):
        return column_reference
    if isinstance(column_reference, str):
        match = re.match(r"^\s*(?:column\s*|col\s*|c\s*|#)?(?P<number>\d+)\s*$", column_reference, re.IGNORECASE)
        if match:
            return int(match.group("number"))
    return None
