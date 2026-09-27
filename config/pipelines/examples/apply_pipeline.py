import json
from physplot import PhysPlot
from physplot.user_paths import user_plugin_dir

pipeline = user_plugin_dir("pipelines") / "uvvis_cleanup.json"
data_file = "sample_A.csv"

pp = PhysPlot()
pp.load(data_file)
for entry in json.loads(pipeline.read_text(encoding="utf-8")):
    params = {}
    for part in entry["params"].split(","):
        if "=" in part:
            name, value = (text.strip() for text in part.split("=", 1))
            try:
                params[name] = float(value)
            except ValueError:
                params[name] = value
    pp.transform(entry["input"], entry["function"], output=entry["output"], **params)
    print("OK:", entry["function"], "->", entry["output"])
print(pp.dataset.dataframe.head())
pp.export_workflow(user_plugin_dir("sequences") / (pipeline.stem + "_sequence.py"))
