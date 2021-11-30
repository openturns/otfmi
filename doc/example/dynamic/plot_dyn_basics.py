# -*- coding: utf-8 -*-
# @Author: Claire-Eleuthèriane Gerrer
# @Date:   2021-10-29 09:28:13
# @Last Modified by:   Claire-Eleuthèriane Gerrer
# @Last Modified time: 2021-11-30 15:18:46

"""
FMUPointToFieldFunction basics
==============================
"""

# %%
# ``otfmi.FMUPointToFieldFunction`` wraps the FMU into an OpenTURNS
# `PointToFieldFunction <http://shorturl.at/abtDU>`_ object.
# This kind of function accepts `Points <http://shorturl.at/mEI46>`_ or
# `Samples <http://shorturl.at/kmpqN>`_ as inputs, and outputs a
# `Sample <http://shorturl.at/kmpqN>`_ or a set of
# `Fields <http://shorturl.at/ptDKW>`_.

# %%
# ------------

# %%
# First, retrieve the path to *epid.fmu*.
# Recall the deviation model is dynamic, i.e. its output evolves over
# time.

import otfmi.example.utility
path_fmu = otfmi.example.utility.get_path_fmu("epid")

# %%
# Define the time grid for the FMU's output. The last value of the time grid,
# here 10., will define the FMU stop time for simulation.

import openturns as ot
mesh = ot.RegularGrid(0.0, 0.1, 100)  
meshSample = mesh.getVertices()
print(meshSample)

# %%
# .. note::
#    The FMU solver uses its own time grid for simulation. 
#    The FMU output is then interpolated on the user-provided time grid. 

# %%
# Wrap the FMU in an OpenTURNS' PointToFieldFunction object:

function = otfmi.FMUPointToFieldFunction(
    mesh,
    path_fmu,
    inputs_fmu=["infection_rate"],
    outputs_fmu=["infected"],
    start_time=0.0,
    final_time=10.0)
print(type(function))

# %%
# .. note::
#    The start and final times must define an interval comprising the mesh.
#    Setting manually the start and final times is recommended to avoid
#    uncontrolled simulation duration.

# %%
# Simulate the function on an input Point yields an output Sample, corresponding
# to the output evolution over time:

inputPoint = ot.Point([0.007])
outputSample = function(inputPoint)

import matplotlib.pyplot as plt
plt.xlabel("FMU simulation time (s)")
plt.ylabel("Number of Infected")
plt.plot(meshSample, outputSample)
plt.show()

# %%
# Simulate the function on a input Sample yields a set of Fields,
# called `ProcessSample <http://shorturl.at/auCM6>`_:

inputSample = ot.Sample(
    [[0.007],
    [0.005],
    [0.003]])
outputProcessSample = function(inputSample)
print(outputProcessSample)

# %%
# Visualize the time evolution of the ``infected`` over time, depending on the
# `ìnfection_rate`` value:

import openturns.viewer as viewer
gridLayout = outputProcessSample.draw()
graph = gridLayout.getGraph(0,0)
graph.setTitle("")
graph.setXTitle("FMU simulation time (s)")
graph.setYTitle("Number of infected")
graph.setLegends([str(line[0]) for line in inputSample])
view = viewer.View(graph, legend_kw={"title": "infection rate"})
view.ShowAll()
