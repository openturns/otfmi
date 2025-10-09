# Otfmi documentation

[Otfmi](https://github.com/openturns/otfmi) facilitates the probabilistic study of functional mockup units (FMUs) by interfacing [OpenTURNS](http://openturns.github.io/openturns/master/contents.html) with [PyFMI](https://pypi.org/project/PyFMI/). Using Otfmi, modelers can perform advanced probabilistic analysis on their FMU.

The core features of [Otfmi](https://github.com/openturns/otfmi) are:

* Load an FMU in an OpenTURNS object
* Set some initial values to ease initialization
* Simulate the model, for a single set of input values or a sample
* Retrieve and store the simulation results

<img src="_static/logo_persalys.png" alt="Otfmi Logo" style="width: 20%; float: left; margin-right: 10px;" />

[Otfmi](https://github.com/openturns/otfmi) is notably employed as backend for [Persalys](https://persalys.fr/?la=en) (OpenTURNS GUI).
The software is free and can be downloaded [here](https://persalys.fr/obtenir.php?la=en).

<br/>

---

```{tableofcontents}
```

---

## About FMI, OpenTURNS and PyFMI

The [functional mock-up interface (FMI) standard](https://fmi-standard.org/) specifies a multipurpose interface to 0D/1D physical models. It is currently supported by many software platforms, such as [OpenModelica](https://openmodelica.org/), [Dymola](https://www.3ds.com/fr/produits-et-services/catia/produits/dymola/), [Amesim](https://www.plm.automation.siemens.com/global/fr/products/simcenter/simcenter-amesim.html), [Ansys](https://www.ansys.com/), [Simulink](https://fr.mathworks.com/products/simulink.html), etc.

[OpenTURNS](http://openturns.github.io/openturns/master/contents.html) library proposes a large range of mathematical methods to quantify, propagate, and handle uncertainties. [PyFMI](https://pypi.org/project/PyFMI/) is a package for loading and interacting with FMUs in Python.

## The need for Otfmi

Using Python to easily perform computer experiments on 0D/1D models is appealing. Yet the toolchain, from the physical model to OpenTURNS, was incomplete. PyFMI objects, close to the FMUs methods, were to be adapted for easier use with OpenTURNS’ methods.

Otfmi is developed by [Phimeca](http://www.phimeca.com), on the demand of EDF Prisme department, to meet this need for compatibility between PyFMI objects and OpenTURNS.

## Terminology

**input, parameter, or input variable?**

The FMI standard and OpenTURNS have a (minor) conflict in the definition of *inputs*. In the [FMI standard](https://fmi-standard.org/docs/3.0.1/#ModelVariables) (see table 18):

* An FMU *parameter* remains constant during simulation (a single value).
* An FMU *input* evolves during simulation (time-dependent values).

In OpenTURNS, the terms *input* and *parameter* are synonymous and designate a variable in input of a probabilistic model. To reconcile the two worlds, we employ in Otfmi the terms of *parameter* and *input* in the sense of FMI. We call the input variables of a probabilistic model *variables*, or *input variables*.

**FMI : ME or CS?**

The FMI standard defines two kinds of FMUs: ModelExchange (ME) or CoSimulation (CS). The CoSimulation FMUs embed the numerical solver of their generation tool whereas the ModelExchange FMUs simulate with the solver of their host tool.

Choosing ME or CS depends on the use of the FMU (see [here](https://www.modelon.com/fmi-functional-mock-up-unit-types/)). Both kinds are handled similarly by Otfmi (and [Persalys](https://persalys.fr/?la=en)).

## Contact

You can contribute to the project or signal issues on the [Otfmi GitHub repository](https://github.com/openturns/otfmi). For questions on the code, contact [Sylvain Girard](https://github.com/SG-phimeca). For questions or remarks concerning the documentation, contact [Valentin Pibernus](https://github.com/vPibernus).

---

This package is licensed under the LGPL3.
