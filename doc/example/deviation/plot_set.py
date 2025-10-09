"""
Set FMU simulation parameters
=============================
"""

# %%
# `~otfmi.FMUPointToFieldFunction` is an OpenTURNS-friendly overlay of the class
# `~otfmi.OpenturnsFMUPointToFieldFunction`, closer to the underlying PyFMI implementation.
# Some FMU simulation parameters can be given to `~otfmi.FMUPointToFieldFunction`, yet most of
# them can only be passed to an `~otfmi.OpenturnsFMUPointToFieldFunction`.

# %%
# First, retrieve the path to the FMU *deviation.fmu*.
# Recall the deviation model is static, i.e. its output does not evolve over
# time.

import otfmi.example.utility
import openturns as ot

path_fmu = otfmi.example.utility.get_path_fmu("deviation")


# %%
# The FMU simulation final time is the only simulation-related parameter that
# can be passed to :class:`~otfmi.FMUPointToFieldFunction`. This parameter is useless if the FMU is
# really time-independent (like this example); yet it can be come in use if the
# FMU requires time to converge.

function = otfmi.FMUPointToFieldFunction(
    path_fmu, inputs_fmu=["E", "I"], outputs_fmu=["y"], final_time=50.0
)

inputPoint = ot.Point([2e9, 7e7])
outputPoint = function(inputPoint)
print(outputPoint[-1])

# %%
# To set more parameters for the FMU simulation, `~otfmi.OpenTURNSFMUPointToFieldFunction` can be
# employed. Below, we set the PyFMI algorithm running the simulation,
# and require simulation silent mode.

midlevel_function = otfmi.OpenTURNSFMUPointToFieldFunction(
    path_fmu, inputs_fmu=["E", "I"], outputs_fmu=["y"]
)

outputPoint = midlevel_function.base.simulate(
    inputPoint, algorithm="FMICSAlg", options={"silent_mode": True}
)

# %%
# For advanced users, the middle-level class :class:`~otfmi.OpenTURNSFMUPointToFieldFunction` also gives
# access to the PyFMI model. We can hence access all PyFMI's object methods:

pyfmi_model = midlevel_function.base.get_model()
print(dir(pyfmi_model))

# %%
# .. note::
#    otfmi' classes `~otfmi.FMUPointToFieldFunction` and `~otfmi.OpenTURNSFMUPointToFieldFunction` are designed to
#    highlight the most useful PyFMI's methods and simplify their use!
