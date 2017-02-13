# -*- coding: utf-8 -*-
#§ Identifying the platform
import platform
key_platform = (platform.system(), platform.architecture()[0])
# Call to either 'platform.system' or 'platform.architecture' *after*
# importing pyfmi causes a segfault.
dict_platform = {("Linux", "64bit"):"linux64",
                 ("Windows", "32bit"):"win32"}

import numpy as np
import unittest
import os

import openturns as ot


import otfmi
import otfmi.example.deviation
from pyfmi.fmi import FMUException
import sys

import os

#§
class TestModel(unittest.TestCase):
    def setUp(self):
        """Load FMU and setup pure python reference."""
        #§ Define the input distribution
        import numpy as np
        E = ot.Beta(0.93, 3.2, 28000000.0, 48000000.0)
        F = ot.LogNormal(30000.0, 9000.0, 15000.0,  ot.LogNormal.MUSIGMA)
        L = ot.Uniform(250.0, 260.0)
        I = ot.Beta(2.5, 4.0, 310.0, 450.0)

        self.model_py = ot.PythonFunction(
            4, 1, otfmi.example.deviation.deviationFunction)
        self.model_py.enableHistory()

        #§ FMU model
        path_example = os.path.dirname(os.path.abspath(
            otfmi.example.__file__))
        try:
            directory_platform = dict_platform[key_platform]
            path_fmu = os.path.join(path_example, "file", "fmu",
                                    directory_platform, "deviation.fmu")
            self.model_fmu = otfmi.FMUFunction(
                path_fmu, inputs_fmu=["E", "F", "L", "I"], outputs_fmu="y")
        except (KeyError, FMUException):
            print ("This example is not available on your platform.\n"
                       "Execution aborted.")
            sys.exit()

        self.model_fmu.enableHistory()

    # def tearDown(self):
        # pass

    def test_empty(self):
        """Check module import and setup."""
        pass

    def test_compare_fmu_pure_python(self):
        """Compare the threshold exceedance probability computed with the FMU
        and the pure python reference.
        """

        seed = 23091926
        coefficient_variation = 1.0
        ot.RandomGenerator.SetSeed(seed)
        probability_py = otfmi.example.deviation.run_monte_carlo(
            self.model_py, coefficient_variation=coefficient_variation)

        ot.RandomGenerator.SetSeed(seed)
        probability_fmu = otfmi.example.deviation.run_monte_carlo(
            self.model_fmu, coefficient_variation=coefficient_variation)

        relative_error = (abs(probability_py - probability_fmu) /
                          (probability_py + probability_fmu) / 2.)

        from numpy import finfo
        assert(relative_error < finfo(float).eps)

#§
if __name__ == '__main__':
    unittest.main()

#§
