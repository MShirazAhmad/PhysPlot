"""Column metadata parsing and role suggestions."""

from __future__ import annotations

import re

MODULE_ID = "physplot.core.metadata"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-05-30-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


_PAREN_UNIT_RE = re.compile(r"^\s*(?P<title>.*?)\s*[\(\[](?P<unit>[^\)\]]+)[\)\]]\s*$")


def parse_column_label(label: str) -> dict:
    """Parse a source column label into title, unit, and source label fields."""
    source_label = str(label)
    match = _PAREN_UNIT_RE.match(source_label)
    if match:
        title = match.group("title").strip() or source_label
        unit = match.group("unit").strip() or None
        return {"title": title, "unit": unit, "source_label": source_label}
    return {"title": source_label, "unit": None, "source_label": source_label}


def infer_suggested_role(column_name: str, unit: str | None = None) -> str:
    """Infer a non-binding role suggestion from a column title and optional unit."""
    name = str(column_name).strip().lower()
    unit_l = str(unit).strip().lower() if unit else None
    tokens = set(re.findall(r"[a-z0-9]+", name))
    if name in {"time", "t", "seconds", "s"} or unit_l in {"s", "sec", "second", "seconds"}:
        return "X"
    if tokens & {"x", "position", "wavelength", "depth"}:
        return "X"
    if tokens & {"voltage", "signal", "intensity", "force", "load", "y"}:
        return "Y"
    if tokens & {"error", "uncertainty", "std", "stdev", "sigma"}:
        return "Y Error"
    if tokens & {"group", "condition", "sample", "batch"}:
        return "Group"
    if tokens & {"label", "name", "id"}:
        return "Label"
    return "Ignore"
