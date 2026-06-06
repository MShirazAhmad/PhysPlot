"""Base workflow step types."""

from __future__ import annotations

MODULE_ID = "physplot.steps.base"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-05-30-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


class WorkflowStep:
    """Abstract workflow step."""

    def apply(self, physplot):
        raise NotImplementedError

    def to_code(self) -> str:
        raise NotImplementedError
