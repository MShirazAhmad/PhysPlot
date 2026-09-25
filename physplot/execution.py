"""Step-by-step sequence execution with per-step results and resume points.

``execute_steps`` runs workflow steps in order and records one
``StepResult`` per step. Execution always stops at the first failing step:
that step is reported as ``failed`` and every later step as ``skipped``. The
caller chooses whether the failure is re-raised (``raise_on_error=True``, the
behavior of ``PhysPlot.run_workflow``) or only reported.

When a ``SnapshotStore`` is supplied, the backend state is captured before
each executed step. ``PhysPlot.rerun_from`` restores one of these snapshots
and resumes from there instead of replaying the whole sequence. Each snapshot
is tagged with a fingerprint of the generated code of every step before it,
so a snapshot is only reused while those earlier steps are unchanged.
"""

from __future__ import annotations

import copy
import hashlib
import time
from dataclasses import dataclass

MODULE_ID = "physplot.execution"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-09-25-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"

STATUS_OK = "ok"
STATUS_FAILED = "failed"
STATUS_SKIPPED = "skipped"

DEFAULT_SNAPSHOT_LIMIT = 20


@dataclass
class StepResult:
    """Outcome of one workflow step in a sequence run."""

    index: int
    step: object
    status: str
    error: str | None = None
    duration_s: float = 0.0

    @property
    def step_name(self) -> str:
        return type(self.step).__name__

    @property
    def ok(self) -> bool:
        return self.status == STATUS_OK


@dataclass
class Snapshot:
    """Backend state captured immediately before step ``index`` ran."""

    index: int
    fingerprint: str
    dataset: object
    fit_result: object
    last_figure: object

    @classmethod
    def capture(cls, physplot, index: int, fingerprint: str) -> "Snapshot":
        dataset = physplot.dataset.copy() if physplot.dataset is not None else None
        return cls(
            index=index,
            fingerprint=fingerprint,
            dataset=dataset,
            fit_result=_safe_deepcopy(physplot.fit_result),
            last_figure=physplot.last_figure,
        )

    def restore_into(self, physplot) -> None:
        # Copy again so the stored snapshot stays pristine for later reruns.
        physplot.dataset = self.dataset.copy() if self.dataset is not None else None
        physplot.fit_result = _safe_deepcopy(self.fit_result)
        physplot.last_figure = self.last_figure


class SnapshotStore:
    """Bounded collection of resume points keyed by step index.

    The earliest snapshot (normally the start of the run) is always kept;
    beyond that the most recent ones are retained up to ``limit``, which
    favours resuming near the end of long sequences where most iteration
    happens.
    """

    def __init__(self, limit: int = DEFAULT_SNAPSHOT_LIMIT):
        self.limit = max(2, int(limit))
        self._items: dict[int, Snapshot] = {}

    def __len__(self) -> int:
        return len(self._items)

    def indices(self) -> list[int]:
        return sorted(self._items)

    def clear(self) -> None:
        self._items.clear()

    def put(self, snapshot: Snapshot) -> None:
        self._items[snapshot.index] = snapshot
        while len(self._items) > self.limit:
            # Keep the earliest resume point; drop the next-oldest one.
            del self._items[sorted(self._items)[1]]

    def discard_after(self, index: int) -> None:
        for key in [key for key in self._items if key > index]:
            del self._items[key]

    def best_for(self, steps, index: int) -> Snapshot | None:
        """Return the latest valid snapshot at or before ``index``."""
        fingerprints = cumulative_fingerprints(steps)
        for key in sorted((key for key in self._items if key <= index), reverse=True):
            snapshot = self._items[key]
            if key < len(fingerprints) and fingerprints[key] == snapshot.fingerprint:
                return snapshot
        return None


def cumulative_fingerprints(steps) -> list[str]:
    """Return ``fingerprints[k]`` identifying ``steps[:k]`` for every ``k``.

    The list has ``len(steps) + 1`` entries. Steps are identified by their
    generated code; a step that cannot produce code is identified by object
    identity, which never matches across edits and so never reuses a stale
    snapshot.
    """
    digest = hashlib.sha1()
    fingerprints = [digest.hexdigest()]
    for step in steps:
        try:
            code = step.to_code()
        except Exception:
            code = f"<{type(step).__name__} at {id(step):#x}>"
        digest.update(code.encode("utf-8", errors="replace"))
        digest.update(b"\x1e")
        fingerprints.append(digest.hexdigest())
    return fingerprints


def execute_steps(
    physplot,
    steps,
    *,
    start_index: int = 0,
    allow_column_number_fallback: bool = False,
    raise_on_error: bool = True,
    snapshots: SnapshotStore | None = None,
    prior_results: list[StepResult] | None = None,
) -> list[StepResult]:
    """Run ``steps[start_index:]`` on ``physplot`` and report every step.

    ``prior_results`` supplies the reported results for steps before
    ``start_index``; steps without one are reported as ``skipped`` because
    they did not run. The complete list is stored on
    ``physplot.last_results`` before any exception is re-raised.
    """
    steps = list(steps)
    if not 0 <= start_index <= len(steps):
        raise IndexError(f"start_index {start_index} is outside a sequence of {len(steps)} steps.")

    prior_by_index = {result.index: result for result in (prior_results or [])}
    results: list[StepResult] = []
    for index in range(start_index):
        results.append(prior_by_index.get(index) or StepResult(index, steps[index], STATUS_SKIPPED))

    fingerprints = cumulative_fingerprints(steps) if snapshots is not None else None

    failure: BaseException | None = None
    for index in range(start_index, len(steps)):
        step = steps[index]
        if failure is not None:
            results.append(StepResult(index, step, STATUS_SKIPPED))
            continue
        if snapshots is not None:
            snapshots.put(Snapshot.capture(physplot, index, fingerprints[index]))
        started = time.perf_counter()
        try:
            step.apply(physplot, allow_column_number_fallback=allow_column_number_fallback)
        except Exception as exc:
            failure = exc
            results.append(
                StepResult(
                    index,
                    step,
                    STATUS_FAILED,
                    error=f"{type(exc).__name__}: {exc}",
                    duration_s=time.perf_counter() - started,
                )
            )
            continue
        results.append(StepResult(index, step, STATUS_OK, duration_s=time.perf_counter() - started))

    physplot.last_results = results
    if failure is not None and raise_on_error:
        raise failure
    return results


def first_failure(results: list[StepResult]) -> StepResult | None:
    for result in results:
        if result.status == STATUS_FAILED:
            return result
    return None


def _safe_deepcopy(value):
    try:
        return copy.deepcopy(value)
    except Exception:
        return copy.copy(value)
