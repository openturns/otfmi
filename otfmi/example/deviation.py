#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2016 EDF. This software was developed with the collaboration of
# Phimeca Engineering (Sylvain Girard, girard@phimeca.com).
"""Estimate a threshold exceedance probability with both Python and FMU models.
The physical model represents the deviation of a cantilever beam subjected to
a load. The probability that the deviation exceeds a given threshold is
estimated by straightforward Monte Carlo sampling.
"""

from __future__ import print_function
#§ Identifying the platform
import platform
key_platform = (platform.system(), platform.architecture()[0])
# Call to either 'platform.system' or 'platform.architecture' *after*
# importing pyfmi causes a segfault.
dict_platform = {("Linux", "64bit"):"linux64",
                 ("Windows", "32bit"):"win32",
                 ("Windows", "64bit"):"win64"}

#§ Define the input distribution
import numpy as np
import openturns as ot

E = ot.Beta(0.93, 3.2, 2.8e7, 4.8e7)
F = ot.LogNormalMuSigma(3.0e4, 9000.0, 15000.0).getDistribution()
L = ot.Uniform(250.0, 260.0)
I = ot.Beta(2.5, 4.0, 310.0, 450.0)

# Create the Spearman correlation matrix of the input random vector
RS = ot.CorrelationMatrix(4)
RS[2,3] = -0.2

# Evaluate the correlation matrix of the Normal copula from RS
R = ot.NormalCopula.GetCorrelationFromSpearmanCorrelation(RS)

# Create the Normal copula parametrized by R
mycopula = ot.NormalCopula(R)

# Create the input probability distribution of dimension 4
inputDistribution = ot.ComposedDistribution([E, F, L, I], mycopula)

# Give a description of each component of the input distribution
inputDistribution.setDescription( ("E", "F", "L", "I") )

# Create the input random vector
inputRandomVector = ot.RandomVector(inputDistribution)

#§ Python model (reference)
def deviationFunction(x):
    """Python version of the physical model.

    Parameters
    ----------
    x : Vector or array with individuals as rows, input values in the
    following order :
      - beam Young's modulus (E)
      - load (F)
      - length (L)
      - section modulus (I)

    """

    E=x[0]
    F=x[1]
    L=x[2]
    I=x[3]
    y=(F*L*L*L)/(3.*E*I)
    return [y]

model_py = ot.PythonFunction(4, 1, deviationFunction)

#§ FMU model
import otfmi
from pyfmi.fmi import FMUException
import sys

import os


path_here = os.path.dirname(os.path.abspath(__file__))
try:
    directory_platform = dict_platform[key_platform]
    path_fmu = os.path.join(path_here, "file", "fmu",
                            directory_platform, "deviation.fmu")
    model_fmu = otfmi.FMUFunction(
        path_fmu, inputs_fmu=["E", "F", "L", "I"], outputs_fmu=["y"])
except KeyError:
    raise RuntimeError("Tests are not available on your platform"
                       " (%s)." % "-".join(key_platform))
    sys.exit()
except FMUException:
    raise FMUException("The test FMU 'deviation.fmu' is not"
                       " available on your platform (%s)." %
                       "-".join(key_platform))
    sys.exit()

def create_monte_carlo(model, inputRandomVector, coefficient_variation):
    """Create a Monte Carlo algorithm.

    Parameters
    ----------
    model : OpenTURNS Function.

    inputRandomVector : OpenTURNS RandomVector, vector of random inputs.

    coefficient_variation : Float, target for the coefficient of variation of
    the estimator.

    """

    outputVariableOfInterest = ot.CompositeRandomVector(model, inputRandomVector)
    # Create an Event from this RandomVector
    threshold = 30
    myEvent = ot.ThresholdEvent(outputVariableOfInterest, ot.Greater(), threshold)
    myEvent.setName("Deviation > %g cm" % threshold)

    # Create a Monte Carlo algorithm
    experiment = ot.MonteCarloExperiment()
    myAlgoMonteCarlo = ot.ProbabilitySimulationAlgorithm(myEvent, experiment)
    myAlgoMonteCarlo.setBlockSize(100)
    myAlgoMonteCarlo.setMaximumCoefficientOfVariation(coefficient_variation)

    return myAlgoMonteCarlo

def run_monte_carlo(model, coefficient_variation=0.20):
    """Run Monte Carlo simulations.

    Parameters
    ----------
    model : OpenTURNS Function.

    coefficient_variation : Float, target for the coefficient of variation of
    the estimator.

    """

    # Setup Monte Carlo algorithm
    myAlgoMonteCarlo = create_monte_carlo(model, inputRandomVector,
                                          coefficient_variation)

    # Perform the simulations
    myAlgoMonteCarlo.run()

    # Get the results
    monte_carlo_result = myAlgoMonteCarlo.getResult()
    probability = monte_carlo_result.getProbabilityEstimate()

    return probability

def run_demo(seed=23091926, coefficient_variation=0.20):
    """Run the demonstration

    Parameters
    ----------
    seed : Integer, seed of the random number generator. The default is
    23091926.

    coefficient_variation : Float, target for the coefficient of variation of
    the estimator.

    """
    import time

    # test evaluation
    print('eval sample...', end='')
    xs = inputRandomVector.getSample(5)
    ys = model_fmu(xs)
    print('ok:', xs, ys)

    ot.RandomGenerator.SetSeed(seed)
    time_start = time.time()
    probability_py = run_monte_carlo(
        model_py, coefficient_variation=coefficient_variation)
    elapsed_py = time.time() - time_start

    ot.RandomGenerator.SetSeed(seed)
    time_start = time.time()
    probability_fmu = run_monte_carlo(
        model_fmu, coefficient_variation=coefficient_variation)
    elapsed_fmu = time.time() - time_start

    title = "Threshold exceedance probability:"
    print("\n%s" % title)
    print("-" * len(title))
    justify = 20
    print("Full python: %f".rjust(justify) % probability_py)
    print("FMU: %f".rjust(justify) % probability_fmu)

    relative_error = (abs(probability_py - probability_fmu) / probability_py)

    from numpy import finfo
    if relative_error < finfo(float).eps:
        print("Relative error is below machine precision.")
    else:
        print(("Relative error: %e" % relative_error))

    title = "Computation time in seconds:"
    print("\n%s" % title)
    print("-" * len(title))
    justify = 20
    print("Full python: %f".rjust(justify) % elapsed_py)
    print("FMU: %f".rjust(justify) % elapsed_fmu)

if __name__ == "__main__":
    import sys
    try:
        coefficient_variation = float(sys.argv[1])
    except IndexError:
        coefficient_variation = 0.50

    run_demo(coefficient_variation=coefficient_variation)

#§
