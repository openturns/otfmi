#!/usr/bin/env python

import openturns as ot
import otfmi
import unittest
import os
import tempfile
import sys
import math as m
import subprocess

class TestExport(unittest.TestCase):

    def test_export_fmu(self):
        # export fmu
        f = ot.SymbolicFunction(['E', 'F', 'L', 'I'], ['(F*L^3)/(3.0*E*I)'])
        start = [3e7, 3e4, 250.0, 400.0]

        if sys.platform.startswith('win'):
            return


        temp_path = tempfile.mkdtemp()
        path_fmu = os.path.join(temp_path, 'Deviation.fmu')
        fe = otfmi.FunctionExporter(f, start)
        fe.export_fmu(path_fmu, fmuType='cs', verbose=False)
        assert os.path.isfile(path_fmu), "fmu not created"

        # reimport fmu
        model_fmu = otfmi.FMUFunction(path_fmu, inputs_fmu=["E", "F", "L", "I"], outputs_fmu=["y0"])
        print(model_fmu)

        # call
        x = [3.1e7, 3.1e4, 255.0, 420.0]
        y = model_fmu(x)
        print(y)
        assert abs(y[0] - 13.1598) < 1e-4, "wrong value"

        if 0:
            # field function
            mesh = ot.RegularGrid(0, 1, 100)
            #g = ot.SymbolicFunction(['t', 'a', 'b'], ['a*sin(t)+b'])
            #f = ot.VertexValuePointToFieldFunction(g, mesh)
            def g(X):
                a, b = X
                Y = [[a*m.sin(t)+b] for t in range(100)]
                return Y
            f = ot.PythonPointToFieldFunction(2, mesh, 1, g)
            start = [4.0, 5.0]

            # export
            fe = otfmi.FunctionExporter(f, start)
            fe.export_fmu(path_fmu, fmuType='cs', verbose=True)
            assert os.path.isfile(path_fmu), "fmu not created"

            # import
            import pyfmi
            model = pyfmi.load_fmu(path_fmu)
            model.initialize()
            res = model.simulate(options={'silent_mode': True})
            print(model.get_model_variables().keys())
            print(res['y0'])

        # shutil.rmtree(temp_path)

    def test_export_model(self):
    #     # export model
        f = ot.SymbolicFunction(['E', 'F', 'L', 'I'], ['(F*L^3)/(3.0*E*I)'])
        start = [3e7, 3e4, 250.0, 400.0]

        temp_path = tempfile.mkdtemp()
        assert os.path.isdir(temp_path), "temp_path not created"
        name_model = 'Deviation.mo'
        className, _ = os.path.splitext(name_model)
        path_model = os.path.join(temp_path, name_model)
        fe = otfmi.FunctionExporter(f, start)
        fe.export_model(path_model, gui=False, verbose=False, move=True)
        assert os.path.isfile(path_model), "model not created"

        # write simulation mos
        path_mos = os.path.join(temp_path, "simulate.mos")
        with open(path_mos, "w") as mos:
            mos.write('cd("{}");\n'.format(temp_path))
            mos.write('loadModel(Modelica);\n')
            mos.write('loadFile("{}"); getErrorString();\n'.format(
                name_model))
            mos.write('simulate ({}, stopTime=3.0);\n'.format(
                className))

        subprocess.run(['omc', '{}'.format(path_mos)], capture_output=True, check=True)

        # shutil.rmtree(temp_path)


if __name__ == '__main__':
    unittest.main()

# note : the GUI model wrapping the OT object is not checked in these tests as
# tests, as command line omc does not support the input/output connectors used
# by OMEdit.