# Figure Editor Plugins: guide for AI assistants

> **PhysPlot users:** attach this file to a chat with any AI assistant (ChatGPT, Claude, Gemini, Copilot, ...), together with a screenshot of the Figure Editor or of the figure you want to change, if that helps to explain the tool. Then describe what you want. The assistant replies with one complete file: save it in `Documents/PhysPlot/config/figureforge_plugins/` and open a new Figure Editor window (**Generate Plot** with the Basic Plotter); the new command is in the **Figure Editor** menu. Step-by-step help: https://physplot.readthedocs.io/en/latest/extensions/ai_assistant.html

## Your task

Write one Python file that adds a command to the Figure Editor. The Figure Editor is FigureForge 0.3 (a PySide6 program) that PhysPlot opens in a separate process for Basic Plotter plots; its plugin menu is renamed **Figure Editor**. The user selects a part of the figure in the **Figure Explorer** tree (the Figure, an Axes, a line, a spine, ...), then chooses the command. FigureForge calls the plugin's `run(obj)` with the selected Matplotlib object, the plugin changes the figure, and FigureForge redraws it.

Good uses: one-click restyling that the Property Inspector and templates cannot do (tick direction, minor ticks), reference lines, annotations, fits, or small calculations shown in a message box. Changes stay in that Figure Editor window. They are not sent back to PhysPlot, not recorded in the protocol, and not part of **Export Plot**; the user saves the result with the editor's **File → Export** or **File → Save**. The user is a scientist, not a programmer, so write plain, readable code with short comments.

## Ask the user first

Ask in one short list for what the request does not say:

1. What the command does, and to which part: the whole figure, one axes, or one line or scatter series.
2. Which settings it asks for each time in a small dialog, and which are fixed values.
3. The menu text, and the submenu to put it in. Existing submenus: **PhysPlot**, **Fitting**, **Ticks**, **Spines**, **Legends**, **Annotations**.

If the request needs something a plugin cannot do (change PhysPlot's table or protocol, or apply to plots that open in a plot window instead of the Figure Editor), say so first.

## The file PhysPlot expects

How the file is loaded:

- Each time PhysPlot opens a Figure Editor window, it copies every `*.py` file from its bundled `config/figureforge_plugins/` folder and then from `Documents/PhysPlot/config/figureforge_plugins/` into FigureForge's own `plugins` folder, overwriting files of the same name. Other file types are not copied. PhysPlot remembers which files it copied and deletes the copy of a file that has since been renamed or deleted, so a renamed plugin does not load twice.
- A file named like one of FigureForge's own files (see **Rules**) is not copied. PhysPlot shows *Figure Editor plugin skipped*, asks the user to rename it, and opens the Figure Editor without it.
- The new Figure Editor process imports each file once, as the module `FigureForge.plugins.<file name>`, while FigureForge itself is imported and before any window exists. It then builds the menu from the imported classes.
- Every class defined in the file becomes one menu command. Imported classes (such as `Axes`) do not count.

The command class:

| Name | Required | Meaning |
|---|---|---|
| `name` | yes | Class attribute, `str`: the menu text. |
| `run(self, obj)` | yes | Called when the user chooses the command, with the object selected in the Figure Explorer. Not called at all when nothing is selected. |
| `tooltip` | no | Class attribute, `str`: shown when the mouse rests on the menu item. |
| `submenu` | no | Class attribute, `str`: puts the command in **Figure Editor → <submenu>**. Commands with the same `submenu` share one submenu, including the existing ones. Without it, the command sits directly in the **Figure Editor** menu. |
| `icon` | no | Do not use: it is a path to an image file, and PhysPlot copies only `.py` files. |

FigureForge creates the class with no arguments: once at start-up (the first class of the file, in alphabetical order, that has a `run` method) and again at every click. An `__init__`, if any, takes no arguments.

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

Most objects have `.axes` (the Axes they belong to, or `None`) and `.figure`. A `Figure` also has an `axes` attribute, but it is a list, so test for `Figure` first. After `run` returns, FigureForge redraws the canvas and rebuilds the Figure Explorer, so `run` does not need to draw.

Before opening the editor, PhysPlot adds hidden placeholders to each axes that lacks such an artist: an empty line labelled `_physplot_template_line`, an empty scatter `_physplot_template_scatter`, an invisible annotation `_physplot_template_annotation` and a hidden empty legend. When looping over `axes.lines` or `axes.collections`, skip artists that are not visible or whose label starts with `_`.

Available in the Figure Editor process: Python 3.11 to 3.13 and its standard library, PySide6 (6.7 or newer), Matplotlib (3.9 or newer), NumPy 1.x (FigureForge requires NumPy below 2), SciPy and pandas. The Qt-free PhysPlot modules also work, for example `physplot_gui.plot_styles` (`apply_style_module`, `list_style_modules`) and `physplot_gui.fit_styles`.

## Rules

- Use PySide6 for every dialog: `QInputDialog`, `QMessageBox`, `QFileDialog`, or a `QDialog` built inside `run`. Never import PyQt6, PyQt5 or tkinter. Use full enum names such as `QMessageBox.Icon.Warning` and `QDialog.DialogCode.Accepted`.
- Top-level code may only import packages and define constants, functions and classes. It runs before a Qt application exists. An error there (a syntax error, a missing package) stops the Figure Editor from opening at all, for every plot, until the file is fixed or removed; PhysPlot then shows *Figure Editor failed* with the file name and the error. Creating a widget or dialog there, or in `__init__`, makes the Figure Editor abort before its window opens.
- Put one command class in the file and write helpers as functions. If a helper class is unavoidable (for example a `QDialog` subclass), add `Helper.__module__ = __name__ + "._internal"` right after it, as PhysPlot's own plugins do. Otherwise FigureForge treats it as a command, fails because it has no `name`, and may drop the real command from the menu.
- Check the type of `obj` first. If the command cannot use it, show a `QMessageBox` warning that says what to select, and return.
- Wrap the work in `try`/`except Exception` and show the error text in a `QMessageBox`. FigureForge does not show errors raised in `run`; nothing visible would happen.
- Change only the figure that `obj` belongs to. Do not use `matplotlib.pyplot` (`plt.gca()`, `plt.figure()`, `plt.show()`), which would create or show other figures.
- No network access, no `subprocess`, no deleting or overwriting files. Write a file only to a path the user chose in a `QFileDialog`. Do not rely on `print`: nobody sees it.
- File name: lowercase letters, digits and underscores, ending in `.py`, for example `journal_ticks.py`. It must not be the name of one of FigureForge's own files, in any capitalisation: `__init__.py`, `add_annotation.py`, `add_legend.py`, `add_minor_data_ticks.py`, `reduce_tick_limits.py`, `set_spine_bounds.py`, `toggle_spines.py`, or `utils.py`. PhysPlot refuses to copy such a file, because it would overwrite part of the Figure Editor. Use `physplot_fit_function.py` or `physplot_save_style_module.py` only to replace PhysPlot's own commands on purpose.
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
from PySide6.QtWidgets import QInputDialog, QMessageBox


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

The command appears as **Figure Editor → Ticks → Journal Ticks**, next to FigureForge's own tick commands. With the Figure selected it changes every axes of the figure.

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
2. Close any open Figure Editor window. It does not see the new file: PhysPlot copies plugins only when it opens a new one. **File → Reload Config Modules** is not needed.
3. In PhysPlot, load data, set the X and Y columns, choose the **Basic Plotter** and click **Generate Plot** (or **Plot → Generate Plot**, Ctrl+G). The Figure Editor opens.
4. Select the right item in the Figure Explorer (for the example: **Axes** or **Figure**), then choose the command in the **Figure Editor** menu.
5. Check the figure, then save it with **File → Export** in the Figure Editor.

Optional check in Python, in the environment where PhysPlot is installed (for example a Jupyter notebook). It runs the file's top-level code as FigureForge does and lists the menu commands it will create; an error here would also stop the Figure Editor from opening. Replace the file name with the real one:

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

When a plugin stops the Figure Editor from starting, PhysPlot shows **Figure Editor failed** a few seconds after **Generate Plot**. The message names the plugin file and quotes the last line of the error. **Show Details...** in that dialog holds the full error output (the Python traceback), which the user can copy into the chat. The traceback shows the path of PhysPlot's copy inside FigureForge's `plugins` folder; its line numbers match the user's file.

| What the user sees | Likely cause and what to change |
|---|---|
| *Figure Editor failed*: "The Figure Editor plugin `<file>` stopped the Figure Editor from opening", with an error such as `SyntaxError`, `NameError` or `AttributeError` | The file raises an error when it is imported: a syntax error, or top-level code that fails. Fix it. The user saves it under the same name and generates the plot again; until then no plot opens in the Figure Editor. |
| *Figure Editor failed* with `QWidget: Must construct a QApplication before a QWidget` (the message may not name a file) | A widget or dialog is created at top level or in `__init__`. Create it inside `run`. |
| `ModuleNotFoundError: No module named '...'` | That package is not installed in PhysPlot's Python. Use only the packages listed above. |
| *Figure Editor plugin skipped* | The file has the name of one of FigureForge's own files (see **Rules**), so PhysPlot did not copy it. Send the file again under a new name; the user deletes the old one. |
| *Figure Editor failed*: "`<file>` in the Figure Editor's plugins folder stopped the Figure Editor from opening. PhysPlot did not copy this file there" | Not one of the user's plugins: a file left in FigureForge's `plugins` folder by an older PhysPlot or by FigureForge's **New Plugin** command. The user deletes the file at the path the message shows. |
| *Figure Editor failed*: "The Figure Editor's own file `<file>` is damaged" | An older PhysPlot copied a plugin over one of FigureForge's files. The user reinstalls FigureForge with PhysPlot's Python. With the PhysPlot install scripts this is, on Windows (Command Prompt), `"%LOCALAPPDATA%\PhysPlot\venv\Scripts\python.exe" -m pip install --force-reinstall --no-deps FigureForge`, and on macOS (Terminal), `~/.physplot/venv/bin/python -m pip install --force-reinstall --no-deps FigureForge`. |
| The Figure Editor does not open and no message appears | Top-level code waits for something (a loop, `input()`, a network call). Move that work into `run`. |
| The command is missing from the menu | The class has no `name`; a helper class was not hidden with `__module__ = __name__ + "._internal"`; the file is in the wrong folder or ends in `.py.txt`; or the Figure Editor was opened before the file was saved. |
| Nothing happens when the command is chosen | Nothing is selected in the Figure Explorer, or `run` raised an error that FigureForge hides. Add the type check and the `try`/`except` with a message box, then ask the user for the message. |
| The command shows an error message | Read the message: usually the wrong kind of object was selected, or data is missing (for example no visible line). Handle that case with a clear warning. |
| The command appears twice | Two files define it, for example the corrected file was saved under a new name and the old one kept. The user deletes one of them from `Documents/PhysPlot/config/figureforge_plugins/`; PhysPlot removes its copy from the Figure Editor when it opens the next one. |
| An old version of the command still runs | That Figure Editor window was opened before the file was saved. Generate the plot again to open a new one. |
