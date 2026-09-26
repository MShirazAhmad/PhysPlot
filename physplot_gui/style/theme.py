"""Light desktop theme for the PhysPlot GUI.

``APP_STYLESHEET`` is a Qt stylesheet (QSS) string. The main window applies it to itself
with ``setStyleSheet``, so it styles the main window and every widget inside it. Widgets
opt into the special looks below through their object name (``setObjectName``) or a
dynamic property (``setProperty``).

What the stylesheet styles:

Window and text
    Every ``QMainWindow`` and ``QWidget`` gets a very light grey background (``#fafafa``),
    near-black text and a 14 px "Helvetica Neue"/Arial/sans-serif font. Widgets without a
    rule of their own, such as the status bar strip, use these defaults.
Panels
    ``QFrame`` widgets named ``Panel`` (the Simple mode panels and the Advanced mode
    protocol sequence and bulk-run panels) are white cards with a light grey 1 px border and 6 px
    rounded corners; labels inside them have a transparent background. ``QLabel`` named
    ``PanelTitle`` is a bold, dark navy panel heading, and ``QLabel`` named
    ``SectionTitle`` a bold blue section heading.
Buttons
    Plain ``QPushButton`` widgets are white with a light grey border, 4 px corners, a
    minimum height of 28 px and a faint blue tint on hover and when pressed.
Primary buttons
    Buttons with the property ``primary`` set to true (for example **Generate Plot** and
    **Run Bulk Workflow**), and the active mode button of the header's mode switcher
    (property ``activeMode``), are filled PhysPlot blue (``#0b65d8``) with bold white text.
Danger buttons
    Buttons with the property ``danger`` set to true get red text and a pink border.
Input fields
    ``QComboBox``, ``QLineEdit``, ``QSpinBox`` and ``QDoubleSpinBox`` are white with a light
    grey border, 4 px corners and a minimum height of 28 px. The central table's role
    dropdowns (``QComboBox`` named ``RoleCombo``) are more compact: minimum height 22 px
    and less padding, so they fit in the table's role row.
Check boxes
    ``QCheckBox`` gets 7 px between the box and its text.
Tables
    ``QTableWidget`` is white with very light alternating rows, light grey grid lines and
    border, and a pale blue selection with dark text. Table headers
    (``QHeaderView::section``) are light grey and bold, with thin right and bottom
    dividers.
Code view
    ``QPlainTextEdit`` named ``CodeView`` (the protocol sequence code in Advanced mode) is
    a dark navy editor with light 12 px monospace text (Menlo, Monaco or Consolas) and
    8 px padding.
Tabs
    ``QTabBar`` tabs are white with a light border and wide padding; the selected tab is
    filled PhysPlot blue with white text. ``QTabWidget`` panes have no border.

The module also defines the colour constants ``BLUE`` (``#0b65d8``, the primary blue),
``GREEN`` (``#1fb34f``, the same green as the status bar's ready dot) and ``RED``
(``#e21d2b``) for code that needs the theme colours.
"""

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
QFrame#Panel QLabel {
    background: transparent;
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
