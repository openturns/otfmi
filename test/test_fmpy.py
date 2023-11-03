import fmpy
import openturns.testing as ott
import otfmi
import otfmi.example
import os
import platform
import pytest
import sysconfig

# Identifying the platform
key_platform = (platform.system(), platform.architecture()[0])
# Call to either 'platform.system' or 'platform.architecture' *after*
# importing pyfmi causes a segfault.
dict_platform = {("Linux", "64bit"): "linux64", ("Windows", "64bit"): "win64"}


@pytest.mark.skipif("linux" not in sysconfig.get_platform(), reason="N/A")
def test_fmpy():
    """Load example FMU."""
    path_example = os.path.dirname(os.path.abspath(otfmi.example.__file__))
    try:
        directory_platform = dict_platform[key_platform]
        path_fmu = os.path.join(
            path_example, "file", "fmu", directory_platform, "DeviationSlave.fmu"
        )
    except KeyError:
        raise RuntimeError(
            "Tests are not available on your platform" " (%s)." % key_platform
        )

    summary = fmpy.dump(path_fmu)
    print(summary)
    start_values = {"E": 6.70455e+10, "F": 300, "L": 2.55, "II": 1.45385e-07}
    result = fmpy.simulate_fmu(path_fmu, start_values=start_values)
    print(result)
    y = result[-1][1]
    ott.assert_almost_equal(y, 0.17011057)
