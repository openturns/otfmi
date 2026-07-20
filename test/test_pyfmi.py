"""Testing basic features with PyFMI only."""

import otfmi.example.utility
import pyfmi
import pytest
import tempfile
import zipfile


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


def test_model_unzipped():
    """Load an fmu."""
    path_fmu = otfmi.example.utility.get_path_fmu("deviation")
    workdir = tempfile.mkdtemp()
    with zipfile.ZipFile(path_fmu, "r") as zf:
        zf.extractall(workdir)
    model = pyfmi.fmi.FMUModelCS2(fmu=workdir, allow_unzipped_fmu=True)
    model.simulate(options={"silent_mode": True})
