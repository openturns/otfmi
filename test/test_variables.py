#!/usr/bin/env python

import openturns as ot
import otfmi
import os
import pytest
import tempfile
import shutil


@pytest.mark.parametrize("fmuType", ["cs", "me"])
@pytest.mark.parametrize("version", ["2.0"])
def test_var_field(fmuType, version):

    temp_path = tempfile.mkdtemp()
    path_mo = os.path.join(temp_path, "test_var_field.mo")
    path_fmu = os.path.join(temp_path, "test_var_field.fmu")
    with open(path_mo, "w") as mo:
        mo.write("model test_var_field\n")
        mo.write("  input Real input1 (start=6);\n")
        mo.write("  input Real input2 (start=8);\n")
        mo.write("  parameter Real param1 = 2.0;\n")
        mo.write("  parameter Real param2 = 100.0;\n")
        mo.write("  Real real1;\n")
        mo.write("  output Real out1;\n")
        mo.write("  Real real2;\n")
        mo.write("initial equation\n")
        mo.write("real2 = 0;\n")
        mo.write("equation\n")
        mo.write("  real1 = input1 * param1 + param2;\n")
        mo.write("  out1 = real1;\n")
        mo.write("  der(real2) = real2 + 3;\n")
        mo.write("end test_var_field;\n")
    otfmi.mo2fmu(path_mo, path_fmu, fmuType=fmuType, version=version, verbose=True)

    # reimport fmu
    f = otfmi.FMUFieldToPointFunction(
        path_fmu, inputs_fmu=["input1", "input2"], outputs_fmu=["out1"]
    )
    print(f)

    # call
    input_mesh = f.getInputMesh()
    N = len(input_mesh.getVertices())
    x = ot.Sample(N, 2)
    for i in range(N):
        x[i, 0] = i + 1
        x[i, 1] = 2 * i + 1

    y = f(x)
    print(y)
    # difference between me and cs
    if fmuType == "cs":
        assert abs(y[0] - 1100.0) < 1e-2, "wrong value"
    shutil.rmtree(temp_path)


@pytest.mark.parametrize("varType", ["input", "parameter"])
@pytest.mark.parametrize("fmuType", ["cs", "me"])
@pytest.mark.parametrize("version", ["2.0"])
def test_var_type(varType, fmuType, version):

    temp_path = tempfile.mkdtemp()
    path_mo = os.path.join(temp_path, "test_var_type.mo")
    path_fmu = os.path.join(temp_path, "test_var_type.fmu")
    with open(path_mo, "w") as mo:
        mo.write("model test_var_type\n")
        mo.write(f"  {varType} Real var1 = 0;\n")
        mo.write("  parameter Real param1 = 2.0;\n")
        mo.write("  parameter Real param2 = 100.0;\n")
        mo.write("  Real real1;\n")
        mo.write("  output Real out1;\n")
        mo.write("  Real real2;\n")
        mo.write("initial equation\n")
        mo.write("real2 = 0;\n")
        mo.write("equation\n")
        mo.write("  real1 = var1 * param1 + param2;\n")
        mo.write("  out1 = real1;\n")
        mo.write("  der(real2) = real2 + 3;\n")
        mo.write("end test_var_type;\n")
    otfmi.mo2fmu(path_mo, path_fmu, fmuType=fmuType, version=version, verbose=True)

    # reimport fmu
    f = otfmi.FMUFunction(
        path_fmu, inputs_fmu=["var1", "param1"], outputs_fmu=["out1"]
    )
    print(f)

    # call
    x = [5.0, 2.5]
    y = f(x)
    print(y)
    assert abs(y[0] - 112.5) < 1e-4, "wrong value"
    shutil.rmtree(temp_path)
