# -*- coding: utf-8 -*-
#§ Identifying the platform
import platform
key_platform = (platform.system(), platform.architecture()[0])
# Call to either 'platform.system' or 'platform.architecture' *after*
# importing pyfmi causes a segfault.
dict_platform = {("Linux", "64bit"):"linux64",
                 ("Windows", "32bit"):"win32",
                 ("Windows", "64bit"):"win64"}

import unittest

import openturns as ot


import otfmi
import otfmi.example.deviation
from pyfmi.fmi import FMUException

import os

#§
class TestModel(unittest.TestCase):
    def setUp(self):
        """Load FMU and setup pure python reference."""

        self.model_py = ot.PythonFunction(
            4, 1, otfmi.example.deviation.deviationFunction)

        #§ FMU model
        path_example = os.path.dirname(os.path.abspath(
            otfmi.example.__file__))
        try:
            directory_platform = dict_platform[key_platform]
            path_fmu = os.path.join(path_example, "file", "fmu",
                                    directory_platform, "deviation.fmu")
            self.model_fmu = otfmi.FMUFunction(
                path_fmu, inputs_fmu=["E", "F", "L", "I"], outputs_fmu="y")
        except KeyError:
            raise RuntimeError ("Tests are not available on your platform"
                                " (%s)." % key_platform)
        except FMUException:
            raise FMUException ("The test FMU 'deviation.fmu' is not"
                                 " available on your platform (%s)." %
                                key_platform)

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
                          probability_py)

        from numpy import finfo
        assert(relative_error < finfo(float).eps)

#§
if __name__ == '__main__':
    unittest.main()

#§
