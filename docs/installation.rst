Installation
============

Prerequisites
-------------

- Python 3.11, 3.12 or 3.13. The Figure Editor (FigureForge) does not support
  newer Python versions yet and keeps numpy below 2.
- pip

Python 3.12 is the recommended default because the Qt/FigureForge dependency
stack has reliable wheels on macOS and Windows. PhysPlot is not yet published on
PyPI; install it with the macOS command below, the Windows installer, or from
source.

macOS: one command
------------------

Open **Terminal** and paste:

.. code-block:: bash

   curl -fsSL https://raw.githubusercontent.com/MShirazAhmad/PhysPlot/indevelopment/scripts/install_macos.sh | bash

The script:

- finds Python 3.11–3.13, or installs Python 3.12 with Homebrew (without
  Homebrew it asks you to install Python 3.12 from python.org first),
- downloads PhysPlot and installs it with its dependencies into ``~/.physplot``
  (about 1 GB the first time),
- creates **PhysPlot.app** in ``~/Applications``.

Run the same command again to update. Uninstall with
``rm -rf ~/.physplot ~/Applications/PhysPlot.app``; your files in
``Documents/PhysPlot`` are kept. Set ``PHYSPLOT_REF`` to install another branch
or tag (``curl … | PHYSPLOT_REF=<ref> bash``).

Install from source
-------------------

Clone the repository
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git clone https://github.com/MShirazAhmad/PhysPlot.git
   cd PhysPlot

Create and activate a virtual environment
-----------------------------------------

Create the project virtual environment in ``.venv``. On macOS, use Python 3.12
when it is available:

.. code-block:: bash

   /opt/homebrew/bin/python3.12 -m venv .venv

Otherwise, use the default Python on your system:

.. code-block:: bash

   python -m venv .venv

On macOS/Linux:

.. code-block:: bash

   source .venv/bin/activate

On Windows (PowerShell):

.. code-block:: powershell

   .venv\Scripts\Activate.ps1

Install Python dependencies
---------------------------

For source development, install PhysPlot in editable mode with the development
extras:

.. code-block:: bash

   python -m pip install --upgrade pip
   python -m pip install -e ".[dev]"

If an environment only supports requirements files, install the runtime
dependencies first and then install the local package:

.. code-block:: bash

   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   python -m pip install -e .

Run PhysPlot
------------

From the project directory:

.. code-block:: bash

   .venv/bin/python -m physplot_gui

When the virtual environment is activated, the console entry point is also
available:

.. code-block:: bash

   physplot-gui

Equivalent entry points:

.. code-block:: bash

   python-physplot-gui
   python -m physplot_gui

Backend command-line entry point:

.. code-block:: bash

   physplot --version
   python-physplot --version
   physplot run-workflow workflow.py --input data.csv --output outputs/run
   physplot run-bulk workflow.py --input-folder data/ --output-folder outputs/batch

Keep the ``physplot/inc`` image assets with the source tree so the GUI can load
the official app icon, centered PhysPlot logo, and left-side LSF/PhysLab header
logos.

Build a Windows installer
-------------------------

Build the standalone Windows app from inside Windows, such as a Windows 11
Parallels VM. The installer build uses PyInstaller for the bundled app and
Inno Setup 6 for the final setup executable.

In Windows PowerShell:

.. code-block:: powershell

   scripts\build_windows_installer.ps1

The script creates:

.. code-block:: text

   dist\PhysPlot\PhysPlot.exe
   dist\installer\PhysPlot-<version>-Windows-Setup.exe

If Inno Setup is not installed, the script still builds the portable
``dist\PhysPlot`` app folder and prints a warning. To intentionally skip the
installer wrapper:

.. code-block:: powershell

   scripts\build_windows_installer.ps1 -SkipInstaller

Install Inno Setup 6 from https://jrsoftware.org/isinfo.php when you need the
single-file setup executable.

The installer places the application under ``Program Files\PhysPlot`` and
seeds an editable copy of the ``config`` tree in
``Documents\PhysPlot\config`` (existing user files are never overwritten).
PhysPlot loads data importers, transformations, plotter modules, plot types,
protocol modules, sequences, pipelines, templates, fit functions, and fit-style
presets from that folder at startup, so users can add, edit, or delete modules
there without recompiling or reinstalling. Choose *File > Open Config Folder*
to jump there and *File > Reload Config Modules* to re-scan while the app is
running.

Extension and template folders
------------------------------

Reusable modules live under ``config/``. The per-user copy in
``Documents/PhysPlot/config/`` (all platforms; override with
``PHYSPLOT_USER_DIR``) is searched first and a file with the same name there
overrides the bundled one:

.. code-block:: text

   config/data_importers/          file-loader plugins scanned at startup
   config/transformations/         transform-function plugins scanned at startup
   config/fit_functions/           legacy curve-fit model plugins scanned at startup
   config/plotter_modules/         reusable custom plotter module definitions
   config/plot_types/              reusable plot-type/protocol metadata
   config/protocol_modules/        reusable protocol/workflow building blocks
   config/sequences/               complete reusable Sequence.py workflow files
   config/templates/               figure-template JSON files refreshed with Template > Reload
   config/figureforge_fit_styles/  LSQ fit-style presets refreshed in Simple Mode
   config/pipelines/               reusable transformation pipeline JSON files

See :doc:`extensions/modularity` for the full auto-loading map.
