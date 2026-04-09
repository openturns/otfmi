Terminology
===========


Input, parameter, or input variable ?
-------------------------------------

The FMI standard and OpenTURNS meet a (minor) conflict in the definition of *inputs*.
In the `FMI standard <https://fmi-standard.org/docs/3.0.2/#ModelVariables>`__
(see section 2.4.7, and table 22):

* a FMU *parameter* remains constant during simulation (a single value);
* a FMU *input* evolves during simulation (time-dependent values).

In OpenTURNS, the terms *input* and *parameter* are synonym and designate a variable in input of a probabilistic model.

To reconcile the two worlds, we employ in otfmi the terms of *parameter* and *input* in the sense of FMI.
We call the input variables of a probabilistic model *variables*, or *input variables*.


FMI : ME or CS ?
----------------

The FMI standard defines two kinds of FMUs: ModelExchange (ME) or CoSimulation (CS).
The CoSimulation FMUs embed the numerical solver of their generation tool whereas
the ModelExchange FMUs simulate with the solver of their host tool.

Choosing ME or CS depends on the use of the FMU (see
`here <https://www.modelon.com/fmi-functional-mock-up-unit-types/>`__).
Both kinds are handled similarly by otfmi (and `Persalys <https://persalys.fr/?la=en>`__).

OpenTURNS objects
-----------------

OTFMI and related examples rely on some OpenTURNS objects such as:

- `Point <https://openturns.github.io/openturns/latest/user_manual/_generated/openturns.Point.html>`__, which is a real multidimensional vector;

- `Mesh <https://openturns.github.io/openturns/latest/user_manual/_generated/openturns.Mesh.html>`__, which is used in OTFMI to model a temporal discretisation.

- `Field <https://openturns.github.io/openturns/latest/auto_stochastic_processes/plot_field_manipulation.html>`__, which combines a mesh and a `sample <https://openturns.github.io/openturns/latest/user_manual/_generated/openturns.Sample.html>`__ to assign a value for each vertex of the mesh.
