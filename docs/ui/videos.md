<!-- Generated from wiki/Video-Tutorials.md by scripts/sync_wiki_to_docs.py. Edit the wiki page. -->

# Video Tutorials

These short videos are live screen recordings of PhysPlot: the real mouse pointer
drives the app. Each video covers one feature. They are grouped in two YouTube
playlists:

- **[PhysPlot Basics](https://www.youtube.com/playlist?list=PLPkYnHekjU24)**:
  Simple Mode, from typing data to curve fitting.
- **[PhysPlot Advanced](https://www.youtube.com/playlist?list=PLelbbYnCXEdU)**:
  recorded protocols, `Sequence.py` files, bulk runs, and writing your own file
  loaders and plotter modules.

## Basics (Simple Mode)

0. **[Install PhysPlot on Windows](https://youtu.be/fVADS4sBwEs)** (2:10): a fresh Windows 11 with no Python,
   the one install command, then PhysPlot from the Start menu with its own taskbar icon.

   ```{youtube} fVADS4sBwEs
   :title: Install PhysPlot on Windows
   ```

1. **[The PhysPlot Window](https://youtu.be/JhQnXwG3moY)** (0:18): the spreadsheet,
   the column-role drop-downs, the three Simple Mode panels and the mode switch.

   ```{youtube} JhQnXwG3moY
   :title: The PhysPlot Window
   ```

2. **[Entering Values](https://youtu.be/Is0FpUS9vv8)** (0:21): type values into the
   table and name the columns.

   ```{youtube} Is0FpUS9vv8
   :title: Entering Values
   ```

3. **[Column Roles](https://youtu.be/PvGC_4iodYI)** (0:11): choose the X and Y columns
   with the role drop-downs.

   ```{youtube} PvGC_4iodYI
   :title: Column Roles
   ```

4. **[Generating Plots](https://youtu.be/DbsN_NGNpCM)** (0:19): plot with the Scatter
   Plotter, then with the Line Plotter.

   ```{youtube} DbsN_NGNpCM
   :title: Generating Plots
   ```

5. **[Error Bars](https://youtu.be/4KBA064UiQc)** (0:24): a Y Error column and the Error Bar Plotter.

   ```{youtube} 4KBA064UiQc
   :title: Error Bars
   ```

6. **[Curve Fitting](https://youtu.be/SnhtG1Fdh4Y)** (0:23): least-squares fit, legend label and PNG export.

   ```{youtube} SnhtG1Fdh4Y
   :title: Curve Fitting
   ```

7. **[Importing Data](https://youtu.be/AzZ-AloPkW0)** (0:16): Auto Loader picks the loader from the file type
   (here a Rigaku `.ras` XRD scan).

   ```{youtube} AzZ-AloPkW0
   :title: Importing Data
   ```

8. **[Transformations](https://youtu.be/8iVsJG8xUQ0)** (0:31): remove the XRD baseline, normalise to the strongest
   peak and plot the result.

   ```{youtube} 8iVsJG8xUQ0
   :title: Transformations
   ```

## Advanced

1. **[Recorded Protocol](https://youtu.be/I5nPKIvLaWk)** (0:17): every step is
   recorded; see it as a table and as Python code, and replay it.

   ```{youtube} I5nPKIvLaWk
   :title: Recorded Protocol
   ```

2. **[Saving a Sequence](https://youtu.be/l1zGnY109j4)** (0:12): save the protocol as
   a `Sequence.py` file.

   ```{youtube} l1zGnY109j4
   :title: Saving a Sequence
   ```

3. **[Bulk Processing](https://youtu.be/XzgZrVX2wkM)** (0:21): run a sequence on every
   file in a folder with Run Sequence (a simulated TiO2 anneal series).

   ```{youtube} XzgZrVX2wkM
   :title: Bulk Processing
   ```

4. **[How to Create a New File Loader](https://youtu.be/M_ypJWTtSnY)** (1:52): read a
   raw instrument text file, write a loader plugin live in Python, then import and
   plot with it. See also [Extending PhysPlot](../extensions/index.rst).

   ```{youtube} M_ypJWTtSnY
   :title: How to Create a New File Loader
   ```

5. **[How to Create a Plotter Module](https://youtu.be/AHWbQDqHvQ0)** (2:01): write a
   plotter module that finds emission peaks and labels their wavelengths, then use
   it with both of its plot types.

   ```{youtube} AHWbQDqHvQ0
   :title: How to Create a Plotter Module
   ```

6. **[Bulk Processing OES Spectra](https://youtu.be/9Waw3iNOO1s)** (1:21): one
   protocol, a labelled peak plot for every spectrum in a folder, and the same run
   from a terminal. See also [Bulk Runs and Headless Use](../user_guide/protocol_sequences.rst).

   ```{youtube} 9Waw3iNOO1s
   :title: Bulk Processing OES Spectra
   ```

The step-by-step written versions of these topics are in the
[Sequence Walkthrough](sequence_walkthrough.md) and the [UI Reference](index.md).
