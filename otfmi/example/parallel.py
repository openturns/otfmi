#!/usr/bin/env python
# Copyright 2016 EDF. This software was developed with the collaboration of
# Phimeca Engineering (Sylvain Girard, girard@phimeca.com).
"""Run multiple FMU simulations in parallel."""

import numpy as np
import openturns as ot
import otfmi
import otfmi.example
import psutil
import time

# Define the input distribution
E = ot.Beta(0.93, 3.2, 28000000.0, 48000000.0)
F = ot.LogNormalMuSigma(3.0e4, 9000.0, 15000.0).getDistribution()
L = ot.Uniform(250.0, 260.0)
II = ot.Beta(2.5, 4.0, 310.0, 450.0)


# Create the input probability distribution of dimension 4
inputDistribution = ot.ComposedDistribution([E, F, L, II])
# Give a description of each component of the input distribution
inputDistribution.setDescription(("E", "F", "L", "I"))
# Create the input random vector
inputRandomVector = ot.RandomVector(inputDistribution)


def instantiate_highlevel(n_cpus=2):
    """Instantiate an FMUFunction and set number of cores to use.

    Parameters
    ----------
    n_cpus : Integer, number of cores to use for multiprocessing.

    """
    path_fmu = otfmi.example.get_fmu_path("deviation.fmu")
    return otfmi.FMUFunction(
        path_fmu, inputs_fmu=["E", "F", "L", "I"], outputs_fmu="y", n_cpus=n_cpus
    )


def instantiate_lowlevel():
    """Instantiate an OpenTURNSFMUFunction."""
    path_fmu = otfmi.example.get_fmu_path("deviation.fmu")
    return otfmi.OpenTURNSFMUFunction(
        path_fmu, inputs_fmu=["E", "F", "L", "I"], outputs_fmu="y"
    )


def ask_n_cpus():
    """Get integer number of cores from user."""
    query = "How many cores do you want to use? "
    try:
        n_cpus = int(input(query))
    except ValueError:
        n_cpus = psutil.cpu_count(logical=False)
        print("(Using the default number of cpus).")
        return n_cpus


def pause():
    """Interrupt execution."""
    input("(press RETURN to continue)")


def run_demo(n_simulation):
    """Run the demonstration.

    Parameters
    ----------
    n_simulation : Integer, number of simulation to perform.

    """

    print(
        "\nWith the high level object 'FMUFunction', the number"
        " of cores is selected at instantiation."
    )
    n_cpus_highlevel = ask_n_cpus()
    highlevel = instantiate_highlevel(n_cpus=n_cpus_highlevel)
    print(
        (
            "Instantiated an 'FMUFunction' with %d cores for"
            " multiprocessing." % n_cpus_highlevel
        )
    )
    outputVariableOfInterest = ot.CompositeRandomVector(highlevel, inputRandomVector)
    print(("Running %d simulations with %d cores." % (n_simulation, n_cpus_highlevel)))
    pause()
    title = "Simulation results:"
    print(title)
    print(("-" * len(title)))
    start = time.time()
    print((outputVariableOfInterest.getSample(n_simulation)))
    elapsed_highlevel = time.time() - start

    print(
        "\nWith the lower level object 'OpenTURNSFMUFunction', the number"
        " of cores can be selected at runtime."
    )
    lowlevel = instantiate_lowlevel()
    print("Instantiated an 'OpenTURNSFMUFunction'")
    n_cpus_lowlevel = ask_n_cpus()
    print(("Running %d simulations with %d cores." % (n_simulation, n_cpus_lowlevel)))
    pause()
    title = "Simulation results:"
    print(title)
    print(("-" * len(title)))

    start = time.time()
    print(
        (
            lowlevel(
                np.array(inputRandomVector.getSample(n_simulation)),
                n_cpus=n_cpus_lowlevel,
            )
        )
    )
    elapsed_lowlevel = time.time() - start
    return (
        n_simulation,
        n_cpus_highlevel,
        elapsed_highlevel,
        n_cpus_lowlevel,
        elapsed_lowlevel,
    )


if __name__ == "__main__":
    n_simulation = 40
    try:
        query = (
            "How many simulations do you want to perform"
            " (%d by default)?" % n_simulation
        )
        n_simulation = int(input(query))
    except ValueError:
        print("(Using the default number of simulations).")

    (
        n_simulation,
        n_cpus_highlevel,
        elapsed_highlevel,
        n_cpus_lowlevel,
        elapsed_lowlevel,
    ) = run_demo(n_simulation=n_simulation)
