#!/usr/bin/env python

import openturns as ot
import otfmi

# create function
f = ot.SymbolicFunction(["E", "F", "L", "I"], ["(F*L^3)/(3.0*E*I)"])
start = [3e7, 3e4, 250.0, 400.0]

# export fmu
path_fmu = "/tmp/deviation.fmu"
fe = otfmi.FunctionExporter(f, start)
fe.export(path_fmu)

# reimport fmu
model_fmu = otfmi.FMUFunction(
    path_fmu, inputs_fmu=["E", "F", "L", "I"], outputs_fmu=["y0"]
)
print(model_fmu)
x = [3.1e7, 3.1e4, 255.0, 420.0]
y = model_fmu(x)
print(y)

# delete support files
fe.cleanup()
