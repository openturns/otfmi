#!/usr/bin/env python

import otfmi
import unittest
import os
import tempfile
import math as m
import shutil


class TestEpid(unittest.TestCase):

    def test_epid(self):
        temp_path = tempfile.mkdtemp()
        path_mo = os.path.join(temp_path, 'epid.mo')
        path_fmu = os.path.join(temp_path, 'epid.fmu')
        with open(path_mo, "w") as mo:
            mo.write('model epid\n')
            mo.write('  parameter Real total_pop = 700;\n')
            mo.write('  Real infected;\n')
            mo.write('  Real susceptible;\n')
            mo.write('  parameter Real infection_rate = 0.07;\n')
            mo.write('  parameter Real healing_rate = 0.02;\n')
            mo.write('  initial equation\n')
            mo.write('    infected = 1;\n')
            mo.write('    total_pop = infected + susceptible;\n')
            mo.write('  equation\n')
            mo.write('    der(susceptible) = - infection_rate*infected*susceptible;\n')
            mo.write('    der(infected) = infection_rate*infected*susceptible - healing_rate*infected;\n')
            mo.write('  annotation(experiment(StartTime = 0, StopTime = 50, Tolerance = 1e-6, Interval = 0.1));\n')
            mo.write('end epid;\n')
        otfmi.mo2fmu(path_mo, path_fmu, fmuType="me", verbose=True)

        model_fmu = otfmi.FMUFunction(path_fmu, inputs_fmu=['infection_rate', 'healing_rate'], outputs_fmu=['infected'])
        x = [0.07, 0.02]
        y = model_fmu(x)
        print('y=', y)
        assert m.fabs(y[0]-258.205) < 1e-2, "wrong value"
        shutil.rmtree(temp_path)

if __name__ == '__main__':
    unittest.main()
