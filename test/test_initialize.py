"""
Use FMU deviation to check if initialization is taken into account.
"""

import otfmi
import otfmi.example.utility
import numpy as np
import os
import pytest


@pytest.fixture
def model():
    """Load FMU"""
    path_fmu = otfmi.example.utility.get_path_fmu("deviation")
    model = otfmi.fmi.load_fmu(path_fmu)
    return model


@pytest.fixture
def var_name():
    return "L"


@pytest.fixture
def var_val():
    return 300.0


def test_no_default(model, var_name, var_val):
    default_init_var = model.get_variable_start(var_name)
    assert var_val != default_init_var


def test_inline_initialization(model, var_name, var_val):
    """Test initialization inline"""
    result = otfmi.fmi.simulate(
        model, input=(var_name, np.atleast_2d([0, var_val]))
    )
    obtained = result.final(var_name)
    assert var_val == obtained


def test_initialization_script(model, var_name, var_val):
    """Test initialization scripts"""

    temporary_file = "initialization.mos"
    with open(temporary_file, "w") as f:
        f.write("{} = {};".format(var_name, var_val))

    # Simulate with this script
    result = otfmi.fmi.simulate(
        model, initialization_script=os.path.abspath(temporary_file)
    )
    obtained = result.final(var_name)
    assert var_val == obtained
