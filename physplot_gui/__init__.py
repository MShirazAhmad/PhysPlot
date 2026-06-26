"""Modern PhysPlot GUI package."""

from __future__ import annotations


def run_app(*args, **kwargs):
    from .app.runner import run_app as _run_app

    return _run_app(*args, **kwargs)

__all__ = ["run_app"]
