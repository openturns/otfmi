"""
Simulate an FMU
===============
"""

# %%
# The otfmi ``simulate`` function instanciates, initializes and simulates the
# FMU.

# %%
# First, retrieve and load the FMU *deviation.fmu*.
#
import openturns as ot
import otfmi.example.utility
import matplotlib.pyplot as plt

path_fmu = otfmi.example.utility.get_path_fmu("deviation")
model = otfmi.fmi.load_fmu(path_fmu)

# %%
# .. note::
#   | *model* is a PyFMI object, loaded with otfmi’s overlay.
#   | As such, ``model.simulate()`` is a pure PyFMI method.
#   | Use ``otfmi.fmi.simulate(model)`` to benefit from otfmi’s overlay.


# %%
# otfmi ``simulate`` function notably eases initializing a FMU, see
# :ref:`sphx_glr_auto_example_low_level_plot_initialize.py`.

# %%
# On top of the initialization keywords, PyFMI simulation keywords can be
# employed:
result = otfmi.fmi.simulate(
    model,
    start_time=0,  # PyFMI keyword
    final_time=1,  # PyFMI keyword
    initialization_parameters=(["L"], [300]),
)  # otfmi keyword
print("y = %g" % result.final("y"))

# %%
# We can use these keyword to plot the deviation Y as function of the beam
# length L:

inputSample = ot.RegularGrid(1.0, 10.0, 10).getValues()

list_output = []
for length in inputSample:
    result = otfmi.fmi.simulate(model, initialization_parameters=(["L"], [length]))
    list_output.append(result.final("y"))
outputSample = ot.Sample([[xx] for xx in list_output])

plt.figure()
plt.plot(inputSample, outputSample)
plt.show()

# %%
# | The interest of the higher-level functions are:
# | - avoid the *for* loop on the points of the design of experiment,
# | - automatic formatting of the simulation outputs.
