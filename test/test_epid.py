#!/usr/bin/env python

import platform
import unittest
import openturns as ot
import otfmi
import otfmi.example.deviation
from pyfmi.fmi import FMUException
import os
import math as m
import pyfmi

key_platform = (platform.system(), platform.architecture()[0])
# Call to either 'platform.system' or 'platform.architecture' *after*
# importing pyfmi causes a segfault.
dict_platform = {("Linux", "64bit"):"linux64",
                 ("Windows", "32bit"):"win32",
                 ("Windows", "64bit"):"win64"}
input_value = [0.007, 0.02]


def simulate_with_pyfmi(path_fmu):
    """Return the last simulation times.
    By default, pyfmi simulation output counts 500 steps.
    """
    check_model = pyfmi.load_fmu(path_fmu)
    check_model.set(["infection_rate", "healing_rate"], input_value)
    check_result = check_model.simulate()
    # Get the infected column
    list_variable = list(check_model.get_model_variables().keys())
    infected_column = list_variable.index("infected") + 1
    # +1 stands for time column, inserted as first in the data matrix
    list_last_infected_value = check_result.data_matrix[infected_column][-5:-1]
    print(list_last_infected_value)
    return list_last_infected_value


class TestEpid(unittest.TestCase):

    def setUp(self):
        """Load FMU and setup pure python reference."""

        fmu_name = "epid.fmu"
        path_example = os.path.dirname(os.path.abspath(
            otfmi.example.__file__))
        try:
            directory_platform = dict_platform[key_platform]
            self.path_fmu = os.path.join(path_example, "file", "fmu",
                directory_platform, fmu_name)
            self.model_fmu = otfmi.FMUFunction(
                self.path_fmu,
                inputs_fmu=["infection_rate", "healing_rate"],
                outputs_fmu=["infected"])
        except KeyError:
            raise RuntimeError(
                "Tests are not available on your platform (%s)." % key_platform)
        except FMUException:
            raise FMUException("The test FMU is not available on your platform (%s)." % key_platform)

    def test_empty(self):
        """Check module import and setup.
        """
        pass

    def test_fmufunction_interpolation(self):
        """Check that FMUFunction returns a point corresponding to Pyfmi's
        interpolated output.
        """
        list_last_infected_value = simulate_with_pyfmi(self.path_fmu)
        y = self.model_fmu(input_value)
        assert y[0] < max(list_last_infected_value)
        assert y[0] > min(list_last_infected_value)

    def test_timevariant_function(self):
        """Check that FMUPointToFieldFunction returns a trajectory."""
        mesh = ot.RegularGrid(0.0, 0.5, 100)
        model_fmu = otfmi.FMUPointToFieldFunction(
            mesh,
            self.path_fmu,
            inputs_fmu=['infection_rate', 'healing_rate'],
            outputs_fmu=['infected'])
        y = model_fmu(input_value)
        print('y=', y)
        assert y.getMax()[0] - y.getMin()[0] > 0
        assert m.fabs(y[0][0] - 1.0) < 1e-2, "wrong value"


if __name__ == '__main__':
    unittest.main()
