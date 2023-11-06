#!/usr/bin/env python

import openturns as ot
import otfmi
import os
import tempfile
import sys
import math as m
import psutil
import shutil
import subprocess
import time
import pytest


@pytest.mark.parametrize("mode", ["pyprocess", "pythonfmu"])
def test_export_fmu_vector(mode):
    # export fmu
    f = ot.SymbolicFunction(["E", "F", "L", "I"], ["(F*L^3)/(3.0*E*I)"])
    start = [3e7, 3e4, 250.0, 400.0]

    if sys.platform.startswith("win"):
        return

    temp_path = tempfile.mkdtemp()
    path_fmu = os.path.join(temp_path, "Deviation.fmu")
    fe = otfmi.FunctionExporter(f, start)
    fe.export_fmu(path_fmu, fmuType="cs", mode=mode, verbose=True)
    assert os.path.isfile(path_fmu), "fmu not created"

    # simulate with OMSimulator
    have_omsimulator = True
    try:
        subprocess.run(["OMSimulator", "--help"], capture_output=True)
    except FileNotFoundError:
        have_omsimulator = False
    if have_omsimulator:
        subprocess.run(["OMSimulator", path_fmu], capture_output=True, check=True)

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

    shutil.rmtree(temp_path)


@pytest.mark.skipif(sys.platform.startswith("win"), reason="N/A")
@pytest.mark.parametrize("mode", ["pyprocess"])
def test_export_fmu_field(mode):
    def g(X):
        a, b = X
        Y = [[a * m.sin(t) + b] for t in range(100)]
        return Y

    mesh = ot.RegularGrid(0, 1, 100)
    f = ot.PythonPointToFieldFunction(2, mesh, 1, g)
    start = [4.0, 5.0]

    temp_path = tempfile.mkdtemp()
    path_fmu = os.path.join(temp_path, "Sin.fmu")

    # export
    fe = otfmi.FunctionExporter(f, start)
    fe.export_fmu(path_fmu, fmuType="cs", mode=mode, verbose=True)
    assert os.path.isfile(path_fmu), "fmu not created"

    # simulate with OMSimulator
    have_omsimulator = True
    try:
        subprocess.run(["OMSimulator", "--help"], capture_output=True)
    except FileNotFoundError:
        have_omsimulator = False
    if have_omsimulator:
        subprocess.run(["OMSimulator", path_fmu], capture_output=True, check=True)

    # simulate with pyfmi
    import pyfmi
    model = pyfmi.load_fmu(path_fmu)
    model.initialize()
    model.reset()
    res = model.simulate(options={"silent_mode": True})
    print(model.get_model_variables().keys())
    print(res["y0"])
    shutil.rmtree(temp_path)


@pytest.mark.parametrize("mode", ["pyprocess", "cpython", "cxx"])
@pytest.mark.parametrize("binary", [True, False])
def test_export_model(mode, binary):

    # OT lib in conda is not compatible with MSVC (compiled with MinGW)
    if sys.platform.startswith("win") and mode == "cxx":
        return

    # export model
    f = ot.SymbolicFunction(["E", "F", "L", "I"], ["(F*L^3)/(3.0*E*I)"])
    start = [3e7, 3e4, 250.0, 400.0]
    name_model = "Deviation.mo"

    temp_path = tempfile.mkdtemp()
    assert os.path.isdir(temp_path), "temp_path not created"
    className, _ = os.path.splitext(name_model)
    path_model = os.path.join(temp_path, name_model)
    fe = otfmi.FunctionExporter(f, start)
    fe.export_model(path_model, gui=False, verbose=True, binary=binary, mode=mode)
    assert os.path.isfile(path_model), "model not created"

    if binary:
        # write simulation mos
        path_mos = os.path.join(temp_path, "simulate.mos")
        with open(path_mos, "w") as mos:
            mos.write(f'cd("{temp_path}");\n')
            mos.write(f'loadFile("{name_model}"); getErrorString();\n')
            mos.write(f"simulate ({className}, stopTime=3.0);\n")
        subprocess.run(["omc", f"{path_mos}"], capture_output=True, check=True)
    else:
        c_ext = ".cxx" if mode == "cxx" else ".c"
        assert os.path.isfile(os.path.join(temp_path, "wrapper" + c_ext)), "wrapper source not created"
        assert os.path.isfile(os.path.join(temp_path, "CMakeLists.txt")), "cmakelists not created"
    shutil.rmtree(temp_path)


# note : the GUI model wrapping the OT object is not checked in these tests as
# tests, as command line omc does not support the input/output connectors used
# by OMEdit.
