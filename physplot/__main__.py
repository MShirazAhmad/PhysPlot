"""Command-line entry point for PhysPlot."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from . import __version__
from .api import PhysPlot
from .bulk import run_folder
from .workflow import load_workflow

MODULE_ID = "physplot.__main__"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-05-30-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="physplot")
    parser.add_argument("--version", action="store_true", help="Print PhysPlot version and exit.")
    subparsers = parser.add_subparsers(dest="command")

    run_workflow = subparsers.add_parser("run-workflow")
    run_workflow.add_argument("workflow")
    run_workflow.add_argument("--input", required=True)
    run_workflow.add_argument("--output", required=True)
    run_workflow.add_argument("--allow-column-number-fallback", action="store_true")

    run_bulk = subparsers.add_parser("run-bulk")
    run_bulk.add_argument("workflow")
    run_bulk.add_argument("--input-folder", required=True)
    run_bulk.add_argument("--output-folder", required=True)
    run_bulk.add_argument("--allow-column-number-fallback", action="store_true")

    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    if args.version:
        print(f"PhysPlot {__version__}")
        return 0
    if args.command == "run-workflow":
        pp = PhysPlot()
        pp.load(args.input)
        pp.run_workflow(load_workflow(args.workflow), allow_column_number_fallback=args.allow_column_number_fallback)
        output = Path(args.output)
        pp.export(output)
        print(f"Workflow output written to {output}")
        return 0
    if args.command == "run-bulk":
        outputs = run_folder(
            args.workflow,
            args.input_folder,
            args.output_folder,
            allow_column_number_fallback=args.allow_column_number_fallback,
        )
        print(f"Bulk workflow wrote {len(outputs)} outputs to {args.output_folder}")
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
