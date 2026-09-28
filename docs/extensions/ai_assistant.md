<!-- Generated from wiki/Build-Modules-with-AI.md by scripts/sync_wiki_to_docs.py. Edit the wiki page. -->

# Build Modules with an AI Assistant

You do not need to know Python to add a file loader, a transformation, a plotter or
any other module to PhysPlot. Every kind of module comes with a **guide file written
for AI assistants**. You give that guide to an AI chat assistant together with an
example of your data and a plain description of what you want. The assistant replies
with one finished module file, which you save in a folder and load in PhysPlot.

```text
guide file  +  your example  +  what you want
                     │
                     ▼
        AI assistant (ChatGPT, Claude, Gemini, Copilot, ...)
                     │
                     ▼
        one module file  ──►  Documents/PhysPlot/config/<folder>/  ──►  File → Reload Config Modules
```

The guide tells the assistant exactly what PhysPlot expects: the names the file must
define, the rules it must follow, a complete working example, and how to answer. That
is why the result usually works the first time. The
[AI Module Examples](ai_examples.md) page shows the tested example of every kind,
with sample data and the resulting plots.

## What you need

- **An AI chat assistant** that accepts file attachments, for example ChatGPT, Claude,
  Gemini or Microsoft Copilot. If yours cannot take files, open the guide on GitHub,
  copy all of its text and paste it at the start of your message.
- **The guide file** for the kind of module you want (see the table below).
- **An example**: a data file from your instrument (or its first 30–50 lines), a
  `Sequence.py` you exported, a template you saved, or a picture of the figure you want.
  Each section below says what helps most.

## Step by step

1. **Find the guide.** Pick the module kind in the table below and open its guide file
   on GitHub. Click **Download raw file** (the ↓ button above the text) to save
   `AI_GUIDE.md`. The same file is also in PhysPlot's own `config/<folder>/`.
2. **Start a new chat** with your AI assistant. Attach `AI_GUIDE.md` and your example.
3. **Describe what you want** in plain words. Each section below has an example
   request you can adapt.
4. **Answer its questions.** The guide tells the assistant to ask instead of guessing,
   for example about units or which column is X.
5. **Save the file.** The assistant replies with a file name and the complete file.
   In PhysPlot, **File → Open Config Folder** opens `Documents/PhysPlot/config/`; open
   the module's folder there. Download the file into it, or copy the code into a
   plain-text editor (Notepad, VS Code, or TextEdit after **Format → Make Plain Text**)
   and save it there with exactly the name the assistant gave. Check that the name ends
   in `.py` or `.json`, not `.txt`: in Notepad choose **Save as type: All files**.
6. **Load it.** In PhysPlot choose **File → Reload Config Modules** (or restart
   PhysPlot). The new module appears in the place given in the table.
7. **Try it on your example.** If PhysPlot shows an error, copy the whole message and
   send it to the assistant: *"PhysPlot shows this error: ..."*. It replies with a
   corrected complete file. Save it over the old one and reload.

`Documents/PhysPlot/config/` is your personal module folder. PhysPlot creates it on
first start and looks there before its built-in folders, so a file there with the same
name as a built-in one replaces it.

## Which guide to use

| To add... | Module kind | Guide file | Save it in `Documents/PhysPlot/config/` | It appears in |
|---|---|---|---|---|
| support for a new instrument file | [Data importer](#data-importers) | [data_importers/AI_GUIDE.md][g-importers] | `data_importers/` | **1. Data Importer → Data Loader** |
| a new column calculation | [Transformation](#transformations) | [transformations/AI_GUIDE.md][g-transformations] | `transformations/` | **2. Mathematical Transformation → Function** |
| a new kind of plot | [Plotter module](#plotter-modules) | [plotter_modules/AI_GUIDE.md][g-plotters] | `plotter_modules/` | **3. Plotter Module → Plotter Module** |
| a named variant of an existing plot | [Plot type preset](#plot-type-presets) | [plot_types/AI_GUIDE.md][g-plot-types] | `plot_types/` | **3. Plotter Module → Plot Type** |
| a complete processing recipe | [Protocol sequence](#protocol-sequences) | [sequences/AI_GUIDE.md][g-sequences] | `sequences/` | **Protocol → Import Sequence.py**, **Run Sequence** |
| a reusable block of protocol steps | [Protocol module](#protocol-modules) | [protocol_modules/AI_GUIDE.md][g-protocol-modules] | `protocol_modules/` | **Protocol → Insert Protocol Module** |
| a reusable chain of transformations | [Transformation pipeline](#transformation-pipelines) | [pipelines/AI_GUIDE.md][g-pipelines] | `pipelines/` | no menu: applied by a short script (a protocol module is usually better) |
| a figure style (size, fonts, colours) | [Figure template](#figure-templates) | [templates/AI_GUIDE.md][g-templates] | `templates/` | **3. Plotter Module → Template** |
| a look for the fitted line | [Fit-style preset](#fit-style-presets) | [figureforge_fit_styles/AI_GUIDE.md][g-fit-styles] | `figureforge_fit_styles/` | **3. Plotter Module → Fit Style** |
| a new tool in the Figure Editor | [Figure Editor plugin](#figure-editor-plugins) | [figureforge_plugins/AI_GUIDE.md][g-plugins] | `figureforge_plugins/` | the Figure Editor |
| a fit model for your data | [Curve fit](#curve-fits) | [fit_functions/AI_GUIDE.md][g-fit-functions] | nothing to save: type the reply's model | **3. Plotter Module → LSQ fit** |

## Data importers

Teaches PhysPlot to read one kind of instrument file: it finds the numbers and returns a
table with named columns and default roles. Guide: [data_importers/AI_GUIDE.md][g-importers].

- **Attach:** the guide, and one real, unedited file from the instrument. If it cannot be
  attached, paste its first 30–50 lines and its last few lines. Optionally add a second
  file that differs (another scan range, a single scan), so the loader handles both.
- **Ask, for example:**

  ```text
  I attached AI_GUIDE.md and an export from our Acme UV-1900 spectrophotometer
  (methylene_blue.uvs). Please write a PhysPlot data importer for these .uvs files.
  Wavelength (nm) should be X, absorbance Y, and the SD column Y Error.
  Our lab PC writes decimal commas, and single-scan exports have no SD column.
  ```

- **Then:** save the reply in `Documents/PhysPlot/config/data_importers/`, choose
  **File → Reload Config Modules**, pick the loader in **Data Loader**, import a file and
  compare the table with the file.

More: [File-Loader Plugins](https://physplot.readthedocs.io/en/latest/extensions/fileloading.html).

## Transformations

Adds a calculation to the **Function** list: it turns one column into a new column, one
value per row, and replays in saved sequences. Guide:
[transformations/AI_GUIDE.md][g-transformations].

- **Attach:** the guide. Give the formula with the units of the input and the result, and
  two or three example inputs with the results you expect.
- **Ask, for example:**

  ```text
  My FTIR spectra have the X column in wavenumber (cm^-1). I want a transformation
  that converts it to wavelength in nm so I can compare with UV-Vis data. Zero or
  negative values should become empty cells. For example, 4000 cm^-1 should give
  2500 nm. Please call it "cm^-1 to nm" in the menu.
  ```

- **Then:** save the reply in `Documents/PhysPlot/config/transformations/`, choose
  **File → Reload Config Modules**, pick it in **Function**, click **Apply** and check a
  few values. Keep the file name: saved sequences refer to it.

More: [Function Plugins](https://physplot.readthedocs.io/en/latest/extensions/functions.html).

## Plotter modules

Adds a new kind of figure to **3. Plotter Module**, drawn from the columns you gave
roles to, and replayed in sequences and bulk runs. Guide:
[plotter_modules/AI_GUIDE.md][g-plotters].

- **Attach:** the guide, a data file (or its first 30–50 lines), which column is X, Y,
  Y Error and so on, and optionally a picture or sketch of the figure you want.
- **Ask, for example:**

  ```text
  I measure current-voltage curves of solar cells (sample file attached).
  Voltage (V) is X and Current (mA) is Y. Please make a plotter with two plot types:
  "iv" (current vs voltage, markers joined by a line) and "power" (P = V x I in mW vs
  voltage, with the maximum power point marked). Label both axes with units and use
  the file name as the title. I will run it over a whole folder of files.
  ```

- **Then:** save the reply in `Documents/PhysPlot/config/plotter_modules/`, choose
  **File → Reload Config Modules**, pick it in **Plotter Module** and click
  **Generate Plot** for each plot type.

More: [Plotter Modules and Plot-Type Presets](https://physplot.readthedocs.io/en/latest/extensions/plotter_modules.html).

## Plot-type presets

Adds a named variant of an existing plot type, with fixed options, to one plotter's
**Plot Type** menu. The options work only in plotters that read them: PhysPlot's
built-in plotters read none, so for restyling them use a
[figure template](#figure-templates) instead. Guide: [plot_types/AI_GUIDE.md][g-plot-types].

- **Attach:** the guide, the plotter and plot type you use now (as named in the menus)
  and, if it is your own plotter, its `.py` file.
- **Ask, for example:**

  ```text
  I use my Derivative Plotter (file attached). Please make a plot type called
  "cooling_rate" based on its "derivative" type. It should smooth over 5 points,
  label the y-axis "Cooling rate (K/s)", use the title "Cooling curve", and make a
  5 x 3.5 inch figure without a grid.
  ```

- **Then:** save the reply in `Documents/PhysPlot/config/plot_types/`, choose
  **File → Reload Config Modules** and pick the new entry in **Plot Type**.

## Protocol sequences

A complete recipe (roles, transformations, a plot) that PhysPlot replays on one file or
on every file in a folder. Guide: [sequences/AI_GUIDE.md][g-sequences].

The most reliable route: do the steps once in PhysPlot on one real file, save them with
**Protocol → Export Sequence.py**, and attach that file, so the assistant edits a
known-good sequence.

- **Attach:** the guide, your exported `Sequence.py` if you have one, and the first
  20–30 lines of one data file. For file types other than `.csv .txt .dat .tsv .msa
  .xls .xlsx .xrdml`, also give the full path of one sample file.
- **Ask, for example:**

  ```text
  I attached PhysPlot's sequence guide and the first lines of one UV-Vis spectrum
  (CSV, columns "Wavelength (nm)" and "Absorbance"). Write a sequence that subtracts
  the blank level 0.02 from Absorbance, scales the strongest peak to 1, and plots it
  against wavelength as a line. I will run it on a folder of about 40 spectra with
  Run Sequence.
  ```

- **Then:** save the reply in `Documents/PhysPlot/config/sequences/`. Try it on one file
  with **Protocol → Import Sequence.py** and **Apply This Sequence**, then on the folder
  with **Run Sequence**.

More: [Sequence Walkthrough](../ui/sequence_walkthrough.md) and
[Sequences, Protocol Modules and Pipelines](https://physplot.readthedocs.io/en/latest/extensions/protocol_files.html).

## Protocol modules

A short block of steps listed under **Protocol → Insert Protocol Module**; choosing it
adds the steps to the end of the current protocol. Guide:
[protocol_modules/AI_GUIDE.md][g-protocol-modules].

- **Attach:** the guide, the first lines of a data file (or an exported `Sequence.py`
  that already contains the steps), and the menu name you want.
- **Ask, for example:**

  ```text
  Using the attached guide, make a protocol module for my resistance-temperature
  files (columns Temperature_C, Resistance_ohm). It should add Temperature_K =
  Temperature_C + 273.15 and plot Resistance_ohm against it with lines and markers.
  Menu name: "Resistance vs Temperature (K)".
  ```

- **Then:** save the reply in `Documents/PhysPlot/config/protocol_modules/`, choose
  **File → Reload Config Modules**, insert it from **Protocol → Insert Protocol Module**
  and click **Apply This Sequence**.

## Transformation pipelines

A JSON list of column transformations. PhysPlot 1.0 has no menu item for pipelines: one
is applied with a short Python script from the guide, which also saves it as a
sequence. For transformations you want in the menus, a
[protocol module](#protocol-modules) is usually the better choice. Guide:
[pipelines/AI_GUIDE.md][g-pipelines].

- **Attach:** the guide, the first lines of a data file, and the list of
  transformations with their values and new column names.
- **Ask, for example:**

  ```text
  With the attached guide, write a pipeline for my UV-Vis CSVs (columns
  "Wavelength (nm)", "Absorbance"): subtract 0.02 from Absorbance into
  Absorbance_corr, then scale the strongest peak to 1 into Absorbance_norm.
  ```

- **Then:** save the reply in `Documents/PhysPlot/config/pipelines/` and run the script
  from the guide.

## Figure templates

Restyles every plot after **Generate Plot**: figure size, fonts of the title and axis
labels, spines, grid, tick-label size, line and marker colours, and the legend. It
cannot change tick direction, minor ticks, marker shape or axis limits (a
[Figure Editor plugin](#figure-editor-plugins) can do ticks). Guide:
[templates/AI_GUIDE.md][g-templates].

- **Attach:** the guide, a template you saved with **Figure Editor → PhysPlot → Save as
  Template** from the kind of plot you use, and optionally a picture of the target style
  or the journal's figure guidelines.
- **Ask, for example:**

  ```text
  Attached is a template I saved from a Basic Plotter scatter plot with an LSQ fit.
  Make it a single-column figure for my journal: 3.4 by 2.6 inches, 8 pt axis labels,
  7 pt tick labels, thin black axes on all four sides, open black circles, a red fit
  line, and a legend without a frame. No grid.
  ```

- **Then:** save the reply in `Documents/PhysPlot/config/templates/`, click **Reload**
  beside **Template**, select it and click **Generate Plot**.

## Fit-style presets

Sets how the LSQ fit line is drawn: line style, width, legend label and whether the
legend is shown. It has no colour (a template can colour the fit line). Guide:
[figureforge_fit_styles/AI_GUIDE.md][g-fit-styles].

- **Attach:** the guide, and optionally an existing preset such as `Default LSQ Fit.json`.
- **Ask, for example:**

  ```text
  Make a fit style called "Thin Dotted Fit": a dotted line 1 pt wide, labelled
  "Exponential fit", with the legend shown.
  ```

- **Then:** save the reply in `Documents/PhysPlot/config/figureforge_fit_styles/`, click
  **Reload** beside **Fit Style** and choose it.

## Figure Editor plugins

Adds a command to the Figure Editor that acts on the part of the figure selected in the
Figure Explorer: tick direction, reference lines, annotations, small calculations.
Guide: [figureforge_plugins/AI_GUIDE.md][g-plugins].

- **Attach:** the guide, a screenshot of the Figure Editor or the figure if it helps, and
  the menu name you want.
- **Ask, for example:**

  ```text
  In the Figure Editor I want a command "Reference Line" under a new submenu
  "Guides". With an Axes selected, it asks me for a y value and draws a thin grey
  dashed horizontal line there.
  ```

- **Then:** save the reply in `Documents/PhysPlot/config/figureforge_plugins/` and
  open a new Figure Editor (**Generate Plot**, then **Advanced Styling…**): each new editor
  loads the plugins. If the command is missing, the editor's status bar names the plugin
  and its error.

More: [Figure Templates, Fit Styles and Figure Editor Plugins](https://physplot.readthedocs.io/en/latest/extensions/figure_extensions.html).

## Curve fits

Fitting needs no file: in **3. Plotter Module** tick **LSQ fit** and type the model,
its parameter names and starting values. An assistant can turn your physics into those
entries. Guide: [fit_functions/AI_GUIDE.md][g-fit-functions].

- **Attach:** the guide, and a few rows of your X and Y data if you can. Describe the
  model, what x and y are, and rough values of the parameters.
- **Ask, for example:**

  ```text
  I measure the voltage of a discharging capacitor against time in seconds. It decays
  exponentially towards a small offset: V = A*exp(-t/tau) + C. Please make a
  curve-fit model for it. Typical values are A about 5 V, tau about 2 s and C about
  0.1 V. Also tell me what to type in LSQ fit.
  ```

- **Then:** type the reply's **Fit Function**, **Params** and **Initial** into **LSQ
  fit** and click **Generate Plot**. The reply also contains a fit-model file; it is
  only used by PhysPlot's older curve-fit window, so you can skip it.

More: [Curve Fitting and Fit-Model Files](https://physplot.readthedocs.io/en/latest/extensions/curvefitting.html).

## Good results, safely

- **Use a real example.** A few dozen lines of a real file tell the assistant more than
  any description. If the data is confidential, keep the layout and replace the numbers.
- **Anything you attach is sent to the AI service.** Do not attach unpublished or
  confidential data unless your institution allows it.
- **One module per chat.** Start a new chat for the next module, and attach the guide again.
- **Ask for changes in plain words**, for example *"show the current in mA instead of A"*.
  The assistant sends the complete file again.
- **Keep names stable.** Saved sequences refer to a transformation by its file name and to a
  plotter by its `plotter_id`. Renaming either breaks sequences that use it.
- **The file is a program that runs on your computer.** The guides tell the assistant not to
  use the network, delete files or run other programs. If a reply imports something like
  `requests`, `subprocess` or `shutil`, or deletes files, ask why before using it.
- **Share what works.** Copy the file to a colleague's `Documents/PhysPlot/config/<folder>/`,
  or offer it to PhysPlot through an
  [issue on GitHub](https://github.com/MShirazAhmad/PhysPlot/issues).

See also: [Extending PhysPlot](index.rst) for writing modules by hand, and the
[Video Tutorials](../ui/videos.md) for a loader and a plotter module written live.

[g-importers]: https://github.com/MShirazAhmad/PhysPlot/blob/indevelopment/config/data_importers/AI_GUIDE.md
[g-transformations]: https://github.com/MShirazAhmad/PhysPlot/blob/indevelopment/config/transformations/AI_GUIDE.md
[g-plotters]: https://github.com/MShirazAhmad/PhysPlot/blob/indevelopment/config/plotter_modules/AI_GUIDE.md
[g-plot-types]: https://github.com/MShirazAhmad/PhysPlot/blob/indevelopment/config/plot_types/AI_GUIDE.md
[g-sequences]: https://github.com/MShirazAhmad/PhysPlot/blob/indevelopment/config/sequences/AI_GUIDE.md
[g-protocol-modules]: https://github.com/MShirazAhmad/PhysPlot/blob/indevelopment/config/protocol_modules/AI_GUIDE.md
[g-pipelines]: https://github.com/MShirazAhmad/PhysPlot/blob/indevelopment/config/pipelines/AI_GUIDE.md
[g-templates]: https://github.com/MShirazAhmad/PhysPlot/blob/indevelopment/config/templates/AI_GUIDE.md
[g-fit-styles]: https://github.com/MShirazAhmad/PhysPlot/blob/indevelopment/config/figureforge_fit_styles/AI_GUIDE.md
[g-plugins]: https://github.com/MShirazAhmad/PhysPlot/blob/indevelopment/config/figureforge_plugins/AI_GUIDE.md
[g-fit-functions]: https://github.com/MShirazAhmad/PhysPlot/blob/indevelopment/config/fit_functions/AI_GUIDE.md
