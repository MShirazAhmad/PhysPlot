from physplot.user_paths import ensure_user_physplot_dirs
from physplot_gui.app.plugin_discovery import discover_fileloaders, discover_functions


def test_user_plugin_directory_overrides_bundled_function(monkeypatch, tmp_path):
    user_root = tmp_path / "PhysPlot"
    functions_dir = user_root / "config" / "transformations"
    functions_dir.mkdir(parents=True)
    (functions_dir / "01_identity.py").write_text(
        "DISPLAY_NAME = 'Edited Identity'\n"
        "def transform(values):\n"
        "    return values\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("PHYSPLOT_USER_DIR", str(user_root))

    entries = discover_functions()
    identity_entries = [entry for entry in entries if entry["path"].name == "01_identity.py"]

    assert len(identity_entries) == 1
    assert identity_entries[0]["display_name"] == "Edited Identity"
    assert identity_entries[0]["path"] == functions_dir / "01_identity.py"


def test_user_plugin_directory_overrides_bundled_fileloader(monkeypatch, tmp_path):
    user_root = tmp_path / "PhysPlot"
    fileloader_dir = user_root / "config" / "data_importers"
    fileloader_dir.mkdir(parents=True)
    (fileloader_dir / "default_loader.py").write_text(
        "title = 'Edited Default Loader'\n"
        "def load_data(file_path):\n"
        "    return [[1, 2]]\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("PHYSPLOT_USER_DIR", str(user_root))

    entries = discover_fileloaders()
    default_entries = [entry for entry in entries if entry["path"].name == "default_loader.py"]

    assert len(default_entries) == 1
    assert default_entries[0]["display_name"] == "Edited Default Loader"
    assert default_entries[0]["path"] == fileloader_dir / "default_loader.py"


def test_ensure_user_physplot_dirs_creates_editable_tree(monkeypatch, tmp_path):
    user_root = tmp_path / "PhysPlot"
    monkeypatch.setenv("PHYSPLOT_USER_DIR", str(user_root))

    root = ensure_user_physplot_dirs()

    assert root == user_root
    for folder_name in (
        "data_importers",
        "transformations",
        "fit_functions",
        "templates",
        "figureforge_fit_styles",
        "pipelines",
        "sequences",
        "plotter_modules",
        "plot_types",
        "protocol_modules",
    ):
        assert (user_root / "config" / folder_name).is_dir()
    assert (user_root / "test_data").is_dir()
