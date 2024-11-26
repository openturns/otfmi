"""
Explore the FMU
===============
"""

# %%
# | Knowledge about the FMU is necessary to setup a probabilistic approach:
# | - What is the name of the FMU variables ?
# | - Which are the inputs, outputs, parameters ?
# | - Which are booleans, reals, integers ?
# | - What is their default start value ?

# %%
# First, retrieve and load the FMU *deviation.fmu*.

import otfmi.example.utility

path_fmu = otfmi.example.utility.get_path_fmu("deviation")
model = otfmi.fmi.load_fmu(path_fmu)

# %%
# Let require the FMU variables names:

list_name = otfmi.fmi.get_name_variable(model)
print(list_name)

# %%
# | This command shows all variables : inputs, parameters, outputs.
# | Let identify their causality in the model:

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
