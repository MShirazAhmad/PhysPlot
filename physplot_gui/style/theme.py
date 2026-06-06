"""Light desktop theme for the PhysPlot GUI."""

APP_STYLESHEET = """
QMainWindow, QWidget {
    background: #fafafa;
    color: #111111;
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 14px;
}
QFrame#Panel {
    background: #ffffff;
    border: 1px solid #dddddd;
    border-radius: 6px;
}
QLabel#PanelTitle {
    color: #0f172a;
    font-weight: 700;
    padding: 1px 0 2px 0;
}
QLabel#SectionTitle {
    color: #0645ad;
    font-weight: 700;
}
QPushButton {
    background: #ffffff;
    border: 1px solid #d5d5d5;
    border-radius: 4px;
    min-height: 28px;
    padding: 3px 10px;
}
QPushButton:hover {
    background: #f3f6fb;
}
QPushButton:pressed {
    background: #e6edf8;
}
QPushButton[primary="true"], QPushButton[activeMode="true"] {
    background: #0b65d8;
    border-color: #0b65d8;
    color: #ffffff;
    font-weight: 700;
}
QPushButton[danger="true"] {
    color: #d21f2b;
    border-color: #ff9da5;
}
QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox {
    background: #ffffff;
    border: 1px solid #d7d7d7;
    border-radius: 4px;
    min-height: 28px;
    padding: 2px 7px;
}
QComboBox#RoleCombo {
    min-height: 22px;
    padding: 1px 4px;
}
QCheckBox {
    spacing: 7px;
}
QTableWidget {
    background: #ffffff;
    alternate-background-color: #fcfcfc;
    border: 1px solid #d8d8d8;
    gridline-color: #e3e3e3;
    selection-background-color: #d9eaff;
    selection-color: #0f172a;
}
QPlainTextEdit#CodeView {
    background: #0f172a;
    color: #e5edf7;
    border: 1px solid #d8d8d8;
    border-radius: 4px;
    font-family: Menlo, Monaco, Consolas, monospace;
    font-size: 12px;
    padding: 8px;
}
QHeaderView::section {
    background: #f5f5f5;
    border: 0;
    border-right: 1px solid #d8d8d8;
    border-bottom: 1px solid #d8d8d8;
    padding: 4px;
    font-weight: 700;
}
QTabBar::tab {
    background: #ffffff;
    border: 1px solid #d4d9e1;
    padding: 5px 24px;
}
QTabBar::tab:selected {
    background: #0b65d8;
    color: #ffffff;
}
QTabWidget::pane {
    border: 0;
}
"""

BLUE = "#0b65d8"
GREEN = "#1fb34f"
RED = "#e21d2b"
