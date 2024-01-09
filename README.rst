.. image:: https://github.com/openturns/otfmi/actions/workflows/build.yml/badge.svg?branch=master
    :target: https://github.com/openturns/otfmi/actions/workflows/build.yml

OTFMI Module
============

This is the source tree or distribution for the otfmi package for simulating
functional mockup units (FMUs) from OpenTURNS.

The functional mock-up interface (FMI) standard specifies a format for
multipurpose, easy to build and reusable data interfaces to numerical models.
A functional mock-up unit (FMU) is a black box defined by the FMI standard,
akin to the wrappers familiar to the OpenTURNS’ community.

The purpose of the otfmi Python module is to promote the use of the
probabilistic approach with system models, in particular those written in
Modelica, by enabling easy manipulation of FMUs with OpenTURNS. The otfmi
module relies on PyFMI, a module for manipulating FMUs within Python.


Installation
============

The preferred installation procedure uses Conda. 

First install OpenTURNS in conda, according to the instructions `here <http://openturns.github.io/openturns/master/install.html#conda>`_.
Once OpenTURNS is installed, use the following commands to install OTFMI::

    conda install -y otfmi 


Documentation
=============

A complete documentation, including onboarding examples and concrete applications, is available `here <http://openturns.github.io/otfmi/master/>`_.

Example FMU files are provided at [FMUDEMOS]_.


License
=======

This package is licensed under the LGPL3.

Bibliography
============
.. [PYFMI] PyFMI Python module. url: https://github.com/modelon-community/PyFMI
.. [FMUDEMOS] FMU demonstration files. https://github.com/openturns/otfmi/tree/master/otfmi/example/file/fmu
