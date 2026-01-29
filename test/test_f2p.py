#!/usr/bin/env python

import openturns as ot
import openturns.testing as ott
import otfmi
import otfmi.example.utility
import pytest


@pytest.fixture
def path_fmu():
    """Load FMU and setup pure python reference."""
    return otfmi.example.utility.get_path_fmu("epid")


@pytest.fixture
def mesh():
    return ot.RegularGrid(2.0, 0.5, 50)


def test_default_mesh(path_fmu):
    f = otfmi.FMUFieldToPointFunction(path_fmu,
                                      inputs_fmu=["infection_rate", "healing_rate"],
                                      outputs_fmu=["infected"])
    mesh = f.getInputMesh()
    start_time = mesh.getVertices().getMin()[0]
    end_time = mesh.getVertices().getMax()[0]
    ott.assert_almost_equal(start_time, 0.0)
    ott.assert_almost_equal(end_time, 200.0)


def test_start_time_coherence(path_fmu, mesh):
    """Check if incoherent start time raises an error"""
    with pytest.raises(ValueError):
        _ = otfmi.FMUFieldToPointFunction(path_fmu, mesh,
                                          inputs_fmu=["infection_rate", "healing_rate"],
                                          outputs_fmu=["infected"],
                                          start_time=10)


def test_start_time(path_fmu, mesh):
    """Check if start times are taken into account."""
    model_fmu_1 = otfmi.FMUFieldToPointFunction(
        path_fmu,
        mesh,
        inputs_fmu=["infection_rate", "healing_rate"],
        outputs_fmu=["infected"],
        start_time=0,
    )
    model_fmu_2 = otfmi.FMUFieldToPointFunction(
        path_fmu,
        mesh,
        inputs_fmu=["infection_rate", "healing_rate"],
        outputs_fmu=["infected"],
        start_time=1,
    )
    n = mesh.getVerticesNumber()
    input_value = [[0.007, 0.02]] * n
    y1 = model_fmu_1(input_value)
    y2 = model_fmu_2(input_value)
    assert y2[0] - y1[0] != 0.0


def test_final_time_coherence(path_fmu, mesh):
    """Check if incoherent final time raises an error."""
    with pytest.raises(ValueError):
        _ = otfmi.FMUFieldToPointFunction(path_fmu, mesh,
                                          inputs_fmu=["infection_rate", "healing_rate"],
                                          outputs_fmu=["infected"],
                                          final_time=10)
