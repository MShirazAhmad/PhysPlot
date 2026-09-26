"""Column role constants used by the spreadsheet header row.

``ROLE_OPTIONS`` is the ordered list of entries shown in every role dropdown in row 0 of the
central table (:class:`physplot_gui.widgets.central_table.CentralTable`). A role tells the
backend how a column should be used when plotting or fitting. Picking a role in a dropdown
sets it on the backend dataset and, for any role other than ``Ignore``, records a
``SetRoleStep`` in the protocol, so replayed and bulk-run sequences use the same columns.
The names match the backend's valid roles in ``physplot.core.dataset``.

The roles, in dropdown order:

``Ignore``
    The default for every column. The column stays in the table and the dataset but no
    plotter uses it. It is the only role that does not make
    :meth:`~physplot_gui.widgets.central_table.CentralTable.to_dataframe` keep an
    otherwise empty column when trimming.
``X``
    The independent variable (horizontal axis). The basic, line, scatter, error-bar,
    overlay and subplot-grid plotters and the least-squares fit overlay require it; the
    histogram plotter uses it when no column is ``Y``.
``Y``
    The dependent variable (vertical axis). Required by the same plotters as ``X``; the
    histogram plotter uses it first.
``X Error``
    Horizontal uncertainty of each point, drawn as x error bars by the error-bar plotter.
    Optional.
``Y Error``
    Vertical uncertainty of each point, drawn as y error bars by the error-bar plotter.
    Optional.
``Group``
    Splits the rows into series by the values in this column: the overlay plotter draws
    one curve per group and the subplot-grid plotter one panel per group.
``Label``
    Also splits rows into series; the overlay and subplot-grid plotters use it when no
    column has the ``Group`` role.
``Batch Key``
    Marks a key column for batches of data. The role is stored on the dataset and recorded
    in the protocol (as ``batch_key``); none of the bundled plotter modules reads it.
``Fit Weight``
    Marks a column of fit weights. The role is stored on the dataset and recorded in the
    protocol (as ``fit_weight``); the bundled least-squares fit overlay does not read it.

``X``, ``Y``, ``X Error``, ``Y Error`` and ``Fit Weight`` are single-use: assigning one of
them to a column makes the backend reset the column that held it before to ``Ignore``, and
the main window then updates that column's dropdown. ``Group``, ``Label`` and ``Batch Key``
may be given to several columns; a plotter uses the first one it finds.
"""

ROLE_OPTIONS = [
    "Ignore",
    "X",
    "Y",
    "X Error",
    "Y Error",
    "Group",
    "Label",
    "Batch Key",
    "Fit Weight",
]
