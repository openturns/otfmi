"""
FMUPointToFieldFunction basics
==============================
"""

# %%
# :class:`~otfmi.FMUPointToFieldFunction` wraps the FMU into an
# :py:class:`openturns.PointToFieldFunction` object.
# This kind of function accepts :py:class:`openturns.Point` or
# :py:class:`openturns.Sample` as inputs, and outputs a
# :py:class:`openturns.Sample` or a set of :py:class:`openturns.Field`.

# %%
import openturns as ot
import otfmi.example.utility
import openturns.viewer as viewer

# %%
# First, retrieve the path to *epid.fmu*.
path_fmu = otfmi.example.utility.get_path_fmu("epid")

# %%
# Wrap the FMU in an :py:class:`openturns.PointToFieldFunction` object:
function = otfmi.FMUPointToFieldFunction(
    path_fmu,
    inputs_fmu=["infection_rate"],
    outputs_fmu=["infected", "susceptible", "removed"],
    start_time=0.0,
    final_time=15.0,
)

# %%
# .. note::
#    The start and final times must define an interval comprising the mesh.
#    Setting manually the start and final times is recommended to avoid
#    uncontrolled simulation duration.

# %%
# Simulate the function on an input :py:class:`openturns.Point` yields an output
# as :py:class:`openturns.Sample`, corresponding to the output evolution over time
x = [2.0]
y = function(x)

# %%
# Retrieve the simulation mesh
timeGrid = function.getOutputMesh().getVertices()

# %%
# Plot the data
graph = ot.Graph("Simulation data", "Simulation time (days)", "Number of individuals", True)
graph.setLegendPosition("upper right")
for i in range(function.getOutputDimension()):
    curve = ot.Curve(timeGrid, y[:, i])
    graph.add(curve)
graph.setLegends(function.getOutputDescription())
graph.setColors(["red", "blue", "green"])
view = viewer.View(graph)

# %%
# Simulate the function on a input :py:class:`openturns.Sample` yields a set of
# fields called :py:class:`openturns.ProcessSample`:
X = [[2.0], [2.25], [2.5]]
Y = function(X)
print(Y)

# %%
# Visualize the time evolution of the ``infected`` over time, depending on the
# `ìnfection_rate`` value:
gridLayout = Y.draw()
graph = gridLayout.getGraph(0, 0)
graph.setTitle("")
graph.setXTitle("Simulation time (days)")
graph.setYTitle(function.getOutputDescription()[0])
graph.setLegends([str(line[0]) for line in X])
view = viewer.View(graph, legend_kw={"title": "infection rate"})

# %%
# Show all plots
view.ShowAll()
