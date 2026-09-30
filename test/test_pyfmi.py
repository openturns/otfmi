"""Testing basic features with PyFMI only."""

import otfmi.example.utility
import pyfmi
import pytest
import tempfile
import zipfile

try:
    from pyfmi import fmi3 as _fmi3
except ImportError:
    # pyfmi release without FMI 3.0 support
    _fmi3 = None

# pyfmi co-simulation class, per FMI version
MODEL_CLASS_CS = {"2.0": pyfmi.fmi.FMUModelCS2}
if _fmi3 is not None:
    MODEL_CLASS_CS["3.0"] = _fmi3.FMUModelCS3


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


def test_model_unzipped(model):
    """Load an unzipped fmu."""
    path_fmu = otfmi.example.utility.get_path_fmu("deviation")
    model_class = MODEL_CLASS_CS.get(model.get_version())
    if model_class is None:
        pytest.skip(f"pyfmi has no co-simulation class for FMI {model.get_version()}")

    def simulate_unzipped_fmu(workdir):
        with zipfile.ZipFile(path_fmu, "r") as zf:
            zf.extractall(workdir)
        model = model_class(
            fmu=workdir,
            allow_unzipped_fmu=True,
        )
        model.simulate(options={"silent_mode": True})

    with tempfile.TemporaryDirectory() as workdir:
        simulate_unzipped_fmu(workdir)
