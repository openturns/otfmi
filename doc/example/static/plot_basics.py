# -*- coding: utf-8 -*-
# @Author: Claire-Eleuthèriane Gerrer
# @Date:   2021-10-26 09:44:54
# @Last Modified by:   Claire-Eleuthèriane Gerrer
# @Last Modified time: 2021-11-30 15:29:32


"""
FMUFunction basics
==================
"""

# %%
# ``otfmi.FMUFunction`` enables to use OpenTURNS' high
# level algorithms by wrapping the FMU into an :py:class:`openturns.Function` object.

# %%
# ------------

# %%
# | First, retrieve the path to the FMU *deviation.fmu*.
# Recall the deviation model is static, i.e. its output does not evolve over
# time.

import otfmi.example.utility
path_fmu = otfmi.example.utility.get_path_fmu("deviation")

# %%
# Wrap the FMU into an OpenTURNS function:

function = otfmi.FMUFunction(
    path_fmu, inputs_fmu=["E", "F", "L", "I"], outputs_fmu=["y"])
print(type(function))

# %%
# Simulate the FMU on a point:

import openturns as ot
inputPoint = ot.Point([3.0e7, 30000, 200, 400])
outputPoint = function(inputPoint)
print("y = {}".format(outputPoint))

# %%
# Simulate the FMU on a sample:

inputSample = ot.Sample(
    [[3.0e7, 30000, 200, 400],
    [3.0e7, 30000, 250, 400],
    [3.0e7, 30000, 300, 400]])
inputSample.setDescription(["E", "F", "L", "I"])

outputSample = function(inputSample)
print(outputSample)
