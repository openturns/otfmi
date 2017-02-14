Otfmi
====

This is the source tree or distribution for the otfmi package for simulating
functional mockup units (FMUs) from OpenTURNS.

The functional mock-up interface (FMI) standard specifies a format for
multipurpose, easy to build and reusable data interfaces to numerical models.
A functional mock-up unit (FMU) is a black box defined by the FMI standard,
akin to the wrappers familiar to the OpenTURNS’ community.

The purpose of the otfmi Python module is to promote the use of the
probabilistic approach with system models, in particular those written in
Modelica, by enabling easy manipulation of FMUs with OpenTURNS. The otfmi
module relies on one PyFMI, a module for manipulating FMUs within Python.


Installation
============

The distutils mechanism can be used:

    python setup.py install

Alternatively, add the package directory ('otfmi') to the PYTHONPATH.

Documentation
=============

See the “User documentation” [1] for more usage instruction.

See the “Project documentation” [2] for information about the module architecture.

Example scripts are given in the 'example' folder in the source tree.

[1] Girard, Sylvain (2017). otfmi: simulate FMUs from OpenTURNS: User documentation. Tech. rep. RT-PMFRE-00997-003. Phimeca.
[2] Girard, Sylvain (2017). otfmi: simulate FMUs from OpenTURNS: Project documentation. Tech. rep. RT-PMFRE-00997-002. Phimeca.


License
=======

This package is the propriety of EDF.
