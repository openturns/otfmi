"""
Set FMU simulation parameters
=============================
"""

# %%
# :class:`~otfmi.FMUPointToFieldFunction` is an OpenTURNS-friendly overlay of the class
# :py:class:`OpenTURNSFMUPointToFieldFunction`, closer to the underlying PyFMI
# implementation.
# Some FMU simulation parameters can be given to :class:`~otfmi.FMUPointToFieldFunction`,
# yet most of them can only be passed to an
# :py:class:`OpenTURNSFMUPointToFieldFunction`.

# %%
# First, retrieve the path to *epid.fmu*.
import otfmi.example.utility
import openturns as ot

path_fmu = otfmi.example.utility.get_path_fmu("epid")

# %%
# The FMU simulation start and final times are the only simulation-related
# parameter that can be passed to :class:`~otfmi.FMUPointToFieldFunction`.

mesh = ot.RegularGrid(0.0, 0.1, 20)

function = otfmi.FMUPointToFieldFunction(
    path_fmu,
    mesh,
    inputs_fmu=["infection_rate", "healing_rate"],
    outputs_fmu=["infected"],
    start_time=0.0,
    final_time=2.0,
)

inputPoint = ot.Point([0.007, 0.02])
outputSample = function(inputPoint)
print(outputSample)

# %%
# To set more parameters for the FMU simulation,
# :py:class:`OpenTURNSFMUPointToFieldFunction` can be employed. Below, we set the PyFMI
# algorithm running the simulation, and require simulation silent mode.

midlevel_function = otfmi.OpenTURNSFMUPointToFieldFunction(
    path_fmu,
    mesh,
    inputs_fmu=["infection_rate", "healing_rate"],
    outputs_fmu=["infected"],
    start_time=0.0,
    final_time=2.0,
)

outputPoint = midlevel_function.base.simulate(
    inputPoint, algorithm="FMICSAlg", options={"silent_mode": True}
)

# %%
# For advanced users, the middle-level class :py:class:`OpenTURNSFMUPointToFieldFunction` also gives
# access to the PyFMI model. We can hence access all PyFMI's object methods:

pyfmi_model = midlevel_function.base.get_model()
print(dir(pyfmi_model))

# %%
# .. note::
#    otfmi' classes :class:`~otfmi.FMUPointToFieldFunction` and :py:class:`OpenTURNSFMUPointToFieldFunction`
#    are designed to highlight the most useful PyFMI's methods and simplify their use!
