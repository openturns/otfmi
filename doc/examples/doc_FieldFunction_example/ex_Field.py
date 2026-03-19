"""
Run simulations with FMUFieldFunction
-------------------------------------
"""

# %%
# While :class:`~otfmi.FMUPointToFieldFunction` deals with scalar inputs
# (parameters) only, the :class:`~otfmi.FMUFieldFunction`
# enable you to define time-dependant outputs to study their effects on
# time-dependent outputs.

# We consider a model of heat exchanger.
# Basically, it models a flow of liquid coolant flowing through tubes,
# which are cooled by a flow of air.
# Here, we define time-dependent temperatures for air and coolant at inlet,
# and we study the evolution the temperature of air and coolant at the outlet.

# Modif :
# Evol en sinus des températures + random, pour faire plusieurs simulations.

# %%
# -------------
# Modelica
# +++++++++++++
# In Modelica models, one can model time-dependent variables with table
# components.
# To use your model with OTFMI, you must set your time-dependent input
# as scalar parameter in the model. The temporal dependency is managed by
# OTFMI.

# %%
# Prerequisites
# ##############
# We use the HeatExchanger example,
# with the function :class:`~otfmi.FMUFieldFunction`.

import numpy as np
import otfmi
import otfmi.example.utility
import openturns as ot
import openturns.viewer as otv

path_fmu = otfmi.example.utility.get_path_fmu("HeatExchanger")

# %%
# Define the `FMUFieldFunction`
# #############################
# We define the model with a `FMUFieldFunction` object, with
# 2 inputs and 2 outputs.
# You can change the time mesh (`input_mesh` and `output_mesh`).
# You can also set start and final times explicitly.
# For this example, We keep the time defined in the FMU.

inputs_vars = ["Temp_air_inlet", "Temp_coolant_inlet"]
outputs_vars = ["Temp_air_outlet", "Temp_coolant_outlet"]

HX_model = otfmi.FMUFieldFunction(path_fmu,
                                  inputs_fmu=inputs_vars,
                                  outputs_fmu=outputs_vars)
print(HX_model)


# %%
# Define the time
# ###############
# The first work consists in defining the times the model will be evaluated.
# You can recover the time grid defined in the model.

input_mesh = HX_model.getInputMesh()


# If you want to override this with your own timegrid,
# you can use :py:class:`openturns.RegularGrid`

# %%
# Define the inputs
# #################
# We want to drive inlet air and coolant temperatures,
# to see their effects on outlet temperatures.
# Inputs are defined in one list.
# Each element is itself a list, giving for each time the values of the inputs.
# Here we suppose a sinusoidal evolution of temperatures.
# You can change the frequency (Hz). The phase is randomly set.

freq_air = 0.5
omega_air = 2 * np.pi * freq_air

freq_cool = 1.5
omega_cool = 2 * np.pi * freq_cool

phi = np.random.uniform(0, 2 * np.pi)

input_timeseries = []
for time in input_mesh.getVertices():
    Temp_air_inlet = float(25 + 4 * np.sin(omega_air * time[0] + phi))
    Temp_coolant_inlet = float(50 + 4 * np.sin(omega_cool * time[0] + phi))
    input_timeseries.append([Temp_air_inlet, Temp_coolant_inlet])

graph_in = ot.Graph("Inlet Temperatures evolution",
                    "FMU simulation time (s)",
                    "Temperature (°C)", True, "")

curve_TairIn = ot.Curve(input_mesh.getVertices(),
                        ot.Sample(np.array(input_timeseries)).getMarginal(0))
curve_TairIn.setColor("green")
graph_in.add(curve_TairIn)

curve_TcoolIn = ot.Curve(input_mesh.getVertices(),
                         ot.Sample(np.array(input_timeseries)).getMarginal(1))
curve_TcoolIn.setColor("blue")
graph_in.add(curve_TcoolIn)

graph_in.setIntegerXTick(True)
view = otv.View(graph_in)
view.show()

# %%
# Run the simulation
# ##################

outlet_temperatures = HX_model(input_timeseries)

# %%
# See results
# ###########

graph = ot.Graph("Outlet Air Temperature evolution",
                 "FMU simulation time (s)",
                 "Temperature (°C)", True, "")

curve = ot.Curve(input_mesh.getVertices(),
                 outlet_temperatures.getMarginal(0))
curve.setColor("red")
graph.add(curve)
graph.setIntegerXTick(True)
view = otv.View(graph)
view.show()

# %%
# Alternative : Define the `FMUFieldToPointFunction`
# ##################################################
# The previous function support timeseries as inputs and outputs.
# If you are interested in only a scalar output, OTFMI offers a
# variant :class:`~otfmi.FMUFieldToPointFunction`, to get only and directly
# the output at the last timestep.

HX_model = otfmi.FMUFieldToPointFunction(path_fmu,
                                         input_mesh,
                                         inputs_fmu=inputs_vars,
                                         outputs_fmu=outputs_vars)

# %%
# Run the simulation
# ##################

outlet_temperatures = HX_model(input_timeseries)
print(outlet_temperatures)
