"""
Run simulations with FMUFieldFunction
--------------------------------------------
"""

# %%
# While :class:`~otfmi.FMUPointToFieldFunction` deals with scalar inputs (parameters) only, the :class:`~otfmi.FMUFieldFunction`
# enable you to define time-dependant outputs to study their effects on time-dependent outputs.

# We consider a model of heat exchanger.
# Basically, it models a flow of liquid coolant flowing through tubes, 
# which are cooled by a flow of air.
# Here, we define time-dependent temperatures for air and coolant at inlet, 
# and we study the evolution the temperature of air and coolant at the outlet.

# TODO : see https://github.com/openturns/otfmi/blob/master/test/test_f2f.py

# %%
# -------------
# Modelica
# +++++++++++++
# In Modelica models, one can model time-dependent variables with table
# components.
# To use your model with OTFMI, you must set your time-dependent input 
# as scalar parameter in the model. The temporal dependency is managed by OTFMI.

# %%
# -------------
# Prerequisites
# +++++++++++++
# We use the HeatExchanger example,
# with the function :class:`~otfmi.FMUFieldFunction`.

import otfmi
import openturns as ot
import matplotlib.pyplot as plt

path_fmu = otfmi.example.utility.get_path_fmu("HeatExchanger")


# %%
# -----------------
# Define the time
# +++++++++++++++++
# The first work consists in defining the times the model will be evaluated.
# By default, the function uses the time defined in the FMU, 
# but you can override it.
# By convenience, we define a custom timegrid to define inputs easier,
# from 0s to 100s, with a timestep of 10s.

input_mesh = ot.RegularGrid(0.0, 10, 100)

# %%
# -----------------
# Define the inputs
# +++++++++++++++++
# We want to drive inlet air and coolant temperatures, 
# to see their effects on outlet temperatures.
# Inputs are defined in one list.
# Each element is itself a list, giving for each time the values of the inputs.
# Here, we suppose a linear dependancy between temperatures and time.

inlet_temperatures = []
for time in input_mesh.getVertices():
    Temp_air_inlet = 25 + 0.01 * time[0]
    Temp_coolant_inlet = 50 + 0.02 * time[0]
    inlet_temperatures.append([Temp_air_inlet, Temp_coolant_inlet])

# %%
# -----------------------------
# Define the `FMUFieldFunction`
# +++++++++++++++++++++++++++++
# For this example, we do not change the output mesh, i.e. 
# the times used by the solver to solve equations.
#

inputs_vars = ["Temp_air_inlet", "Temp_coolant_inlet"]
outputs_vars = ["Temp_air_outlet", "Temp_coolant_outlet"]

HX_model = otfmi.FMUFieldFunction(path_fmu,
                                  input_mesh,
                                  inputs_fmu=inputs_vars,
                                  outputs_fmu=outputs_vars)
print(HX_model)

# You can modify the time-grid with `output_mesh` argument.
# You can also set start and final times explicitly.

# %%
# -------------------
# Run the simulation
# +++++++++++++++++++

outlet_temperatures = HX_model(inlet_temperatures)

# %%
# -------------------
# See results
# +++++++++++++++++++

plt.xlabel("FMU simulation time (s)")
plt.ylabel(outputs_vars[0])
plt.plot(input_mesh.getVertices(), outlet_temperatures[0])
plt.show()

plt.xlabel(inputs_vars[0])
plt.ylabel(outputs_vars[0])
plt.plot(inlet_temperatures[0], outlet_temperatures[0])
plt.show()


# %%
# -----------------------
# Change other parameters 
# +++++++++++++++++++++++
# By the same method, you can change other parameters to another constant value.
# Let's change the heat transfer coefficient, from is default value
# 192 kW/K, to 180kW/K.

input_values = []
for time in input_mesh.getVertices():
    Temp_air_inlet = 25 + 0.01 * time[0]
    Temp_coolant_inlet = 50 + 0.02 * time[0]
    HeatTransfer = 180.0
    input_values.append([Temp_air_inlet, Temp_coolant_inlet, HeatTransfer])

inputs_vars = ["Temp_air_inlet", "Temp_coolant_inlet", "HeatTransfer_coeff"]
outputs_vars = ["Temp_air_outlet", "Temp_coolant_outlet"]

HX_model = otfmi.FMUFieldFunction(path_fmu,
                                  input_mesh,
                                  inputs_fmu=inputs_vars,
                                  outputs_fmu=outputs_vars)

outlet_temperatures = HX_model(input_values)

plt.xlabel(inputs_vars[0])
plt.ylabel(outputs_vars[0])
plt.plot(inlet_temperatures[0], outlet_temperatures[0])
plt.show()


# %%
# --------------------------------------------------
# Alternative : Define the `FMUFieldToPointFunction`
# ++++++++++++++++++++++++++++++++++++++++++++++++++
# The previous function support timeseries as inputs and outputs.
# If you are interested in only a scalar output, OTFMI offers a
# variant :class:`~otfmi.FMUFieldToPointFunction`, to get only and directly
# the output at the last timestep.

HX_model = otfmi.FMUFieldToPointFunction(path_fmu,
                                         input_mesh,
                                         inputs_fmu=inputs_vars,
                                         outputs_fmu=outputs_vars)

# %%
# -------------------
# Run the simulation
# +++++++++++++++++++

outlet_temperatures = HX_model(inlet_temperatures)
print(outlet_temperatures)
