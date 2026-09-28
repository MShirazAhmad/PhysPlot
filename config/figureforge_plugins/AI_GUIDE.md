# Figure Editor Plugins: guide for AI assistants

> **PhysPlot users:** attach this file to a chat with any AI assistant (ChatGPT, Claude, Gemini, Copilot, ...), together with a screenshot of the Figure Editor or of the figure you want to change, if that helps to explain the tool. Then describe what you want. The assistant replies with one complete file: save it in `Documents/PhysPlot/config/figureforge_plugins/` and open a new Figure Editor window (**Generate Plot**, then **Advanced Styling…** in the plot window); the new command is in the **Figure Editor** menu. Step-by-step help: https://physplot.readthedocs.io/en/latest/extensions/ai_assistant.html

## Your task

Write one Python file that adds a command to the Figure Editor. The Figure Editor is built into PhysPlot (package `physplot_gui.figure_editor`, a PyQt6 window that started from FigureForge 0.3). It opens inside PhysPlot, on the same figure as the plot window, from **Advanced Styling…** in any plot window (or straight away when **Advanced Figure Editor** is ticked). The user selects a part of the figure, by clicking it on the figure or in the **Figure Explorer** tree (the Figure, an Axes, a line, a spine, ...), then chooses the command. The editor calls the plugin's `run(obj)` with the selected Matplotlib object, the plugin changes the figure, and the editor redraws it.

Good uses: one-click restyling that the Property Inspector and templates cannot do (tick direction, minor ticks), reference lines, annotations, fits, or small calculations shown in a message box. Changes apply to the plot window's figure straight away and are included in **Export Plot**, but they are not recorded in the protocol, so replays and bulk runs do not repeat them; the user can also save the result with the editor's **Export Figure**. The user is a scientist, not a programmer, so write plain, readable code with short comments.

## Ask the user first

Ask in one short list for what the request does not say:

1. What the command does, and to which part: the whole figure, one axes, or one line or scatter series.
2. Which settings it asks for each time in a small dialog, and which are fixed values.
3. The menu text, and the submenu to put it in. Existing submenus: **PhysPlot**, **Fitting**, **Ticks**, **Spines**, **Legends**, **Annotations**.

If the request needs something a plugin cannot do (change PhysPlot's table or protocol, or be repeated automatically in replays and bulk runs), say so first.

## The file PhysPlot expects

How the file is loaded:

- Each time a Figure Editor window opens, it loads every `*.py` file in place from PhysPlot's bundled `config/figureforge_plugins/` folder and then from `Documents/PhysPlot/config/figureforge_plugins/`; a file in the Documents folder replaces a bundled or built-in one of the same name. Nothing is copied anywhere.
- Each file is imported as the module `physplot_gui.figure_editor.plugins.<file name>` while the editor window is being built, inside the running PhysPlot application. The editor then builds the menu from the imported classes. A file that fails to import is left out of the menu, and the editor's status bar names it and the error.
- Every class defined in the file becomes one menu command. Imported classes (such as `Axes`) do not count.

The command class:

| Name | Required | Meaning |
|---|---|---|
| `name` | yes | Class attribute, `str`: the menu text. |
| `run(self, obj)` | yes | Called when the user chooses the command, with the object selected in the Figure Explorer. Not called at all when nothing is selected. |
| `tooltip` | no | Class attribute, `str`: shown when the mouse rests on the menu item. |
| `submenu` | no | Class attribute, `str`: puts the command in **Figure Editor → <submenu>**. Commands with the same `submenu` share one submenu, including the existing ones. Without it, the command sits directly in the **Figure Editor** menu. |
| `icon` | no | Path to a small PNG shown next to the menu text, for example `os.path.join(os.path.dirname(__file__), "journal_ticks.png")` with the image saved next to the plugin. Usually leave it out. |

The editor creates the class with no arguments: once at start-up (the first class of the file, in alphabetical order, that has a `run` method) and again at every click. An `__init__`, if any, takes no arguments.

What `run` receives, depending on the selected tree item:

| Selected item | `obj` |
|---|---|
| **Figure** (top of the tree) | `matplotlib.figure.Figure`. Its axes: `obj.get_axes()`. |
| **Axes** | `matplotlib.axes.Axes` |
| A line, the LSQ fit line | `matplotlib.lines.Line2D` |
| A scatter series | `matplotlib.collections.PathCollection` |
| Title, axis label, tick label, other text | `matplotlib.text.Text` |
| A spine | `matplotlib.spines.Spine` |
| **XAxis** / **YAxis** | `matplotlib.axis.XAxis` / `matplotlib.axis.YAxis` |
| Legend, background patches, annotations | `Legend`, `Rectangle`, `Annotation`, ... |

Most objects have `.axes` (the Axes they belong to, or `None`) and `.figure`. A `Figure` also has an `axes` attribute, but it is a list, so test for `Figure` first. After `run` returns, the editor redraws the canvas (and the plot window) and rebuilds the Figure Explorer, so `run` does not need to draw.

Before opening the editor, PhysPlot adds hidden placeholders to each axes that lacks such an artist: an empty line labelled `_physplot_template_line`, an empty scatter `_physplot_template_scatter`, an invisible annotation `_physplot_template_annotation` and a hidden empty legend. When looping over `axes.lines` or `axes.collections`, skip artists that are not visible or whose label starts with `_`.

Available in PhysPlot's Python: Python 3.12 to 3.14 and its standard library, PyQt6 (6.11 or newer), Matplotlib (3.11 or newer), NumPy 2.x, SciPy and pandas. The Qt-free PhysPlot modules also work, for example `physplot_gui.plot_styles` (`apply_style_module`, `list_style_modules`) and `physplot_gui.fit_styles`.

## Rules

- Use PyQt6 for every dialog (`from PyQt6.QtWidgets import ...`): `QInputDialog`, `QMessageBox`, `QFileDialog`, or a `QDialog` built inside `run`. Never import PySide6, PyQt5 or tkinter: the editor runs inside PhysPlot's PyQt6 application. Use full enum names such as `QMessageBox.Icon.Warning` and `QDialog.DialogCode.Accepted`.
- Top-level code may only import packages and define constants, functions and classes. An error there (a syntax error, a missing package) leaves the command out of the menu; the editor's status bar names the file and the error. Do not create widgets or dialogs there or in `__init__`: create them inside `run`.
- Put one command class in the file and write helpers as functions. If a helper class is unavoidable (for example a `QDialog` subclass), add `Helper.__module__ = __name__ + "._internal"` right after it, as PhysPlot's own plugins do. Otherwise the editor treats it as a command, fails because it has no `name`, and may drop the real command from the menu.
- Check the type of `obj` first. If the command cannot use it, show a `QMessageBox` warning that says what to select, and return.
- Wrap the work in `try`/`except Exception` and show a clear `QMessageBox` that says what went wrong and what to do. (An error that escapes `run` is caught by the editor and shown as *Plugin Error* with the traceback, which is harder for the user to read.)
- Change only the figure that `obj` belongs to. Do not use `matplotlib.pyplot` (`plt.gca()`, `plt.figure()`, `plt.show()`), which would create or show other figures.
- No network access, no `subprocess`, no deleting or overwriting files. Write a file only to a path the user chose in a `QFileDialog`. Do not rely on `print`: nobody sees it.
- File name: lowercase letters, digits and underscores, ending in `.py`, for example `journal_ticks.py`. Do not reuse the name of a built-in command file (`add_annotation.py`, `add_legend.py`, `add_minor_data_ticks.py`, `reduce_tick_limits.py`, `set_spine_bounds.py`, `toggle_spines.py`) or of PhysPlot's `physplot_fit_function.py` / `physplot_save_style_module.py` unless you mean to replace that command: a file with the same name replaces it in the menu.
- Start the file with a docstring that says what the command does and what to select. No `if __name__ == "__main__":` block and no test code.

## Complete working example

The user asked: "The journal wants ticks pointing inward on all four sides, with minor ticks. Templates cannot do that; I want one click in the Figure Editor, and to choose in or out each time."

`journal_ticks.py`:

```python
"""Figure Editor plugin: journal-style ticks on every side of the axes.

Select the Figure (all axes), an Axes, or any part of one axes, then choose
Figure Editor > Ticks > Journal Ticks. A dialog asks for the tick direction.
The command draws major and minor ticks on the bottom, top, left and right
axes, with lengths and widths that suit a single-column figure.
"""

from matplotlib.axes import Axes
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QInputDialog, QMessageBox


class JournalTicks:
    name = "Journal Ticks"
    tooltip = "Ticks on all four sides with minor ticks, pointing in, out, or both."
    submenu = "Ticks"

    def run(self, obj):
        axes_list = self._axes_for(obj)
        if not axes_list:
            self._warn("Select the Figure, an Axes, or a part of an Axes first.")
            return

        direction, ok = QInputDialog.getItem(
            None, "Journal Ticks", "Tick direction:", ["in", "out", "inout"], 0, False
        )
        if not ok:
            return  # the user pressed Cancel

        try:
            for axes in axes_list:
                axes.minorticks_on()
                axes.tick_params(axis="both", which="both", direction=direction, top=True, right=True)
                axes.tick_params(axis="both", which="major", length=4.0, width=0.8)
                axes.tick_params(axis="both", which="minor", length=2.0, width=0.6)
        except Exception as exc:
            self._warn(str(exc))

    @staticmethod
    def _axes_for(obj):
        """Return the axes to change for the selected object (empty list if none)."""
        if isinstance(obj, Figure):
            return list(obj.get_axes())
        if isinstance(obj, Axes):
            return [obj]
        axes = getattr(obj, "axes", None)  # lines, spines, texts, XAxis, YAxis, legends
        if isinstance(axes, Axes):
            return [axes]
        return []

    @staticmethod
    def _warn(message):
        box = QMessageBox()
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle("Journal Ticks")
        box.setText("Could not change the ticks.")
        box.setInformativeText(message)
        box.exec()
```

The command appears as **Figure Editor → Ticks → Journal Ticks**, next to the editor's own tick commands. With the Figure selected it changes every axes of the figure.

## Reply format

```
Reply with:
1. The file name on its own line, for example `journal_ticks.py`.
2. The complete file in one code block. Never shorten it or leave placeholders such as "..." or "rest unchanged".
3. Two or three short sentences: what the module does and anything the user should check.
If you change the file after the user reports an error, send the complete corrected file again.
```

## How the user tests it

1. Save the file in `Documents/PhysPlot/config/figureforge_plugins/` (**File → Open Config Folder** opens `Documents/PhysPlot/config/`). The name must end in `.py`, not `.py.txt`.
2. Close any open Figure Editor window: plugins are loaded when a new one opens. **File → Reload Config Modules** is not needed.
3. In PhysPlot, load data, set the roles and click **Generate Plot** (or **Plot → Generate Plot**, Ctrl+G), then **Advanced Styling…** in the plot window. The Figure Editor opens.
4. Select the right part (click it on the figure, or in the Figure Explorer; for the example: **Axes** or **Figure**), then choose the command in the **Figure Editor** menu.
5. Check the figure (the plot window follows), then save it with **Export Figure** in the editor or **Export Plot** in PhysPlot.

Optional check in Python, in the environment where PhysPlot is installed (for example a Jupyter notebook). It runs the file's top-level code as the editor does and lists the menu commands it will create; an error here would also stop the Figure Editor from opening. Replace the file name with the real one:

```python
import importlib.util
import inspect
from physplot.user_paths import user_plugin_dir

path = user_plugin_dir("figureforge_plugins") / "journal_ticks.py"
spec = importlib.util.spec_from_file_location("plugin_check", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
for _, cls in inspect.getmembers(module, inspect.isclass):
    if cls.__module__ == module.__name__:
        print(getattr(cls, "submenu", "(no submenu)"), ">", cls.name, "| run:", callable(getattr(cls, "run", None)))
```

For the example it prints `Ticks > Journal Ticks | run: True`.

## If PhysPlot shows an error

The user will paste the message or describe what they see. Find the matching case, fix the cause and send the complete corrected file.

| What the user sees | Likely cause and what to change |
|---|---|
| The editor's status bar says *Plugins that could not be loaded: <file>: <error>* | The file raises an error when it is imported: a syntax error, a missing package, or code at top level. Fix it, save it under the same name and open a new Figure Editor window. |
| The command is missing from the menu | The class has no `name`; a helper class was not hidden with `__module__ = __name__ + "._internal"`; the file is in the wrong folder or ends in `.py.txt`; or the Figure Editor was opened before the file was saved. |
| The status bar says *Select a part of the figure first* | Nothing was selected. Click a part of the figure (or an item in the Figure Explorer) before choosing the command. |
| A *Plugin Error* box with a traceback appears | `run` raised an error. Read the message: usually the wrong kind of object was selected, or data is missing (for example no visible line). Add the type check and a `try`/`except` with a clear message. |
| The command shows its own error message | Read the message and handle that case with a clearer warning. |
| An old version of the command still appears | The file was renamed and the old file is still in `Documents/PhysPlot/config/figureforge_plugins/`. Delete it. |
| `ModuleNotFoundError: No module named '...'` | That package is not installed in PhysPlot's Python. Use only the packages listed above. |

Finding an import error: the editor's status bar names the file and the error when it opens. The Python check under *How the user tests it* prints the full traceback.
