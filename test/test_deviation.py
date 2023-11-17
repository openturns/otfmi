import openturns as ot
import otfmi
import otfmi.example.utility
import otfmi.example.deviation
import sys


def test_deviation():
    model_py = ot.PythonFunction(
        4, 1, otfmi.example.deviation.deviationFunction
    )

    # FMU model
    path_fmu = path_fmu = otfmi.example.utility.get_path_fmu("deviation")
    model_fmu = otfmi.FMUFunction(
        path_fmu, inputs_fmu=["E", "F", "L", "I"], outputs_fmu="y"
    )

    seed = 23091926
    coefficient_variation = 1.0
    ot.RandomGenerator.SetSeed(seed)
    probability_py = otfmi.example.deviation.run_monte_carlo(
        model_py, coefficient_variation=coefficient_variation
    )

    ot.RandomGenerator.SetSeed(seed)
    probability_fmu = otfmi.example.deviation.run_monte_carlo(
        model_fmu, coefficient_variation=coefficient_variation
    )

    relative_error = abs(probability_py - probability_fmu) / probability_py
    assert relative_error < sys.float_info.epsilon
