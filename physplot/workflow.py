"""Workflow import and execution helpers."""

from __future__ import annotations

from pathlib import Path

MODULE_ID = "physplot.workflow"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-05-30-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


def load_workflow_source(source: str, name: str = "physplot_user_workflow") -> list:
    """Load workflow steps from Python source text.

    The GUI code editor uses this helper so the visible sequence table and the
    editable Python source can round-trip through the same public workflow
    format. Loading a workflow file already executes user-authored Python, so
    this follows the same trust model for editor text.
    """
    namespace = {"__name__": name}
    exec(compile(source, name, "exec"), namespace)
    if "WORKFLOW_STEPS" in namespace:
        return list(namespace["WORKFLOW_STEPS"])
    if "build_workflow" in namespace:
        return list(namespace["build_workflow"]())
    raise ValueError("Workflow source must define WORKFLOW_STEPS or build_workflow().")


def load_workflow(path) -> list:
    path = Path(path)
    if not path.exists():
        raise ValueError(f"Could not load workflow '{path}'.")
    try:
        return load_workflow_source(path.read_text(encoding="utf-8"), name=str(path))
    except ValueError as exc:
        raise ValueError(f"Workflow '{path}' must define WORKFLOW_STEPS or build_workflow().") from exc


def discover_protocol_modules() -> list[dict]:
    """Return reusable protocol modules from ``config/protocol_modules``.

    Each entry is a normal PhysPlot sequence file (``WORKFLOW_STEPS`` or
    ``build_workflow()``). ``DISPLAY_NAME`` and ``DESCRIPTION`` are optional.
    Entries are returned without executing the files; use ``load_workflow``
    to obtain their steps.
    """
    from physplot.user_paths import plugin_search_dirs

    entries_by_name = {}
    for folder in plugin_search_dirs("protocol_modules"):
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.py")):
            if path.name.startswith(".") or path.name == "__init__.py" or path.name in entries_by_name:
                continue
            entries_by_name[path.name] = {
                "display_name": _module_constant(path, "DISPLAY_NAME") or path.stem.replace("_", " ").title(),
                "description": _module_constant(path, "DESCRIPTION") or "",
                "path": path,
            }
    return [entries_by_name[name] for name in sorted(entries_by_name)]


def _module_constant(path: Path, name: str) -> str | None:
    import ast

    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return None
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                return node.value.value
    return None
