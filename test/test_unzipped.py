import openturns.testing as ott
import otfmi.example.utility
import otfmi
import tempfile
import zipfile


def test_unzipped():
    path_fmu = otfmi.example.utility.get_path_fmu("deviation")

    def call_unzipped_fmu(workdir):
        with zipfile.ZipFile(path_fmu, "r") as zf:
            zf.extractall(workdir)
        f = otfmi.FMUFunction(workdir)
        assert f.getOutputDimension() == 1
        x = [0.1] * 4
        y = f(x)
        assert y.getDimension() == 1

    with tempfile.TemporaryDirectory() as workdir:
        call_unzipped_fmu(workdir)


def test_unzipped_error():
    with tempfile.TemporaryDirectory() as workdir:
        with ott.assert_raises(FileNotFoundError):
            otfmi.FMUFunction(workdir)
