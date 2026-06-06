Installation
============

Prerequisites
-------------

- Python 3.10 or newer
- pip

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

Backend command-line entry point:

.. code-block:: bash

   physplot --version

Keep the ``physplot/inc`` image assets with the source tree so the GUI can load
the official app icon and logo.
