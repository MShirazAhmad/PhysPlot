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
