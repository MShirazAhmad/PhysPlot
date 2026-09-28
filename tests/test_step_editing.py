"""Editable, reorderable, and disableable steps (Advanced Mode plan, phase 2)."""

from __future__ import annotations

import pandas as pd
import pytest

from physplot import PhysPlot
from physplot.execution import SKIP_AFTER_FAILURE, SKIP_DISABLED
from physplot.steps import (
    STEP_TYPES,
    CalculateColumnStep,
    SetRoleStep,
    TransformColumnStep,
)
from physplot.steps.fields import format_field
from physplot.workflow import load_workflow, load_workflow_source

COLUMNS = ["Time", "Voltage"]


def _physplot() -> PhysPlot:
    pp = PhysPlot()
    pp.load(pd.DataFrame({"Time": [1.0, 2.0, 3.0], "Voltage": [2.0, 4.0, 8.0]}), loader="dataframe")
    return pp


@pytest.mark.parametrize("step_type", STEP_TYPES, ids=lambda cls: cls.__name__)
def test_every_step_type_round_trips_through_editor_text(step_type):
    step = step_type.template(COLUMNS)
    spec = step.describe()
    assert spec["enabled"]["type"] == "bool"
    assert list(spec)[-1] == "enabled"

    # What the editor shows, validated again, must reproduce the same step.
    shown = {name: (field["value"] if field["type"] == "bool" else format_field(field)) for name, field in spec.items()}
    before = step.to_code()
    step.update(**shown)
    assert step.to_code() == before


@pytest.mark.parametrize("step_type", STEP_TYPES, ids=lambda cls: cls.__name__)
def test_disabled_flag_round_trips_through_generated_code(step_type):
    step = step_type.template(COLUMNS)
    step.update(enabled=False)
    code = step.to_code()
    assert code.rstrip().endswith("enabled=False,\n)")

    source = f"from physplot.steps import *\nWORKFLOW_STEPS = [{code}]\n"
    (loaded,) = load_workflow_source(source)
    assert loaded.enabled is False
    assert loaded.to_code() == code


def test_enabled_steps_do_not_mention_enabled_in_code():
    assert "enabled" not in TransformColumnStep("Voltage", "multiply", "mV").to_code()


def test_disabled_step_is_skipped_and_later_steps_still_run():
    pp = _physplot()
    steps = [
        TransformColumnStep("Voltage", "multiply", "V_mV", params={"factor": 1000}, enabled=False),
        TransformColumnStep("Time", "multiply", "T_ms", params={"factor": 1000}),
    ]

    results = pp.run_workflow_detailed(steps)

    assert [(result.status, result.skip_reason) for result in results] == [("skipped", SKIP_DISABLED), ("ok", None)]
    assert "V_mV" not in pp.dataset.dataframe.columns
    assert pp.dataset.dataframe["T_ms"].tolist() == [1000.0, 2000.0, 3000.0]


def test_disabled_step_apply_is_a_no_op_when_called_directly():
    pp = _physplot()
    step = TransformColumnStep("Voltage", "multiply", "V_mV", enabled=False)
    assert step.apply(pp) is None
    assert "V_mV" not in pp.dataset.dataframe.columns


def test_steps_after_a_failure_record_why_they_were_skipped():
    pp = _physplot()
    results = pp.run_workflow_detailed(
        [
            TransformColumnStep("Missing", "multiply", "out"),
            TransformColumnStep("Voltage", "multiply", "a"),
            TransformColumnStep("Voltage", "multiply", "b", enabled=False),
        ]
    )
    assert [result.skip_reason for result in results] == [None, SKIP_AFTER_FAILURE, SKIP_DISABLED]


def test_validate_converts_editor_text_and_reports_bad_values():
    step = TransformColumnStep("Voltage", "multiply", "V_mV", params={"factor": 1000}, input_column_number=2)

    assert step.validate(params="{'divisor': 2}", input_column_number="1", output_column_number="") == {
        "params": {"divisor": 2},
        "input_column_number": 1,
        "output_column_number": None,
    }
    with pytest.raises(ValueError, match="Parameters must be a dict"):
        step.validate(params="[1, 2]")
    with pytest.raises(ValueError, match="Input column number fallback must be a whole number"):
        step.validate(input_column_number="two")
    with pytest.raises(ValueError, match="Output column is required"):
        step.validate(output="  ")
    with pytest.raises(ValueError, match="no editable field"):
        step.validate(colour="red")
    # Validation never changes the step.
    assert step.params == {"factor": 1000}


def test_update_changes_replay_result():
    pp = _physplot()
    step = TransformColumnStep("Voltage", "multiply", "V_out", params={"factor": 1000})
    step.update(function_name="divide", params="{'divisor': 2}")
    pp.run_workflow([step])
    assert pp.dataset.dataframe["V_out"].tolist() == [1.0, 2.0, 4.0]


def test_set_role_step_edits_each_role_and_blank_removes_it():
    step = SetRoleStep({"x": "Time", "y": "Voltage", "fit_weight": "W"})
    spec = step.describe()
    assert list(spec)[:6] == ["x", "y", "xerr", "yerr", "group", "label"]
    assert spec["fit_weight"]["value"] == "W"

    step.update(y="", yerr="Error")

    assert step.roles == {"x": "Time", "fit_weight": "W", "yerr": "Error"}


def test_calculate_step_formula_edit_resets_stale_sources():
    step = CalculateColumnStep("C2/C1", "ratio", "col2/col1", ["Voltage", "Time"], [2, 1])
    step.update(formula_original="col1 * 3")
    assert (step.formula, step.formula_original, step.source_columns) == ("col1 * 3", "col1 * 3", [])

    pp = _physplot()
    pp.run_workflow([step])
    assert pp.dataset.dataframe["ratio"].tolist() == [3.0, 6.0, 9.0]


def test_insert_and_move_steps():
    pp = PhysPlot()
    a, b, c = (TransformColumnStep("Voltage", "multiply", name) for name in "abc")
    pp.workflow = [a, c]

    pp.insert_step(1, b)
    assert pp.workflow == [a, b, c]
    pp.insert_step(3, a)
    assert pp.workflow[-1] is a

    pp.workflow = [a, b, c]
    assert pp.move_step(0, 2) is a
    assert pp.workflow == [b, c, a]

    with pytest.raises(IndexError):
        pp.insert_step(5, a)
    with pytest.raises(IndexError):
        pp.move_step(0, 3)


def test_disabled_step_survives_export_and_import(tmp_path):
    pp = _physplot()
    pp.workflow = [
        TransformColumnStep("Voltage", "multiply", "V_mV", params={"factor": 1000}, enabled=False),
        SetRoleStep({"x": "Time", "y": "Voltage"}),
    ]
    path = pp.export_workflow(tmp_path / "sequence.py")

    steps = load_workflow(path)

    assert [step.enabled for step in steps] == [False, True]
    assert steps[0].params == {"factor": 1000}
