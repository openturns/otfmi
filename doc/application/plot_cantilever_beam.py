# -*- coding: utf-8 -*-
# @Author: Claire-Eleuthèriane Gerrer
# @Date:   2021-07-08 14:08:28
# @Last Modified by:   Claire-Eleuthèriane Gerrer
# @Last Modified time: 2022-06-16 11:05:56

"""
Estimate the probability of a threshold excedance
=================================================
"""
# %%
# A load is applied to a cantilever beam. For construction
# reasons, the beam must not exceed a bending of 30 cm. The load (F), beam
# Young’s modulus (E), length (L) and section modulus (I) are uncertain.
# 
# .. image:: /_static/beam.png
#    :width: 132px
#    :height: 126px
#    :scale: 100 %
#    :alt: alternate text
#    :align: center
#
# --------
#
# See the cantilever beam model :doc:`here<../fmus/deviation>`.
# 
# --------
#
#
# **What is the probability that the deviation exceeds the
# threshold ?**
#
#
# We load the FMU as a FMUFunction (see the
# :doc:`tutorial<../_generated/otfmi.FMUFunction>`):

import otfmi
import otfmi.example.utility
path_fmu = otfmi.example.utility.get_path_fmu("deviation")

model_fmu = otfmi.FMUFunction(
 path_fmu, inputs_fmu=["E", "F", "L", "I"], outputs_fmu="y")

# %%
# We test the function wrapping the deviation model on a point:
import openturns as ot
point = ot.Point([3e7, 2e4, 255, 350])
model_evaluation = model_fmu(point)
print("Running the FMU: deviation = {}".format(model_evaluation))


# %%
# We define probability laws on the 4 uncertain inputs:

E = ot.Beta(0.93, 3.2, 2.8e7, 4.8e7)
F = ot.LogNormal() 
F.setParameter(ot.LogNormalMuSigma()([30.e3, 9e3, 15.e3]))
L = ot.Uniform(250.0, 260.0)
I = ot.Beta(2.5, 4.0, 310.0, 450.0)

# %%
# According to the laws of mechanics, when the length L increases, the moment 
# of inertia I decreases.
# The variables L and I are thus negatively correlated.
# 
# **We assume that the random variables E, F, L and I are dependent and
# associated with a gaussian copula which correlation matrix:**
#
# .. math::
#    \begin{pmatrix}
#    1 & 0 & 0 & 0 \\
#    0 & 1 & 0 & 0 \\
#    0 & 0 & 1 & -0.2 \\
#    0 & 0 & -0.2 & 1 \\
#    \end{pmatrix}

# %%
# We implement this correlation:

# Create the Spearman correlation matrix of the input random vector
RS = ot.CorrelationMatrix(4)
RS[2,3] = -0.2

# Evaluate the correlation matrix of the Normal copula from RS
R = ot.NormalCopula.GetCorrelationFromSpearmanCorrelation(RS)

# Create the Normal copula parametrized by R
mycopula = ot.NormalCopula(R)

# %%
# And we endly create the composed input probability distribution.
inputDistribution = ot.ComposedDistribution([E, F, L, I], mycopula)
inputDistribution.setDescription( ("E", "F", "L", "I") )

# %%
# Create the event whose probability we want to estimate:

inputRandomVector = ot.RandomVector(inputDistribution)
outputVariableOfInterest = ot.CompositeRandomVector(model_fmu,
   inputRandomVector)

threshold = 30
event = ot.ThresholdEvent(outputVariableOfInterest, ot.Greater(), threshold)
event.setName("Deviation > %g cm" % threshold)

# %%
# Parameterize and run the Monte Carlo algorithm:

ot.RandomGenerator.SetSeed(23091926) #  set seed for reproducibility

experiment = ot.MonteCarloExperiment()
algo = ot.ProbabilitySimulationAlgorithm(event, experiment)
algo.setMaximumOuterSampling(200)
algo.setMaximumCoefficientOfVariation(0.2)
algo.run()

# %%
# Draw the distribution of threshold excedance probability:

from openturns.viewer import View
monte_carlo_result = algo.getResult()
probabilityDistribution = monte_carlo_result.getProbabilityDistribution()
graph = View(probabilityDistribution.drawPDF())

# %%
# Get the probability with which the beam deviation exceeds 30 cm:

probability = monte_carlo_result.getProbabilityEstimate()
print("Threshold excedance probability: {}".format(probability))

# %%
# Given the uncertainties on the load applied and the beam mechanical
# parameters, the beam bending has a probability of 0.01 to exceed 30 cm.
# Is this probability low or not ? It depends on your context 🙂