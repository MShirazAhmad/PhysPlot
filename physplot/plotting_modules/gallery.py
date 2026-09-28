"""Every Matplotlib chart kind, grouped like the Matplotlib gallery.

Covers https://matplotlib.org/stable/plot_types/ and the chart kinds of the plotting
sections of https://matplotlib.org/stable/gallery/ (lines, bars and markers; statistics;
images, contours and fields; pie and polar; 3D; specialty plots).

The Basic Plotter offers these as its plot types. Each entry of :data:`PLOT_CATEGORIES`
names a category and its plot types; each plot type has

* ``id``: the plot-type string stored in ``PlotModuleStep`` (for example ``"contourf"``);
* ``label``: what the Plot Type menu shows, the Matplotlib call (``"contourf(X, Y, Z)"``);
* ``roles``: the column roles it needs, in order (``("X", "Y", "Z")``);
* ``optional``: roles it uses when a column has them (``("Y Error",)``).

Data comes from the table columns with those roles. Gridded types take a long table (one
row per point with X, Y and Z columns): a regular grid is pivoted as is, scattered points
are interpolated onto a 100 x 100 grid.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .utils import numeric_series, role_column

MODULE_ID = "physplot.plotting_modules.gallery"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-09-28-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


def _t(id_, label, roles, optional=(), description=""):
    return {"id": id_, "label": label, "roles": tuple(roles), "optional": tuple(optional), "description": description}


PLOT_CATEGORIES = [
    {
        "name": "Lines, bars and markers",
        "types": [
            # scatter stays first: it is the Basic Plotter's default plot type.
            _t("scatter", "scatter(x, y)", ("X", "Y"), description="Markers at each point."),
            _t("line", "plot(x, y) – line", ("X", "Y"), description="Line through the points."),
            _t("scatter_line", "plot(x, y) – markers and line", ("X", "Y"), description="Markers joined by a line."),
            _t("scatter_colored", "scatter(x, y, c=z)", ("X", "Y", "Z"), description="Markers coloured by Z."),
            _t("scatter_hist", "scatter with histograms", ("X", "Y"), description="Scatter with marginal histograms of X and Y."),
            _t("multicolor_line", "multicolored line (LineCollection)", ("X", "Y", "Z"), description="Line coloured by Z."),
            _t("step", "step(x, y)", ("X", "Y"), description="Step line through the points."),
            _t("stairs", "stairs(values)", ("Y",), ("X",), description="Step outline of the Y values."),
            _t("stem", "stem(x, y)", ("X", "Y"), description="Vertical stems from the baseline."),
            _t("vlines", "vlines(x, 0, y)", ("X", "Y"), description="A vertical line from zero to Y at each X."),
            _t("bar", "bar(x, height)", ("X", "Y"), description="A bar per X, Y tall."),
            _t("barh", "barh(y, width)", ("X", "Y"), description="Horizontal bars."),
            _t("bar_grouped", "grouped bar chart", ("X", "Y", "Y2"), description="Y and Y2 bars side by side."),
            _t("bar_stacked", "stacked bar chart", ("X", "Y", "Y2"), description="Y2 bars stacked on Y."),
            _t("bar_categorical", "bar(categories, values)", ("Label", "Y"), description="A bar per Label text."),
            _t("broken_barh", "broken_barh(xranges, yrange)", ("X", "Y"), ("Group",), description="Bars from X lasting Y (a row per Group)."),
            _t("fill", "fill(x, y) – filled polygon", ("X", "Y"), description="Polygon through the points, filled."),
            _t("fill_between", "fill_between(x, y1, y2)", ("X", "Y"), ("Y2",), description="Area between Y and Y2 (or zero)."),
            _t("stackplot", "stackplot(x, y)", ("X", "Y"), ("Y2",), description="Stacked areas of Y and Y2."),
            _t("streamgraph", "stackplot(..., baseline='wiggle')", ("X", "Y"), ("Y2",), description="Streamgraph of Y and Y2."),
            _t("twinx", "twin y axes (twinx)", ("X", "Y", "Y2"), description="Y on the left axis, Y2 on the right."),
        ],
    },
    {
        "name": "Statistics",
        "types": [
            _t("hist", "hist(x)", ("Y",), description="Histogram of the Y values."),
            _t("hist_step", "hist(x, histtype='step')", ("Y",), ("Y2",), description="Outline histograms of Y (and Y2)."),
            _t("hist_multi", "hist([y, y2]) – side by side", ("Y", "Y2"), description="Histograms of Y and Y2 side by side."),
            _t("bihistogram", "bihistogram", ("Y", "Y2"), description="Y above, Y2 mirrored below."),
            _t("ecdf", "ecdf(x)", ("Y",), description="Empirical cumulative distribution of Y."),
            _t("boxplot", "boxplot(X)", ("Y",), ("Y2", "Group"), description="Box plot of Y (per Group, or Y and Y2)."),
            _t("violinplot", "violinplot(D)", ("Y",), ("Y2", "Group"), description="Violin plot of Y (per Group, or Y and Y2)."),
            _t("errorbar", "errorbar(x, y, yerr, xerr)", ("X", "Y"), ("Y Error", "X Error"), description="Points with error bars."),
            _t("error_band", "curve with error band", ("X", "Y", "Y Error"), description="Line with a shaded ±error band."),
            _t("confidence_ellipse", "confidence ellipse", ("X", "Y"), description="Scatter with 1σ, 2σ and 3σ covariance ellipses."),
            _t("hist2d", "hist2d(x, y)", ("X", "Y"), description="2D histogram of X and Y."),
            _t("hexbin", "hexbin(x, y, C)", ("X", "Y"), ("Z",), description="Hexagonal bins, coloured by count or mean Z."),
            _t("eventplot", "eventplot(D)", ("Y",), ("Group",), description="A tick at each Y value (a row per Group)."),
            _t("acorr", "acorr(x)", ("Y",), description="Autocorrelation of Y."),
            _t("xcorr", "xcorr(x, y)", ("Y", "Y2"), description="Cross-correlation of Y and Y2."),
            _t("psd", "psd(x)", ("Y",), ("X",), description="Power spectral density of Y (sampling from X)."),
            _t("csd", "csd(x, y)", ("Y", "Y2"), ("X",), description="Cross spectral density of Y and Y2."),
            _t("cohere", "cohere(x, y)", ("Y", "Y2"), ("X",), description="Coherence of Y and Y2."),
            _t("magnitude_spectrum", "magnitude_spectrum(x)", ("Y",), ("X",), description="Magnitude spectrum of Y."),
        ],
    },
    {
        "name": "Images, contours and fields",
        "types": [
            _t("imshow", "imshow(Z)", ("X", "Y", "Z"), description="Z on the X, Y grid as an image."),
            _t("matshow", "matshow(Z)", ("X", "Y", "Z"), description="Z grid as a matrix."),
            _t("heatmap", "annotated heatmap", ("X", "Y", "Z"), description="Z grid with each value written in its cell."),
            _t("pcolor", "pcolor(X, Y, Z)", ("X", "Y", "Z"), description="Coloured grid cells (pcolor)."),
            _t("pcolormesh", "pcolormesh(X, Y, Z)", ("X", "Y", "Z"), description="Coloured grid cells."),
            _t("contour", "contour(X, Y, Z)", ("X", "Y", "Z"), description="Labelled contour lines of Z."),
            _t("contourf", "contourf(X, Y, Z)", ("X", "Y", "Z"), description="Filled contours of Z."),
            _t("spy", "spy(Z)", ("X", "Y", "Z"), description="Non-zero pattern of the Z grid."),
            _t("specgram", "specgram(x)", ("Y",), ("X",), description="Spectrogram of the signal Y."),
            _t("barcode", "barcode", ("Y",), description="Y as a one-row barcode image."),
            _t("barbs", "barbs(X, Y, U, V)", ("X", "Y", "U", "V"), description="Wind barbs of the U, V field."),
            _t("quiver", "quiver(X, Y, U, V)", ("X", "Y", "U", "V"), description="Arrows of the U, V field."),
            _t("streamplot", "streamplot(X, Y, U, V)", ("X", "Y", "U", "V"), description="Streamlines of the U, V field."),
            _t("tricontour", "tricontour(x, y, z)", ("X", "Y", "Z"), description="Contour lines on scattered points."),
            _t("tricontourf", "tricontourf(x, y, z)", ("X", "Y", "Z"), description="Filled contours on scattered points."),
            _t("tripcolor", "tripcolor(x, y, z)", ("X", "Y", "Z"), description="Coloured triangles."),
            _t("triplot", "triplot(x, y)", ("X", "Y"), description="The triangulation of the points."),
        ],
    },
    {
        "name": "Pie and polar charts",
        "types": [
            _t("pie", "pie(x)", ("Y",), ("Label",), description="Pie of the Y values."),
            _t("donut", "pie(x, wedgeprops=width) – donut", ("Y",), ("Label",), description="Donut chart of the Y values."),
            _t("nested_pie", "nested pie", ("Y", "Group"), ("Label",), description="Inner ring per Group, outer ring per row."),
            _t("polar_line", "polar plot", ("X", "Y"), description="Y (radius) against X (angle, radians)."),
            _t("polar_scatter", "scatter on polar axis", ("X", "Y"), description="Markers at angle X, radius Y."),
            _t("polar_bar", "bar on polar axis", ("X", "Y"), description="Bars at angle X, Y long."),
            _t("polar_errorbar", "errorbar on polar axis", ("X", "Y", "Y Error"), description="Polar points with radial error bars."),
        ],
    },
    {
        "name": "3D plotting",
        "types": [
            _t("plot3d", "plot(xs, ys, zs)", ("X", "Y", "Z"), description="3D line."),
            _t("scatter3d", "scatter(xs, ys, zs)", ("X", "Y", "Z"), description="3D markers."),
            _t("stem3d", "stem(x, y, z)", ("X", "Y", "Z"), description="3D stems."),
            _t("bar3d", "bar3d(x, y, z, dx, dy, dz)", ("X", "Y", "Z"), description="3D bars Z tall at X, Y."),
            _t("hist3d", "3D histogram of 2D data", ("X", "Y"), description="3D bars counting X, Y pairs."),
            _t("fill_between3d", "fill_between(x1, y1, z1, x2, y2, z2)", ("X", "Y", "Z"), description="Area between the 3D curve and z = 0."),
            _t("quiver3d", "quiver(X, Y, Z, U, V, W)", ("X", "Y", "Z", "U", "V", "W"), description="3D arrows."),
            _t("plot_surface", "plot_surface(X, Y, Z)", ("X", "Y", "Z"), description="Surface of Z over X, Y."),
            _t("surface_projected", "surface with projected contours", ("X", "Y", "Z"), description="Surface with its contours on the walls."),
            _t("plot_wireframe", "plot_wireframe(X, Y, Z)", ("X", "Y", "Z"), description="Wireframe of Z over X, Y."),
            _t("plot_trisurf", "plot_trisurf(x, y, z)", ("X", "Y", "Z"), description="Surface through scattered points."),
            _t("contour3d", "contour(X, Y, Z) in 3D", ("X", "Y", "Z"), description="Contour lines at their Z height."),
            _t("contourf3d", "contourf(X, Y, Z) in 3D", ("X", "Y", "Z"), description="Filled contours in 3D."),
            _t("tricontour3d", "tricontour(x, y, z) in 3D", ("X", "Y", "Z"), description="Contours on scattered points in 3D."),
            _t("tricontourf3d", "tricontourf(x, y, z) in 3D", ("X", "Y", "Z"), description="Filled contours on scattered points in 3D."),
            _t("voxels", "voxels([x, y, z], filled)", ("X", "Y", "Z"), description="A cube at each integer X, Y, Z."),
        ],
    },
    {
        "name": "Specialty plots",
        "types": [
            _t("radar", "radar (spider) chart", ("Label", "Y"), ("Y2",), description="A spoke per Label, Y (and Y2) as polygons."),
            _t("hinton", "Hinton diagram", ("X", "Y", "Z"), description="Squares sized by |Z|, coloured by sign."),
            _t("hillshade", "hillshading", ("X", "Y", "Z"), description="Z grid as a shaded relief."),
            _t("sankey", "Sankey diagram", ("Y",), ("Label",), description="Flows: positive Y in, negative Y out."),
        ],
    },
]

PLOT_TYPES = {entry["id"]: dict(entry, category=category["name"]) for category in PLOT_CATEGORIES for entry in category["types"]}
PLOT_TYPE_IDS = tuple(PLOT_TYPES)
THREE_D = {entry["id"] for entry in next(c for c in PLOT_CATEGORIES if c["name"] == "3D plotting")["types"]}
POLAR = {"polar_line", "polar_scatter", "polar_bar", "polar_errorbar", "radar"}


def plot_type_info(plot_type: str) -> dict | None:
    """Return the catalogue entry of ``plot_type`` (with its ``category``), or ``None``."""
    return PLOT_TYPES.get(plot_type)


def roles_hint(plot_type: str) -> str:
    """Return a short hint such as ``"Uses: X, Y, Z"`` or ``"Uses: X, Y (Y2 optional)"``."""
    info = plot_type_info(plot_type)
    if not info:
        return ""
    hint = "Uses: " + ", ".join(info["roles"])
    if info["optional"]:
        hint += f" ({', '.join(info['optional'])} optional)"
    return hint


def _values(dataset, role, required=True):
    column = role_column(dataset, role, required=required)
    if column is None:
        return None, None
    return numeric_series(dataset, column).to_numpy(dtype=float), column


def _grid(x, y, z):
    """Turn long X, Y, Z columns into 2D grids (pivot if regular, else interpolate)."""
    frame = pd.DataFrame({"x": x, "y": y, "z": z}).dropna()
    xs, ys = np.unique(frame["x"]), np.unique(frame["y"])
    if len(xs) * len(ys) <= 4 * len(frame) and len(xs) > 1 and len(ys) > 1:
        table = frame.pivot_table(index="y", columns="x", values="z", aggfunc="mean")
        if table.notna().to_numpy().mean() > 0.9:
            table = table.interpolate(axis=0, limit_direction="both").interpolate(axis=1, limit_direction="both")
            gx, gy = np.meshgrid(table.columns.to_numpy(float), table.index.to_numpy(float))
            return gx, gy, table.to_numpy(float)
    from scipy.interpolate import griddata

    gx, gy = np.meshgrid(
        np.linspace(frame["x"].min(), frame["x"].max(), 100),
        np.linspace(frame["y"].min(), frame["y"].max(), 100),
    )
    gz = griddata((frame["x"], frame["y"]), frame["z"], (gx, gy), method="linear")
    return gx, gy, gz


def _groups(dataset, values, group_role="Group"):
    """Split ``values`` by the Group column; returns (list of arrays, list of names)."""
    column = role_column(dataset, group_role, required=False)
    if column is None:
        return [values[~np.isnan(values)]], [None]
    keys = dataset.dataframe[column].astype(str).to_numpy()
    names = list(dict.fromkeys(keys))
    return [values[(keys == name) & ~np.isnan(values)] for name in names], names


def plt_rectangle(xy, width, height, color):
    from matplotlib.patches import Rectangle

    return Rectangle(xy, width, height, facecolor=color, edgecolor=color)


def matplotlib_cm(name):
    import matplotlib

    return matplotlib.colormaps[name]


def _scatter_hist(figure, x, y, name):
    """Scatter of X, Y with marginal histograms (gallery: Scatter plot with histograms)."""
    grid = figure.add_gridspec(2, 2, width_ratios=(4, 1), height_ratios=(1, 4), wspace=0.05, hspace=0.05)
    ax = figure.add_subplot(grid[1, 0])
    top = figure.add_subplot(grid[0, 0], sharex=ax)
    right = figure.add_subplot(grid[1, 1], sharey=ax)
    keep = ~(np.isnan(x) | np.isnan(y))
    ax.scatter(x[keep], y[keep], s=10)
    top.hist(x[keep], bins="auto")
    right.hist(y[keep], bins="auto", orientation="horizontal")
    top.tick_params(axis="x", labelbottom=False)
    right.tick_params(axis="y", labelleft=False)
    ax.set_xlabel(name["X"])
    ax.set_ylabel(name["Y"])
    top.set_title(f"{name['Y']} vs {name['X']}")
    return ax


def draw(figure, dataset, plot_type: str):
    """Draw ``plot_type`` from ``dataset`` into ``figure``; returns the axes."""
    info = plot_type_info(plot_type)
    if info is None:
        raise ValueError(f"Unknown plot type '{plot_type}'.")
    projection = "3d" if plot_type in THREE_D else "polar" if plot_type in POLAR else None
    text_roles = ("Group", "Label")
    for role in info["roles"]:
        if role in text_roles:
            role_column(dataset, role, required=True)  # clear error when missing
    get = {role: _values(dataset, role, required=True) for role in info["roles"] if role not in text_roles}
    # Group and Label hold text; they are read where used, not as numbers.
    opt = {
        role: _values(dataset, role, required=False)
        for role in info["optional"]
        if role not in text_roles
    }
    v = {role: pair[0] for role, pair in {**get, **opt}.items()}
    name = {role: pair[1] for role, pair in {**get, **opt}.items()}
    if plot_type == "scatter_hist":
        return _scatter_hist(figure, v["X"], v["Y"], name)
    ax = figure.add_subplot(projection=projection)
    x, y, z = v.get("X"), v.get("Y"), v.get("Z")
    mappable = None

    if plot_type == "line":
        ax.plot(x, y, linestyle="-")
    elif plot_type == "scatter":
        ax.scatter(x, y)
    elif plot_type == "scatter_line":
        ax.plot(x, y, marker="o", linestyle="-")
    elif plot_type == "bar":
        width = np.min(np.diff(np.unique(x))) * 0.8 if len(np.unique(x)) > 1 else 0.8
        ax.bar(x, y, width=width)
    elif plot_type == "stem":
        ax.stem(x, y)
    elif plot_type == "fill_between":
        ax.fill_between(x, y, v["Y2"] if v.get("Y2") is not None else 0, alpha=0.6)
        ax.plot(x, y)
    elif plot_type == "stackplot":
        series = [y] + ([v["Y2"]] if v.get("Y2") is not None else [])
        ax.stackplot(x, *series, labels=[n for n in (name["Y"], name.get("Y2")) if n])
        ax.legend(loc="upper left")
    elif plot_type == "stairs":
        values = y[~np.isnan(y)]
        edges = None
        if v.get("X") is not None and len(v["X"]) == len(values) + 1:
            edges = v["X"]
        ax.stairs(values, edges)
    elif plot_type == "hist":
        ax.hist(y[~np.isnan(y)], bins="auto")
    elif plot_type in ("boxplot", "violinplot"):
        data, labels = _groups(dataset, y)
        if labels == [None] and v.get("Y2") is not None:
            data = [y[~np.isnan(y)], v["Y2"][~np.isnan(v["Y2"])]]
            labels = [name["Y"], name["Y2"]]
        if plot_type == "boxplot":
            ax.boxplot(data, tick_labels=[str(label or name["Y"]) for label in labels])
        else:
            ax.violinplot(data, showmedians=True)
            ax.set_xticks(range(1, len(data) + 1), [str(label or name["Y"]) for label in labels])
    elif plot_type == "errorbar":
        ax.errorbar(x, y, yerr=v.get("Y Error"), xerr=v.get("X Error"), fmt="o", capsize=3)
    elif plot_type == "eventplot":
        data, labels = _groups(dataset, y)
        ax.eventplot(data)
        if labels != [None]:
            ax.set_yticks(range(len(labels)), labels)
    elif plot_type == "hist2d":
        *_, mappable = ax.hist2d(x, y, bins=40)
    elif plot_type == "hexbin":
        mappable = ax.hexbin(x, y, C=v.get("Z"), gridsize=30)
    elif plot_type == "pie":
        label_column = role_column(dataset, "Label", required=False)
        labels = dataset.dataframe[label_column].astype(str).tolist() if label_column else None
        ax.pie(np.abs(np.nan_to_num(y)), labels=labels, autopct="%1.1f%%")
        ax.set_aspect("equal")
    elif plot_type == "ecdf":
        ax.ecdf(y[~np.isnan(y)])
    elif plot_type in ("imshow", "pcolormesh", "contour", "contourf"):
        gx, gy, gz = _grid(x, y, z)
        if plot_type == "imshow":
            mappable = ax.imshow(
                gz, origin="lower", aspect="auto",
                extent=(np.nanmin(gx), np.nanmax(gx), np.nanmin(gy), np.nanmax(gy)),
            )
        elif plot_type == "pcolormesh":
            mappable = ax.pcolormesh(gx, gy, gz, shading="auto")
        elif plot_type == "contour":
            mappable = ax.contour(gx, gy, gz)
            ax.clabel(mappable, fontsize=8)
        else:
            mappable = ax.contourf(gx, gy, gz, levels=20)
    elif plot_type in ("barbs", "quiver"):
        getattr(ax, plot_type)(x, y, v["U"], v["V"])
    elif plot_type == "streamplot":
        gx, gy, gu = _grid(x, y, v["U"])
        _, _, gv = _grid(x, y, v["V"])
        ax.streamplot(gx, gy, np.nan_to_num(gu), np.nan_to_num(gv))
    elif plot_type in ("tricontour", "tricontourf", "tripcolor"):
        keep = ~(np.isnan(x) | np.isnan(y) | np.isnan(z))
        mappable = getattr(ax, plot_type)(x[keep], y[keep], z[keep])
    elif plot_type == "triplot":
        ax.triplot(x, y, marker="o")
    elif plot_type == "bar3d":
        dx = np.min(np.diff(np.unique(x))) * 0.8 if len(np.unique(x)) > 1 else 0.8
        dy = np.min(np.diff(np.unique(y))) * 0.8 if len(np.unique(y)) > 1 else 0.8
        ax.bar3d(x - dx / 2, y - dy / 2, np.zeros_like(z), dx, dy, z, shade=True)
    elif plot_type == "fill_between3d":
        ax.fill_between(x, y, z, x, y, np.zeros_like(z), alpha=0.5)
        ax.plot(x, y, z)
    elif plot_type == "plot3d":
        ax.plot(x, y, z)
    elif plot_type == "quiver3d":
        ax.quiver(x, y, z, v["U"], v["V"], v["W"], length=0.1, normalize=True)
    elif plot_type == "scatter3d":
        ax.scatter(x, y, z)
    elif plot_type == "stem3d":
        ax.stem(x, y, z)
    elif plot_type in ("plot_surface", "plot_wireframe"):
        gx, gy, gz = _grid(x, y, z)
        if plot_type == "plot_surface":
            mappable = ax.plot_surface(gx, gy, gz, cmap="viridis")
        else:
            ax.plot_wireframe(gx, gy, gz)
    elif plot_type == "plot_trisurf":
        keep = ~(np.isnan(x) | np.isnan(y) | np.isnan(z))
        mappable = ax.plot_trisurf(x[keep], y[keep], z[keep], cmap="viridis")
    elif plot_type == "voxels":
        ix, iy, iz = (np.round(a - np.nanmin(a)).astype(int) for a in (x, y, z))
        filled = np.zeros((ix.max() + 1, iy.max() + 1, iz.max() + 1), dtype=bool)
        filled[ix, iy, iz] = True
        ax.voxels(filled, edgecolor="k")

    # --- gallery chart kinds -------------------------------------------------------
    if plot_type == "scatter_colored":
        mappable = ax.scatter(x, y, c=z, cmap="viridis")
    elif plot_type == "multicolor_line":
        from matplotlib.collections import LineCollection

        points = np.column_stack([x, y]).reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        mappable = LineCollection(segments, cmap="viridis", linewidth=2)
        mappable.set_array(z[:-1])
        ax.add_collection(mappable)
        ax.autoscale()
    elif plot_type == "step":
        ax.step(x, y, where="mid")
    elif plot_type == "vlines":
        ax.vlines(x, 0, y)
        ax.axhline(0, color="0.5", linewidth=0.8)
    elif plot_type == "barh":
        height = np.min(np.diff(np.unique(x))) * 0.8 if len(np.unique(x)) > 1 else 0.8
        ax.barh(x, y, height=height)
        ax.set_xlabel(name["Y"])
        ax.set_ylabel(name["X"])
    elif plot_type in ("bar_grouped", "bar_stacked"):
        positions = np.arange(len(x))
        if plot_type == "bar_grouped":
            ax.bar(positions - 0.2, y, width=0.4, label=name["Y"])
            ax.bar(positions + 0.2, v["Y2"], width=0.4, label=name["Y2"])
        else:
            ax.bar(positions, y, label=name["Y"])
            ax.bar(positions, v["Y2"], bottom=np.nan_to_num(y), label=name["Y2"])
        ax.set_xticks(positions, [f"{value:g}" for value in x])
        ax.legend()
    elif plot_type == "bar_categorical":
        labels = dataset.dataframe[role_column(dataset, "Label")].astype(str).tolist()
        ax.bar(labels, y)
        ax.tick_params(axis="x", labelrotation=45)
    elif plot_type == "broken_barh":
        data_x, rows = _groups(dataset, x)
        data_w, _ = _groups(dataset, y)
        for index, (starts, widths) in enumerate(zip(data_x, data_w)):
            ax.broken_barh(list(zip(starts, widths)), (index - 0.4, 0.8))
        ax.set_yticks(range(len(rows)), [str(row or name["Y"]) for row in rows])
    elif plot_type == "fill":
        ax.fill(x, y, alpha=0.6)
    elif plot_type == "streamgraph":
        series = [y] + ([v["Y2"]] if v.get("Y2") is not None else [])
        ax.stackplot(x, *series, baseline="wiggle", labels=[n for n in (name["Y"], name.get("Y2")) if n])
        ax.legend(loc="upper left")
    elif plot_type == "twinx":
        ax.plot(x, y, color="C0")
        ax.set_ylabel(name["Y"], color="C0")
        right = ax.twinx()
        right.plot(x, v["Y2"], color="C1")
        right.set_ylabel(name["Y2"], color="C1")
        ax.set_xlabel(name["X"])
    elif plot_type == "hist_step":
        ax.hist(y[~np.isnan(y)], bins="auto", histtype="step", label=name["Y"])
        if v.get("Y2") is not None:
            ax.hist(v["Y2"][~np.isnan(v["Y2"])], bins="auto", histtype="step", label=name["Y2"])
            ax.legend()
    elif plot_type == "hist_multi":
        ax.hist([y[~np.isnan(y)], v["Y2"][~np.isnan(v["Y2"])]], bins="auto", label=[name["Y"], name["Y2"]])
        ax.legend()
    elif plot_type == "bihistogram":
        clean_y, clean_y2 = y[~np.isnan(y)], v["Y2"][~np.isnan(v["Y2"])]
        bins = np.histogram_bin_edges(np.concatenate([clean_y, clean_y2]), bins="auto")
        ax.hist(clean_y, bins=bins, label=name["Y"])
        counts, _ = np.histogram(clean_y2, bins=bins)
        ax.bar(bins[:-1], -counts, width=np.diff(bins), align="edge", label=name["Y2"])
        ax.axhline(0, color="0.3", linewidth=0.8)
        ax.legend()
    elif plot_type == "error_band":
        err = np.nan_to_num(v["Y Error"])
        ax.plot(x, y)
        ax.fill_between(x, y - err, y + err, alpha=0.3)
    elif plot_type == "confidence_ellipse":
        from matplotlib.patches import Ellipse

        keep = ~(np.isnan(x) | np.isnan(y))
        ax.scatter(x[keep], y[keep], s=8)
        covariance = np.cov(x[keep], y[keep])
        eigenvalues, eigenvectors = np.linalg.eigh(covariance)
        angle = np.degrees(np.arctan2(*eigenvectors[:, 1][::-1]))
        for n_std, style in ((1, "-"), (2, "--"), (3, ":")):
            width, height = 2 * n_std * np.sqrt(eigenvalues[::-1])
            ax.add_patch(
                Ellipse((x[keep].mean(), y[keep].mean()), width, height, angle=angle,
                        fill=False, edgecolor="C3", linestyle=style, label=f"{n_std}σ")
            )
        ax.legend()
    elif plot_type == "acorr":
        ax.acorr(y[~np.isnan(y)] - np.nanmean(y), maxlags=min(50, len(y) - 1))
    elif plot_type == "xcorr":
        keep = ~(np.isnan(y) | np.isnan(v["Y2"]))
        ax.xcorr(y[keep] - y[keep].mean(), v["Y2"][keep] - v["Y2"][keep].mean(), maxlags=min(50, keep.sum() - 1))
    elif plot_type in ("psd", "csd", "cohere", "magnitude_spectrum", "specgram"):
        fs = 1.0
        if v.get("X") is not None and len(v["X"]) > 1:
            step = np.nanmedian(np.diff(v["X"]))
            fs = 1.0 / step if step else 1.0
        signal = np.nan_to_num(y)
        nfft = int(2 ** np.floor(np.log2(max(8, min(256, len(signal))))))
        if plot_type == "psd":
            ax.psd(signal, NFFT=nfft, Fs=fs)
        elif plot_type == "csd":
            ax.csd(signal, np.nan_to_num(v["Y2"]), NFFT=nfft, Fs=fs)
        elif plot_type == "cohere":
            ax.cohere(signal, np.nan_to_num(v["Y2"]), NFFT=max(8, nfft // 2), Fs=fs)
        elif plot_type == "magnitude_spectrum":
            ax.magnitude_spectrum(signal, Fs=fs)
        else:
            *_, mappable = ax.specgram(signal, NFFT=max(8, nfft // 2), Fs=fs, noverlap=max(0, nfft // 4))
    elif plot_type == "barcode":
        ax.imshow(np.nan_to_num(y).reshape(1, -1), cmap="binary", aspect="auto", interpolation="nearest")
        ax.set_yticks([])
    elif plot_type in ("matshow", "heatmap", "pcolor", "spy", "hinton", "hillshade"):
        gx, gy, gz = _grid(x, y, z)
        if plot_type == "matshow":
            mappable = ax.matshow(gz)
        elif plot_type == "pcolor":
            mappable = ax.pcolor(gx, gy, gz, shading="auto")
        elif plot_type == "spy":
            ax.spy(np.nan_to_num(gz), markersize=4)
        elif plot_type == "heatmap":
            mappable = ax.imshow(gz, cmap="viridis", origin="lower")
            if gz.size <= 400:
                for (row, col), value in np.ndenumerate(gz):
                    ax.text(col, row, f"{value:.2g}", ha="center", va="center", fontsize=7, color="w")
            ax.set_xticks(range(gz.shape[1]), [f"{value:g}" for value in gx[0]], rotation=45)
            ax.set_yticks(range(gz.shape[0]), [f"{value:g}" for value in gy[:, 0]])
        elif plot_type == "hinton":
            ax.set_facecolor("gray")
            biggest = np.nanmax(np.abs(gz)) or 1.0
            for (row, col), value in np.ndenumerate(np.nan_to_num(gz)):
                size = np.sqrt(abs(value) / biggest)
                ax.add_patch(plt_rectangle((col - size / 2, row - size / 2), size, size, "white" if value > 0 else "black"))
            ax.set_xlim(-1, gz.shape[1])
            ax.set_ylim(-1, gz.shape[0])
            ax.set_aspect("equal")
        else:
            from matplotlib.colors import LightSource

            shaded = LightSource(azdeg=315, altdeg=45).shade(np.nan_to_num(gz), cmap=matplotlib_cm("gist_earth"), blend_mode="overlay")
            ax.imshow(shaded, origin="lower", extent=(np.nanmin(gx), np.nanmax(gx), np.nanmin(gy), np.nanmax(gy)), aspect="auto")
    elif plot_type in ("donut", "nested_pie"):
        label_column = role_column(dataset, "Label", required=False)
        labels = dataset.dataframe[label_column].astype(str).tolist() if label_column else None
        if plot_type == "donut":
            ax.pie(np.abs(np.nan_to_num(y)), labels=labels, wedgeprops={"width": 0.4})
        else:
            data, groups = _groups(dataset, np.abs(np.nan_to_num(y)))
            ax.pie([values.sum() for values in data], radius=0.7, labels=[str(g) for g in groups],
                   labeldistance=0.4, wedgeprops={"width": 0.3, "edgecolor": "w"})
            ax.pie(np.concatenate(data), radius=1.0, labels=labels, wedgeprops={"width": 0.3, "edgecolor": "w"})
        ax.set_aspect("equal")
    elif plot_type == "polar_line":
        ax.plot(x, y)
    elif plot_type == "polar_scatter":
        ax.scatter(x, y)
    elif plot_type == "polar_bar":
        width = 2 * np.pi / max(len(x), 1)
        ax.bar(x, y, width=width * 0.9, alpha=0.7)
    elif plot_type == "polar_errorbar":
        ax.errorbar(x, y, yerr=v["Y Error"], fmt="o", capsize=3)
    elif plot_type == "radar":
        labels = dataset.dataframe[role_column(dataset, "Label")].astype(str).tolist()
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)
        closed = np.append(angles, angles[0])
        for series, series_name in ((y, name["Y"]), (v.get("Y2"), name.get("Y2"))):
            if series is not None:
                values = np.append(np.nan_to_num(series), np.nan_to_num(series)[0])
                ax.plot(closed, values, label=series_name)
                ax.fill(closed, values, alpha=0.25)
        ax.set_xticks(angles, labels)
        ax.legend(loc="upper right")
    elif plot_type == "hist3d":
        counts, xedges, yedges = np.histogram2d(x[~np.isnan(x)], y[~np.isnan(y)], bins=10)
        xpos, ypos = np.meshgrid(xedges[:-1], yedges[:-1], indexing="ij")
        dx, dy = np.diff(xedges)[0] * 0.8, np.diff(yedges)[0] * 0.8
        ax.bar3d(xpos.ravel(), ypos.ravel(), 0, dx, dy, counts.ravel(), shade=True)
        ax.set_zlabel("count")
    elif plot_type in ("contour3d", "contourf3d", "surface_projected"):
        gx, gy, gz = _grid(x, y, z)
        if plot_type == "contour3d":
            ax.contour(gx, gy, gz, levels=15, cmap="viridis")
        elif plot_type == "contourf3d":
            ax.contourf(gx, gy, gz, levels=15, cmap="viridis")
        else:
            ax.plot_surface(gx, gy, gz, cmap="viridis", alpha=0.7)
            # Wall projections cannot take NaN cells (interpolated grids have NaN edges).
            filled = np.where(np.isnan(gz), np.nanmin(gz), gz)
            ax.contour(gx, gy, filled, zdir="z", offset=np.nanmin(gz), cmap="viridis")
            ax.contour(gx, gy, filled, zdir="x", offset=np.nanmin(gx), cmap="viridis")
            ax.contour(gx, gy, filled, zdir="y", offset=np.nanmax(gy), cmap="viridis")
    elif plot_type in ("tricontour3d", "tricontourf3d"):
        keep = ~(np.isnan(x) | np.isnan(y) | np.isnan(z))
        getattr(ax, plot_type.replace("3d", ""))(x[keep], y[keep], z[keep], cmap="viridis")
    elif plot_type == "sankey":
        from matplotlib.sankey import Sankey

        label_column = role_column(dataset, "Label", required=False)
        labels = dataset.dataframe[label_column].astype(str).tolist() if label_column else None
        flows = np.nan_to_num(y)
        Sankey(ax=ax, unit=None).add(flows=flows, labels=labels, orientations=[0] * len(flows)).finish()
        ax.axis("off")

    if mappable is not None and plot_type not in ("contour",):
        figure.colorbar(mappable, ax=ax, label=name.get("Z") or None)
    no_axis_labels = {"pie", "donut", "nested_pie", "sankey", "radar", "barh", "barcode", "twinx",
                      "psd", "csd", "cohere", "magnitude_spectrum", "specgram", "acorr", "xcorr"} | POLAR
    if name.get("X") and plot_type not in no_axis_labels:
        ax.set_xlabel(name["X"])
    y_on_x = {"hist", "hist_step", "hist_multi", "bihistogram", "ecdf", "stairs"}
    if name.get("Y") and plot_type not in no_axis_labels | y_on_x | {"boxplot", "violinplot", "eventplot", "broken_barh"}:
        ax.set_ylabel(name["Y"])
    elif name.get("Y") and plot_type in y_on_x:
        ax.set_xlabel(name["Y"])
    if name.get("Z") and plot_type in THREE_D:
        ax.set_zlabel(name["Z"])
    ax.set_title(info["label"].split(" – ")[0] if not name.get("Y") else f"{name['Y']}" + (f" vs {name['X']}" if name.get("X") else ""))
    return ax
