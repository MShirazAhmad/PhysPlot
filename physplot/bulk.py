"""Bulk workflow execution."""

from __future__ import annotations

import logging
from pathlib import Path

from .api import PhysPlot
from .steps.load_data import load_input, plugin_load_step
from .workflow import load_workflow

MODULE_ID = "physplot.bulk"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-09-25-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"

LOGGER = logging.getLogger(__name__)
TABULAR_SUFFIXES = {".csv", ".txt", ".dat", ".xls", ".xlsx"}


def run_folder(
    workflow,
    input_folder,
    output_folder,
    loader="auto",
    allow_column_number_fallback=False,
):
    steps = load_workflow(workflow) if not isinstance(workflow, list) else workflow
    # A sequence loaded through a personal plugin (e.g. OES .HRF) processes files
    # with that file's extension; otherwise the built-in tabular formats.
    template = plugin_load_step(steps)
    suffixes = TABULAR_SUFFIXES
    if template is not None and template.path and loader == "auto":
        suffixes = {Path(str(template.path)).suffix.lower()}
    input_folder = Path(input_folder)
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    results = []
    for path in sorted(input_folder.iterdir()):
        if not path.is_file() or path.suffix.lower() not in suffixes:
            continue
        pp = PhysPlot()
        try:
            remaining = load_input(pp, path, steps, loader=loader)
            pp.run_workflow(remaining, allow_column_number_fallback=allow_column_number_fallback)
        except Exception as exc:
            LOGGER.exception("Workflow failed for %s", path)
            exc.input_path = path  # lets callers such as the GUI name the failing file
            raise
        dataset_output = output_folder / path.stem
        pp.export(dataset_output)
        results.append(dataset_output)
    return results
