import unittest
import openturns as ot
import otfmi
import otfmi.example
import otfmi.example.deviation


class TestModel(unittest.TestCase):
    def setUp(self):
        """Load FMU and setup pure python reference."""

        self.model_py = ot.PythonFunction(
            4, 1, otfmi.example.deviation.deviationFunction
        )

        # FMU model
        path_fmu = path_fmu = otfmi.example.utility.get_path_fmu("deviation")
        self.model_fmu = otfmi.FMUFunction(
            path_fmu, inputs_fmu=["E", "F", "L", "I"], outputs_fmu="y"
        )

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
            self.model_py, coefficient_variation=coefficient_variation
        )

        ot.RandomGenerator.SetSeed(seed)
        probability_fmu = otfmi.example.deviation.run_monte_carlo(
            self.model_fmu, coefficient_variation=coefficient_variation
        )

        relative_error = abs(probability_py - probability_fmu) / probability_py

        from numpy import finfo

        assert relative_error < finfo(float).eps


if __name__ == "__main__":
    unittest.main()
