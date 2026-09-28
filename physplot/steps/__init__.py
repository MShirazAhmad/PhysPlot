"""Workflow step classes."""

from .calculate_column import CalculateColumnStep
from .delete_columns import DeleteColumnsStep
from .delete_rows import DeleteRowsStep
from .load_data import LoadDataStep
from .plot_module import PlotModuleStep
from .rename_column import RenameColumnStep
from .set_cell_value import SetCellValueStep
from .set_role import SetRoleStep
from .transform_column import TransformColumnStep

# Step types offered by the GUI "Insert Step..." action, in menu order.
STEP_TYPES = [
    SetRoleStep,
    TransformColumnStep,
    CalculateColumnStep,
    RenameColumnStep,
    SetCellValueStep,
    DeleteRowsStep,
    DeleteColumnsStep,
    PlotModuleStep,
    LoadDataStep,
]

__all__ = [
    "CalculateColumnStep",
    "DeleteColumnsStep",
    "DeleteRowsStep",
    "LoadDataStep",
    "PlotModuleStep",
    "RenameColumnStep",
    "STEP_TYPES",
    "SetCellValueStep",
    "SetRoleStep",
    "TransformColumnStep",
]
