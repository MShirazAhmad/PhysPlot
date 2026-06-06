import pandas as pd

from physplot.loaders import CSVLoader, DataFrameLoader, ExcelLoader, NanoindentationLoader, TXTLoader


def test_loader_metadata_for_csv_txt_excel_and_dataframe(tmp_path):
    df = pd.DataFrame({"Time (s)": [1, 2], "Voltage [V]": [3.0, 4.0]})
    csv_path = tmp_path / "data.csv"
    txt_path = tmp_path / "data.txt"
    xlsx_path = tmp_path / "data.xlsx"
    df.to_csv(csv_path, index=False)
    df.to_csv(txt_path, index=False)
    df.to_excel(xlsx_path, index=False)

    for loader, source, expected_id in [
        (CSVLoader(), csv_path, "csv"),
        (TXTLoader(), txt_path, "txt"),
        (ExcelLoader(), xlsx_path, "excel"),
        (DataFrameLoader(), df, "dataframe"),
    ]:
        ds = loader.load(source)
        assert ds.metadata["loader_id"] == expected_id
        assert ds.metadata["rows"] == 2
        assert ds.metadata["columns"] == 2
        assert ds.column_metadata["Time (s)"]["unit"] == "s"
        assert ds.column_metadata["Voltage [V]"]["unit"] == "V"
        assert ds.column_metadata["Time (s)"]["suggested_role"] == "X"
        assert ds.column_metadata["Voltage [V]"]["suggested_role"] == "Y"


def test_nanoindentation_loader_sets_dataset_type(tmp_path):
    path = tmp_path / "nano.csv"
    path.write_text(
        "Depth (nm),Load (mN),Hardness (GPa),Modulus (GPa),Stiffness (N/m)\n"
        "0,0,0,0,0\n"
        "50,1.2,20,350,1000\n",
        encoding="utf-8",
    )

    ds = NanoindentationLoader().load(path)

    assert ds.metadata["loader_id"] == "nanoindentation"
    assert ds.metadata["dataset_type"] == "nanoindentation"
    assert ds.metadata["instrument_family"] == "Agilent/KLA/Keysight"
