# -*- coding: utf-8 -*-
# Copyright 2016 EDF. This software was developed with the collaboration of
# Phimeca Engineering (Sylvain Girard, girard@phimeca.com).
"""Provide a class for simulation and result handling of FMU.
FMUFunction is NumericalMathFunction factory similar to OpenTURNS'
PythonFunction.
It relies on the lower level OpenTURNSFMUFunction, which is similar to
OpenTURNS' (OpenTURNSPythonFunction.
"""

#§
import openturns as ot
import pyfmi
import numpy as np

from .fmi import (apply_initialization_script, reshape_input,
                  parse_kwargs_simulate, strip_simulation, get_name_variable)
import fmi


from .fmu_pool import FMUPool
#§
class FMUFunction(ot.NumericalMathFunction):
    """
    Override NumericalMathFunction from Python.

    Parameters
    ----------
    path_fmu : String, path to the FMU file.

    inputs_fmu : Sequence of string, names of the variable from the fmu to be
    used as input variables.

    outputs_fmu : Sequence of string, names of the variable from the fmu to be
    used as output variables.

    inputs : Sequence of string, optional names to use as variables
    descriptions.

    outputs : Sequence of string, optional names to use as variables
    descriptions.

    n_cpus :  Integer, number of cores to use for multiprocessing.

    initialization_script : String (optional), path to the initialization
    script.

    kind : String, one of "ME" (model exchange) or "CS" (co-simulation) to
    select a kind of FMU if both are available.
    Note:
    Contrary to pyfmi, the default here is "CS" (co-simulation). The rationale
    behind this choice is is that co-simulation may be used to impose a solver
    not available in pyfmi.

    """
    # expect_trajectory : Boolean, if True, the call inputs are assumed to be
    # time dependent trajectories. Default is False
    # TODO: Not implemented yet. Currently the __call__ from
    # NumericalMathFunction gets in the way and switch to sample execution.
    # Hence a sequence of vectors is expected but a single vector is
    # outputted.


    def __new__(self, path_fmu=None, inputs_fmu=None, outputs_fmu=None,
                inputs=None, outputs=None, n_cpus=None, kind=None,
                initialization_script=None):
        lowlevel = OpenTURNSFMUFunction(
            path_fmu=path_fmu, inputs_fmu=inputs_fmu, outputs_fmu=outputs_fmu,
            inputs=inputs, n_cpus=n_cpus, outputs=outputs, kind=kind,
            initialization_script=initialization_script)

        highlevel = ot.NumericalMathFunction(lowlevel)
        # highlevel._model = lowlevel.model
        return highlevel

#§
class OpenTURNSFMUFunction(ot.OpenTURNSPythonFunction):
    """
    Override NumericalMathFunction from Python.

    Parameters
    ----------
    path_fmu : String, path to the FMU file.

    inputs_fmu : Sequence of string, names of the variable from the fmu to be
    used as input variables.

    outputs_fmu : Sequence of string, names of the variable from the fmu to be
    used as output variables.

    inputs : Sequence of string, optional names to use as variables
    descriptions.

    outputs : Sequence of string, optional names to use as variables
    descriptions.

    n_cpus :  Integer, number of cores to use for multiprocessing.

    initialization_script : String (optional), path to the initialization
    script.

    kind : String, one of "ME" (model exchange) or "CS" (co-simulation) to
    select a kind of FMU if both are available.
    Note:
    Contrary to pyfmi, the default here is "CS" (co-simulation). The rationale
    behind this choice is is that co-simulation may be used to impose a solver
    not available in pyfmi.

    expect_trajectory : Boolean, if True, the call inputs are assumed to be
    time dependent trajectories. Default is False


    """

    def __init__(self, path_fmu, inputs_fmu, outputs_fmu=None,
                 inputs=None, outputs=None, n_cpus=None,
                 initialization_script=None, kind=None,
                 expect_trajectory=False):
        self.load_fmu(path_fmu=path_fmu, kind=kind)

        self.inputs_fmu = inputs_fmu
        if outputs_fmu is None:
            outputs_fmu = get_name_variable(self.model)

        self.outputs_fmu = outputs_fmu

        super(OpenTURNSFMUFunction, self).__init__(n=len(inputs_fmu),
                                                   p=len(outputs_fmu))

        if inputs is None:
            inputs = inputs_fmu
        if outputs is None:
            outputs = outputs_fmu

        self.setInputDescription(inputs)
        self.setOutputDescription(outputs)

        self.n_cpus = n_cpus

        self.initialize(initialization_script)

        self.__final = True # Boolean, if True (default), return only final
                            # values  instead of whole trajectories.

        self.__expect_trajectory = expect_trajectory


    def __call__(self, X, **kwargs):
        X = np.atleast_1d(np.squeeze(X))
        if self.__expect_trajectory:
            if X.ndim > 2:
                return self._exec_sample(X, **kwargs)
            else:
                return self._exec(X, **kwargs)
        else:
            if X.ndim > 1:
                return self._exec_sample(X, **kwargs)
            else:
                return self._exec(X, **kwargs)

    def _exec(self, value_input, **kwargs):
        """Simulate the FMU for a given set of input values.

        Parameters:
        ----------
        value_input : Vector or array-like with time steps as rows.

        See the 'simulate' method for additional keyword arguments.

        """

        return self.simulate(value_input=value_input, **kwargs)


    def _exec_sample(self, list_value_input, **kwargs):
        """Simulate the FMU multiple times.

        Parameters:
        ----------
        list_value_input : Sequence of vectors of input values.

        n_cpus :  Integer, number of cores to use for multiprocessing. Use the
        value of the 'n_cpus" attribute as default, or 1 (no multiprocessing)
        if not set.

        Additional keyword arguments are passed on to the 'simulate' method of
        the underlying PyFMI model object.

        """

        n_cpus = kwargs.pop("n_cpus", None)
        return self.simulate_sample(list_value_input, n_cpus=n_cpus, **kwargs)

    def load_fmu(self, path_fmu, kind=None, **kwargs):
        """Load an FMU.

        Parameters
        ----------
        path_fmu : String, path to the FMU file.

        kind : String, one of "ME" (model exchange) or "CS" (co-simulation) to
        select a kind of FMU if both are available.
        Note:
        Contrary to pyfmi, the default here is "CS" (co-simulation). The
        rationale behind this choice is  is that co-simulation may be used to
        impose a solver not available in pyfmi.

        Additional keyword arguments are passed on to pyfmi's 'load_fmu'
        function.

        """

        self.model = fmi.load_fmu(path_fmu=path_fmu, kind=kind, **kwargs)

    def getFMUInputDescription(self):
        """Get the list of input variable names."""
        return self.inputs_fmu

    def getFMUOutputDescription(self):
        """Get the list of output variable names."""
        return self.outputs_fmu

    def initialize(self, initialization_script=None):
        """Initialize the FMU, using initialization script if available.

        Parameters:
        ----------
        initialization_script : String (optional), path to the initialization
        script.

        """

        self.initialization_script = initialization_script
        self.model.setup_experiment()
        try:
            apply_initialization_script(self.model,
                                        self.initialization_script)
        except TypeError:
            pass # No initialization script.
        self.model.initialize()


    def simulate(self, value_input=None, reset=True, **kwargs):
        """Simulate the fmu.

        Parameters:
        ----------
        value_input : Vector of input values.

        reset : Boolean, toggle reseting the FMU prior to simulation. True by
        default.

        Optional keyword arguments:
        time : Sequence of floats, time vector.

        timestep : Float, timestep in seconds.

        Additional keyword arguments are passed on to the 'simulate' method of
        the underlying PyFMI model object.

        """


        kwargs.setdefault("initialization_script", self.initialization_script)

        kwargs_simulate = parse_kwargs_simulate(
            value_input, name_input=self.getFMUInputDescription(),
            name_output=self.getFMUOutputDescription(),
            dimension_input=self.getInputDimension(), final=self.__final,
            **kwargs)

        simulation = fmi.simulate(self.model, reset=reset, **kwargs_simulate)

        return strip_simulation(simulation,
                                name_output=self.getOutputDescription(),
                                final=self.__final)

    def simulate_sample(self, list_value_input, n_cpus=None, **kwargs):
        """Simulate the FMU multiple times.

        Parameters:
        ----------
        list_value_input : Sequence of vectors of input values.

        n_cpus :  Integer, number of cores to use for multiprocessing. Use the
        value of the 'n_cpus" attribute as default, or 1 (no multiprocessing)
        if not set.

        Additional keyword arguments are passed on to the 'simulate' method of
        the underlying PyFMI model object.

        """

        if n_cpus is None:
            if self.n_cpus is None:
                n_cpus = 1
            else:
                n_cpus = self.n_cpus

        kwargs.setdefault("initialization_script", self.initialization_script)

        #T?ODO: refactorize parsing of kwargs?

        list_kwargs = []
        for value_input in list_value_input:
            kwargs_simulate = parse_kwargs_simulate(
                value_input, name_input=self.getFMUInputDescription(),
                name_output=self.getFMUOutputDescription(),
                dimension_input=self.getInputDimension())
            list_kwargs.append(kwargs_simulate)


        # if n_cpus > 1: # TODO?
        pool = FMUPool(self.model, n_process=n_cpus)
        return pool.run(list_kwargs)

#§
