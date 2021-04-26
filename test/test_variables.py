#!/usr/bin/env python

import openturns as ot
import otfmi
import unittest
import os
import tempfile
import sys
import math as m
import shutil
import subprocess

def variable_tcase(varType, fmuType):

        temp_path = tempfile.mkdtemp()
        path_mo = os.path.join(temp_path, 'ParamInput.mo')
        path_fmu = os.path.join(temp_path, 'ParamInput.fmu')
        with open(path_mo, "w") as mo:
            mo.write('model ParamInput\n')
            mo.write('  '+varType+' Real p1;\n')
            mo.write('  Real a;\n')
            mo.write('  output Real out1;\n')
            mo.write('  Real d;\n')
            mo.write('equation\n')
            mo.write('  a = p1 + 10;\n')
            mo.write('  out1 = a * 2;\n')
            mo.write('  der(d) = d + 2;\n')
            mo.write('end ParamInput;\n')
        otfmi.mo2fmu(path_mo, path_fmu, fmuType=fmuType, verbose=True)
        
        # reimport fmu
        model_fmu = otfmi.FMUFunction(path_fmu, inputs_fmu=["p1"], outputs_fmu=["out1"])
        print(model_fmu)

        # call
        x = [2.0]
        y = model_fmu(x)
        print(y)
        assert abs(y[0] - 24.0) < 1e-4, "wrong value"
        shutil.rmtree(temp_path)

class TestExport(unittest.TestCase):

    def test_input_cs(self):
        variable_tcase("input", "cs")

    def test_parameter_cs(self):
        variable_tcase("parameter", "cs")

    def test_input_me(self):
        variable_tcase("input", "me")

    # TODO: parameter/me, have to use model.set
    #def test_parameter_me(self):
        #variable_tcase("parameter", "me")

if __name__ == '__main__':
    unittest.main()

