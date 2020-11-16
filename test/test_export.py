#!/usr/bin/env python

import openturns as ot
import otfmi
import unittest
import os
import tempfile
import sys
import shutil

class TestExport(unittest.TestCase):

    def test_export(self):
        # create function
        f = ot.SymbolicFunction(['E', 'F', 'L', 'I'], ['(F*L^3)/(3.0*E*I)'])
        start = [3e7, 3e4, 250.0, 400.0]

        if sys.platform.startswith('win'):
            return

        # export fmu
        temp_path = tempfile.mkdtemp()
        path_fmu = os.path.join(temp_path, 'deviation.fmu')
        fe = otfmi.FunctionExporter(f, start)
        fe.export(path_fmu, fmuType='cs', verbose=True)
        assert os.path.isfile(path_fmu), "fmu not created"

        # reimport fmu
        model_fmu = otfmi.FMUFunction(path_fmu, inputs_fmu=["E", "F", "L", "I"], outputs_fmu=["y0"])
        print(model_fmu)

        # call
        x = [3.1e7, 3.1e4, 255.0, 420.0]
        y = model_fmu(x)
        print(y)
        assert abs(y[0] - 13.1598) < 1e-4, "wrong value"

        shutil.rmtree(temp_path)

if __name__ == '__main__':
    unittest.main()
