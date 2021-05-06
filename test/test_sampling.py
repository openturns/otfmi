#!/usr/bin/env python

import openturns as ot
import otfmi
import unittest
import os
import tempfile
import sys
import math as m
import shutil
from time import time
import psutil

class TestSampling(unittest.TestCase):

    def test_sobol(self):
        temp_path = tempfile.mkdtemp()
        path_mo = os.path.join(temp_path, 'IshigamiFunction.mo')
        path_fmu = os.path.join(temp_path, 'IshigamiFunction.fmu')
        with open(path_mo, "w") as mo:
            mo.write('model IshigamiFunction\n')
            mo.write('  final parameter Real a = 7;\n')
            mo.write('  final parameter Real b = 0.05;\n')
            mo.write('  input Real x1 = 1;\n')
            mo.write('  input Real x2 = 1;\n')
            mo.write('  input Real x3 = 1;\n')
            mo.write('  output Real f;\n')
            mo.write('  Real d;\n')
            mo.write('equation\n')
            mo.write('  f = sin(x1) + a * sin(x2)^2 + b * x3^4 * sin(x1);\n')
            mo.write('  der(d) = d + 2;\n')
            mo.write('end IshigamiFunction;\n')
        otfmi.mo2fmu(path_mo, path_fmu, fmuType="cs", verbose=True)

        # reimport fmu
        model_fmu = otfmi.FMUFunction(path_fmu)
        print(model_fmu, model_fmu.getInputDescription(), model_fmu.getOutputDescription())
        model_symbolic = ot.SymbolicFunction(['x1', 'x2', 'x3'], ['sin(x1) + 7 * sin(x2)^2 + 0.05 * x3^4 * sin(x1)'])

        # Sobol' DOE
        X = ot.ComposedDistribution([ot.Uniform(-m.pi, m.pi)] * 3)
        N = 20
        x = ot.SobolIndicesExperiment(X, N).generate()
        size = len(x)

        # evaluate DOE
        t0 = time()
        process = psutil.Process(os.getpid())
        mem0 = process.memory_info().rss / 1000000
        for i in range(size):
            xi = x[i]
            yi = model_fmu(xi)
            yi_ref = model_symbolic(xi)
            assert m.fabs(yi[0] - yi_ref[0]) < 1e-8, "wrong value"
            print(i, xi, yi, process.memory_info().rss / 1000000, flush=True)
        t1 = time()
        mem1 = process.memory_info().rss / 1000000
        print("Speed=", size / (t1 - t0), "evals/s")
        print("Memory=", mem1-mem0)
        shutil.rmtree(temp_path)

if __name__ == '__main__':
    unittest.main()
