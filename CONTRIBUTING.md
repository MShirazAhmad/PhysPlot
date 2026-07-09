# Contributing to PhysPlot

Thank you for your interest in improving PhysPlot.

## Noncommercial Development

Forks and pull requests are welcome for noncommercial development. You may study the code, make noncommercial improvements, create tutorials, write guides, report issues, and propose revisions through pull requests.

Commercial use of PhysPlot, including commercial distribution, commercial services, or commercial products based on PhysPlot, is not allowed without prior written permission from the project originator.

## Pull Requests

Only pull requests merged by the maintainer are official PhysPlot revisions. Opening a pull request does not make a change part of an official PhysPlot release.

Please keep pull requests focused and explain:

- What problem the change solves
- How the change was tested
- Whether the change affects the GUI, file loaders, functions, plotter modules,
  curve fitting, workflow steps, documentation, or packaging

For GUI changes, check the table-first layout, Simple/Advanced mode switcher,
native menu bar, Help/About links, and branded header. Scientific logic should
remain in `physplot/`; the GUI should orchestrate backend APIs rather than
duplicating loader, transformation, plotting, fitting, or workflow behavior.

Useful local checks:

```bash
python -m pytest
QT_QPA_PLATFORM=offscreen python -m pytest tests/test_protocol_sequence_editor.py
python -m build
python -m twine check dist/*
```

## Reporting Issues

Bug reports and feature requests may be submitted at:

https://github.com/MShirazAhmad/PhysPlot/issues

Project documentation is available at:

https://physplot.readthedocs.io/en/latest/
