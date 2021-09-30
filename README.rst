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

The preferred installation procedure uses Conda. Use the following commands::

    conda config --add channels conda-forge
    conda install otfmi 

It can be installed using the distutils mechanism (setup.py) or the windows installer.
Alternatively, it can be used without installation by adding the package directory ('otfmi') to the
PYTHONPATH.

Usage without installation
---------------------------
The module can be imported in a Python session as soon as
the otfmi folder is listed in the PYTHONPATH environment variable. If you installed Python
using Anaconda, the otfmi folder can be placed in any directory “monitored” by Anaconda,
for instance C:\\Users\\username\\Anaconda\\lib\\site-packages on Windows.

Installation from sources
-------------------------
The otfmi module can be installed from sources using the
classical distutils procedure. From the main folder, run the following command:

    python setup.py install

On windows, it is possible to avoid resorting to command line interface by using the
installer program otfmi-X.X.win32.exe (where X.X is the version number).

Manual removal
--------------
Removing otfmi if you installed it from sources with setup.py is just
a matter of removing all created files. Usually, it is a single file, otfmi-X.X-py2.7.egg
(X.X is the version number) located in the default directory for external module. The
path to this directory depends on your Python installation. On Windows with Anaconda, it
is C:\\Users\\username\\Anaconda\\lib\\site-packages.
The list of all created file can be retrieved by the following command

    python setup.py install --record list_file.txt

Documentation
=============

See the “User documentation” [USERDOC]_ for more usage instruction.

See the “Project documentation” [PROJECTDOC]_ for information about the module architecture.

Example scripts are given in the 'example' folder in the source tree.

Example FMU files are provided at [FMUDEMOS]_.

License
=======

This package is licensed under the LGPL3.

References
==========
.. [PYFMI] PyFMI Python module. url: https://github.com/modelon-community/PyFMI
.. [ANACONDA] Anaconda, Python distribution. url: http://continuum.io/downloads
.. [USERDOC] Girard, Sylvain (2017). otfmi: simulate FMUs from OpenTURNS: User documentation. Tech. rep. RT-PMFRE-00997-003. EDF. url: https://openturns.github.io/openturns/papers/otfmi_user_documentation.pdf
.. [PROJECTDOC] Girard, Sylvain (2017). otfmi: simulate FMUs from OpenTURNS: Project documentation. Tech. rep. RT-PMFRE-00997-002. EDF. url: https://openturns.github.io/openturns/papers/otfmi_project_documentation.pdf
.. [FMUDEMOS] FMU demonstration files. https://github.com/openturns/otfmi/tree/master/otfmi/example/file/fmu
