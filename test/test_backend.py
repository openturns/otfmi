"""Testing backend selection and switching."""

import re
import shutil
import zipfile
from pathlib import Path
import tempfile

import numpy as np
import openturns.testing as ott
import otfmi
import otfmi.example.utility
import pytest


# The example FMUs are not equally compliant: win-amd64/deviation.fmu declares
# its outputs and inputs with variability="fixed", which FMI 2.0 forbids.
# fmpy rejects such a model description whereas pyfmi tolerates it.
_X = [6.70455e10, 300, 2.55, 1.45385e-07]
_INPUTS = ["E", "F", "L", "I"]
_EXPECTED_Y = 0.17011057


def select_backend(name):
    """Activate a backend and return the path to the deviation example FMU.

    Skips the test when the backend cannot read the example FMU, which happens
    with a model description that does not comply with the FMI standard.
    """
    module = pytest.importorskip(name)
    otfmi.use_backend(name)
    path_fmu = otfmi.example.utility.get_path_fmu("deviation")
    if name == "fmpy":
        try:
            module.read_model_description(path_fmu)
        except Exception as exc:
            pytest.skip(f"fmpy cannot read {Path(path_fmu).name}: {exc}")
    return path_fmu


@pytest.fixture(autouse=True)
def restore_backend():
    """Restore the initially selected backend after each test.

    The active backend is global state: without this, a test switching to
    fmpy would leak into every test collected after it.
    """
    backend = otfmi.backend.BACKEND
    yield
    otfmi.use_backend(backend)


def test_backend_auto_selection():
    """A backend is selected on import, pyfmi being preferred."""
    assert otfmi.backend.BACKEND in ("pyfmi", "fmpy")


def test_use_backend_pyfmi():
    """Switch to the pyfmi backend."""
    pytest.importorskip("pyfmi")
    otfmi.use_backend("pyfmi")
    assert otfmi.backend.BACKEND == "pyfmi"


def test_use_backend_fmpy():
    """Switch to the fmpy backend."""
    pytest.importorskip("fmpy")
    otfmi.use_backend("fmpy")
    assert otfmi.backend.BACKEND == "fmpy"


def test_use_backend_unknown():
    """An unknown backend name is rejected."""
    with pytest.raises(ValueError, match="Unknown backend"):
        otfmi.use_backend("unknown-backend")


@pytest.mark.parametrize("name", ["pyfmi", "fmpy"])
def test_backend_simulation(name):
    """Both backends simulate the deviation model identically."""
    path_fmu = select_backend(name)
    model = otfmi.FMUFunction(path_fmu, inputs_fmu=_INPUTS, outputs_fmu="y")
    ott.assert_almost_equal(model(_X), [_EXPECTED_Y])


@pytest.mark.parametrize("name", ["pyfmi", "fmpy"])
def test_backend_field_output(name):
    """Both backends return the same trajectory for a field output."""
    path_fmu = select_backend(name)
    model = otfmi.FMUPointToFieldFunction(
        path_fmu, inputs_fmu=_INPUTS, outputs_fmu="y"
    )
    field = model(_X)
    # the example FMUs do not share the same default experiment, so compare
    # with the mesh the function reports instead of a hardcoded size
    mesh_size = model.getOutputMesh().getVertices().getSize()
    assert field.getSize() == mesh_size
    ott.assert_almost_equal(field[-1], [_EXPECTED_Y])


@pytest.mark.parametrize("name", ["pyfmi", "fmpy"])
def test_backend_constant_input(name):
    """A point input and a repeated field input must agree.

    fmpy releases older than 0.3.23 cannot interpolate an input table holding a
    single sample, so the backend passes such inputs as start values instead.
    This checks that both routes give the same result.
    """
    path_fmu = select_backend(name)

    # a single set of input values, sampled once
    point_model = otfmi.FMUFunction(path_fmu, inputs_fmu=_INPUTS, outputs_fmu="y")
    # the same values, held constant over the time steps of the field
    field_model = otfmi.FMUFieldToPointFunction(
        path_fmu, inputs_fmu=_INPUTS, outputs_fmu="y"
    )
    repeated = np.tile(_X, (field_model.getInputMesh().getVertices().getSize(), 1))

    ott.assert_almost_equal(point_model(_X), field_model(repeated))


def test_fmpy_input_version_gate():
    """The single-sample workaround is enabled exactly for old fmpy releases."""
    fmpy = pytest.importorskip("fmpy")
    from packaging.version import Version
    from otfmi.backend import fmpy_backend

    expected = Version(fmpy.__version__) < Version("0.3.23")
    assert fmpy_backend._FMPY_INPUT_FIXED is not expected


@pytest.mark.parametrize("name", ["pyfmi", "fmpy"])
def test_backend_default_experiment_fallbacks(name):
    """Both backends agree on the default experiment of an FMU without one.

    Not every FMU declares a step size, or a default experiment at all. pyfmi
    substitutes 0.0 / 1.0 / 0.01 in that case, and fmpy must do the same so
    that both backends build the same mesh.
    """
    source = select_backend(name)

    # rebuild the example FMU without any default experiment. The directory is
    # removed leniently: on Windows the backend may still hold the file open
    workdir = tempfile.mkdtemp()
    try:
        target = Path(workdir) / "deviation.fmu"
        with zipfile.ZipFile(source) as zin, zipfile.ZipFile(target, "w") as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == "modelDescription.xml":
                    text = re.sub(r"<DefaultExperiment[^>]*/?>", "", data.decode())
                    data = text.encode()
                zout.writestr(item, data)

        model = otfmi.backend.load_fmu(target)
        assert model.get_default_experiment_start_time() == 0.0
        assert model.get_default_experiment_stop_time() == 1.0
        assert model.get_default_experiment_step() == 0.01
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
