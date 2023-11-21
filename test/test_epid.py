#!/usr/bin/env python

import otfmi
import otfmi.example.deviation
import otfmi.example.utility
import pyfmi
import pytest


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


@pytest.fixture
def path_fmu():
    return otfmi.example.utility.get_path_fmu("epid")


@pytest.fixture
def model_fmu(path_fmu):
    return otfmi.FMUFunction(path_fmu,
                             inputs_fmu=["infection_rate", "healing_rate"],
                             outputs_fmu=["infected"])


def test_final_value(model_fmu):
    """Check reproducibility of the final value."""
    y = model_fmu(input_value)
    assert abs(y[0] - 265.68) < 1e-2, "wrong value"


def test_fmufunction_interpolation(path_fmu, model_fmu):
    """Check that FMUFunction returns a point corresponding to Pyfmi's
    interpolated output.
    """
    list_last_infected_value = simulate_with_pyfmi(path_fmu)
    y = model_fmu(input_value)
    assert y[0] < max(list_last_infected_value)
    assert y[0] > min(list_last_infected_value)


def test_final_time(path_fmu):
    """Check that specified final time is taken into account."""
    final_time = 2.0
    model_fmu_1 = otfmi.FMUFunction(
        path_fmu,
        inputs_fmu=["infection_rate", "healing_rate"],
        outputs_fmu=["infected"],
        final_time=final_time,
    )
    list_last_infected_value = simulate_with_pyfmi(
        path_fmu, final_time=final_time
    )
    y = model_fmu_1(input_value)
    assert y[0] < max(list_last_infected_value)
    assert y[0] > min(list_last_infected_value)


def test_keyword(path_fmu):
    """Check that specifying final time at simulation raises a Warning."""
    lowlevel_model_fmu = otfmi.OpenTURNSFMUFunction(
        path_fmu,
        inputs_fmu=["infection_rate", "healing_rate"],
        outputs_fmu=["infected"],
    )
    with pytest.raises(Warning):
        lowlevel_model_fmu._exec(input_value, final_time=50.0)
