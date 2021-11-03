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
                 ("Windows", "64bit"):"win64"}
input_value = [0.007, 0.02]


def simulate_with_pyfmi(path_fmu, final_time=None):
    """Return the output on the 5 last simulation times.
    By default, pyfmi simulation output counts 500 steps.
    """
    check_model = pyfmi.load_fmu(path_fmu)
    check_model.set(["infection_rate", "healing_rate"], input_value)
    if final_time is not None:
        check_result = check_model.simulate(final_time=final_time)
    else:
        check_result = check_model.simulate()
    # Get the infected column
    list_variable = list(check_model.get_model_variables().keys())
    infected_column = list_variable.index("infected") + 1
    # +1 stands for time column, inserted as first in the data matrix
    list_last_infected_value = check_result.data_matrix[infected_column][-5:-1]
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

    def test_final_value(self):
        """Check reproducibility of the final value.
        """
        y = self.model_fmu(input_value)
        assert m.fabs(y[0] - 265.68) < 1e-2, "wrong value"

    def test_fmufunction_interpolation(self):
        """Check that FMUFunction returns a point corresponding to Pyfmi's
        interpolated output.
        """
        list_last_infected_value = simulate_with_pyfmi(self.path_fmu)
        y = self.model_fmu(input_value)
        assert y[0] < max(list_last_infected_value)
        assert y[0] > min(list_last_infected_value)

    def test_final_time(self):
        """Check that specified final time is taken into account.
        """
        final_time = 2.
        model_fmu_1 = otfmi.FMUFunction(
            self.path_fmu,
            inputs_fmu=["infection_rate", "healing_rate"],
            outputs_fmu=["infected"],
            final_time=final_time)
        list_last_infected_value = simulate_with_pyfmi(self.path_fmu,
            final_time=final_time)
        y = model_fmu_1(input_value)
        assert y[0] < max(list_last_infected_value)
        assert y[0] > min(list_last_infected_value)

    def test_keyword(self):
        """Check that specifying final time at simulation raises a Warning.
        """
        lowlevel_model_fmu = otfmi.OpenTURNSFMUFunction(
            self.path_fmu,
            inputs_fmu=["infection_rate", "healing_rate"],
            outputs_fmu=["infected"])
        self.assertRaises(Warning, lowlevel_model_fmu._exec, input_value,
            final_time=50.)

if __name__ == '__main__':
    unittest.main()
