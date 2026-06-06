"""Bulk workflow execution."""

from __future__ import annotations

import logging
from pathlib import Path

from .api import PhysPlot
from .workflow import load_workflow

MODULE_ID = "physplot.bulk"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-05-30-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"

LOGGER = logging.getLogger(__name__)


def run_folder(
    workflow,
    input_folder,
    output_folder,
    loader="auto",
    allow_column_number_fallback=False,
):
    steps = load_workflow(workflow) if not isinstance(workflow, list) else workflow
    input_folder = Path(input_folder)
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    results = []
    for path in sorted(input_folder.iterdir()):
        if not path.is_file() or path.suffix.lower() not in {".csv", ".txt", ".dat", ".xls", ".xlsx"}:
            continue
        pp = PhysPlot()
        pp.load(path, loader=loader)
        try:
            pp.run_workflow(steps, allow_column_number_fallback=allow_column_number_fallback)
        except Exception:
            LOGGER.exception("Workflow failed for %s", path)
            raise
        dataset_output = output_folder / path.stem
        pp.export(dataset_output)
        results.append(dataset_output)
    return results
