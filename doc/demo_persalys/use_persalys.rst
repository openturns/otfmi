Sensitivity analysis with Persalys
==================================

.. image:: ../_static/logo_persalys.png
     :align: left
     :scale: 5%

`Persalys <https://persalys.fr/>`__ is a graphical user interface to some otfmi
and `OpenTURNS <http://openturns.github.io/openturns/master/contents.html>`__ methods.
The software is free and can be downloaded `here <https://persalys.fr/obtenir.php?la=en">`__.

.. container:: clearer

  .. image :: ../_static/spacer.jpg

A parabolic solar collector concentrates the sun light on a tube via parabolic mirrors.
A fluid (generally oil) circulates in this tube and heats up thanks to the reverberated sunlight.

We model this installation in Modelica using the
`ThermoSysPro <https://thermosyspro.com/>`__ component
`SolarCollector <https://thermosyspro.gitlab.io/documentation/src/Solar/Collectors/SolarCollector.html>`__.
The collector inputs (atmospheric temperature, sun radiation and sun incidence angle) are set to constant values.
We collect the heat flow between the collector output and a source of constant
temperature symbolizing an infinite oil flow in the tube.

This model is static, i.e. \ **its output does not depend on time**.

* :download:`Download the Modelica model <./Solar.mo>`
* :download:`Download the FMU (Windows 64) <./win64/Solar.fmu>`
* :download:`Download the FMU (Linux 64) <./linux64/Solar.fmu>`

.. image:: /_static/demo_persalys/SolarCollector.png
   :scale: 80 %
   :alt: alternate text
   :align: center

**Which input variable(s) influence the most the heat flow ?**

Sobol’ first-order indices quantify the proportion of the output variance explained by an input variable.
As Sobol’ first-order indices for all input variables sum to 1, they provide a ranking of the input variables.
The higher the index, the more influent the input variable.

We use Persalys to compute the Sobol’ indices for the three input variables:
the atmospheric temperature ``T_atm.k``, ``angle_incidence.k``, ``radiation.k``.

--------------

The solar collector model is exported under the FMI standard 2.0 (Co-Simulation format) into *Solar.fmu*.
We first load the FMU in Persalys:

.. image:: /_static/demo_persalys/select_fmu.png
   :scale: 60 %
   :alt: alternate text
   :align: center

To select the FMU in the files tree view, we click on the three dots at the right of the empty line.
A new window opens, in which we select the FMU named *Solar.fmu*.

.. image:: /_static/demo_persalys/select_fmu_name.png
   :scale: 60 %
   :alt: alternate text
   :align: center

Once the FMU is loaded, all its variables (inputs, outputs, local quantities, etc) are displayed.
We select the variables for the sensitivity analysis:

* output variable: ``heatFlow``,
* input variables: ``T_atm.k``, ``angle_incidence.k``, ``radiation.k``.

.. image:: /_static/demo_persalys/select_one_input.png
   :scale: 60 %
   :alt: alternate text
   :align: center

Now that the variables are set, Persalys ‘’tree of possibles’’ appears.
The methods which can be used are colored in deep blue, whereas the methods with
prerequisite steps appear with a forbidden pannel.

We can see that, before performing sensitivity analysis, we first have to set a probabilistic model.
In other words, we have to set the probability distribution of the 3 input variables.

.. image:: /_static/demo_persalys/tree.png
   :scale: 60 %
   :alt: alternate text
   :align: center

We consider the following laws for the input variables:

* sun incidence angle: normal law :math:`\mathcal{N}(30, 3)`.
  It corresponds to a fixed time in the day (with the sun incidence angle varying slightly around its nominal value).
* sun radiation: normal law :math:`\mathcal{N}(70, 50)` truncated at 0.
  It corresponds to a standard sunlight, varying depending on the weather.
* atmospheric temperature: normal law :math:`\mathcal{N}(300, 10)`.
  It corresponds to variations depending on the season.

.. image:: /_static/demo_persalys/probabilistic_model.png
   :scale: 60 %
   :alt: alternate text
   :align: center

We select the Sobol’ indices as method for sensitivity analysis.
The maximal computation time must be set to 5 minutes to enable convergence.

.. image:: /_static/demo_persalys/start_sobol.png
   :scale: 60 %
   :alt: alternate text
   :align: center

Sobol’ indices are displayed as a graph. The sun radiation is the
variable with the strongest influence on the output.

.. image:: /_static/demo_persalys/sobol_result.png
   :scale: 60 %
   :alt: alternate text
   :align: center

Keep in mind that the result relies on 2 assumptions:

* the input variables are independent,
* the input variables follow the probability distributions set here above.

--------------

For further exploration of the solar collector model with Persalys, see
`Analysis and reduction of models using
Persalys <https://www.researchgate.net/publication/354810878_Analysis_and_reduction_of_models_using_Persalys>`__.
In this paper, metamodeling (aka model reduction) is performed on the solar collector.
The OpenTURNS metamodel is then inserted in a solar power plant model using
`FMUExporter </auto_example/ot_to_fmu/plot_model_exporter>`__.
