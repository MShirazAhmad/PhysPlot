"""Utilities shared by plotting modules."""

from __future__ import annotations

import re

import pandas as pd

MODULE_ID = "physplot.plotting_modules.utils"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-06-05-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


def role_column(dataset, role: str, required: bool = True) -> str | None:
    for column, column_role in dataset.column_roles.items():
        if column_role == role and column in dataset.dataframe.columns:
            return column
    if required:
        raise ValueError(f"No column has role {role!r}.")
    return None


def numeric_series(dataset, column: str) -> pd.Series:
    values = pd.to_numeric(dataset.dataframe[column], errors="coerce")
    if values.notna().sum() == 0:
        raise ValueError(f"Column '{column}' does not contain numeric data.")
    return values


def first_numeric_column(dataset) -> str:
    for column in dataset.dataframe.columns:
        values = pd.to_numeric(dataset.dataframe[column], errors="coerce")
        if values.notna().sum() > 0:
            return column
    raise ValueError("No numeric columns are available to plot.")


def group_column(dataset) -> str | None:
    return role_column(dataset, "Group", required=False) or role_column(dataset, "Label", required=False)


def normalize_label(label: str) -> str:
    lowered = str(label).lower()
    lowered = re.sub(r"\([^)]*\)|\[[^]]*]", " ", lowered)
    return re.sub(r"[^a-z0-9]+", "", lowered)


def find_column(dataset, aliases: tuple[str, ...]) -> str | None:
    normalized_aliases = {normalize_label(alias) for alias in aliases}
    for column in dataset.dataframe.columns:
        metadata = dataset.column_metadata.get(column, {})
        candidates = [column, metadata.get("title", ""), metadata.get("source_label", "")]
        for candidate in candidates:
            if normalize_label(candidate) in normalized_aliases:
                return column
    return None


def require_columns(dataset, plot_name: str, columns: dict[str, tuple[str, ...]]) -> dict[str, str]:
    found = {}
    missing = []
    for logical_name, aliases in columns.items():
        column = find_column(dataset, aliases)
        if column is None:
            missing.append(logical_name)
        else:
            found[logical_name] = column
    if missing:
        joined = " and ".join(missing)
        raise ValueError(f"{plot_name} requires columns: {joined}.")
    return found
