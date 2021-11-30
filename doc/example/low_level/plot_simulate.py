# -*- coding: utf-8 -*-
# @Author: Claire-Eleuthèriane Gerrer
# @Date:   2021-10-25 09:17:56
# @Last Modified by:   Claire-Eleuthèriane Gerrer
# @Last Modified time: 2021-10-26 08:56:08

"""
Simulate an FMU
===============
"""

# %%
# The Otfmi ``simulate`` function instanciates, initializes and simulates the
# FMU.

# %%
# First, retrieve and load the FMU *deviation.fmu*.
#
import otfmi.example.utility
path_fmu = otfmi.example.utility.get_path_fmu("deviation")
model = otfmi.fmi.load_fmu(path_fmu)

# %%
# .. note::
#   | *model* is a PyFMI object, loaded with Otfmi’s overlay.
#   | As such, ``model.simulate()`` is a pure PyFMI method.
#   | Use ``òtfmi.fmi.simulate(model)`` to benefit from Otfmi’s overlay.


# %%
# Otfmi ``simulate`` function notably eases initializing a FMU, see
# :ref:`sphx_glr_auto_example_low_level_plot_initialize.py`.

# %%
# On top of the initialization keywords, PyFMI simulation keywords can be
# employed:
result = otfmi.fmi.simulate(model,
    start_time=0,  # PyFMI keyword
    final_time=1,  # PyFMI keyword
    initialization_parameters=(["L"], [300]))  # Otfmi keyword
print("y = %g" % result.final("y"))

# %%
# We can use these keyword to plot the deviation Y as function of the beam
# length L:

import openturns as ot
inputSample = ot.RegularGrid(1.0, 10.0, 10).getValues()

list_output = []
for length in inputSample:
    result = otfmi.fmi.simulate(model,
        initialization_parameters=(["L"], [length]))
    list_output.append(result.final("y"))
outputSample = ot.Sample([[xx] for xx in list_output])

import matplotlib.pyplot as plt
plt.figure()
plt.plot(inputSample, outputSample)
plt.show()

# %%
# | The interest of the higher-level functions TODO are:  
# | - avoid the *for* loop on the points of the design of experiment,
# | - automatic formatting of the simulation outputs.
