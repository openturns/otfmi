"""
Load an FMU
===========
"""
# %%
# First, retrieve the path to the example FMU *deviation.fmu*.
#
import otfmi
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
# otfmi drives the FMU through an FMI backend, PyFMI by default, FMPy as a
# fallback. Both expose the same interface, so the code below is
# backend-independent.
print(f"backend = {otfmi.backend.BACKEND}")

# %%
# Backend-specific loading options can be passed on to otfmi.
# With PyFMI, for instance, the log file name can be specified:
model = otfmi.fmi.load_fmu(path_fmu, kind="CS", log_file_name="deviation.log")

# %%
# .. note::
#    otfmi `load_fmu` is an overlay of the backend `load_fmu` function.
#    Hence the FMU loaded here upper benefits of all the backend methods.

# %%
# The model object also gives access to the underlying backend model, e.g. to
# inspect the variables it exposes:
sorted(model.get_model_variables().keys())
