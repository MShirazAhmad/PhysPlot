"""Safe arithmetic formula evaluation for derived columns."""

from __future__ import annotations

import ast
import re

import pandas as pd

from .column_resolver import resolve_column

MODULE_ID = "physplot.core.formula"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-05-30-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"

_COL_REF_RE = re.compile(r"(?<![A-Za-z0-9_])(?:col|column|c|#)\s*(\d+)(?![A-Za-z0-9_])", re.IGNORECASE)
_ALLOWED_NODES = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Pow,
    ast.USub,
    ast.UAdd,
    ast.Load,
    ast.Name,
    ast.Constant,
)


def evaluate_formula(dataset, formula: str) -> tuple[pd.Series, str, list[str], list[int]]:
    """Evaluate a restricted arithmetic formula and return result/provenance."""
    if not formula or not str(formula).strip():
        raise ValueError("Formula cannot be empty.")
    original = str(formula)
    resolved_columns: list[str] = []

    def replace_col_ref(match: re.Match) -> str:
        reference = match.group(0)
        column = resolve_column(dataset, reference)
        if not column.isidentifier():
            raise ValueError(
                f"Column reference '{reference}' resolved to '{column}', which cannot be used in formulas yet."
            )
        resolved_columns.append(column)
        return column

    normalized_formula = _COL_REF_RE.sub(replace_col_ref, original)
    try:
        tree = ast.parse(normalized_formula, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"Invalid formula '{original}'.") from exc
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise ValueError(f"Formula '{original}' uses unsupported or unsafe syntax.")
        if isinstance(node, ast.Name):
            if node.id not in dataset.dataframe.columns:
                raise ValueError(f"Unknown formula column '{node.id}'.")
            resolved_columns.append(node.id)
    code = compile(tree, "<physplot-formula>", "eval")
    env = {column: dataset.dataframe[column] for column in dataset.dataframe.columns if str(column).isidentifier()}
    try:
        result = eval(code, {"__builtins__": {}}, env)
    except Exception as exc:
        raise ValueError(f"Formula '{original}' failed: {exc}") from exc
    source_columns = list(dict.fromkeys(resolved_columns))
    source_numbers = [dataset.get_column_number(column) for column in source_columns]
    return result, normalized_formula, source_columns, source_numbers
