# -*- coding: utf-8 -*-
# @Author: Claire-Eleuthèriane Gerrer
# @Date:   2021-10-26 09:44:54
# @Last Modified by:   Claire-Eleuthèriane Gerrer
# @Last Modified time: 2021-11-22 14:44:20


"""
Export a function as Modelica model
===================================
"""

# %%
# ``otfmi.FunctionExporter`` enables to export OpenTURNS functions as Modelica model.
# The main interest is to use OpenTURNS metamodels in a simulation environment.
#
# .. warning::
#    ⚠️ **This functionality is experimental**.
#
# Currently, the inclusion of a metamodel in `OpenModelica GUI <https://openmodelica.org/?id=78:omconnectioneditoromedit&catid=10:main-category>`_ has been performed once (see
# `this paper <https://www.researchgate.net/publication/354810878_Analysis_and_reduction_of_models_using_Persalys>`_).
#
# ------------
#
# Model generation
# ++++++++++++++++
#
# First, we create the OpenTURNS function to export as Modelica model.

import openturns as ot
func = ot.SymbolicFunction('x', 'exp(x)')
inputPoint = ot.Point([2])
print(func(inputPoint))

# %%
# We create the model constructor and the folder in which save the model:

import otfmi
fmuExporter = otfmi.FunctionExporter(func)

import tempfile
from os.path import join
model_path = join(tempfile.mkdtemp(), "myExponential.mo")
print(model_path)

# %%
# We create the FunctionExporter instance and export the exponential function.
# We specify ``gui=True`` to use the model in a Modelica GUI in connection
# with other components.

modelExporter = otfmi.FunctionExporter(func)
modelExporter.export_model(model_path, gui=True)

# %%
# Simple as it looks, this function actually does the following :
#
# - write a C-wrapper for the OpenTURNS function,
# - write a Modelica model calling the C-wrapper as `External <shorturl.at/fhCU2>`_ function.
#
# .. note::
#   The export requires `CMake <https://cmake.org/>`_, a C compiler, and the OpenModelica compiler `OMC <https://www.openmodelica.org/?id=51:open-modelica-compiler-omccecatid=10:main-category>`_.
#
# ----------------------
#
# Model validation
# ++++++++++++++++
#
# We import this model in OpenModelica GUI. We can check the Modelica code:
#
# .. image:: /_static/modelica_gui_code.png
#    :width: 264px
#    :height: 252px
#    :scale: 100 %
#    :alt: alternate text
#    :align: center
#
# .. note::
#    The path to the C-wrapper is hard-coded in the model.
#
# We can also check the connectors position:
#
# .. image:: /_static/modelica_gui_interface.png
#    :width: 264px
#    :height: 252px
#    :scale: 100 %
#    :alt: alternate text
#    :align: center
# 
# We connect the wrapper to an input sine signal 
# (*Modelica.Blocks.Sources.Sine*) and to an output block 
# (*Modelica.Blocks.Interfaces.RealOutput*):
#
# .. image:: /_static/TestMyExponential.png
#    :width: 264px
#    :height: 252px
#    :scale: 100 %
#    :alt: alternate text
#    :align: center
# 
# We simulate the model on 1 second, with 50 time steps. We can verify that `y`
# output corresponds to the exponential of the sine signal.
# 
# .. image:: /_static/show_output.png
#    :width: 264px
#    :height: 252px
#    :scale: 100 %
#    :alt: alternate text
#    :align: center
#
# .. warning::
#    ⚠️ Compared to native Modelica functions, the included OpenTURNS function is
#    slow. In this case, 11 seconds of simulation were required for 50 time
#    steps (i.e. 50 function calls).