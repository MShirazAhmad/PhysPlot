# Protocol Modules

Reusable building blocks for protocol sequences. Each file is a normal PhysPlot
sequence file that defines `WORKFLOW_STEPS` (or `build_workflow()`), plus
optional `DISPLAY_NAME` and `DESCRIPTION` strings.

Modules appear under **Protocol > Insert Protocol Module** in the GUI; choosing
one appends its steps to the current Build Protocol sequence. Headless users
can import them like any sequence:

```python
from physplot.workflow import load_workflow
steps = load_workflow("config/protocol_modules/normalize_and_plot.py")
```

Use `config/sequences/` for complete runnable sequences and this folder for
smaller reusable fragments. The per-user copy in
`Documents/PhysPlot/config/protocol_modules/` is searched first.
