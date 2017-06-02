#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2016 EDF. This software was developed with the collaboration of
# Phimeca Engineering (Sylvain Girard, girard@phimeca.com).
"""Run multiple FMU simulations in parallel."""


#§ Identifying the platform
import platform
key_platform = (platform.system(), platform.architecture()[0])
# Call to either 'platform.system' or 'platform.architecture' *after*
# importing pyfmi causes a segfault.
dict_platform = {("Linux", "64bit"):"linux64",
                 ("Windows", "32bit"):"win32"}

#§ Define the input distribution
import openturns as ot

E = ot.Beta(0.93, 3.2, 28000000.0, 48000000.0)
F = ot.LogNormal(30000.0, 9000.0, 15000.0,  ot.LogNormal.MUSIGMA)
L = ot.Uniform(250.0, 260.0)
I = ot.Beta(2.5, 4.0, 310.0, 450.0)


# Create the input probability distribution of dimension 4
inputDistribution = ot.ComposedDistribution([E, F, L, I])
# Give a description of each component of the input distribution
inputDistribution.setDescription( ("E", "F", "L", "I") )
# Create the input random vector
inputRandomVector = ot.RandomVector(inputDistribution)

#§ FMU model
import otfmi
from pyfmi.fmi import FMUException
import sys

import os

import time


path_here = os.path.dirname(os.path.abspath(__file__))

def instantiate_highlevel(n_cpus=2):
    """Instantiate an FMUFunction and set number of cores to use.

    Parameters
    ----------
    n_cpus : Integer, number of cores to use for multiprocessing.

    """
    try:
        directory_platform = dict_platform[key_platform]
        path_fmu = os.path.join(path_here, "file", "fmu",
                                directory_platform, "deviation.fmu")
        return otfmi.FMUFunction(
            path_fmu, inputs_fmu=["E", "F", "L", "I"], outputs_fmu="y",
            n_cpus=n_cpus)
    except KeyError:
        raise RuntimeError("Examples are not available on your platform"
                           " (%s)." % "-".join(key_platform))
        sys.exit()
    except FMUException:
        raise FMUException("The example FMU 'deviation.fmu' is not"
                           " available on your platform (%s)." %
                           "-".join(key_platform))
        sys.exit()

def instantiate_lowlevel():
    """Instantiate an OpenTURNSFMUFunction."""
    try:
        directory_platform = dict_platform[key_platform]
        path_fmu = os.path.join(path_here, "file", "fmu",
                                directory_platform, "deviation.fmu")
        return otfmi.OpenTURNSFMUFunction(
            path_fmu, inputs_fmu=["E", "F", "L", "I"], outputs_fmu="y")
    except KeyError:
        raise RuntimeError("Examples are not available on your platform"
                           " (%s)." % "-".join(key_platform))
        sys.exit()
    except FMUException:
        raise FMUException("The example FMU 'deviation.fmu' is not"
                           " available on your platform (%s)." %
                           "-".join(key_platform))
        sys.exit()

def ask_n_cpus():
    """Get integer number of cores from user."""
    while True:
        how_many = eval(input("How many cores do you want to use? "))
        if how_many.lower() in ("", "q", "quit", "exit"):
            print("Aborted.")
            sys.exit()
        try:
            return int(how_many)
        except ValueError:
            print("Please enter an integer.")

def pause():
    """Interrupt execution."""
    eval(input("(press RETURN to continue)"))

def run_demo(n_simulation):
    """Run the demonstration.

    Parameters
    ----------
    n_simulation : Integer, number of simulation to perform.

    """

    print ("\nWith the high level object 'FMUFunction', the number"
           " of cores is selected at instantiation.")
    n_cpus_highlevel = ask_n_cpus()
    highlevel = instantiate_highlevel(n_cpus=n_cpus_highlevel)
    print(("Instantiated an 'FMUFunction' with %d cores for"
           " multiprocessing." % n_cpus_highlevel))
    outputVariableOfInterest = ot.RandomVector(highlevel, inputRandomVector)
    print(("Running %d simulations with %d cores." % (n_simulation,
                                                     n_cpus_highlevel)))
    pause()
    title = "Simulation results:"
    print(title)
    print(("-" * len(title)))
    start = time.time()
    print((outputVariableOfInterest.getSample(n_simulation)))
    elapsed_highlevel = time.time() - start

    print ("\nWith the lower level object 'OpenTURNSFMUFunction', the number"
           " of cores can be selected at runtime.")
    lowlevel = instantiate_lowlevel()
    print("Instantiated an 'OpenTURNSFMUFunction'")
    n_cpus_lowlevel = ask_n_cpus()
    print(("Running %d simulations with %d cores." % (n_simulation,
                                                     n_cpus_lowlevel)))
    pause()
    title = "Simulation results:"
    print(title)
    print(("-" * len(title)))
    import numpy as np
    start = time.time()
    print((lowlevel(np.array(inputRandomVector.getSample(n_simulation)),
                   n_cpus=n_cpus_lowlevel)))
    elapsed_lowlevel = time.time() - start
    return (n_simulation,
            n_cpus_highlevel, elapsed_highlevel,
            n_cpus_lowlevel, elapsed_lowlevel)

if __name__ == "__main__":
    n_simulation = 40
    try:
        n_simulation = int(eval(input("How many simulations do you want to"
                                     " perform (%d by default)? " %
                                     n_simulation)))
    except ValueError:
        print("(Using the default number of simulations).")

    (n_simulation,
     n_cpus_highlevel, elapsed_highlevel,
     n_cpus_lowlevel, elapsed_lowlevel) = run_demo(n_simulation=n_simulation)

#§
