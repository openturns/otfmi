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

To install Conda, see `here <http://openturns.github.io/openturns/master/install.html#conda>`_.  
Once Conda is available, use the following commands to install OTFMI::

    conda config --add channels conda-forge
    conda config --set channel_priority strict
    conda install -y otfmi 



References
==========

See the “User documentation” [USERDOC]_ for more usage instruction.

See the “Project documentation” [PROJECTDOC]_ for information about the module architecture.

Example scripts are given in the 'example' folder in the source tree.

Example FMU files are provided at [FMUDEMOS]_.

License
=======

This package is licensed under the LGPL3.

Bibliography
============
.. [PYFMI] PyFMI Python module. url: https://github.com/modelon-community/PyFMI
.. [ANACONDA] Anaconda, Python distribution. url: http://continuum.io/downloads
.. [USERDOC] Girard, Sylvain (2017). otfmi: simulate FMUs from OpenTURNS: User documentation. Tech. rep. RT-PMFRE-00997-003. EDF. url: https://openturns.github.io/openturns/papers/otfmi_user_documentation.pdf
.. [PROJECTDOC] Girard, Sylvain (2017). otfmi: simulate FMUs from OpenTURNS: Project documentation. Tech. rep. RT-PMFRE-00997-002. EDF. url: https://openturns.github.io/openturns/papers/otfmi_project_documentation.pdf
.. [FMUDEMOS] FMU demonstration files. https://github.com/openturns/otfmi/tree/master/otfmi/example/file/fmu
