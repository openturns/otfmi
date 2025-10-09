#!/usr/bin/env python

import openturns as ot
import openturns.testing as ott
import otfmi
import os
import tempfile
import math as m
import shutil
from time import time
import psutil
import concurrent.futures


def test_sampling_sobol():
    temp_path = tempfile.mkdtemp()
    path_mo = os.path.join(temp_path, "IshigamiFunction.mo")
    path_fmu = os.path.join(temp_path, "IshigamiFunction.fmu")
    with open(path_mo, "w") as mo:
        mo.write("model IshigamiFunction\n")
        mo.write("  final parameter Real a = 7;\n")
        mo.write("  final parameter Real b = 0.05;\n")
        mo.write("  input Real x1 = 1;\n")
        mo.write("  input Real x2 = 1;\n")
        mo.write("  input Real x3 = 1;\n")
        mo.write("  output Real f;\n")
        mo.write("  Real d;\n")
        mo.write("equation\n")
        mo.write("  f = sin(x1) + a * sin(x2)^2 + b * x3^4 * sin(x1);\n")
        mo.write("  der(d) = d + 2;\n")
        mo.write("end IshigamiFunction;\n")
    otfmi.mo2fmu(path_mo, path_fmu, fmuType="cs", verbose=True)

    # reimport fmu
    model_fmu = otfmi.FMUPointToFieldFunction(path_fmu)
    print(
        model_fmu, model_fmu.getInputDescription(), model_fmu.getOutputDescription()
    )
    model_symbolic = ot.SymbolicFunction(
        ["x1", "x2", "x3"], ["sin(x1) + 7 * sin(x2)^2 + 0.05 * x3^4 * sin(x1)"]
    )

    # MC DOE
    N = 200
    x = ot.ComposedDistribution([ot.Uniform(-m.pi, m.pi)] * 3).getSample(N)

    # evaluate DOE
    process = psutil.Process(os.getpid())
    mem0 = process.memory_info().rss / 1000000
    y = [None] * N
    t0 = time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        future_to_i = {executor.submit(model_fmu, x[i]): i for i in range(N)}
        for future in concurrent.futures.as_completed(future_to_i):
            i = future_to_i[future]
            y[i] = future.result()[-1]
    t1 = time()
    y_ref = model_symbolic(x)
    ott.assert_almost_equal(y, y_ref)

    mem1 = process.memory_info().rss / 1000000
    print("Speed=", N / (t1 - t0), "evals/s")
    print("Memory=", mem1 - mem0)
    shutil.rmtree(temp_path)
