# Figure Editor plugins

FigureForge plugins copied into the Figure Editor's plugin folder each time the
editor opens. Bundled plugins are copied first; files with the same name in
`Documents/PhysPlot/config/figureforge_plugins/` override them.

Only `*.py` files are copied. When a file here is renamed or deleted, PhysPlot also
deletes its copy from the Figure Editor. A file named like one of the Figure Editor's
own files (`__init__.py`, `add_legend.py`, `utils.py`, ...) is not copied.

To have an AI assistant write a plugin, attach `AI_GUIDE.md` from this folder to the chat.
