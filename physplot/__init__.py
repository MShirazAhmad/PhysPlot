"""PhysPlot application package.

Input data structure:
    No external input is consumed at import time.

Return type:
    Exposes ``run_app`` as the public package entry point.

Optional main/runtime behavior:
    Importing this package does not start the GUI. Call ``run_app()`` or run
    ``python -m physplot`` to launch PhysPlot.
"""

from .runner import run_app

__all__ = ["run_app"]
