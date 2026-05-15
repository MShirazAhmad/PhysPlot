Installation
============

Prerequisites
-------------

- Python 3.7 or newer
- pip

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
   python -m pip install -r requirements.txt

Run PhysPlot
------------

From the project directory:

.. code-block:: bash

   python PhysPlot.py

Alternative module entry point:

.. code-block:: bash

   python -m physplot

Keep the ``physplot/inc`` image assets with the source tree so the GUI can load
the official app icon and logo.
