"""Testing basic features with PyFMI only."""

import otfmi.example.utility
import pyfmi
import pytest


@pytest.fixture
def model():
    """Load an fmu."""
    path_fmu = otfmi.example.utility.get_path_fmu("deviation")
    model = pyfmi.load_fmu(path_fmu)
    return model


def test_pyfmi_load(model):
    pass


def test_pyfmi_simulate(model):
    """Simulate an fmu."""
    model.simulate(options={"silent_mode": True})


def test_pyfmi_reset(model):
    """Reset an fmu."""
    model.simulate(options={"silent_mode": True})
    model.reset()
    model.simulate(options={"silent_mode": True})
