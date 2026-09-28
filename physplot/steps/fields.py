"""Editable-field descriptions for workflow steps.

``WorkflowStep.describe()`` returns an ordered mapping of field name to a
spec built with :func:`field`. The GUI step editor renders one widget per
field from the spec alone, and ``WorkflowStep.validate()`` converts edited
values back to Python with :func:`coerce_field`, so the GUI never needs
step-specific code.

Field types:

``str``      free text
``int``      integer
``float``    floating-point number
``bool``     checkbox
``column``   a table column name; the editor offers the current columns
``choice``   one of ``choices`` (``editable=True`` also allows free text)
``path``     a file path; the editor adds a Browse button
``literal``  a Python literal such as ``{"factor": 2}`` or ``[1, 2]``;
             ``python_type`` restricts it to ``dict`` or ``list``
``value``    a Python literal when it parses as one, otherwise text
"""

from __future__ import annotations

import ast

MODULE_ID = "physplot.steps.fields"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-09-25-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"

FIELD_TYPES = {"str", "int", "float", "bool", "column", "choice", "path", "literal", "value"}
TEXT_TYPES = {"str", "column", "choice", "path"}


def field(
    value,
    type: str = "str",
    *,
    label: str | None = None,
    choices=None,
    optional: bool = False,
    editable: bool = False,
    help: str | None = None,
    number_field: str | None = None,
    python_type: type | None = None,
) -> dict:
    """Build one field spec for ``WorkflowStep.describe()``."""
    if type not in FIELD_TYPES:
        raise ValueError(f"Unknown field type {type!r}.")
    spec = {"value": value, "type": type, "optional": optional}
    if label is not None:
        spec["label"] = label
    if choices is not None:
        spec["choices"] = list(choices)
    if editable:
        spec["editable"] = True
    if help:
        spec["help"] = help
    if number_field:
        spec["number_field"] = number_field
    if python_type is not None:
        spec["python_type"] = python_type
    return spec


def field_label(name: str, spec: dict) -> str:
    return spec.get("label") or name.replace("_", " ").capitalize()


def coerce_field(name: str, spec: dict, raw):
    """Convert an edited value to the Python value the step stores.

    Accepts either already-typed values or the text a line edit produced.
    Raises ``ValueError`` naming the field when the value is invalid.
    """
    kind = spec.get("type", "str")
    label = field_label(name, spec)
    if _is_blank(raw):
        if spec.get("optional"):
            return None
        if kind == "literal" and spec.get("python_type") in (dict, list):
            return spec["python_type"]()
        if kind == "value":
            return ""
        raise ValueError(f"{label} is required.")

    if kind == "bool":
        if isinstance(raw, str):
            lowered = raw.strip().lower()
            if lowered in {"true", "yes", "1", "on"}:
                return True
            if lowered in {"false", "no", "0", "off"}:
                return False
            raise ValueError(f"{label} must be true or false.")
        return bool(raw)
    if kind == "int":
        try:
            if isinstance(raw, float) and not raw.is_integer():
                raise ValueError
            return int(str(raw).strip()) if isinstance(raw, str) else int(raw)
        except (TypeError, ValueError):
            raise ValueError(f"{label} must be a whole number.") from None
    if kind == "float":
        try:
            return float(raw)
        except (TypeError, ValueError):
            raise ValueError(f"{label} must be a number.") from None
    if kind == "literal":
        value = raw
        if isinstance(raw, str):
            try:
                value = ast.literal_eval(raw.strip())
            except (SyntaxError, ValueError):
                raise ValueError(f"{label} must be a Python literal such as {{'factor': 2}} or [1, 2].") from None
        expected = spec.get("python_type")
        if expected is not None and not isinstance(value, expected):
            raise ValueError(f"{label} must be a {expected.__name__}.")
        return value
    if kind == "value":
        if isinstance(raw, str):
            try:
                return ast.literal_eval(raw.strip())
            except (SyntaxError, ValueError):
                return raw
        return raw
    text = str(raw).strip()
    if kind == "choice" and not spec.get("editable") and spec.get("choices") and text not in spec["choices"]:
        raise ValueError(f"{label} must be one of: {', '.join(map(str, spec['choices']))}.")
    return text


def format_field(spec: dict) -> str:
    """Return the text a line edit should show for a field's current value."""
    value = spec.get("value")
    if value is None:
        return ""
    kind = spec.get("type")
    if kind == "literal":
        return repr(value)
    if kind == "value":
        if not isinstance(value, str):
            return repr(value)
        # Quote text that would otherwise read back as a number or literal.
        try:
            ast.literal_eval(value.strip())
        except (SyntaxError, ValueError):
            return value
        return repr(value)
    return str(value)


def safe_choices(factory) -> list:
    """Call a choice factory, returning ``[]`` if a registry cannot load."""
    try:
        return list(factory())
    except Exception:
        return []


def _is_blank(raw) -> bool:
    return raw is None or (isinstance(raw, str) and not raw.strip())
