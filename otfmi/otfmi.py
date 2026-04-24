# Copyright 2016-2025 EDF Phimeca

"""Middle and high level classes to simulate FMU files through OpenTURNS objects."""

import openturns as ot
import pyfmi
import numpy as np
from . import fmi


class _FMUBaseFunction:
    """Base Function skeleton."""

    def __init__(
        self,
        path_fmu,
        field_input=False,
        field_output=True,
        input_mesh=None,
        output_mesh=None,
        inputs_fmu=None,
        outputs_fmu=None,
        initialization_script=None,
        kind=None,
        start_time=None,
        final_time=None,
        **kwargs
    ):
        self.load_fmu(path_fmu=path_fmu, kind=kind)
        # for serialization we have to reload the pyfmi model, so save the parameters needed to reload
        self._path_fmu = path_fmu
        self._kind = kind

        self._set_simulation_time(start_time, final_time)

        # set input mesh
        self._set_input_mesh(input_mesh, field_input)

        # set output mesh
        self._set_output_mesh(output_mesh, field_output)

        self._set_inputs_fmu(inputs_fmu)
        self._set_outputs_fmu(outputs_fmu)

        self.initialize(initialization_script)

    def _set_inputs_fmu(self, inputs_fmu):
        """Set input variable names.

        Parameters
        ----------
        inputs_fmu : Sequence of str
            Names of the variable from the fmu to be used as input variables.
        """

        all_vars = fmi.get_name_variable(self._model)
        causality = dict(zip(all_vars, fmi.get_causality(self._model, all_vars)))

        if inputs_fmu is None:
            # choose all variables with variability INPUT
            fmix_input = (
                pyfmi.fmi.FMI2_INPUT
                if self._model.get_version() == "2.0"
                else pyfmi.fmi.FMI_INPUT
            )
            inputs_fmu = [name for name in all_vars if causality[name] == fmix_input]
        else:
            difference = set(inputs_fmu).difference(all_vars)
            if difference:
                raise pyfmi.common.io.VariableNotFoundError(", ".join(difference))

            input_causality_map = {"1.0": pyfmi.fmi.FMI_INPUT,
                                   "2.0": pyfmi.fmi.FMI2_INPUT}
            accepted_causality = [input_causality_map[self._model.get_version()]]
            if self._model.get_version() == "2.0" and not self._field_input:
                accepted_causality.append(pyfmi.fmi.FMI2_PARAMETER)
            for name in inputs_fmu:
                if not causality[name] in accepted_causality:
                    raise ValueError(f"Variable {name} cannot be used as a function input"
                                     f" (causality {fmi.get_causality_str(self._model, name)})")
        self._inputs_fmu = inputs_fmu

    def _set_outputs_fmu(self, outputs_fmu):
        """Set output variable names.

        Parameters
        ----------
        outputs_fmu : Sequence of str
            Names of the variable from the fmu to be used as output variables.
        """

        all_vars = fmi.get_name_variable(self._model)
        causality = dict(zip(all_vars, fmi.get_causality(self._model, all_vars)))

        if outputs_fmu is None:
            # choose all variables with variability OUTPUT
            fmix_output = (
                pyfmi.fmi.FMI2_OUTPUT
                if self._model.get_version() == "2.0"
                else pyfmi.fmi.FMI_OUTPUT
            )
            outputs_fmu = [name for name in all_vars if causality[name] == fmix_output]
            if len(outputs_fmu) == 0:
                raise pyfmi.common.io.VariableNotFoundError(
                    "No variables marked as OUTPUT please specify outputs_fmu"
                )
        else:
            difference = set(outputs_fmu).difference(fmi.get_name_variable(self._model))
            if difference:
                raise pyfmi.common.io.VariableNotFoundError(", ".join(difference))

            for name in outputs_fmu:
                if (
                    self._model.get_version() == "2.0"
                    and not causality[name]
                    in [pyfmi.fmi.FMI2_LOCAL, pyfmi.fmi.FMI2_OUTPUT]
                ) or (
                    self._model.get_version() == "1.0"
                    and causality[name] != pyfmi.fmi.FMI_OUTPUT
                ):
                    raise ValueError(
                        'Variable "'
                        + name
                        + '" cannot be used as a function output (causality '
                        + fmi.get_causality_str(self._model, name)
                        + ")"
                    )
        self._outputs_fmu = outputs_fmu

    def _set_input_mesh(self, input_mesh, field_input):
        self._field_input = field_input
        self._input_mesh = None
        if field_input:
            if input_mesh is None:
                input_mesh = self._get_default_mesh(self._start_time, self._final_time)
            else:
                if not isinstance(input_mesh, ot.Mesh):
                    raise TypeError("Expected mesh of type ot.Mesh")
            self._input_mesh = input_mesh
            self._check_mesh_validity(input_mesh)

    def _set_output_mesh(self, output_mesh, field_output):
        self._field_output = field_output
        self._output_mesh = None
        if field_output:
            if output_mesh is None:
                output_mesh = self._get_default_mesh(self._start_time, self._final_time)
            else:
                if not isinstance(output_mesh, ot.Mesh):
                    raise TypeError("Expected mesh of type ot.Mesh")
            self._output_mesh = output_mesh
            self._check_mesh_validity(output_mesh)

    def _check_mesh_validity(self, mesh):
        """Check if the mesh time interval and simulation time interval are consistent."""
        mesh_time = ot.Interval(mesh.getVertices().getMin(), mesh.getVertices().getMax())
        simulation_time = ot.Interval(self._start_time, self._final_time)
        if simulation_time.intersect(mesh_time).isEmpty():
            raise ValueError(f"The mesh time interval {mesh_time} does not overlap"
                             f" the simulation time interval {simulation_time}")

    def _get_default_mesh(self, start_time, final_time):
        tmin = self._model.get_default_experiment_start_time()
        tmax = self._model.get_default_experiment_stop_time()
        if start_time is not None:
            tmin = max(tmin, start_time)
        if final_time is not None:
            tmax = min(tmax, final_time)
        step = self._model.get_default_experiment_step()
        n = int((tmax - tmin) / step)
        mesh = ot.RegularGrid(tmin, step, n + 1)
        return mesh

    def _set_simulation_time(self, start_time, final_time):
        """Set start/final time.

        Parameters
        ----------
        start_time : float (must be >= 0)
        final_time : float (must be >= 0).
        """
        if start_time is not None:
            assert start_time >= 0.0, "Start time must be positive"
            self._start_time = start_time
        else:
            self._start_time = self._model.get_default_experiment_start_time()
        if final_time is not None:
            assert final_time >= 0.0, "Final time must be positive"
            self._final_time = final_time
        else:
            self._final_time = self._model.get_default_experiment_stop_time()
        assert self._final_time > self._start_time, "Final time must be > start time"

    def load_fmu(self, path_fmu, kind=None, **kwargs):
        """Load an FMU.

        Parameters
        ----------
        path_fmu : str or path-like
            Path to the FMU file.

        kind : str, one of "ME" (model exchange) or "CS" (co-simulation)
            Select a kind of FMU if both are available.
            Note:
            Contrary to pyfmi, the default here is "CS" (co-simulation). The
            rationale behind this choice is is that co-simulation may be used
            to impose a solver not available in pyfmi.

        Additional keyword arguments are passed on to pyfmi's 'load_fmu'
        function.

        """
        self._model = fmi.load_fmu(
            path_fmu=path_fmu, kind=kind, **kwargs
        )

    def initialize(self, initialization_script=None):
        """Initialize the FMU, using initialization script if available.

        Parameters
        ----------
        initialization_script : str (optional)
            path to the initialization script.

        """

        self.initialization_script = initialization_script
        try:
            self._model.setup_experiment()
        except AttributeError:
            pass  # Probably FMI version 1.
        try:
            fmi.apply_initialization_script(self._model, self.initialization_script)
        except TypeError:
            pass  # No initialization script.
        try:
            self._model.initialize()
        except pyfmi.fmi.FMUException as ex:
            raise pyfmi.fmi.FMUException(
                str(ex) + "\n" + "\n".join([str(line) for line in self._model.get_log()])
            )

    def simulate(self, value_input=None, reset=True, **kwargs):
        """Simulate the fmu.

        Parameters
        ----------
        value_input : Vector of input values.

        reset : bool, toggle resetting the FMU prior to simulation. True by
        default.

        time : Sequence of floats, time vector (optional).

        timestep : float, time step in seconds (optional).

        Additional keyword arguments are passed on to the 'simulate' method of
        the underlying PyFMI model object.

        """

        if "final_time" in kwargs.keys():
            raise Warning("final_time must be set in the constructor.")
        if "start_time" in kwargs.keys():
            raise Warning("start_time must be set in the constructor.")

        kwargs.setdefault("initialization_script", self.initialization_script)

        if self._field_input:
            kwargs.setdefault("time", self._input_mesh.getVertices().asPoint())

        kwargs_simulate = fmi.parse_kwargs_simulate(
            value_input,
            name_input=self._inputs_fmu,
            name_output=self._outputs_fmu,
            model=self._model,
            **kwargs
        )

        # do not override simulation time
        if self._field_input:
            kwargs_simulate.pop("start_time")
            kwargs_simulate.pop("final_time")

        simulation = fmi.simulate(
            self._model,
            reset=reset,
            start_time=self._start_time,
            final_time=self._final_time,
            **kwargs_simulate
        )

        if self._field_output:
            time, values = fmi.strip_simulation(simulation, name_output=self.get_outputs_fmu(), final="trajectory")
            local_mesh = ot.Mesh(
                [[t] for t in time], [[i, i + 1] for i in range(len(time) - 1)]
            )
            interpolation = ot.P1LagrangeInterpolation(
                local_mesh, self._output_mesh, len(self.get_outputs_fmu())
            )
            return interpolation(values)
        else:
            # output is a vector
            return fmi.strip_simulation(simulation, name_output=self.get_outputs_fmu())

    def __getstate__(self):
        data = super(_FMUBaseFunction, self).__getstate__()
        # remove pyfmi model
        if "_model" in data:
            data.pop("_model")
        return data

    def __setstate__(self, data):
        self.__dict__.update(data)
        # reload pyfmi model
        self.load_fmu(self._path_fmu, self._kind)

    def get_inputs_fmu(self):
        """Get the list of input variable names."""
        return self._inputs_fmu

    def get_outputs_fmu(self):
        """Get the list of output variable names."""
        return self._outputs_fmu

    def get_input_mesh(self):
        """Get the input mesh."""
        return self._input_mesh

    def get_output_mesh(self):
        """Get the output mesh."""
        return self._output_mesh

    def get_model(self):
        """Get the fmi model."""
        return self._model


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

    initialization_script : str, default=None
        Path to the initialization script.

    start_time : float, default=None
        The FMU simulation start time.
        The default behavior is to use the default start time defined the FMU.

    final_time : float, default=None
        The FMU simulation stop time.
        The default behavior is to use the default stop time defined the FMU.

    kind : str, one of "ME" (model exchange) or "CS", default=None
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
        kind=None,
        initialization_script=None,
        start_time=None,
        final_time=None,
    ):
        lowlevel = OpenTURNSFMUFunction(
            path_fmu=path_fmu,
            inputs_fmu=inputs_fmu,
            outputs_fmu=outputs_fmu,
            kind=kind,
            initialization_script=initialization_script,
            start_time=start_time,
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

    initialization_script : str, default=None
        Path to the initialization script.

    start_time : float, default=None
        The FMU simulation start time.
        The default behavior is to use the default start time defined the FMU.

    final_time : float, default=None
        The FMU simulation stop time.
        The default behavior is to use the default stop time defined the FMU.

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
        initialization_script=None,
        kind=None,
        start_time=None,
        final_time=None,
        **kwargs
    ):
        self.base = _FMUBaseFunction(path_fmu, kind=kind,
                                     inputs_fmu=inputs_fmu, outputs_fmu=outputs_fmu,
                                     start_time=start_time, final_time=final_time,
                                     initialization_script=initialization_script,
                                     field_input=False, field_output=False)

        super().__init__(
            n=len(self.base.get_inputs_fmu()), p=len(self.base.get_outputs_fmu())
        )
        self.setInputDescription(self.base.get_inputs_fmu())
        self.setOutputDescription(self.base.get_outputs_fmu())

    def __call__(self, X, **kwargs):
        X = np.atleast_1d(np.squeeze(X))
        if X.ndim > 1:
            return self._exec_sample(X, **kwargs)
        else:
            return self._exec(X, **kwargs)

    def _exec(self, value_input, **kwargs):
        """Simulate the FMU for a given set of input values.

        Parameters
        ----------
        value_input : Vector or array-like with time steps as rows.

        See the 'simulate' method for additional keyword arguments.

        """

        return self.base.simulate(value_input=value_input, **kwargs)


class FMUPointToFieldFunction(ot.PointToFieldFunction):
    """
    Define a PointToFieldFunction from a FMU file.

    Parameters
    ----------
    path_fmu : str, path to the FMU file.

    mesh : :class:`openturns.Mesh`, default=None
        Time grid of the output variables, must overlap the simulation time interval defined by start_time/final_time.
        By default defined to a regular grid with the start/final time and default step defined the FMU.
        It does not override the start/final time of the simulation
        but returned values are interpolated on the simulation time grid according to the given mesh.

    inputs_fmu : Sequence of str, default=None
        Names of the variable from the fmu to be used as input variables.
        By default assigns variables with FMI causality INPUT.

    outputs_fmu : Sequence of str, default=None
        Names of the variable from the fmu to be used as output variables.
        By default assigns variables with FMI causality OUTPUT.

    initialization_script : str, default=None
        Path to the initialization script.

    kind : str, default=None
        Either "ME" (model exchange) or "CS" (co-simulation)
        Select a kind of FMU if both are available.
        Note:
        Contrary to pyfmi, the default here is "CS" (co-simulation). The
        rationale behind this choice is that co-simulation may be used to
        impose a solver not available in pyfmi.

    start_time : float, default=None
        The FMU simulation start time.
        The default behavior is to use the default start time defined the FMU.

    final_time : float, default=None
        The FMU simulation stop time.
        The default behavior is to use the default stop time defined the FMU.

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
        self.base = _FMUBaseFunction(path_fmu, kind=kind,
                                     inputs_fmu=inputs_fmu, outputs_fmu=outputs_fmu,
                                     start_time=start_time, final_time=final_time,
                                     initialization_script=initialization_script,
                                     field_input=False, field_output=True, output_mesh=mesh)

        super().__init__(
            len(self.base.get_inputs_fmu()), self.base.get_output_mesh(), len(self.base.get_outputs_fmu())
        )
        self.setInputDescription(self.base.get_inputs_fmu())
        self.setOutputDescription(self.base.get_outputs_fmu())

    def _exec(self, value_input, **kwargs):
        """Simulate the FMU for a given set of input values.

        Parameters
        ----------
        value_input : Vector or array-like with time steps as rows.

        See the 'simulate' method for additional keyword arguments.

        """

        return self.base.simulate(value_input=value_input, **kwargs)


class FMUFieldToPointFunction(ot.FieldToPointFunction):
    """
    Define a FieldToPointFunction from a FMU file.

    Parameters
    ----------
    path_fmu : str, path to the FMU file.

    mesh : :class:`openturns.Mesh`, default=None
        Time grid of the input variables, must overlap the simulation time interval defined by start_time/final_time.
        By default defined to a regular grid with the start/final time and default step defined the FMU.
        It does not override the start/final time of the simulation
        but input values are interpolated on the simulation time grid according to the given mesh.

    inputs_fmu : Sequence of str, default=None
        Names of the variable from the fmu to be used as input variables.
        By default assigns variables with FMI causality INPUT.

    outputs_fmu : Sequence of str, default=None
        Names of the variable from the fmu to be used as output variables.
        By default assigns variables with FMI causality OUTPUT.

    initialization_script : str, default=None
        Path to the initialization script.

    kind : str, default=None
        Either "ME" (model exchange) or "CS" (co-simulation)
        Select a kind of FMU if both are available.
        Note:
        Contrary to pyfmi, the default here is "CS" (co-simulation). The
        rationale behind this choice is that co-simulation may be used to
        impose a solver not available in pyfmi.

    start_time : float, default=None
        The FMU simulation start time.
        The default behavior is to use the default start time defined the FMU.

    final_time : float, default=None
        The FMU simulation stop time.
        The default behavior is to use the default stop time defined the FMU.

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
        lowlevel = OpenTURNSFMUFieldToPointFunction(
            path_fmu=path_fmu,
            mesh=mesh,
            inputs_fmu=inputs_fmu,
            outputs_fmu=outputs_fmu,
            kind=kind,
            initialization_script=initialization_script,
            start_time=start_time,
            final_time=final_time,
        )

        highlevel = ot.FieldToPointFunction(lowlevel)
        # highlevel._model = lowlevel.model
        return highlevel


class OpenTURNSFMUFieldToPointFunction(ot.OpenTURNSPythonFieldToPointFunction):
    """Define a FieldToPointFunction from a FMU file."""

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
        self.base = _FMUBaseFunction(path_fmu, kind=kind,
                                     inputs_fmu=inputs_fmu, outputs_fmu=outputs_fmu,
                                     start_time=start_time, final_time=final_time,
                                     initialization_script=initialization_script,
                                     field_input=True, input_mesh=mesh, field_output=False)

        super().__init__(
            self.base.get_input_mesh(), len(self.base.get_inputs_fmu()), len(self.base.get_outputs_fmu())
        )
        self.setInputDescription(self.base.get_inputs_fmu())
        self.setOutputDescription(self.base.get_outputs_fmu())

    def _exec(self, value_input, **kwargs):
        """Simulate the FMU for a given set of input values.

        Parameters
        ----------
        value_input : Vector or array-like with time steps as rows.

        See the 'simulate' method for additional keyword arguments.

        """
        return self.base.simulate(value_input=value_input, **kwargs)


class FMUFieldFunction(ot.FieldFunction):
    """
    Define a FieldFunction from a FMU file.

    Parameters
    ----------
    path_fmu : str, path to the FMU file.

    input_mesh : :class:`openturns.Mesh`, default=None
        Time grid of the input variables, must overlap the simulation time interval defined by start_time/final_time.
        By default defined to a regular grid with the start/final time and default step defined the FMU.
        It does not override the start/final time of the simulation
        but input values are interpolated on the simulation time grid according to the given mesh.

    output_mesh : :class:`openturns.Mesh`, default=None
        Time grid of the input variables, must overlap the simulation time interval defined by start_time,final_time.
        By default defined to a regular grid with the start/final time and default step defined the FMU.
        It does not override the start/final time of the simulation
        but returned values are interpolated on the simulation time grid according to the given mesh.

    inputs_fmu : Sequence of str, default=None
        Names of the variable from the fmu to be used as input variables.
        By default assigns variables with FMI causality INPUT.

    outputs_fmu : Sequence of str, default=None
        Names of the variable from the fmu to be used as output variables.
        By default assigns variables with FMI causality OUTPUT.

    initialization_script : str, default=None
        Path to the initialization script.

    kind : str, default=None
        Either "ME" (model exchange) or "CS" (co-simulation)
        Select a kind of FMU if both are available.
        Note:
        Contrary to pyfmi, the default here is "CS" (co-simulation). The
        rationale behind this choice is that co-simulation may be used to
        impose a solver not available in pyfmi.

    start_time : float, default=None
        The FMU simulation start time.
        The default behavior is to use the default start time defined the FMU.

    final_time : float, default=None
        The FMU simulation stop time.
        The default behavior is to use the default stop time defined the FMU.

    """

    def __new__(
        self,
        path_fmu,
        input_mesh=None,
        output_mesh=None,
        inputs_fmu=None,
        outputs_fmu=None,
        kind=None,
        initialization_script=None,
        start_time=None,
        final_time=None,
    ):
        lowlevel = OpenTURNSFMUFieldFunction(
            path_fmu=path_fmu,
            input_mesh=input_mesh,
            output_mesh=output_mesh,
            inputs_fmu=inputs_fmu,
            outputs_fmu=outputs_fmu,
            kind=kind,
            initialization_script=initialization_script,
            start_time=start_time,
            final_time=final_time,
        )

        highlevel = ot.FieldFunction(lowlevel)
        # highlevel._model = lowlevel.model
        return highlevel


class OpenTURNSFMUFieldFunction(ot.OpenTURNSPythonFieldFunction):
    """Define a FieldFunction from a FMU file."""

    def __init__(
        self,
        path_fmu,
        input_mesh=None,
        output_mesh=None,
        inputs_fmu=None,
        outputs_fmu=None,
        initialization_script=None,
        kind=None,
        start_time=None,
        final_time=None,
        **kwargs
    ):
        self.base = _FMUBaseFunction(path_fmu, kind=kind,
                                     inputs_fmu=inputs_fmu, outputs_fmu=outputs_fmu,
                                     start_time=start_time, final_time=final_time,
                                     initialization_script=initialization_script,
                                     field_input=True, input_mesh=input_mesh,
                                     output_mesh=output_mesh, field_output=True)

        super().__init__(
            self.base.get_input_mesh(), len(self.base.get_inputs_fmu()),
            self.base.get_output_mesh(), len(self.base.get_outputs_fmu())
        )
        self.setInputDescription(self.base.get_inputs_fmu())
        self.setOutputDescription(self.base.get_outputs_fmu())

    def _exec(self, value_input, **kwargs):
        """Simulate the FMU for a given set of input values.

        Parameters
        ----------
        value_input : Vector or array-like with time steps as rows.

        See the 'simulate' method for additional keyword arguments.

        """
        return self.base.simulate(value_input=value_input, **kwargs)
