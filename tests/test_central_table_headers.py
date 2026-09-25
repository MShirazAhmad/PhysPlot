import os

import pandas as pd
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PyQt6")

from physplot.qt_compat import QtWidgets
from physplot_gui.widgets.central_table import CentralTable


def test_long_column_headers_are_not_clipped():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    table = CentralTable()
    header = table.table.horizontalHeader()
    default_width = header.defaultSectionSize()

    table.set_dataframe(pd.DataFrame({"Time": [1, 2], "Voltage_squared_output": [1.0, 4.0]}))

    assert table.table.columnWidth(1) >= header.sectionSizeHint(1) > default_width
    assert table.table.columnWidth(0) == default_width

    table.rename_column_to(0, "Elapsed time since trigger")
    assert table.table.columnWidth(0) >= header.sectionSizeHint(0) > default_width

    table.table.setColumnWidth(1, 400)
    table.set_dataframe(pd.DataFrame({"Time": [1, 2], "Voltage_squared_output": [1.0, 4.0]}))
    assert table.table.columnWidth(1) == 400

    table.close()
    app.processEvents()
