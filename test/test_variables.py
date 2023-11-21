#!/usr/bin/env python

import otfmi
import os
import pytest
import tempfile
import shutil


@pytest.mark.parametrize("varType", ["input", "parameter"])
@pytest.mark.parametrize("fmuType", ["cs", "me"])
def variable_tcase(varType, fmuType):

    temp_path = tempfile.mkdtemp()
    path_mo = os.path.join(temp_path, "ParamInput.mo")
    path_fmu = os.path.join(temp_path, "ParamInput.fmu")
    with open(path_mo, "w") as mo:
        mo.write("model ParamInput\n")
        mo.write("  " + varType + " Real p1;\n")
        mo.write("  parameter Real p2 = 80;\n")
        mo.write("  Real a;\n")
        mo.write("  output Real out1;\n")
        mo.write("  Real d;\n")
        mo.write("equation\n")
        mo.write("  a = p1 + 10 + p2;\n")
        mo.write("  out1 = a * 2;\n")
        mo.write("  der(d) = d + 2;\n")
        mo.write("end ParamInput;\n")
    otfmi.mo2fmu(path_mo, path_fmu, fmuType=fmuType, verbose=True)

    # reimport fmu
    model_fmu = otfmi.FMUFunction(
        path_fmu, inputs_fmu=["p1", "p2"], outputs_fmu=["out1"]
    )
    print(model_fmu)

    # call
    x = [2.0, 0]
    y = model_fmu(x)
    print(y)
    assert abs(y[0] - 24.0) < 1e-4, "wrong value"
    shutil.rmtree(temp_path)
