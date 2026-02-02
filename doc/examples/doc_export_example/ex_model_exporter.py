"""
Export a function as Modelica model
===================================
"""

# %%
# :class:`~otfmi.FunctionExporter` export OpenTURNS functions as Modelica model.
# You can use OpenTURNS metamodels in a simulation environment.
#
# Currently, the inclusion of a metamodel in
# `OpenModelica GUI <https://openmodelica.org/?id=78:omconnectioneditoromedit&catid=10:main-category>`_
# has been performed once (see
# `this paper <https://www.researchgate.net/publication/354810878_Analysis_and_reduction_of_models_using_Persalys>`_).
#
# ------------
#
# Model generation
# ++++++++++++++++
#
# First, we create the OpenTURNS function to export as Modelica model.

import openturns as ot
import otfmi
import tempfile
from os.path import join

func = ot.SymbolicFunction("x", "exp(x)")
inputPoint = [2.0]
print(func(inputPoint))

# %%
# We create the model constructor and the folder in which save the model:
fmuExporter = otfmi.FunctionExporter(func)

model_path = join(tempfile.mkdtemp(), "myExponential.mo")
print(model_path)

# %%
# We create the FunctionExporter instance and export the exponential function.
# We specify ``gui=True`` to use the model in a Modelica GUI in connection
# with other components.
modelExporter = otfmi.FunctionExporter(func)
modelExporter.export_model(model_path, gui=True)

# %%
# Simple as it looks, this function actually writes a C-wrapper for
# the OpenTURNS function, then writes a Modelica model calling the C-wrapper
# as `External function <https://specification.modelica.org/master/functions.html#external-function-interface>`_.
#
# .. note::
#   The export requires `CMake <https://cmake.org/>`_, a C compiler, and the
#   OpenModelica compiler `OMC <https://www.openmodelica.org/?id=51:open-modelica-compiler-omccecatid=10:main-category>`_.
#
# ----------------------
#
# Model validation
# ++++++++++++++++
#
# We import this model in OpenModelica GUI. We can check the Modelica code:
#
# .. image:: /_static/modelica_gui_code.png
#    :scale: 80 %
#    :alt: alternate text
#    :align: center
#
# .. note::
#    The path to the C-wrapper is hard-coded in the model.
#
# We can also check the connectors position:
#
# .. image:: /_static/modelica_gui_interface.png
#    :scale: 60 %
#    :alt: alternate text
#    :align: center
#
# We connect the wrapper to an input sine signal
# (*Modelica.Blocks.Sources.Sine*) and to an output block
# (*Modelica.Blocks.Interfaces.RealOutput*):
#
# .. image:: /_static/TestMyExponential.png
#    :scale: 100 %
#    :alt: alternate text
#    :align: center
#
# We simulate the model on 1 second, with 50 time steps. We can verify that `y`
# output corresponds to the exponential of the sine signal.
#
# .. image:: /_static/show_output.png
#    :scale: 80 %
#    :alt: alternate text
#    :align: center
#
# .. note::
#    3 modes are available to export the function (see :class:`~otfmi.FunctionExporter`).
#    By default, the mode used to export the function is 'cxx'.
#    This mode leads to the fastest version of the model, but you need to
#    install OpenTURNS with conda.
