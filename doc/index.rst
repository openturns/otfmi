Otfmi documentation
===================

Otfmi facilitates the probabilistic study of functional mockup units (FMUs) by interfacing `OpenTURNS <http://openturns.github.io/openturns/master/contents.html>`__ with `PyFMI <https://pypi.org/project/PyFMI/>`__. Using Otfmi, modelers can perform advanced probabilistic analysis on their FMU.

The core features of Otfmi are:

* load an FMU in an OpenTURNS object
* set some initial values to ease initialisation
* simulate the model, for a single set of input values or a sample
* retrieve and store the simulation results.

.. image:: _static/logo_persalys.png
     :align: left
     :scale: 5%

| Otfmi is notably employed as backend for `Persalys <https://persalys.fr/?la=en>`__ (`OpenTURNS <http://openturns.github.io/openturns/master/contents.html>`__ GUI). 
| The software is free and can be downloaded `here <https://persalys.fr/obtenir.php?la=en">`__.

.. container:: clearer

  .. image :: _static/spacer.jpg

--------------

.. toctree::
   :maxdepth: 1

   install

.. toctree::
   :maxdepth: 1

   api

.. toctree::
   :maxdepth: 1
   :glob:

   example/index

.. toctree::
   :maxdepth: 1
   :glob:

   application/index

--------------

About FMI, OpenTURNS and PyFMI
------------------------------

The `functional mock-up interface (FMI)
standard <https://fmi-standard.org/>`__ specifies a multipurpose
interfaces to 0D/1D physical models. It is currently supported by many
softwares, such as `OpenModelica <https://openmodelica.org/>`__,
`Dymola <https://www.3ds.com/fr/produits-et-services/catia/produits/dymola/>`__,
`Amesim <https://www.plm.automation.siemens.com/global/fr/products/simcenter/simcenter-amesim.html>`__,
`Ansys <https://www.ansys.com/>`__,
`Simulink <https://fr.mathworks.com/products/simulink.html>`__, etc.

`OpenTURNS <http://openturns.github.io/openturns/master/contents.html>`__
library proposes a large range of mathematical methods to quantify,
propagate and handle uncertainties.
`PyFMI <https://pypi.org/project/PyFMI/>`__ is a package for loading and
interacting with FMUs in Python.

The need for Otfmi
------------------

Using Python to easily perform computer experiments on 0D/1D models is
seducing. Yet the tool chain, from the physical model to OpenTURNS, was
incomplete. PyFMI objects, close to the FMUs methods, were to be adapted
for an easier use with OpenTURNS’ methods.

Otfmi is developed by `Phimeca <http://www.phimeca.com>`__, on the
demand of EDF Prisme department, to meet this need of compatibility
between PyFMI objects and OpenTURNS.

Terminology
-----------

**input, parameter, or input variable?**

| The FMI standard and OpenTURNS meet a (minor) conflict in the definition of *inputs*.
In the `FMI standard <https://fmi-standard.org/docs/3.0-dev/#definition-of-model-variables>`__
(see table 18):

* a FMU *parameter* remains constant during simulation (a single value).
* a FMU *input* evolves during simulation (time-dependent values).

In OpenTURNS, the terms *input* and *parameter* are synonym and designate a variable in input of a probabilistic model. To reconcile the two worlds, we employ in Otfmi the terms of *parameter* and *input* in the sense of FMI. We call the input variables of a probabilistic model *variables*, or *input variables*.

**FMI : ME or CS?**

The FMI standard defines 2 kinds of FMUs : ModelExchange (ME) or CoSimulation (CS). The CoSimulation FMUs embed the numerical solver of their generation tool whereas the ModelExchange FMUs simulate with the solver of their host tool.

Choosing ME or CS depends on the use of the FMU (see
`here <https://www.modelon.com/fmi-functional-mock-up-unit-types/>`__).
Both kinds are handled similarly by Otfmi (and `Persalys <https://persalys.fr/?la=en>`__).

Contact
-------

| You can contribute to the project or signal issues on `Otfmi GitHub
  repository <https://github.com/openturns/otfmi>`__.
| For questions on the code, contact `Sylvain
  Girard <https://github.com/SG-phimeca>`__ or `Claire-Eleuthèriane
  Gerrer <https://github.com/Claire-Eleutheriane>`__.
| For questions or remarks concerning the documentation, contact
  `Claire-Eleuthèriane
  Gerrer <https://github.com/Claire-Eleutheriane>`__.

--------------

This package is licensed under the LGPL3.
