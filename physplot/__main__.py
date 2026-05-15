"""Run PhysPlot with ``python -m physplot``.

Input data structure:
    Uses command-line arguments already present in ``sys.argv``; no custom
    arguments are currently parsed.

Return type:
    No Python value is returned. The process exits when the Qt event loop
    finishes.

Optional main/runtime behavior:
    When executed as a module, calls ``run_app()`` to launch the GUI.
"""

from .runner import run_app


if __name__ == "__main__":
    run_app()
