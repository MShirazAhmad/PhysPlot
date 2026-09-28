import json
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from physplot_gui.app import updates


def _fake_latest(sha):
    return lambda channel: {"sha": sha, "date": "2026-09-28T10:00:00Z", "message": f"Newest on {channel}\n\nbody"}


def test_channels_are_the_three_branches():
    assert [ref for ref, _, _ in updates.CHANNELS] == ["main", "indevelopment", "bleedingedge"]
    assert updates.CHANNEL_LABELS["main"] == "Stable"


def test_update_detection_from_install_record(tmp_path, monkeypatch):
    monkeypatch.setattr(updates, "install_dir", lambda: tmp_path)
    (tmp_path / "install.json").write_text(json.dumps({"ref": "bleedingedge", "commit": "abc1234def"}))
    assert updates.installed_channel() == "bleedingedge"

    same = updates.check_for_update(fetch=_fake_latest("abc1234def"))
    assert same.channel == "bleedingedge" and not same.available and same.installed_by_installer

    newer = updates.check_for_update(fetch=_fake_latest("fff9999aaa"))
    assert newer.available and newer.latest_message.startswith("Newest on bleedingedge")

    # Switching channel always offers the other branch.
    other = updates.check_for_update("main", fetch=_fake_latest("abc1234def"))
    assert other.available


def test_source_checkout_is_compared_by_git_commit(tmp_path, monkeypatch):
    monkeypatch.setattr(updates, "install_dir", lambda: tmp_path)  # no install.json
    monkeypatch.setattr(updates, "source_checkout_commit", lambda: "1234567abc")
    info = updates.check_for_update("indevelopment", fetch=_fake_latest("1234567abc"))
    assert not info.available and not info.installed_by_installer


def test_daily_check_and_installer_commands():
    assert updates.check_due(None)
    assert not updates.check_due(1000.0, now=1000.0 + 3600)
    assert updates.check_due(1000.0, now=1000.0 + 2 * 24 * 3600)
    mac = updates.installer_command("main", platform="darwin")
    assert "PHYSPLOT_REF=main" in mac[-1] and "PhysPlot/main/scripts/install_macos.sh" in mac[-1]
    assert "PHYSPLOT_RELAUNCH=1" in mac[-1]
    win = updates.installer_command("bleedingedge", platform="win32")
    assert win[0] == "powershell" and "PHYSPLOT_REF='bleedingedge'" in win[-1]
    assert "bleedingedge/scripts/install_windows.ps1" in win[-1]


def test_help_menu_update_flow(tmp_path, monkeypatch):
    pytest.importorskip("PyQt6")
    from physplot.qt_compat import QtCore, QtWidgets
    from physplot_gui.app.main_window import MainWindow

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    stored = {}
    monkeypatch.setattr(QtCore.QSettings, "value", lambda self, key, default=None: stored.get(key, default))
    monkeypatch.setattr(QtCore.QSettings, "setValue", lambda self, key, value: stored.__setitem__(key, value))
    monkeypatch.setattr(updates, "install_dir", lambda: tmp_path)
    (tmp_path / "install.json").write_text(json.dumps({"ref": "main", "commit": "aaaaaaa1"}))
    window = MainWindow()
    titles = [a.text() for a in window.help_menu.actions()]
    assert "Check for Updates…" in titles and "Check for Updates Automatically" in titles
    assert window.auto_update_action.isChecked()
    assert window.update_channel() == "main"

    # An update is offered with Install / Skip / Later; Install launches the installer.
    launched = []
    monkeypatch.setattr(updates, "launch_installer", launched.append)
    monkeypatch.setattr(QtWidgets.QApplication, "quit", lambda *a: None)
    shown = []

    def fake_exec(box):
        shown.append((box.text(), [b.text() for b in box.buttons()]))
        box._clicked = next(b for b in box.buttons() if b.text() == "Install Update")

    monkeypatch.setattr(QtWidgets.QMessageBox, "exec", fake_exec)
    monkeypatch.setattr(QtWidgets.QMessageBox, "clickedButton", lambda box: box._clicked)
    info = updates.check_for_update(fetch=_fake_latest("bbbbbbb2"))
    window._update_check_finished(info, manual=False)
    assert "Stable (main)" in shown[0][0]
    assert {"Install Update", "Skip This Update", "Later"} <= set(shown[0][1])
    assert launched == ["main"]
    assert stored["updates/last_check"] > 0

    # Choosing a channel saves it.
    monkeypatch.setattr(window, "check_for_updates", lambda manual=True: None)
    window.set_update_channel("bleedingedge")
    assert window.update_channel() == "bleedingedge"
    window.close()
    app.processEvents()


def test_install_from_local_checkout_is_treated_as_a_checkout(tmp_path, monkeypatch):
    monkeypatch.setattr(updates, "install_dir", lambda: tmp_path)
    (tmp_path / "install.json").write_text(json.dumps({"ref": "bleedingedge", "commit": None, "local_source": True}))
    monkeypatch.setattr(updates, "source_checkout_commit", lambda: "7777777abc")
    info = updates.check_for_update("bleedingedge", fetch=_fake_latest("7777777abc"))
    assert not info.available and not info.installed_by_installer
