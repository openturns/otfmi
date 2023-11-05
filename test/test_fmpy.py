import fmpy
import openturns.testing as ott
import otfmi
import otfmi.example.utility
import pytest
import sysconfig


def test_fmpy():
    path_fmu = path_fmu = otfmi.example.utility.get_path_fmu("DeviationSlave")
    summary = fmpy.dump(path_fmu)
    print(summary)
    start_values = {"E": 6.70455e+10, "F": 300, "L": 2.55, "II": 1.45385e-07}
    result = fmpy.simulate_fmu(path_fmu, start_values=start_values)
    print(result)
    y = result[-1][1]
    ott.assert_almost_equal(y, 0.17011057)
