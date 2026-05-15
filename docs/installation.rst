Installation
============

Prerequisites
-------------

- Python 3.7 or newer
- pip

Usage modes
-----------

PhysPlot is available in two common modes:

1. Packaged desktop builds when provided by the official PhysPlot project.
2. Python script execution using ``PhysPlot.py``.

Install Python dependencies
---------------------------

.. code-block:: bash

   pip install PyQt5 matplotlib numpy scipy pandas

Run PhysPlot
------------

From the project directory:

.. code-block:: bash

   python PhysPlot.py

Keep the ``physplot/inc`` image assets with the source tree so the GUI can load
the official app icon and logo.
