# -*- coding: utf-8 -*-
# Copyright 2016 EDF. This software was developed with the collaboration of
# Phimeca Engineering (Sylvain Girard, girard@phimeca.com).
"""Estimate expectation of an output variable after uncertainty propagation.
The physical model simulate the secondary loop of a pressurized water nuclear
reactor. The considered output is a partial power balance called “BIL100”.
"""

#§ Identifying the platform
import os
path_here = os.path.dirname(os.path.abspath(__file__))
print path_here

import imp
utility = imp.load_source('utility', os.path.join(path_here, "utility.py"))
# import importlib
# utility = importlib.import_module("utility", path_here)

# On certain platforms, the platform identification must be performed before
# importing 'pyfmi' (or, consequently, 'otfmi') because of a clash between the
# 'platform' module and 'pyfmi'.

#§
import openturns as ot
import otfmi
from pyfmi.fmi import FMUException
import sys

#§ 1. FMU model
inputs_fmu = ["sinkQPUR1.T0", "sinkQPUR2.T0",
              "sinkQPUR3.T0", "sinkQPUR4.T0",
              "sourcePQARE.P0", "sourcePQARE.Q0",
              "sourcePQARE.T0",
              "sinkQGSS.Q0", "sinkQGSS.T0",
              "sinkQGRE.Q0", "sinkQGRE.T0",
              "sinkQSTR.T0"]

inputs_fmu = ["sourcePQARE.P0", "sourcePQARE.Q0", "sourcePQARE.T0",
              "sinkQGSS.Q0", "sinkQGRE.Q0"]

outputs_fmu = ["BIL100.W_BIL100.signal"]

def instantiate_model(with_initialization_script=False):
    """Instantiate an FMUFunction and set number of cores to use.

    Parameters:
    ----------
    with_initialization_script : Boolean, wether or not to use an
    initialization script. If not (default), appropriate start values are
    hardcoded in the FMU.

    """
    if with_initialization_script:
        initialization_script = os.path.join(
            path_here, "file", "initialization_script", "bil100.mos")
        filename_fmu = "bil100_initialization_script.fmu"
    else:
        initialization_script = None
        filename_fmu = "bil100.fmu"

    try:
        path_fmu = os.path.join(path_here, "file", "fmu",
                                utility.get_directory_platform(),
                                filename_fmu)
        model = otfmi.FMUFunction(path_fmu, inputs_fmu=inputs_fmu,
                                  outputs_fmu=outputs_fmu)
    except (KeyError, FMUException):
        print ("This example is not available on your platform.\n"
               "Execution aborted.")
        sys.exit()
    model.enableHistory()
    return model

#§ 2. Random vector definition
# Create the marginal distributions of the input random vector
dict_distribution = {
    "sinkQPUR1.T0":ot.Normal(500.2497543, 3.0),
    "sinkQPUR2.T0":ot.Normal(500.2497543, 3.0),
    "sinkQPUR3.T0":ot.Normal(500.2497543, 3.0),
    "sinkQPUR4.T0":ot.Normal(500.2497543, 3.0),
    "sourcePQARE.P0":ot.Normal(7032392.1, 20700.0),
    "sourcePQARE.Q0":ot.Normal(2142.972222, 8.5),
    "sourcePQARE.T0":ot.Normal(500.2497543, 3.0),
    "sinkQGSS.Q0":ot.Normal(183.713226, 0.75),
    "sinkQGSS.T0":ot.Normal(552.6833333, 3.2),
    "sinkQGRE.Q0":ot.Normal(1922.331218, 8.5),
    "sinkQGRE.T0":ot.Normal(552.6833333, 3.2),
    "sinkQSTR.T0":ot.Normal(552.6833333, 3.2)
}

dict_distribution = {
    "sourcePQARE.P0":ot.Normal(7032392.1, 20700.0),
    "sourcePQARE.Q0":ot.Normal(2142.972222, 8.5),
    "sourcePQARE.T0":ot.Normal(500.2497543, 3.0),
    "sinkQGSS.Q0":ot.Normal(183.713226, 0.75),
    "sinkQGRE.Q0":ot.Normal(1922.331218, 8.5),
}


# Create a collection of the marginal distributions
collectionMarginals = ot.DistributionCollection()
# for name, distribution in dict_distribution:
for distribution in dict_distribution.values():
    collectionMarginals.add(ot.Distribution(distribution))


# Create the Spearman correlation matrix of the input random vector
RS = ot.CorrelationMatrix(12)
RS[4,6] = 0.0
# Evaluate the correlation matrix of the Normal copula from RS
R = ot.NormalCopula.GetCorrelationFromSpearmanCorrelation(RS)
# Create the Normal copula parametrized by R
copula = ot.NormalCopula(R)

# Create the input probability distribution of dimension
# inputDistribution = ot.ComposedDistribution(collectionMarginals,
#                                             ot.Copula(copula))
inputDistribution = ot.ComposedDistribution(collectionMarginals) #TMP

# Give a description of each component of the input distribution
inputDistribution.setDescription(dict_distribution.keys())
inputRandomVector = ot.RandomVector(inputDistribution)

#§
def run_demo(with_initialization_script, seed=None, n_simulation=None):
    """Run the demonstration

    Parameters:
    ----------
    with_initialization_script : Boolean, wether or not to use an
    initialization script. If not (default), appropriate start values are
    hardcoded in the FMU.


    seed : Integer, seed of the random number generator. The default is
    23091926.

    n_simulation : Integer, number of simulations. The default is 100.

    """

    if seed is None:
        seed = 23091926
    if n_simulation is None:
        # n_simulation = 100
        n_simulation = 10 #TODO TMP

    import time
    import numpy as np

    ot.RandomGenerator.SetSeed(seed)

    model = instantiate_model(
        with_initialization_script=with_initialization_script)
    # Create the output random vector
    outputRandomVector = ot.RandomVector(model, inputRandomVector)
    outputRandomVector.setDescription(["Puissance thermique du primaire"])


    # Probabilistic Study: central dispersion
    inputSample = inputRandomVector.getSample(n_simulation)
    time_start = time.time()
    outputSample = model(inputSample)
    elapsed = time.time() - time_start

    # Get the empirical mean and standard deviations
    empiricalMean = np.mean(outputSample)
    standardDeviation = np.std(outputSample)

    # Printing results
    print "\n"
    if with_initialization_script:
        print "The FMU was initialized with an initialization script."
    else:
        print "The FMU was initialized with hardcoded start values."
    title = ("Empirical moments of the BIL100 computed with %d simulations:" %
             n_simulation)
    print "\n%s" % title
    print "-" * len(title)
    justify = 30
    print "Mean : %g MW".rjust(justify)  % (empiricalMean / 1.e6)
    print ("Standard deviation : %g MW".rjust(justify)  %
           (standardDeviation / 1.e6))

    print "\nTotal simulation time: %.2f s".rjust(justify) % elapsed
    print "\n\n"

if __name__ == "__main__":
    run_demo(with_initialization_script=False)

#§
# Local Variables:
# tmux-temp-file: "/home/girard/.tmp/tmux_buffer"
# tmux-repl-window: "fmot"
# End:
