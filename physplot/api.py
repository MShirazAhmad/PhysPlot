"""Public backend API for PhysPlot."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .core.formula import evaluate_formula
from .core.transformations import get_transform
from .loaders import get_loader
from .plotting_modules import PlotterRegistry
from .steps.calculate_column import CalculateColumnStep
from .steps.delete_columns import DeleteColumnsStep
from .steps.delete_rows import DeleteRowsStep
from .steps.load_data import LoadDataStep
from .steps.plot_module import PlotModuleStep
from .steps.rename_column import RenameColumnStep
from .steps.set_cell_value import SetCellValueStep
from .steps.set_role import SetRoleStep
from .steps.transform_column import TransformColumnStep

MODULE_ID = "physplot.api"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-05-30-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


class PhysPlot:
    """Package-first backend facade for loading, transforming, fitting, and exporting data."""

    def __init__(self):
        self.dataset = None
        self.workflow: list = []
        self.fit_result = None
        self.last_figure = None
        self.last_plot_path = None
        self.recording = False

    def load(self, path, loader="auto", dataset_name=None):
        self.dataset = get_loader(loader).load(path, dataset_name=dataset_name)
        return self.dataset

    def set_roles(self, **roles):
        self._require_dataset()
        role_names = {
            "x": "X",
            "y": "Y",
            "xerr": "X Error",
            "x_error": "X Error",
            "yerr": "Y Error",
            "y_error": "Y Error",
            "group": "Group",
            "label": "Label",
            "batch_key": "Batch Key",
            "fit_weight": "Fit Weight",
        }
        for role, column_reference in roles.items():
            if column_reference is not None:
                self.dataset.set_role(column_reference, role_names.get(role.lower(), role))
        return self

    def transform(self, input_column, function_name, output=None, record=True, **params):
        self._require_dataset()
        source_column = self.dataset.resolve_column(input_column)
        source_number = self.dataset.get_column_number(source_column)
        output = output or f"{source_column}_{function_name}"
        transform = get_transform(function_name)
        values = transform(self.dataset.dataframe[source_column], **params)
        metadata = {
            "title": output,
            "source_label": output,
            "column_number": len(self.dataset.dataframe.columns) + 1,
            "unit": None,
            "dtype": str(pd.Series(values).dtype),
            "suggested_role": "Ignore",
            "derived": True,
            "source_columns": [source_column],
            "source_column_numbers": [source_number],
            "transformation": {"function": function_name, "params": dict(params)},
            "formula": None,
        }
        self.dataset.add_column(output, values, metadata)
        output_number = self.dataset.get_column_number(output)
        self.dataset.column_metadata[output]["column_number"] = output_number
        if record:
            self.workflow.append(
                TransformColumnStep(
                    input_column=source_column,
                    input_column_number=source_number,
                    function_name=function_name,
                    output=output,
                    output_column_number=output_number,
                    params=dict(params),
                )
            )
        return self.dataset.dataframe[output]

    def calculate(self, formula: str, output: str, record=True):
        self._require_dataset()
        values, normalized_formula, source_columns, source_numbers = evaluate_formula(self.dataset, formula)
        metadata = {
            "title": output,
            "source_label": output,
            "column_number": len(self.dataset.dataframe.columns) + 1,
            "unit": None,
            "dtype": str(pd.Series(values).dtype),
            "suggested_role": "Ignore",
            "derived": True,
            "source_columns": source_columns,
            "source_column_numbers": source_numbers,
            "formula": normalized_formula,
            "formula_original": formula,
            "transformation": None,
        }
        self.dataset.add_column(output, values, metadata)
        output_number = self.dataset.get_column_number(output)
        if record:
            self.workflow.append(
                CalculateColumnStep(
                    formula=normalized_formula,
                    output=output,
                    formula_original=formula,
                    source_columns=source_columns,
                    source_column_numbers=source_numbers,
                    output_column_number=output_number,
                )
            )
        return self.dataset.dataframe[output]

    def describe_columns(self):
        self._require_dataset()
        return self.dataset.describe_columns()

    def get_column_metadata(self, column_reference):
        self._require_dataset()
        return self.dataset.get_column_metadata(column_reference)

    def rename_column(self, old_reference, new_name: str):
        self._require_dataset()
        return self.dataset.rename_column(old_reference, new_name)

    def set_cell_value(self, row_index: int, column_reference, value):
        self._require_dataset()
        self.dataset.set_cell_value(row_index, column_reference, value)
        return self

    def delete_rows(self, row_indices):
        self._require_dataset()
        self.dataset.delete_rows(row_indices)
        return self

    def delete_columns(self, column_references):
        self._require_dataset()
        self.dataset.delete_columns(column_references)
        return self

    def fit(self, kind="linear"):
        self._require_dataset()
        if kind != "linear":
            raise ValueError("Only linear fitting is currently available in the backend API.")
        x_col, y_col = self._role_column("X"), self._role_column("Y")
        x = self.dataset.dataframe[x_col].astype(float)
        y = self.dataset.dataframe[y_col].astype(float)
        slope, intercept = np.polyfit(x, y, 1)
        self.fit_result = {"kind": kind, "x": x_col, "y": y_col, "slope": slope, "intercept": intercept}
        return self.fit_result

    def plot(self, mode="single", output=None):
        self._require_dataset()
        x_col, y_col = self._role_column("X"), self._role_column("Y")
        fig, ax = plt.subplots()
        ax.plot(self.dataset.dataframe[x_col], self.dataset.dataframe[y_col], marker="o", linestyle="-")
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        if self.fit_result:
            x = self.dataset.dataframe[x_col].astype(float)
            ax.plot(x, self.fit_result["slope"] * x + self.fit_result["intercept"], linestyle="--")
        if output is None:
            output = Path("outputs") / f"{self.dataset.name}_plot.png"
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output, dpi=150)
        plt.close(fig)
        self.last_plot_path = output
        return output

    def plot_with_module(self, plotter_id, plot_type=None, record=True, **config):
        """Render a plot through the modular plotter registry."""
        self._require_dataset()
        plotter = PlotterRegistry.default().get(plotter_id)
        figure = plotter.plot(self.dataset, plot_type=plot_type, config=config)
        self.last_figure = figure
        if record:
            self.workflow.append(PlotModuleStep(plotter_id=plotter_id, plot_type=plot_type, config=dict(config)))
        return figure

    def export(self, output):
        self._require_dataset()
        output = Path(output)
        output.mkdir(parents=True, exist_ok=True)
        self.dataset.dataframe.to_csv(output / "data.csv", index=False)
        self.describe_columns().to_csv(output / "columns.csv", index=False)
        self.export_workflow(output / "workflow.py")
        if self.fit_result:
            pd.Series(self.fit_result).to_json(output / "fit.json")
        if self.last_figure is not None:
            self.last_figure.savefig(output / "plot.png", dpi=150)
        return output

    def export_workflow(self, path):
        """Write an importable and headless-runnable Python sequence file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.workflow_script(), encoding="utf-8")
        return path

    def workflow_script(self) -> str:
        """Return the same runnable Python source used by ``export_workflow``."""
        steps_code = ",\n".join(_indent(step.to_code(), 4) for step in self.workflow)
        return (
            "from __future__ import annotations\n\n"
            "\"\"\"PhysPlot sequence generated by the GUI.\n\n"
            "Edit WORKFLOW_STEPS directly, import build_workflow() in Python, or run\n"
            "this file from a terminal with --input/--output for headless batches.\n"
            "\"\"\"\n\n"
            "import argparse\n\n"
            "from physplot import PhysPlot\n"
            "from physplot.steps import (\n"
            "    CalculateColumnStep,\n"
            "    DeleteColumnsStep,\n"
            "    DeleteRowsStep,\n"
            "    LoadDataStep,\n"
            "    PlotModuleStep,\n"
            "    RenameColumnStep,\n"
            "    SetCellValueStep,\n"
            "    SetRoleStep,\n"
            "    TransformColumnStep,\n"
            ")\n\n"
            f"WORKFLOW_STEPS = [\n{steps_code}\n]\n\n"
            "def build_workflow():\n"
            "    \"\"\"Return a copy of the ordered GUI sequence steps.\"\"\"\n"
            "    return list(WORKFLOW_STEPS)\n\n"
            "def run(input_path=None, output_dir='outputs/sequence_run', loader='auto'):\n"
            "    \"\"\"Run the sequence headlessly and export data/metadata/plots.\"\"\"\n"
            "    pp = PhysPlot()\n"
            "    steps = build_workflow()\n"
            "    if input_path:\n"
            "        pp.load(input_path, loader=loader)\n"
            "        steps = [step for step in steps if not isinstance(step, LoadDataStep)]\n"
            "    pp.run_workflow(steps, allow_column_number_fallback=True)\n"
            "    pp.export(output_dir)\n"
            "    return pp\n\n"
            "if __name__ == '__main__':\n"
            "    parser = argparse.ArgumentParser(description='Run a PhysPlot sequence headlessly.')\n"
            "    parser.add_argument('--input', dest='input_path', default=None)\n"
            "    parser.add_argument('--output', dest='output_dir', default='outputs/sequence_run')\n"
            "    parser.add_argument('--loader', default='auto')\n"
            "    args, _unknown = parser.parse_known_args()\n"
            "    run(args.input_path, args.output_dir, args.loader)\n"
        )

    def start_recording(self):
        self.recording = True
        return self

    def stop_recording(self):
        self.recording = False
        return self

    def save_workflow(self, path):
        return self.export_workflow(path)

    def load_workflow(self, path):
        from .workflow import load_workflow as load_workflow_steps

        return load_workflow_steps(path)

    def run_bulk(self, workflow, input_folder, output_folder, **kwargs):
        from .bulk import run_folder

        return run_folder(workflow, input_folder, output_folder, **kwargs)

    def run_workflow(self, steps, allow_column_number_fallback=False):
        for step in steps:
            step.apply(self, allow_column_number_fallback=allow_column_number_fallback)
        return self

    def get_active_dataset(self):
        self._require_dataset()
        return self.dataset

    def _role_column(self, role):
        for column, column_role in self.dataset.column_roles.items():
            if column_role == role:
                return column
        raise ValueError(f"No column has role {role!r}.")

    def _require_dataset(self):
        if self.dataset is None:
            raise RuntimeError("No dataset loaded.")


def _indent(text: str, spaces: int) -> str:
    pad = " " * spaces
    return "\n".join(pad + line if line else line for line in text.splitlines())
