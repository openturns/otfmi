"""
Load an FMU
===========
"""
# %%
# First, retrieve the path to the example FMU *deviation.fmu*.
#
import pyfmi
import otfmi.example.utility

path_fmu = otfmi.example.utility.get_path_fmu("deviation")

# %%
# Loading an FMU only requires the FMU name or path.

model = otfmi.fmi.load_fmu(path_fmu)

# %%
# If the FMU is both ModelExchange and CoSimulation, the CoSimulation type is
# favoured.
# This choice, **opposite to PyFMI's default**, enables the CoSimulation
# to impose a solver not available in PyFMI.

# %%
# All options of `pyfmi.load_fmu` can be passed on to otfmi:
print(help(pyfmi.load_fmu))

# %%
# For instance, enforce CoSimulation kind and specify the filename for the
# logs writing:
model = otfmi.fmi.load_fmu(path_fmu, kind="CS", log_file_name="deviation.log")

# %%
# .. note::
#    otfmi `load_fmu` is an overlay of PyFMI `load_fmu` function.
#    Hence the FMU loaded here upper benefits of all PyFMI's methods.

# %%
# For example, ``get_description`` is a PyFMI method (not re-implemented in
# otfmi):
model.get_description()
