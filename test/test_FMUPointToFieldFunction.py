#!/usr/bin/env python

import unittest
import openturns as ot
import otfmi
import otfmi.example.deviation
import pyfmi

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

        self.path_fmu = otfmi.example.utility.get_path_fmu("epid")
        self.mesh = ot.RegularGrid(2.0, 0.5, 50)

    def test_start_time_coherence(self):
        """Check if incoherent start time raises an error"""
        self.assertRaises(
            AssertionError,
            otfmi.FMUPointToFieldFunction,
            self.mesh,
            self.path_fmu,
            inputs_fmu=["infection_rate", "healing_rate"],
            outputs_fmu=["infected"],
            start_time=10,
        )

    def test_start_time(self):
        """Check if start times are taken into account."""
        model_fmu_1 = otfmi.FMUPointToFieldFunction(
            self.mesh,
            self.path_fmu,
            inputs_fmu=["infection_rate", "healing_rate"],
            outputs_fmu=["infected"],
            start_time=0,
        )
        model_fmu_2 = otfmi.FMUPointToFieldFunction(
            self.mesh,
            self.path_fmu,
            inputs_fmu=["infection_rate", "healing_rate"],
            outputs_fmu=["infected"],
            start_time=1,
        )
        y1 = model_fmu_1(input_value)
        y2 = model_fmu_2(input_value)
        assert y2[0][0] - y1[0][0] != 0

    def test_final_time_coherence(self):
        """Check if incoherent final time raises an error."""
        self.assertRaises(
            AssertionError,
            otfmi.FMUPointToFieldFunction,
            self.mesh,
            self.path_fmu,
            inputs_fmu=["infection_rate", "healing_rate"],
            outputs_fmu=["infected"],
            final_time=10,
        )


if __name__ == "__main__":
    unittest.main()
