:hide-sidebar-secondary: true:

otfmi documentation
===================

A bridge between `OpenTURNS <http://openturns.github.io/openturns/master/contents.html>`__ and functional mockup units (FMUs), based on `PyFMI <https://pypi.org/project/PyFMI/>`__ .

.. grid::
   :gutter: 3

   .. grid-item::
      :columns: auto

      .. button-link:: install.html
         :color: primary
         :shadow:

         🚀 Get Started

.. grid:: 1 2 1 2
    :gutter: 3

    .. grid-item-card:: 🎲 Load a FMU in OpenTURNS

      You have a model in FMU format ? OTFMI transforms it into a `OpenTURNS <http://openturns.github.io/openturns/master/contents.html>`__ object, to let you analyze your model.

    .. grid-item-card:: 🚀 Simulate the model

      Initialise your model and run simulations, for a single set of input values or a sample

    .. grid-item-card:: 🔌 Integrate an OpenTURNS model into a Modelica model.

      You can export your machine learning model built with OpenTURNS, to use it as a component of your Modelica model.        

    .. grid-item-card:: 🍒 Use OTFMI through Persalys

      .. image:: _static/logo_persalys.png
         :align: left
         :scale: 3%

      OTFMI is used within the OpenTURNS GUI `Persalys <https://persalys.fr/?la=en>`__ .
      Persalys is free and can be downloaded `here <https://persalys.fr/obtenir.php?la=en">`__.




You can contribute to the project or signal issues on `otfmi GitHub repository <https://github.com/openturns/otfmi>`__.

This package is licensed under the LGPL3.


.. toctree::
   :hidden:
   :maxdepth: 1

   why_otfmi

.. toctree::
   :hidden:
   :maxdepth: 1

   terminology

.. toctree::
   :hidden:
   :maxdepth: 1

   Installation instructions <install>

.. toctree::
   :hidden:
   :maxdepth: 1
   :glob:

   Examples <auto_example/index>

.. toctree::
   :hidden:
   :maxdepth: 1

   api

