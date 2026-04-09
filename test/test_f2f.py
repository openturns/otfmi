#!/usr/bin/env python

import math as m
import openturns as ot
import openturns.testing as ott
import otfmi
import otfmi.example.utility
import pytest
import sys


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


@pytest.mark.skipif(sys.platform.startswith("win"), reason="N/A")
def test_heat_exchanger():
    path_fmu = otfmi.example.utility.get_path_fmu("HeatExchanger")
    inputs_vars = ["Temp_air_inlet", "Temp_coolant_inlet"]
    outputs_vars = ["Temp_air_outlet", "Temp_coolant_outlet"]
    HX_model = otfmi.FMUFieldFunction(path_fmu, inputs_fmu=inputs_vars, outputs_fmu=outputs_vars)
    input_mesh = HX_model.getInputMesh()
    freq_air = 0.5
    omega_air = 2 * m.pi * freq_air
    freq_cool = 1.5
    omega_cool = 2 * m.pi * freq_cool
    phi = 3.78
    input_timeseries = ot.Sample(0, 2)
    for time in input_mesh.getVertices().asPoint():
        Temp_air_inlet = 25.0 + 4.0 * m.sin(omega_air * time + phi)
        Temp_coolant_inlet = 50.0 + 4.0 * m.sin(omega_cool * time + phi)
        input_timeseries.add([Temp_air_inlet, Temp_coolant_inlet])
    outlet_temperatures = HX_model(input_timeseries)
    ott.assert_almost_equal(outlet_temperatures[-1], [41.6793, 47.7767])
