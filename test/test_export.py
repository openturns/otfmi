#!/usr/bin/env python

import fmpy
import glob
import openturns as ot
import otfmi
import os
import tempfile
import sys
import psutil
import shutil
import subprocess
import time
import pytest
from pathlib import Path


@pytest.mark.parametrize("mode", ["pyprocess", "pythonfmu"])
@pytest.mark.parametrize("fmuType", ["cs", "me"])
def test_export_fmu_vector(mode, fmuType):
    if mode == "pyprocess" and sys.platform.startswith("win"):
        # omc mingw cross-compiler cannot use otfmi msvc wrapper binary: Linking cwrapper-NOTFOUND
        return

    # export fmu
    f = ot.SymbolicFunction(["E", "F", "L", "I"], ["(F*L^3)/(3.0*E*I)"])
    start = [3e7, 3e4, 250.0, 400.0]
    temp_path = Path(tempfile.mkdtemp())
    path_fmu = temp_path / "Deviation.fmu"
    fe = otfmi.FunctionExporter(f, start)
    fe.export_fmu(path_fmu, fmuType=fmuType, mode=mode, verbose=True)
    assert path_fmu.exists(), "fmu not created"

    # simulate with OMSimulator
    have_omsimulator = True
    try:
        subprocess.run(["OMSimulator", "--help"], capture_output=True)
    except FileNotFoundError:
        have_omsimulator = False
    if have_omsimulator and mode != "pythonfmu":
        # requires LD_PRELOAD for pythonfmu
        subprocess.run(["OMSimulator", str(path_fmu)], capture_output=True, check=True)

    if mode == "pyprocess":
        # reimport fmu
        model_fmu = otfmi.FMUFunction(
            path_fmu, inputs_fmu=["E", "F", "L", "I"], outputs_fmu=["y0"]
        )
        print(model_fmu)

        # call
        x = [3.1e7, 3.1e4, 255.0, 420.0]
        y = model_fmu(x)
        print(y)
        assert abs(y[0] - 13.1598) < 1e-4, "wrong value"

        # bench speed
        t0 = time.time()
        process = psutil.Process(os.getpid())
        size = 10
        mem0 = process.memory_info().rss / 1000000
        for i in range(size):
            x = [3.1e7, 3.1e4 + i, 255.0, 420.0]
            y = model_fmu(x)
            print(i, x, y, process.memory_info().rss / 1000000, flush=True)
        t1 = time.time()
        mem1 = process.memory_info().rss / 1000000
        print("Speed=", size / (t1 - t0), "evals/s")
        print("Memory=", mem1 - mem0)

    elif mode == "pythonfmu":
        summary = fmpy.dump(path_fmu)
        print(summary)
        start_values = {"E": 6.70455e+10, "F": 300, "L": 2.55, "I": 1.45385e-07}
        result = fmpy.simulate_fmu(path_fmu, start_values=start_values)
        print(result)

    shutil.rmtree(temp_path)


@pytest.mark.skipif(sys.platform.startswith("win"), reason="N/A")
@pytest.mark.parametrize("fmuType", ["cs", "me"])
def test_export_fmu_field(fmuType, mode="pythonfmu"):

    N = 100
    start = 0.0
    step = 1.570796 / N
    mesh = ot.RegularGrid(start, step, N)
    g = ot.SymbolicFunction(["t", "a", "b"], ["a*sin(t)+b"])
    f = ot.VertexValuePointToFieldFunction(g, mesh)
    x0 = [4.0, 5.0]

    temp_path = Path(tempfile.mkdtemp())
    path_fmu = temp_path / "Sin.fmu"

    # export
    fe = otfmi.FunctionExporter(f, x0)
    fe.export_fmu(path_fmu, fmuType=fmuType, mode=mode, verbose=True)
    assert path_fmu.exists(), f"fmu not created in {path_fmu}"

    summary = fmpy.dump(path_fmu)
    print(summary)
    var1, var2 = f.getInputDescription()
    start_values = {var1: 4.0, var2: 5.0}
    result = fmpy.simulate_fmu(path_fmu, start_values=start_values)
    print(result)

    # simulate with OMSimulator
    have_omsimulator = True
    try:
        subprocess.run(["OMSimulator", "--help"], capture_output=True)
    except FileNotFoundError:
        have_omsimulator = False
    if have_omsimulator and mode != "pythonfmu":
        # requires LD_PRELOAD for pythonfmu
        subprocess.run(["OMSimulator", str(path_fmu)], capture_output=True, check=True)

    shutil.rmtree(temp_path)


@pytest.mark.parametrize("mode", ["pyprocess", "cpython", "cxx"])
@pytest.mark.parametrize("binary", [True, False])
def test_export_model(mode, binary):

    # export model
    f = ot.SymbolicFunction(["E", "F", "L", "I"], ["(F*L^3)/(3.0*E*I)"])
    start = [3e7, 3e4, 250.0, 400.0]
    className = "Deviation"
    model_file = className + ".mo"

    temp_path = Path(tempfile.mkdtemp())
    path_model = temp_path / model_file
    fe = otfmi.FunctionExporter(f, start)
    fe.export_model(path_model, gui=False, verbose=True, binary=binary, mode=mode)
    assert path_model.exists(), f"model not created in file {path_model}"

    if binary:
        libfiles = glob.glob(str(temp_path / "*cwrapper*"))
        assert len(libfiles) > 0, "lib file not created"

        # write simulation mos
        path_mos = temp_path / "simulate.mos"
        with open(path_mos, "w") as mos:
            mos.write(f'cd("{temp_path}");\n')
            mos.write(f'loadFile("{model_file}"); getErrorString();\n')
            mos.write(f"simulate ({className}, stopTime=3.0);\n")
        subprocess.run(["omc", str(path_mos)], capture_output=True, check=True)
    else:
        c_ext = ".cxx" if mode == "cxx" else ".c"
        assert (temp_path / ("wrapper" + c_ext)).exists(), "wrapper source not created"
        assert (temp_path / "CMakeLists.txt").exists(), "CMakeLists not created"
    shutil.rmtree(temp_path)


# note : the GUI model wrapping the OT object is not checked in these tests as
# tests, as command line omc does not support the input/output connectors used
# by OMEdit.
