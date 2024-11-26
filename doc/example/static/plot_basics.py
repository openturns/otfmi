"""
FMUFunction basics
==================
"""

# %%
# :class:`~otfmi.FMUFunction` enables to use OpenTURNS' high
# level algorithms by wrapping the FMU into an :py:class:`openturns.Function` object.

# %%
# ------------

# %%
# First, retrieve the path to the FMU *deviation.fmu*.
# Recall the deviation model is static, i.e. its output does not evolve over time.
import openturns as ot
import otfmi.example.utility
path_fmu = otfmi.example.utility.get_path_fmu("deviation")

# %%
# Wrap the FMU into an OpenTURNS function:
function = otfmi.FMUFunction(
    path_fmu, inputs_fmu=["E", "F", "L", "I"], outputs_fmu=["y"]
)
print(type(function))

# %%
# Simulate the FMU on a point:
inputPoint = ot.Point([3.0e7, 30000, 200, 400])
outputPoint = function(inputPoint)
print(f"y = {outputPoint}")

# %%
# Simulate the FMU on a sample:
inputSample = ot.Sample(
    [[3.0e7, 30000, 200, 400], [3.0e7, 30000, 250, 400], [3.0e7, 30000, 300, 400]]
)
inputSample.setDescription(["E", "F", "L", "I"])
outputSample = function(inputSample)
print(outputSample)
