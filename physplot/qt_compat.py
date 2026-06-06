"""PyQt6 compatibility helpers for PhysPlot GUI modules."""

from __future__ import annotations

from PyQt6 import QtCore, QtGui, QtWidgets

QT_API = "PyQt6"
MODULE_ID = "physplot.qt_compat"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-06-05-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"

Signal = QtCore.pyqtSignal
Slot = QtCore.pyqtSlot
Qt = QtCore.Qt

Qt.AA_DontShowIconsInMenus = Qt.ApplicationAttribute.AA_DontShowIconsInMenus
Qt.AlignCenter = Qt.AlignmentFlag.AlignCenter
Qt.AlignLeft = Qt.AlignmentFlag.AlignLeft
Qt.AlignTop = Qt.AlignmentFlag.AlignTop
Qt.AlignVCenter = Qt.AlignmentFlag.AlignVCenter
Qt.ArrowCursor = Qt.CursorShape.ArrowCursor
Qt.ClickFocus = Qt.FocusPolicy.ClickFocus
Qt.ContiguousSelection = QtWidgets.QAbstractItemView.SelectionMode.ContiguousSelection
Qt.CustomContextMenu = Qt.ContextMenuPolicy.CustomContextMenu
Qt.DontConfirmOverwrite = QtWidgets.QFileDialog.Option.DontConfirmOverwrite
Qt.DoubleClicked = QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked
Qt.EditKeyPressed = QtWidgets.QAbstractItemView.EditTrigger.EditKeyPressed
Qt.AnyKeyPressed = QtWidgets.QAbstractItemView.EditTrigger.AnyKeyPressed
Qt.ItemIsEditable = Qt.ItemFlag.ItemIsEditable
Qt.KeepAspectRatio = Qt.AspectRatioMode.KeepAspectRatio
Qt.RichText = Qt.TextFormat.RichText
Qt.ScrollBarAsNeeded = Qt.ScrollBarPolicy.ScrollBarAsNeeded
Qt.SmoothTransformation = Qt.TransformationMode.SmoothTransformation
Qt.StrongFocus = Qt.FocusPolicy.StrongFocus
Qt.TextSelectableByMouse = Qt.TextInteractionFlag.TextSelectableByMouse
Qt.WindowActive = Qt.WindowState.WindowActive
Qt.WindowMinimized = Qt.WindowState.WindowMinimized
Qt.WA_ShowWithoutActivating = Qt.WidgetAttribute.WA_ShowWithoutActivating

Qt.Key_Delete = Qt.Key.Key_Delete
Qt.ImhDigitsOnly = Qt.InputMethodHint.ImhDigitsOnly
Qt.ImhFormattedNumbersOnly = Qt.InputMethodHint.ImhFormattedNumbersOnly
Qt.ImhNone = Qt.InputMethodHint.ImhNone
Qt.LeftToRight = Qt.LayoutDirection.LeftToRight

QtWidgets.QAction = QtGui.QAction
QtWidgets.QActionGroup = QtGui.QActionGroup
QtWidgets.QApplication.exec_ = QtWidgets.QApplication.exec
QtWidgets.QDialog.exec_ = QtWidgets.QDialog.exec
QtWidgets.QMessageBox.Critical = QtWidgets.QMessageBox.Icon.Critical
QtWidgets.QMessageBox.Ok = QtWidgets.QMessageBox.StandardButton.Ok
QtWidgets.QFileDialog.Options = QtWidgets.QFileDialog.Option
QtWidgets.QFileDialog.DontConfirmOverwrite = QtWidgets.QFileDialog.Option.DontConfirmOverwrite
QtWidgets.QAbstractItemView.AnyKeyPressed = QtWidgets.QAbstractItemView.EditTrigger.AnyKeyPressed
QtWidgets.QAbstractItemView.ContiguousSelection = QtWidgets.QAbstractItemView.SelectionMode.ContiguousSelection
QtWidgets.QAbstractItemView.DoubleClicked = QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked
QtWidgets.QAbstractItemView.EditKeyPressed = QtWidgets.QAbstractItemView.EditTrigger.EditKeyPressed
QtWidgets.QAbstractItemView.SelectItems = QtWidgets.QAbstractItemView.SelectionBehavior.SelectItems
QtWidgets.QHeaderView.Stretch = QtWidgets.QHeaderView.ResizeMode.Stretch
QtWidgets.QHeaderView.Interactive = QtWidgets.QHeaderView.ResizeMode.Interactive
QtWidgets.QHeaderView.ResizeToContents = QtWidgets.QHeaderView.ResizeMode.ResizeToContents
QtWidgets.QFrame.NoFrame = QtWidgets.QFrame.Shape.NoFrame
QtWidgets.QSizePolicy.Expanding = QtWidgets.QSizePolicy.Policy.Expanding
QtWidgets.QSizePolicy.Fixed = QtWidgets.QSizePolicy.Policy.Fixed
QtWidgets.QSizePolicy.Minimum = QtWidgets.QSizePolicy.Policy.Minimum
QtWidgets.QMainWindow.AllowTabbedDocks = QtWidgets.QMainWindow.DockOption.AllowTabbedDocks
QtWidgets.QMainWindow.AnimatedDocks = QtWidgets.QMainWindow.DockOption.AnimatedDocks
QtWidgets.QMainWindow.VerticalTabs = QtWidgets.QMainWindow.DockOption.VerticalTabs
QtGui.QAction.NoRole = QtGui.QAction.MenuRole.NoRole
QtCore.QLocale.English = QtCore.QLocale.Language.English
QtCore.QLocale.Pakistan = QtCore.QLocale.Country.Pakistan
QtCore.QLocale.UnitedStates = QtCore.QLocale.Country.UnitedStates
