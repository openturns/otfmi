Terminology
===========


Input, parameter, or input variable ?
-------------------------------------

The FMI standard and OpenTURNS meet a (minor) conflict in the definition of *inputs*.
In the `FMI standard <https://fmi-standard.org/docs/3.0.1/#ModelVariables>`__
(see table 18):

* a FMU *parameter* remains constant during simulation (a single value).
* a FMU *input* evolves during simulation (time-dependent values).

In OpenTURNS, the terms *input* and *parameter* are synonym and designate a variable in input of a probabilistic model.

To reconcile the two worlds, we employ in otfmi the terms of *parameter* and *input* in the sense of FMI.
We call the input variables of a probabilistic model *variables*, or *input variables*.


FMI : ME or CS ?
----------------

The FMI standard defines 2 kinds of FMUs: ModelExchange (ME) or CoSimulation (CS).
The CoSimulation FMUs embed the numerical solver of their generation tool whereas
the ModelExchange FMUs simulate with the solver of their host tool.

Choosing ME or CS depends on the use of the FMU (see
`here <https://www.modelon.com/fmi-functional-mock-up-unit-types/>`__).
Both kinds are handled similarly by otfmi (and `Persalys <https://persalys.fr/?la=en>`__).
