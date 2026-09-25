"""Per-step execution results and rerun-from-step (Advanced Mode plan, phase 1)."""

from __future__ import annotations

import pandas as pd
import pytest

from physplot import PhysPlot
from physplot.execution import Snapshot, SnapshotStore, first_failure
from physplot.steps import SetRoleStep, TransformColumnStep
from physplot.steps.base import WorkflowStep


class CountingStep(WorkflowStep):
    """Adds a constant column and counts how often it really ran."""

    def __init__(self, name: str, value: float = 1.0):
        self.name = name
        self.value = value
        self.calls = 0

    def apply(self, physplot, allow_column_number_fallback: bool = False):
        self.calls += 1
        physplot.dataset.add_column(self.name, [self.value] * len(physplot.dataset.dataframe), {"derived": True})

    def to_code(self) -> str:
        return f"CountingStep({self.name!r}, {self.value!r})"


def _physplot() -> PhysPlot:
    pp = PhysPlot()
    pp.load(pd.DataFrame({"Time": [1.0, 2.0, 3.0], "Voltage": [2.0, 4.0, 8.0]}), loader="dataframe")
    return pp


def _statuses(results):
    return [result.status for result in results]


def test_failure_marks_failed_step_and_skips_the_rest():
    pp = _physplot()
    steps = [
        SetRoleStep(roles={"x": "Time", "y": "Voltage"}),
        TransformColumnStep("Volts", "normalize_max", "V_norm"),
        TransformColumnStep("Voltage", "multiply", "V_mV", params={"factor": 1000}),
        SetRoleStep(roles={"y": "V_mV"}),
    ]

    results = pp.run_workflow_detailed(steps)

    assert _statuses(results) == ["ok", "failed", "skipped", "skipped"]
    assert results[1].error == "ValueError: Column 'Volts' not found."
    assert results[1].step is steps[1]
    assert first_failure(results) is results[1]
    assert pp.last_results == results
    assert "V_mV" not in pp.dataset.dataframe.columns
    assert pp.dataset.column_roles == {"Time": "X", "Voltage": "Y"}


def test_successful_run_reports_ok_with_durations():
    pp = _physplot()
    results = pp.run_workflow_detailed([TransformColumnStep("Voltage", "normalize_max", "V_norm")])

    assert _statuses(results) == ["ok"]
    assert results[0].duration_s >= 0
    assert pp.dataset.dataframe["V_norm"].tolist() == [0.25, 0.5, 1.0]


def test_run_workflow_still_raises_original_exception_and_records_results():
    pp = _physplot()
    steps = [SetRoleStep(roles={"x": "Time"}), TransformColumnStep("Missing", "normalize_max", "out")]

    with pytest.raises(ValueError, match="Column 'Missing' not found"):
        pp.run_workflow(steps)

    assert _statuses(pp.last_results) == ["ok", "failed"]


def test_raise_on_error_reraises_after_recording_results():
    pp = _physplot()
    with pytest.raises(ValueError):
        pp.run_workflow_detailed([TransformColumnStep("Missing", "normalize_max", "out")], raise_on_error=True)
    assert _statuses(pp.last_results) == ["failed"]


def test_rerun_from_fixed_step_does_not_replay_earlier_steps():
    pp = _physplot()
    first = CountingStep("Offset", 5.0)
    steps = [
        first,
        TransformColumnStep("Volts", "multiply", "V_mV", params={"factor": 1000}),
        SetRoleStep(roles={"x": "Time", "y": "V_mV"}),
    ]
    pp.run_workflow_detailed(steps)
    assert first.calls == 1

    steps[1] = TransformColumnStep("Voltage", "multiply", "V_mV", params={"factor": 1000})
    results = pp.rerun_from(1, steps)

    assert first.calls == 1
    assert _statuses(results) == ["ok", "ok", "ok"]
    assert pp.dataset.dataframe["V_mV"].tolist() == [2000.0, 4000.0, 8000.0]
    assert pp.dataset.dataframe["Offset"].tolist() == [5.0, 5.0, 5.0]
    assert pp.dataset.column_roles["V_mV"] == "Y"


def test_rerun_restores_state_from_before_the_step():
    pp = _physplot()
    steps = [CountingStep("A"), CountingStep("B")]
    pp.run_workflow_detailed(steps)
    pp.dataset.dataframe.loc[0, "Voltage"] = -1.0  # later mutation must not leak into the resume point

    pp.rerun_from(1, steps)

    assert pp.dataset.dataframe.loc[0, "Voltage"] == 2.0
    assert list(pp.dataset.dataframe.columns) == ["Time", "Voltage", "A", "B"]
    assert steps[1].calls == 2


def test_rerun_falls_back_to_start_when_earlier_steps_changed():
    pp = _physplot()
    steps = [CountingStep("A"), CountingStep("B")]
    pp.run_workflow_detailed(steps)

    edited = [CountingStep("A", 99.0), steps[1]]
    results = pp.rerun_from(1, edited)

    # The resume point before step 2 no longer matches, so the run restarts
    # from the saved start state and replays the edited first step.
    assert _statuses(results) == ["ok", "ok"]
    assert edited[0].calls == 1
    assert pp.dataset.dataframe["A"].tolist() == [99.0, 99.0, 99.0]


def test_rerun_without_a_previous_run_raises():
    pp = _physplot()
    with pytest.raises(RuntimeError):
        pp.rerun_from(0, [CountingStep("A")])
    with pytest.raises(IndexError):
        pp.rerun_from(3, [CountingStep("A")])


def test_run_workflow_does_not_keep_snapshots():
    pp = _physplot()
    pp.run_workflow([CountingStep("A")])
    assert len(pp._snapshots) == 0


def test_snapshot_store_keeps_earliest_and_latest():
    pp = _physplot()
    store = SnapshotStore(limit=3)
    for index in range(6):
        store.put(Snapshot.capture(pp, index, f"f{index}"))
    assert store.indices() == [0, 4, 5]


def test_dataset_copy_is_independent():
    pp = _physplot()
    pp.dataset.set_role("Time", "X")
    duplicate = pp.dataset.copy()

    duplicate.dataframe.loc[0, "Time"] = 100.0
    duplicate.column_roles["Voltage"] = "Y"
    duplicate.column_metadata["Time"]["unit"] = "s"

    assert pp.dataset.dataframe.loc[0, "Time"] == 1.0
    assert pp.dataset.column_roles["Voltage"] == "Ignore"
    assert pp.dataset.column_metadata["Time"].get("unit") is None
    assert duplicate.column_roles["Time"] == "X"
