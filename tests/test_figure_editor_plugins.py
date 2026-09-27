import importlib.util
import json
import os
import textwrap
import time
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from physplot_gui.app.figure_editor import (
    MANIFEST_NAME,
    REINSTALL_COMMAND,
    EditorProcess,
    describe_start_failure,
    install_plugins,
    read_log,
    skipped_plugins_message,
)


def write(path: Path, text: str = "") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def figureforge_plugins_folder(tmp_path: Path) -> Path:
    """A stand-in for FigureForge's own plugins folder."""
    plugin_dir = tmp_path / "FigureForge" / "plugins"
    write(plugin_dir / "__init__.py", "# FigureForge loader\n")
    write(plugin_dir / "add_legend.py", "# FigureForge add_legend\n")
    write(plugin_dir / "utils" / "add_legend_dialog.py")
    return plugin_dir


def test_plugins_are_copied_with_user_files_winning_and_listed_in_a_manifest(tmp_path):
    plugin_dir = figureforge_plugins_folder(tmp_path)
    bundled = tmp_path / "bundled"
    user = tmp_path / "user"
    write(bundled / "physplot_fit_function.py", "bundled = True\n")
    write(bundled / "README.md", "not a plugin")
    write(user / "physplot_fit_function.py", "user = True\n")
    write(user / "journal_ticks.py", "ticks = True\n")

    install = install_plugins([bundled, user], plugin_dir)

    assert install.installed == {
        "physplot_fit_function.py": user / "physplot_fit_function.py",
        "journal_ticks.py": user / "journal_ticks.py",
    }
    assert (plugin_dir / "physplot_fit_function.py").read_text() == "user = True\n"
    assert not (plugin_dir / "README.md").exists()
    manifest = json.loads((plugin_dir / MANIFEST_NAME).read_text())
    assert sorted(manifest["installed"]) == ["journal_ticks.py", "physplot_fit_function.py"]


def test_copy_of_a_renamed_or_deleted_plugin_is_removed(tmp_path):
    plugin_dir = figureforge_plugins_folder(tmp_path)
    user = tmp_path / "user"
    write(user / "old_name.py", "raise ImportError('broken')\n")
    write(user / "deleted.py")
    install_plugins([user], plugin_dir)
    write(plugin_dir / "__pycache__" / "old_name.cpython-312.pyc")
    write(plugin_dir / "new_plugin.py", "# made with FigureForge's New Plugin\n")

    (user / "old_name.py").rename(user / "new_name.py")
    (user / "deleted.py").unlink()
    install = install_plugins([user], plugin_dir)

    assert sorted(install.removed) == ["deleted.py", "old_name.py"]
    assert not (plugin_dir / "old_name.py").exists()
    assert not (plugin_dir / "deleted.py").exists()
    assert not (plugin_dir / "__pycache__" / "old_name.cpython-312.pyc").exists()
    assert (plugin_dir / "new_name.py").exists()
    # Files PhysPlot did not copy stay.
    assert (plugin_dir / "new_plugin.py").exists()
    assert (plugin_dir / "add_legend.py").read_text() == "# FigureForge add_legend\n"


def test_plugin_named_like_a_figureforge_file_is_not_copied(tmp_path):
    plugin_dir = figureforge_plugins_folder(tmp_path)
    user = tmp_path / "user"
    for name in ("__init__.py", "add_legend.py", "Toggle_Spines.py", "utils.py", "good.py"):
        write(user / name, "raise SystemExit('should not run')\n")

    install = install_plugins([user], plugin_dir)

    assert sorted(path.name for path in install.skipped) == [
        "Toggle_Spines.py",
        "__init__.py",
        "add_legend.py",
        "utils.py",
    ]
    assert list(install.installed) == ["good.py"]
    assert (plugin_dir / "__init__.py").read_text() == "# FigureForge loader\n"
    assert (plugin_dir / "add_legend.py").read_text() == "# FigureForge add_legend\n"
    assert not (plugin_dir / "utils.py").exists()
    message = skipped_plugins_message(install.skipped)
    assert "add_legend.py" in message and str(user) in message
    assert "Rename" in message


def test_manifest_never_deletes_outside_the_plugins_folder_or_figureforge_files(tmp_path):
    plugin_dir = figureforge_plugins_folder(tmp_path)
    outside = write(tmp_path / "FigureForge" / "outside.py", "keep\n")
    write(
        plugin_dir / MANIFEST_NAME,
        json.dumps({"installed": {"../outside.py": "x", "add_legend.py": "x", "__init__.py": "x"}}),
    )
    user = write(tmp_path / "user" / "good.py").parent

    install = install_plugins([user], plugin_dir)

    assert install.removed == []
    assert outside.exists()
    assert (plugin_dir / "add_legend.py").exists()
    assert (plugin_dir / "__init__.py").exists()


def test_unreadable_manifest_counts_as_empty(tmp_path):
    plugin_dir = figureforge_plugins_folder(tmp_path)
    write(plugin_dir / MANIFEST_NAME, "{not json")
    user = write(tmp_path / "user" / "good.py").parent

    install = install_plugins([user], plugin_dir)

    assert install.installed == {"good.py": user / "good.py"}
    assert json.loads((plugin_dir / MANIFEST_NAME).read_text())["installed"] == {"good.py": str(user / "good.py")}


def traceback_through(*paths: Path, error: str) -> str:
    frames = "".join(f'  File "{path}", line 3, in <module>\n    something()\n' for path in paths)
    return f"Traceback (most recent call last):\n{frames}{error}\n"


def test_start_failure_names_the_plugin_that_failed(tmp_path):
    plugin_dir = figureforge_plugins_folder(tmp_path)
    user = write(tmp_path / "user" / "journal_ticks.py").parent
    install = install_plugins([user], plugin_dir)
    error = "ModuleNotFoundError: No module named 'not_a_real_package'"

    # FigureForge's plugins/__init__.py imports every plugin; the plugin itself is innermost.
    output = traceback_through(plugin_dir / "__init__.py", plugin_dir / "journal_ticks.py", error=error)
    message = describe_start_failure(output, 1, install)
    assert "journal_ticks.py" in message
    assert str(user / "journal_ticks.py") in message
    assert error in message

    stray = describe_start_failure(traceback_through(plugin_dir / "new_plugin.py", error=error), 1, install)
    assert "PhysPlot did not copy this file" in stray and str(plugin_dir / "new_plugin.py") in stray

    damaged = describe_start_failure(traceback_through(plugin_dir / "add_legend.py", error=error), 1, install)
    assert REINSTALL_COMMAND in damaged

    unknown = describe_start_failure("QWidget: Must construct a QApplication before a QWidget\n", -6, install)
    assert "QWidget: Must construct a QApplication before a QWidget" in unknown

    assert "exited with code 3" in describe_start_failure("", 3, None)


def test_read_log_keeps_the_end_of_a_long_log(tmp_path):
    log = write(tmp_path / "editor.log", "noise\n" * 50_000 + "ValueError: the real error\n")

    text = read_log(log, limit=1000)

    assert text.startswith("...\n")
    assert text.rstrip().endswith("ValueError: the real error")
    assert read_log(tmp_path / "missing.log") == ""


# ---------------------------------------------------------------------------
# The real launcher, run against a small fake FigureForge package.

needs_pyside6 = pytest.mark.skipif(
    importlib.util.find_spec("PySide6") is None or importlib.util.find_spec("PyQt6") is None,
    reason="needs PyQt6 for PhysPlot and PySide6 for the Figure Editor process",
)

FAKE_FIGUREFORGE = {
    "__init__.py": "from . import plugins\n",
    # Imports every plugin at package import, as FigureForge 0.3 does.
    "plugins/__init__.py": textwrap.dedent(
        """
        import importlib
        import os

        for name in sorted(os.listdir(os.path.dirname(__file__))):
            if name.endswith(".py") and name != "__init__.py":
                importlib.import_module(f"{__name__}.{name[:-3]}")
        """
    ),
    "main.py": textwrap.dedent(
        """
        class _Splash:
            def finish(self, window):
                pass


        def create_splash():
            return _Splash()
        """
    ),
    "gui.py": textwrap.dedent(
        """
        from PySide6.QtWidgets import QMainWindow


        class MainWindow(QMainWindow):
            def __init__(self, splash, figure):
                super().__init__()
                self.plugin_menu = self.menuBar().addMenu("Plugins")
        """
    ),
}


def start_editor_with_plugin(tmp_path, monkeypatch, plugin_source: str):
    from physplot.qt_compat import QtWidgets
    from physplot_gui.app.main_window import MainWindow

    fake_root = tmp_path / "fake_site"
    for name, text in FAKE_FIGUREFORGE.items():
        write(fake_root / "FigureForge" / name, text)
    plugin_dir = fake_root / "FigureForge" / "plugins"
    user = write(tmp_path / "user" / "user_plugin.py", plugin_source).parent
    monkeypatch.setenv("PYTHONPATH", str(fake_root))
    monkeypatch.setattr(
        MainWindow, "_install_figureforge_plugins", staticmethod(lambda: install_plugins([user], plugin_dir))
    )

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    errors = []
    monkeypatch.setattr(window, "_error", lambda title, exc, details="": errors.append((title, str(exc), details)))
    from matplotlib.figure import Figure

    window._open_figureforge_editor(Figure())
    return app, window, errors, user / "user_plugin.py"


def wait_until(app, condition, timeout=30.0):
    deadline = time.monotonic() + timeout
    while not condition() and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.05)
    return condition()


@needs_pyside6
def test_plugin_import_error_after_1_2_s_is_reported_with_its_error_output(tmp_path, monkeypatch):
    # The plugin writes far more than a pipe holds, then fails well after 1.2 s.
    plugin = textwrap.dedent(
        """
        import sys
        import time

        sys.stderr.write("noise from a chatty plugin\\n" * 20000)
        time.sleep(1.5)
        import not_a_real_package
        """
    )
    started = time.monotonic()
    app, window, errors, source = start_editor_with_plugin(tmp_path, monkeypatch, plugin)
    editor = window._figureforge_processes[0]

    assert wait_until(app, lambda: errors), "the failed Figure Editor was never reported"

    assert time.monotonic() - started > 1.5
    (title, message, details), = errors
    assert title == "Figure Editor failed"
    assert str(source) in message
    assert "No module named 'not_a_real_package'" in message
    assert details.endswith("ModuleNotFoundError: No module named 'not_a_real_package'")
    assert window._figureforge_processes == []
    assert not editor.log_path.exists() and not editor.figure_path.exists()
    assert not window._figureforge_timer.isActive()
    window.close()


@needs_pyside6
def test_checking_stops_once_the_editor_window_is_open(tmp_path, monkeypatch):
    app, window, errors, _ = start_editor_with_plugin(tmp_path, monkeypatch, "VALUE = 1\n")
    editor = window._figureforge_processes[0]
    try:
        assert wait_until(app, lambda: not editor.watching), "the Figure Editor window never opened"
        assert editor.ready_path.exists()
        assert editor.process.poll() is None
        assert not window._figureforge_timer.isActive()
        assert errors == []
    finally:
        editor.process.kill()
        editor.process.wait(timeout=10)
    window._reap_figureforge_processes()
    assert window._figureforge_processes == []
    assert not editor.log_path.exists()
    window.close()


def test_failed_editor_is_kept_until_its_failure_is_reported(tmp_path):
    pytest.importorskip("PyQt6")
    from physplot.qt_compat import QtWidgets
    from physplot_gui.app.main_window import MainWindow

    class ExitedProcess:
        returncode = 1

        def poll(self):
            return 1

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    editor = EditorProcess(
        ExitedProcess(),
        write(tmp_path / "f.pkl"),
        write(tmp_path / "f.log", "RuntimeError: boom\n"),
        tmp_path / "f.ready",
    )
    window._figureforge_processes = [editor]

    # Opening another editor reaps finished ones; this one has not been reported yet.
    window._reap_figureforge_processes()
    assert window._figureforge_processes == [editor]

    window._check_figureforge_processes()
    assert window.last_error[0] == "Figure Editor failed"
    assert "RuntimeError: boom" in str(window.last_error[1])
    assert window._figureforge_processes == []
    assert not editor.log_path.exists()
    window.close()
