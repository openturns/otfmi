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
def input_mesh():
    return ot.RegularGrid(2.0, 0.5, 50)


def test_default_mesh(path_fmu):
    f = otfmi.FMUFieldFunction(
        path_fmu,
        inputs_fmu=["infection_rate", "healing_rate"],
        outputs_fmu=["infected"],
    )
    input_mesh = f.getInputMesh()
    start_time = input_mesh.getVertices().getMin()[0]
    end_time = input_mesh.getVertices().getMax()[0]
    ott.assert_almost_equal(start_time, 0.0)
    ott.assert_almost_equal(end_time, 200.0)

    output_mesh = f.getOutputMesh()
    start_time = output_mesh.getVertices().getMin()[0]
    end_time = output_mesh.getVertices().getMax()[0]
    ott.assert_almost_equal(start_time, 0.0)
    ott.assert_almost_equal(end_time, 200.0)


def test_start_time_coherence(path_fmu, input_mesh):
    """Check if incoherent start time raises an error"""
    with pytest.raises(ValueError):
        _ = otfmi.FMUFieldFunction(
            path_fmu,
            input_mesh,
            inputs_fmu=["infection_rate", "healing_rate"],
            outputs_fmu=["infected"],
            start_time=10,
        )


def test_start_time(path_fmu, input_mesh):
    """Check if start times are taken into account."""
    model_fmu_1 = otfmi.FMUFieldFunction(
        path_fmu,
        input_mesh,
        inputs_fmu=["infection_rate", "healing_rate"],
        outputs_fmu=["infected"],
        start_time=0,
    )
    model_fmu_2 = otfmi.FMUFieldFunction(
        path_fmu,
        input_mesh,
        inputs_fmu=["infection_rate", "healing_rate"],
        outputs_fmu=["infected"],
        start_time=1,
    )
    n = input_mesh.getVerticesNumber()
    input_value = [[0.007, 0.02]] * n
    y1 = model_fmu_1(input_value)[-1]
    y2 = model_fmu_2(input_value)[-1]
    assert y2[0] - y1[0] != 0.0


def test_final_time_coherence(path_fmu, input_mesh):
    """Check if incoherent final time raises an error."""
    with pytest.raises(ValueError):
        _ = otfmi.FMUFieldFunction(
            path_fmu,
            input_mesh,
            inputs_fmu=["infection_rate", "healing_rate"],
            outputs_fmu=["infected"],
            final_time=10,
        )
