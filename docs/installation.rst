Installation
============

Prerequisites
-------------

- Python 3.10 or newer
- pip

For local GUI development on macOS, Python 3.12 is currently a safe default
because Qt/FigureForge wheels may lag the newest Python releases.

Install from PyPI
-----------------

.. code-block:: bash

   python -m pip install python-physplot

Launch the GUI:

.. code-block:: bash

   physplot-gui

Clone the repository
--------------------

.. code-block:: bash

   git clone https://github.com/MShirazAhmad/PhysPlot.git
   cd PhysPlot

Create and activate a virtual environment
-----------------------------------------

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

.. code-block:: bash

   python -m pip install --upgrade pip
   python -m pip install -e ".[dev]"

Run PhysPlot
------------

From the project directory:

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

Local GUI virtual environment
-----------------------------

If the system Python is newer than the GUI dependency stack supports, create a
local GUI environment with Python 3.12:

.. code-block:: bash

   /opt/homebrew/bin/python3.12 -m venv .gui-venv
   .gui-venv/bin/python -m pip install -e ".[dev]"
   .gui-venv/bin/python -m physplot_gui

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

Extension and template folders
------------------------------

When running from source, keep these top-level folders in the project root:

.. code-block:: text

   fileloader/     user file-loader plugins scanned at startup
   functions/      user transform-function plugins scanned at startup
   curvefitting/   legacy curve-fit model plugins scanned at startup
   styling/        figure-template JSON files refreshed with Template > Reload

See :doc:`extensions/modularity` for the full auto-loading map.
