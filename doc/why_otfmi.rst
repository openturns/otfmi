Why OTFMI ?
===========

About FMI, OpenTURNS and the FMI backends
------------------------------------------

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

`PyFMI <https://pypi.org/project/PyFMI/>`__ and
`FMPy <https://pypi.org/project/fmpy/>`__ are packages for loading and
interacting with FMUs in Python. otfmi uses PyFMI by default, and falls back
to FMPy when PyFMI is not available.

The need for otfmi
-------------------

Using Python to easily perform computer experiments on 0D/1D models is
seductive. Yet the tool chain, from the physical model to OpenTURNS, was
incomplete. FMI backend objects, close to the FMU methods, had to be
adapted for easier use with OpenTURNS methods.

otfmi is developed by `Phimeca <http://www.phimeca.com>`__, at the
request of EDF Prisme department, to meet this need of compatibility
between FMI backend objects and OpenTURNS.
