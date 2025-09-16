"""
Initialize an FMU with non-default values
=========================================
"""

# %%
# The interest of using FMUs in Python lies in the ease to change its input
# / parameter values. This notably enables to study the behavior of the FMU
# with uncertain inputs / parameters.

# %%
# .. note::
#    | A FMU *parameter* remains constant during simulation (a single value).
#    | A FMU *input* evolves during simulation (time-dependent values).
#    | See the `FMI Standard <http://shorturl.at/kpJR5>`_ for more details.

# %%
# First, retrieve and load the FMU *deviation.fmu*.
#
import otfmi.example.utility
from os.path import abspath

path_fmu = otfmi.example.utility.get_path_fmu("deviation")
model = otfmi.fmi.load_fmu(path_fmu)

# check the beam default length and bending load values
print(model.get_variable_start("L"))
print(model.get_variable_start("F"))

# %%
# We want to set the cantilever beam length to 300 m and the bending load to
# 25000 N.

# %%
# Using inline argument
# ---------------------

# %%
# The beam length can be required directly in the ``simulate`` function:
result = otfmi.fmi.simulate(model, initialization_parameters=[("L", "F"), (300, 25000)])

# check parameters value and show output value
print("L = %g" % result.final("L"))  # check parameter value
print("F = %g" % result.final("F"))  # check parameter value
print("y = %g" % result.final("y"))  # print output value

# %%
# This way of doing is practical when only a few number of parameters / inputs
# must be set. For larger numbers of variables to initialize, the use of scripts
# is recommended.

# %%
# Using initialization scripts
# ----------------------------

# %%
# Initialization scripts can gather a large number of initial values.
# The use of initialization scripts (*.mos* files) is common in Dymola:
# - to save the value of all the variables of a model after simulation,
# - to restart simulation from a given point.

# %% First, write the initialization script.
# .. note::
#    The initialization script can be automatically created in Dymola.

# %%
# For clarity, we write the initialization script using Python.
temporary_file = "initialization.mos"
with open(temporary_file, "w") as f:
    f.write("L = 300;\n")
    f.write("F = 25000;\n")

# %%
# otfmi ``simulate`` function launches FMU initialization, using the
# designated script, then simulates the FMU.
result = otfmi.fmi.simulate(model, initialization_script=abspath(temporary_file))

# check parameters value and show output value
print("L = %g" % result.final("L"))  # check parameter value
print("F = %g" % result.final("F"))  # check parameter value
print("y = %g" % result.final("y"))  # print output value
