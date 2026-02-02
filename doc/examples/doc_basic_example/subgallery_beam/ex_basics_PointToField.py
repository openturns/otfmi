"""
Run simulations with high-level functions
-----------------------------------------
"""

# %%
# Prerequisites
# #############

# %%
# Load the following libraries :

import openturns as ot
import openturns.viewer as viewer
import otfmi
import otfmi.example.utility
from os.path import abspath

# %%
# Run simulations
# ###############

# %%
# Instead of loading the model with :class:`otfmi.fmi.load_fmu`,
# you can load it with the higher level object
# :class:`~otfmi.FMUPointToFieldFunction`.
# It enables you to use OpenTURNS' high level algorithms by wrapping the FMU
# into an :py:class:`openturns.Function` object.
# So, let's load the FMU *deviation.fmu*.
# Recall the deviation model is static, i.e. its output does not evolve over
# time.

path_fmu = otfmi.example.utility.get_path_fmu("deviation")
function = otfmi.FMUPointToFieldFunction(
    path_fmu, inputs_fmu=["E", "F", "L", "I"], outputs_fmu=["y"]
)

# %%
# Simulate the FMU on a point
inputPoint = ot.Point([3.0e7, 30000, 200, 400])
outputPoint = function(inputPoint)[-1]
print(f"y = {outputPoint}")

# %%
# Prepare the sample
inputSample = ot.Sample(
    [[3.0e7, 29000, 200, 400],
     [3.1e7, 30000, 250, 450],
     [2.9e7, 30000, 300, 350]]
)
inputSample.setDescription(["E", "F", "L", "I"])

# %%
# Now, simulate the FMU on the sample. The printed output show you 3
# series of results, from the 3 points in the sample.
# Why do we get series ? Because, even with a time-independent model like here,
# the simulation is time dependant, and last here 1s.

outputSample = function(inputSample)
print(outputSample)

# %%
# To get a simpler view of the results, you can use :

outputSample = [y[-1][0] for y in outputSample]
print(outputSample)


# %%
# Initialize FMUPointToFieldFunction
# ##################################

# %%
# The interest of using FMUs in Python lies in the ease to change its input
# / parameter values. This notably enables to study the behavior of the FMU
# with uncertain inputs / parameters.

# %%
# Initialization scripts can gather a large number of initial values.
# The use of initialization scripts (*.mos* files) is common in Dymola :
#
# - to save the value of all the variables of a model after simulation,
# - to restart simulation from a given point.
#
# The initialization script must be provided to
# :class:`~otfmi.FMUPointToFieldFunction` constructor.
# We thus create it now (using Python for clarity).

# %%
# .. note::
#    The initialization script can be automatically created in Dymola.

temporary_file = "initialization.mos"
with open(temporary_file, "w") as f:
    f.write("L = 300;\n")
    f.write("F = 25000;\n")

# %%
# If no initial value is provided for an input / parameter, it is set to its
# default initial value (as set in the FMU).

# %%
# We can now build the :class:`~otfmi.FMUPointToFieldFunction`.
# In the example below, we use the initialization script to fix the values
# of ``L`` and ``F`` in the FMU whereas ``E`` and ``I`` are the function
# variables.

function = otfmi.FMUPointToFieldFunction(
    path_fmu,
    inputs_fmu=["E", "I"],
    outputs_fmu=["y"],
    initialization_script=abspath("initialization.mos"),
)

# %%
# Come back to the function with 2 input variables defined above.
# ``F`` and ``L`` initial values are defined in the initialization script, and
# remain constant over time. We can now set probability laws on the function
# input variables ``E`` and ``I`` to propagate their uncertainty through the
# model:

lawE = ot.Uniform(65e9, 75e9)
lawI = ot.Uniform(1.3e7, 1.7e7)
dist = ot.ComposedDistribution([lawE, lawI])
inputSample = dist.getSample(10)

outputSample = function(inputSample)
outputSample = [y[-1] for y in outputSample]

graph = ot.HistogramFactory().build(outputSample).drawPDF()
view = viewer.View(graph)
view.ShowAll()


# %%
# .. note::
#    It is possible to set the value of a  model input in the
#    initialization script *and* use it as a function input variable. In this
#    case, the initial value from the initialization script is overriden.

# %%
# For instance, we consider the 4 model parameters as variables. Note the
# result is different from above, as the input point overrides the values from
# the initialization script.

smallExampleFunction = otfmi.FMUPointToFieldFunction(
    path_fmu,
    inputs_fmu=["E", "F", "L", "I"],
    outputs_fmu=["y"],
    initialization_script=abspath("initialization.mos"),
)

inputPoint = ot.Point([2e9, 2e4, 800, 7e7])
outputPoint = smallExampleFunction(inputPoint)
print(outputPoint[-1])

# %%
# Tune the simulation
# ###################

# %%
# :class:`~otfmi.FMUPointToFieldFunction` is an OpenTURNS-friendly overlay of
# the class :class:`~otfmi.OpenturnsFMUPointToFieldFunction`, closer to
# the underlying PyFMI implementation.
# Some FMU simulation parameters can be given to
# :class:`~otfmi.FMUPointToFieldFunction`, yet most of them can only be passed
# to an `~otfmi.OpenturnsFMUPointToFieldFunction`.

# %%
# The FMU simulation final time is the only simulation-related parameter that
# can be passed to :class:`~otfmi.FMUPointToFieldFunction`.
# This parameter is useless if the FMU is really time-independent
# (like this example); yet it can be come in use if the
# FMU requires time to converge.

function = otfmi.FMUPointToFieldFunction(
    path_fmu, inputs_fmu=["E", "I"], outputs_fmu=["y"], final_time=50.0
)

inputPoint = ot.Point([2e9, 7e7])
outputPoint = function(inputPoint)
print(outputPoint[-1])

# %%
# To set more parameters for the FMU simulation,
# :class:`~otfmi.OpenTURNSFMUPointToFieldFunction` can be
# employed. Below, we set the PyFMI algorithm running the simulation,
# and require simulation silent mode.

midlevel_function = otfmi.OpenTURNSFMUPointToFieldFunction(
    path_fmu, inputs_fmu=["E", "I"], outputs_fmu=["y"]
)

outputPoint = midlevel_function.base.simulate(
    inputPoint, algorithm="FMICSAlg", options={"silent_mode": True}
)

# %%
# For advanced users, the middle-level class
# :class:`~otfmi.OpenTURNSFMUPointToFieldFunction` also gives
# access to the PyFMI model. We can hence access all PyFMI's object methods:

pyfmi_model = midlevel_function.base.get_model()
print(dir(pyfmi_model))

# %%
# .. note::
#    otfmi' classes :class:`~otfmi.FMUPointToFieldFunction`
#    and :class:`~otfmi.OpenTURNSFMUPointToFieldFunction` are designed to
#    highlight the most useful PyFMI's methods and simplify their use!
