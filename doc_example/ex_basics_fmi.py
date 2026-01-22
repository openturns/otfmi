"""
Run simulations with low-level functions
----------------------------------------
"""


# %%
# Prerequisites
# #############

# %%
# First, load the following libraries :
import otfmi.example.utility
import pyfmi
import openturns as ot
import matplotlib.pyplot as plt

# %%
# Load the model
# ##############

# %%
# First, retrieve the path to the example FMU *deviation.fmu*.
# Then, load the fmu with the `load_fmu` method.
#

path_fmu = otfmi.example.utility.get_path_fmu("deviation")
model = otfmi.fmi.load_fmu(path_fmu)

# %%
# You can load your model by enforcing CoSimulation kind and specifying the filename for the
# logs writing:
model = otfmi.fmi.load_fmu(path_fmu, kind="CS", log_file_name="deviation.log")

# %%
# .. note::
#   If the FMU is both ModelExchange and CoSimulation, the CoSimulation type is
#   favoured.
#   This choice, **opposite to PyFMI's default**, enables the CoSimulation
#   to impose a solver not available in PyFMI.

# %%
# The link betwen otfmi and pyfmi
# ###############################

# %%
# OTFMI `load_fmu` is an overlay of PyFMI `load_fmu` function.
# Hence the FMU loaded here upper benefits of all PyFMI's methods.
# You can get the list of options of `pyfmi.load_fmu` by typing :

print(help(pyfmi.load_fmu))

# %%
# For example, ``get_description`` is a PyFMI method :
model.get_description()

# %%
# FMU exploration
# ###############

# %%
# Knowledge about the FMU is necessary to setup a simulations.
#
# - What is the name of each variable ?
# - Which are the inputs, outputs, parameters ?
# - Which are booleans, reals, integers ?
# - What is their default start value ?

# %%
# You can get the FMU variables names with the ``get_name_variable`` method.
# This shows all variables : inputs, parameters, outputs.

list_name = otfmi.fmi.get_name_variable(model)
print(list_name)

# %%
# You need to identify their causality in the model:

for name in list_name:
    causality = otfmi.fmi.get_causality_str(model, name)
    print(f"{name}: {causality}")

# %%
# | Yet the variables type is not known: real, integer, boolean, string?
# | Let check using `PyFMI's method <http://shorturl.at/dJ157>`_:

for name in list_name:
    typ = model.get_variable_data_type(name)
    print(f"{name}: {typ}")

# %%
# | The type `0` corresponds to `Real` (aka "float") variables.
# | Let check the variables default start value in the FMU:

dict_start_value = otfmi.fmi.get_start_value(model)
print(dict_start_value)

# %%
# .. note::
#    Function `otfmi.fmi.get_start_value` only returns the start value of
#    variables with types Real, Integer or Boolean.

# %%
# With this knowledge on the FMU variables, we can now simulate it (with
# non-default initialization values if required).


# %%
# Run a simulation
# ################

# %%
# The otfmi ``simulate`` function instanciates, initializes and simulates the
# FMU.

# Here, we define a simulation with our `model`, from time 0 to 1s,
# and we initialize the beam's length `L` at 300:
result = otfmi.fmi.simulate(
    model,
    start_time=0,  # PyFMI keyword
    final_time=1,  # PyFMI keyword
    initialization_parameters=(["L"], [300]),  # otfmi keyword
)
print("y = %g" % result.final("y"))

# %%
# .. note::
#    The *model* is a PyFMI object, loaded with otfmi’s overlay.
#    As such, ``model.simulate()`` is a pure PyFMI method.
#    Use ``otfmi.fmi.simulate(model)`` to benefit from otfmi’s overlay.


# %%
# At this stage, simulations are ready to be executed.
# We use OpenTURNS to generate a set of simulations, by sampling the initial
# value of the the beam's length `L` with 10 different values from 1 to 100.

inputSample = ot.RegularGrid(1.0, 10.0, 10).getValues()

list_output = []
for length in inputSample:
    result = otfmi.fmi.simulate(
        model,
        initialization_parameters=(["L"], [length]))
    list_output.append(result.final("y"))

outputSample = ot.Sample([[xx] for xx in list_output])

# %%
# Finally, we use matplotlib to plot the results

plt.figure()
plt.plot(inputSample, outputSample)
plt.xlabel("Initial value of the beam's length.")
plt.ylabel("Deviation.")
plt.show()

# %%
# Conclusion
# ################

# %%
# You have just seen how to run several simulations, by tuning just one parameter.
# OTFMI provides higher-level functions to :
#
# - avoid the *for* loop on the points of the design of experiment,
# - automatic formatting of the simulation outputs.
#
# The next example shows you a shorter and easier way to run a set of simulations.
