# Copyright 2016 EDF. This software was developed with the collaboration of
# Phimeca Engineering (Sylvain Girard, girard@phimeca.com).
"""Provide a class for simulation and result handling of FMU.
FMUFunction is Function factory similar to OpenTURNS'
PythonFunction.
It relies on the lower level OpenTURNSFMUFunction, which is similar to
OpenTURNS' OpenTURNSPythonFunction.
"""

import openturns as ot
import pyfmi
import numpy as np
import os
from . import fmi
from . import fmu_pool


class FMUFunction(ot.Function):
    """
    Define a Function from a FMU file.

    Parameters
    ----------
    path_fmu : str, path to the FMU file.

    inputs_fmu : Sequence of str, default=None
        Names of the variable from the fmu to be used as input variables.
        By default assigns variables with FMI causality INPUT.

    outputs_fmu : Sequence of str, default=None
        Names of the variable from the fmu to be used as output variables.
        By default assigns variables with FMI causality OUTPUT.

    n_cpus : int
        Number of cores to use for multiprocessing.

    initialization_script : str (optional)
        Path to the initialization script.

    final_time : float
        The output variables value is collected at t=final_time and returned by
        FMUFunction.

    kind : str, one of "ME" (model exchange) or "CS"
        (co-simulation)
        Select a kind of FMU if both are available.
        Note:
        Contrary to pyfmi, the default here is "CS" (co-simulation). The
        rationale behind this choice is that co-simulation may be used to
        impose a solver not available in pyfmi.

    """

    def __new__(
        self,
        path_fmu=None,
        inputs_fmu=None,
        outputs_fmu=None,
        n_cpus=None,
        kind=None,
        initialization_script=None,
        final_time=None,
    ):
        lowlevel = OpenTURNSFMUFunction(
            path_fmu=path_fmu,
            inputs_fmu=inputs_fmu,
            outputs_fmu=outputs_fmu,
            n_cpus=n_cpus,
            kind=kind,
            initialization_script=initialization_script,
            final_time=final_time,
        )

        highlevel = ot.Function(lowlevel)
        # highlevel._model = lowlevel.model
        return highlevel


class OpenTURNSFMUFunction(ot.OpenTURNSPythonFunction):
    """
    Define a Function from a FMU file.

    Parameters
    ----------
    path_fmu : str, path to the FMU file.

    inputs_fmu : Sequence of str, default=None
        Names of the variable from the fmu to be used as input variables.
        By default assigns variables with FMI causality INPUT.

    outputs_fmu : Sequence of str, default=None
        Names of the variable from the fmu to be used as output variables.
        By default assigns variables with FMI causality OUTPUT.

    n_cpus : int
        Number of cores to use for multiprocessing.

    initialization_script : str (optional)
        Path to the initialization script.

    final_time : float
        The output variables value is collected at t=final_time and returned by
        FMUFunction.

    kind : str, one of "ME" (model exchange) or "CS" (co-simulation)
        Select a kind of FMU if both are available.
        Note:
        Contrary to pyfmi, the default here is "CS" (co-simulation). The
        rationale behind this choice is is that co-simulation may be used to
        impose a solver not available in pyfmi.

    """

    def __init__(
        self,
        path_fmu,
        inputs_fmu=None,
        outputs_fmu=None,
        n_cpus=None,
        initialization_script=None,
        kind=None,
        final_time=None,
        **kwargs
    ):
        self.load_fmu(path_fmu=path_fmu, kind=kind)

        self._set_inputs_fmu(inputs_fmu)
        self._set_outputs_fmu(outputs_fmu)

        super(OpenTURNSFMUFunction, self).__init__(
            n=len(self.inputs_fmu), p=len(self.outputs_fmu)
        )
        self.setInputDescription(self.inputs_fmu)
        self.setOutputDescription(self.outputs_fmu)

        self._set_final_time(final_time)

        self.n_cpus = n_cpus

        self.initialize(initialization_script)

        self.__final = kwargs.pop("final", None)

    def _set_inputs_fmu(self, inputs_fmu):
        """Set input variable names.

        Parameters
        ----------
        inputs_fmu : Sequence of strings
            Names of the variable from the fmu to be used as input variables.
        """

        all_vars = fmi.get_name_variable(self.model)
        causality = dict(zip(all_vars, fmi.get_causality(self.model, all_vars)))

        if inputs_fmu is None:
            # choose all variables with variability INPUT
            fmix_input = (
                pyfmi.fmi.FMI2_INPUT
                if self.model.get_version() == "2.0"
                else pyfmi.fmi.FMI_INPUT
            )
            inputs_fmu = [name for name in all_vars if causality[name] == fmix_input]
        else:
            difference = set(inputs_fmu).difference(all_vars)
            if difference:
                raise pyfmi.common.io.VariableNotFoundError(", ".join(difference))

            for name in inputs_fmu:
                if (
                    self.model.get_version() == "2.0"
                    and not causality[name]
                    in [pyfmi.fmi.FMI2_PARAMETER, pyfmi.fmi.FMI2_INPUT]
                ) or (
                    self.model.get_version() == "1.0"
                    and causality[name] != pyfmi.fmi.FMI_INPUT
                ):
                    raise ValueError(
                        'Variable "'
                        + name
                        + '" cannot be used as a function input (causality '
                        + fmi.get_causality_str(self.model, name)
                        + ")"
                    )

        self.inputs_fmu = inputs_fmu

    def _set_outputs_fmu(self, outputs_fmu):
        """Set output variable names.

        Parameters
        ----------
        outputs_fmu : Sequence of strings
            Names of the variable from the fmu to be used as output variables.
        """

        all_vars = fmi.get_name_variable(self.model)
        causality = dict(zip(all_vars, fmi.get_causality(self.model, all_vars)))

        if outputs_fmu is None:
            # choose all variables with variability OUTPUT
            fmix_output = (
                pyfmi.fmi.FMI2_OUTPUT
                if self.model.get_version() == "2.0"
                else pyfmi.fmi.FMI_OUTPUT
            )
            outputs_fmu = [name for name in all_vars if causality[name] == fmix_output]
            if len(outputs_fmu) == 0:
                raise pyfmi.common.io.VariableNotFoundError(
                    "No variables marked as OUTPUT please specify outputs_fmu"
                )
        else:
            difference = set(outputs_fmu).difference(fmi.get_name_variable(self.model))
            if difference:
                raise pyfmi.common.io.VariableNotFoundError(", ".join(difference))

            for name in outputs_fmu:
                if (
                    self.model.get_version() == "2.0"
                    and not causality[name]
                    in [pyfmi.fmi.FMI2_LOCAL, pyfmi.fmi.FMI2_OUTPUT]
                ) or (
                    self.model.get_version() == "1.0"
                    and causality[name] != pyfmi.fmi.FMI_OUTPUT
                ):
                    raise ValueError(
                        'Variable "'
                        + name
                        + '" cannot be used as a function output (causality '
                        + fmi.get_causality_str(self.model, name)
                        + ")"
                    )
        self.outputs_fmu = outputs_fmu

    def __call__(self, X, **kwargs):
        X = np.atleast_1d(np.squeeze(X))
        if X.ndim > 1:
            return self._exec_sample(X, **kwargs)
        else:
            return self._exec(X, **kwargs)

    def _set_final_time(self, final_time):
        """Extract final time from keywords if exists.

        Parameters
        ----------
        final_time: float (must be >= 0).

        """
        if final_time is not None:
            self.final_time = final_time
        else:
            self.final_time = self.model.get_default_experiment_stop_time()

    def _exec(self, value_input, **kwargs):
        """Simulate the FMU for a given set of input values.

        Parameters
        ----------
        value_input : Vector or array-like with time steps as rows.

        See the 'simulate' method for additional keyword arguments.

        """

        return self.simulate(value_input=value_input, **kwargs)

    def _exec_sample(self, list_value_input, **kwargs):
        """Simulate the FMU multiple times.

        Parameters
        ----------
        list_value_input : Sequence of vectors of input values.

        Additional keyword arguments are passed on to the 'simulate' method of
        the underlying PyFMI model object.

        """
        return self.simulate_sample(list_value_input, **kwargs)

    def load_fmu(self, path_fmu, kind=None, **kwargs):
        """Load an FMU.

        Parameters
        ----------
        path_fmu : String, path to the FMU file.

        kind : String, one of "ME" (model exchange) or "CS" (co-simulation)
            Select a kind of FMU if both are available.
            Note:
            Contrary to pyfmi, the default here is "CS" (co-simulation). The
            rationale behind this choice is is that co-simulation may be used
            to impose a solver not available in pyfmi.

        Additional keyword arguments are passed on to pyfmi's 'load_fmu'
        function.

        """

        self.model = fmi.load_fmu(
            path_fmu=os.path.expanduser(path_fmu), kind=kind, **kwargs
        )

    def getFMUInputDescription(self):
        """Get the list of input variable names."""
        return self.inputs_fmu

    def getFMUOutputDescription(self):
        """Get the list of output variable names."""
        return self.outputs_fmu

    def initialize(self, initialization_script=None):
        """Initialize the FMU, using initialization script if available.

        Parameters
        ----------
        initialization_script : String (optional), path to the initialization
        script.

        """

        self.initialization_script = initialization_script
        try:
            self.model.setup_experiment()
        except AttributeError:
            pass  # Probably FMI version 1.
        try:
            fmi.apply_initialization_script(self.model, self.initialization_script)
        except TypeError:
            pass  # No initialization script.
        try:
            self.model.initialize()
        except pyfmi.fmi.FMUException as ex:
            raise pyfmi.fmi.FMUException(
                str(ex) + "\n" + "\n".join([str(line) for line in self.model.get_log()])
            )

    def simulate(self, value_input=None, reset=True, **kwargs):
        """Simulate the fmu.

        Parameters
        ----------
        value_input : Vector of input values.

        reset : Boolean, toggle resetting the FMU prior to simulation. True by
        default.

        time : Sequence of floats, time vector (optional).

        timestep : Float, time step in seconds (optional).

        Additional keyword arguments are passed on to the 'simulate' method of
        the underlying PyFMI model object.

        """

        kwargs.setdefault("initialization_script", self.initialization_script)

        kwargs_simulate = fmi.parse_kwargs_simulate(
            value_input,
            name_input=self.getFMUInputDescription(),
            name_output=self.getFMUOutputDescription(),
            model=self.model,
            **kwargs
        )

        if "final_time" in kwargs.keys():
            raise Warning("final_time must be set in the constructor.")

        simulation = fmi.simulate(
            self.model, reset=reset, final_time=self.final_time, **kwargs_simulate
        )

        return fmi.strip_simulation(
            simulation, name_output=self.getOutputDescription(), final=self.__final
        )

    def simulate_sample(self, list_value_input, **kwargs):
        """Simulate the FMU multiple times.

        Parameters
        ----------
        list_value_input : Sequence of vectors of input values.

        Additional keyword arguments are passed on to the 'simulate' method of
        the underlying PyFMI model object.

        """

        n_cpus = 1 if self.n_cpus is None else self.n_cpus
        if n_cpus == 1:
            return [self.simulate(point, **kwargs) for point in list_value_input]

        kwargs.setdefault("initialization_script", self.initialization_script)

        # TODO: re-factorize parsing of kwargs?

        list_kwargs = []
        for value_input in list_value_input:
            kwargs_simulate = fmi.parse_kwargs_simulate(
                value_input,
                name_input=self.getFMUInputDescription(),
                name_output=self.getFMUOutputDescription(),
                model=self.model,
                **kwargs
            )
            list_kwargs.append(kwargs_simulate)

        pool = fmu_pool.FMUPool(self.model, n_process=n_cpus)
        return pool.run(list_kwargs, final=self.__final)


class FMUPointToFieldFunction(ot.PointToFieldFunction):
    """
    Define a PointToFieldFunction from a FMU file.

    Parameters
    ----------
    path_fmu : str, path to the FMU file.

    mesh : :class:`openturns.Mesh`
        Time grid, has to be included in the start/end time defined in the FMU.
        By default it takes into account the start/end time and default step defined the FMU.

    inputs_fmu : Sequence of str, default=None
        Names of the variable from the fmu to be used as input variables.
        By default assigns variables with FMI causality INPUT.

    outputs_fmu : Sequence of str, default=None
        Names of the variable from the fmu to be used as output variables.
        By default assigns variables with FMI causality OUTPUT.

    initialization_script : str (optional)
        Path to the initialization script.

    kind : str, one of "ME" (model exchange) or "CS" (co-simulation)
        Select a kind of FMU if both are available.
        Note:
        Contrary to pyfmi, the default here is "CS" (co-simulation). The
        rationale behind this choice is that co-simulation may be used to
        impose a solver not available in pyfmi.

    start_time : float
        The FMU simulation start time.

    final_time : float
        The FMU simulation stop time.

    """

    def __new__(
        self,
        path_fmu,
        mesh=None,
        inputs_fmu=None,
        outputs_fmu=None,
        kind=None,
        initialization_script=None,
        start_time=None,
        final_time=None,
    ):
        lowlevel = OpenTURNSFMUPointToFieldFunction(
            path_fmu=path_fmu,
            mesh=mesh,
            inputs_fmu=inputs_fmu,
            outputs_fmu=outputs_fmu,
            kind=kind,
            initialization_script=initialization_script,
            start_time=start_time,
            final_time=final_time,
        )

        highlevel = ot.PointToFieldFunction(lowlevel)
        # highlevel._model = lowlevel.model
        return highlevel


class OpenTURNSFMUPointToFieldFunction(ot.OpenTURNSPythonPointToFieldFunction):
    """Define a PointToFieldFunction from a FMU file."""

    def __init__(
        self,
        path_fmu,
        mesh=None,
        inputs_fmu=None,
        outputs_fmu=None,
        initialization_script=None,
        kind=None,
        start_time=None,
        final_time=None,
        **kwargs
    ):
        self.load_fmu(path_fmu=path_fmu, kind=kind)

        if mesh is None:
            tmin = self.model.get_default_experiment_start_time()
            tmax = self.model.get_default_experiment_stop_time()
            if start_time is not None:
                tmin = max(tmin, start_time)
            if final_time is not None:
                tmax = min(tmax, final_time)
            step = self.model.get_default_experiment_step()
            n = int((tmax - tmin) / step)
            mesh = ot.IntervalMesher([n]).build(ot.Interval(tmin, tmax))
        else:
            assert isinstance(mesh, ot.Mesh), "Expected mesh of type ot.Mesh"

        self._set_inputs_fmu(inputs_fmu)
        self._set_outputs_fmu(outputs_fmu)

        super(OpenTURNSFMUPointToFieldFunction, self).__init__(
            len(self.inputs_fmu), mesh, len(self.outputs_fmu)
        )
        self.setInputDescription(self.inputs_fmu)
        self.setOutputDescription(self.outputs_fmu)
        self._set_final_time(final_time)
        self._set_start_time(start_time)
        self._assert_mesh_validity()

        self.initialize(initialization_script)

    def _set_inputs_fmu(self, inputs_fmu):
        """Set input variable names.

        Parameters
        ----------
        inputs_fmu : Sequence of strings
            Names of the variable from the fmu to be used as input variables.
        """

        all_vars = fmi.get_name_variable(self.model)
        causality = dict(zip(all_vars, fmi.get_causality(self.model, all_vars)))

        if inputs_fmu is None:
            # choose all variables with variability INPUT
            fmix_input = (
                pyfmi.fmi.FMI2_INPUT
                if self.model.get_version() == "2.0"
                else pyfmi.fmi.FMI_INPUT
            )
            inputs_fmu = [name for name in all_vars if causality[name] == fmix_input]
        else:
            difference = set(inputs_fmu).difference(all_vars)
            if difference:
                raise pyfmi.common.io.VariableNotFoundError(", ".join(difference))

            for name in inputs_fmu:
                if (
                    self.model.get_version() == "2.0"
                    and not causality[name]
                    in [pyfmi.fmi.FMI2_PARAMETER, pyfmi.fmi.FMI2_INPUT]
                ) or (
                    self.model.get_version() == "1.0"
                    and causality[name] != pyfmi.fmi.FMI_INPUT
                ):
                    raise ValueError(
                        'Variable "'
                        + name
                        + '" cannot be used as a function input (causality '
                        + fmi.get_causality_str(self.model, name)
                        + ")"
                    )

        self.inputs_fmu = inputs_fmu

    def _set_outputs_fmu(self, outputs_fmu):
        """Set output variable names.

        Parameters
        ----------
        outputs_fmu : Sequence of strings
            Names of the variable from the fmu to be used as output variables.
        """

        all_vars = fmi.get_name_variable(self.model)
        causality = dict(zip(all_vars, fmi.get_causality(self.model, all_vars)))

        if outputs_fmu is None:
            # choose all variables with variability OUTPUT
            fmix_output = (
                pyfmi.fmi.FMI2_OUTPUT
                if self.model.get_version() == "2.0"
                else pyfmi.fmi.FMI_OUTPUT
            )
            outputs_fmu = [name for name in all_vars if causality[name] == fmix_output]
            if len(outputs_fmu) == 0:
                raise pyfmi.common.io.VariableNotFoundError(
                    "No variables marked as OUTPUT please specify outputs_fmu"
                )
        else:
            difference = set(outputs_fmu).difference(fmi.get_name_variable(self.model))
            if difference:
                raise pyfmi.common.io.VariableNotFoundError(", ".join(difference))

            for name in outputs_fmu:
                if (
                    self.model.get_version() == "2.0"
                    and not causality[name]
                    in [pyfmi.fmi.FMI2_LOCAL, pyfmi.fmi.FMI2_OUTPUT]
                ) or (
                    self.model.get_version() == "1.0"
                    and causality[name] != pyfmi.fmi.FMI_OUTPUT
                ):
                    raise ValueError(
                        'Variable "'
                        + name
                        + '" cannot be used as a function output (causality '
                        + fmi.get_causality_str(self.model, name)
                        + ")"
                    )
        self.outputs_fmu = outputs_fmu

    def _set_final_time(self, final_time):
        """Extract final time from keywords if exists.

        Parameters
        ----------
        final_time: float (must be >= 0).

        """
        if final_time is not None:
            self.final_time = final_time
        else:
            self.final_time = self.model.get_default_experiment_stop_time()

    def _set_start_time(self, start_time):
        """Extract start time from keywords if exists.

        Parameters
        ----------
        start_time: float (must be >= 0)

        """
        if start_time is not None:
            self.start_time = start_time
        else:
            self.start_time = self.model.get_default_experiment_start_time()

    def _assert_mesh_validity(self):
        """Raise an error if the mesh is not comprised between the start and
        final simulation time.
        """
        mesh = self.getOutputMesh()
        mesh_min = mesh.getVertices().getMin()[0]
        mesh_max = mesh.getVertices().getMax()[0]
        tol = (mesh_max - mesh_min) * 1e-6
        assert (
            mesh_min + tol >= self.start_time
        ), """The mesh start time must be >= to FMU start time.\n
            To set the FMU start time, use the argument *start_time* in
            FMUPointToFieldFunction constructor."""

        assert (
            mesh_max <= self.final_time + tol
        ), f"""The mesh final time ({mesh_max}) must be <= to FMU final time ({self.final_time}).\n
            To set the FMU final time, use the argument final_time in
            FMUPointToFieldFunction constructor."""

    def _exec(self, value_input, **kwargs):
        """Simulate the FMU for a given set of input values.

        Parameters
        ----------
        value_input : Vector or array-like with time steps as rows.

        See the 'simulate' method for additional keyword arguments.

        """

        return self.simulate(value_input=value_input, **kwargs)

    def load_fmu(self, path_fmu, kind=None, **kwargs):
        """Load an FMU.

        Parameters
        ----------
        path_fmu : String, path to the FMU file.

        kind : String, one of "ME" (model exchange) or "CS" (co-simulation)
            Select a kind of FMU if both are available.
            Note:
            Contrary to pyfmi, the default here is "CS" (co-simulation). The
            rationale behind this choice is is that co-simulation may be used
            to impose a solver not available in pyfmi.

        Additional keyword arguments are passed on to pyfmi's 'load_fmu'
        function.

        """

        self.model = fmi.load_fmu(
            path_fmu=os.path.expanduser(path_fmu), kind=kind, **kwargs
        )

    def getFMUInputDescription(self):
        """Get the list of input variable names."""
        return self.inputs_fmu

    def getFMUOutputDescription(self):
        """Get the list of output variable names."""
        return self.outputs_fmu

    def initialize(self, initialization_script=None):
        """Initialize the FMU, using initialization script if available.

        Parameters
        ----------
        initialization_script : String (optional), path to the initialization
        script.

        """

        self.initialization_script = initialization_script
        try:
            self.model.setup_experiment()
        except AttributeError:
            pass  # Probably FMI version 1.
        try:
            fmi.apply_initialization_script(self.model, self.initialization_script)
        except TypeError:
            pass  # No initialization script.
        try:
            self.model.initialize()
        except pyfmi.fmi.FMUException as ex:
            raise pyfmi.fmi.FMUException(
                str(ex) + "\n" + "\n".join([str(line) for line in self.model.get_log()])
            )

    def simulate(self, value_input=None, reset=True, **kwargs):
        """Simulate the fmu.

        Parameters
        ----------
        value_input : Vector of input values.

        reset : Boolean, toggle resetting the FMU prior to simulation. True by
        default.

        time : Sequence of floats, time vector (optional).

        timestep : Float, time step in seconds (optional).

        Additional keyword arguments are passed on to the 'simulate' method of
        the underlying PyFMI model object.

        """

        kwargs.setdefault("initialization_script", self.initialization_script)

        kwargs_simulate = fmi.parse_kwargs_simulate(
            value_input,
            name_input=self.getFMUInputDescription(),
            name_output=self.getFMUOutputDescription(),
            model=self.model,
            **kwargs
        )

        if "final_time" in kwargs.keys():
            raise Warning("final_time must be set in the constructor.")
        if "start_time" in kwargs.keys():
            raise Warning("start_time must be set in the constructor.")

        simulation = fmi.simulate(
            self.model,
            reset=reset,
            start_time=self.start_time,
            final_time=self.final_time,
            **kwargs_simulate
        )

        time, values = fmi.strip_simulation(
            simulation, name_output=self.getOutputDescription(), final="trajectory"
        )
        local_mesh = ot.Mesh(
            [[t] for t in time], [[i, i + 1] for i in range(len(time) - 1)]
        )
        interpolation = ot.P1LagrangeInterpolation(
            local_mesh, self.getOutputMesh(), self.getOutputDimension()
        )
        return interpolation(values)
