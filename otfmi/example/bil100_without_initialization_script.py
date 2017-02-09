# -*- coding: utf-8 -*-
# Copyright 2016 EDF. This software was developed with the collaboration of
# Phimeca Engineering (Sylvain Girard, girard@phimeca.com).
"""Run the “BIL100” example (see “bil100.py”) using an FMU with harcoded
initialization guess values."""

#§
import os
path_here = os.path.dirname(os.path.abspath(__file__))
import imp
bil100 = imp.load_source('bil100', os.path.join(path_here, "bil100.py"))

def run_demo(seed=None, n_simulation=None):
    """Run the demonstration.

    Parameters:
    ----------
    seed : Integer, seed of the random number generator.

    n_simulation : Integer, number of simulations.

    (See 'bil100.py' for more details)

    """

    bil100.run_demo(with_initialization_script=False, seed=seed,
                    n_simulation=n_simulation)

if __name__ == "__main__":
    run_demo()


#§
