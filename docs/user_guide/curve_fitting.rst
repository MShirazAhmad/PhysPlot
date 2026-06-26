Curve Fitting
=============

For a full step-by-step flow, see :ref:`GUI Walkthrough — Adding Fit Functions in the Figure Editor <gui-curve-fitting-and-fit-labels>`.

Modern Figure Editor fitting
----------------------------

For Basic Plotter output, click **Generate Plot** to open the Figure Editor.
Select an axes, line, or scatter series and choose **Figure Editor > Fitting >
Add Fit Function**.

The fit dialog accepts a Python-style expression and parameter guesses. Examples:

- ``a*x + b``
- ``a*x**2 + b*x + c``
- ``a*np.exp(b*x) + c``

The fitted curve is added to the figure as a normal Matplotlib line, so it can
be styled in the Property Inspector and saved into a reusable template with
**Figure Editor > PhysPlot > Save as Template**.

Legacy fit models
-----------------

PhysPlot supports 11 optional fit models:

1. Linear
2. Quadratic
3. Cubic
4. 4th degree
5. 5th degree
6. 6th degree
7. 7th degree
8. 8th degree
9. 9th degree
10. 10th degree
11. ``Ae^(-bx)`` (implemented as exponential ``a*exp(bx)`` fit)

Enable and label legacy fits
----------------------------

For each fit, you can:

- Enable/disable with checkbox
- Choose label mode:
  - Off
  - Equation
  - Custom Label

.. image:: ../_static/gui_walkthrough/05_curve_fitting_label_mode.png
   :alt: Curve fitting controls
   :width: 700px
