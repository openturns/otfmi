# Copyright 2016-2026 EDF Phimeca

"""Low level utility functions for common FMU manipulations."""

import numpy as np
import warnings
import otfmi
from . import backend


def _model_backend_name(model=None):
    """Get the backend name bound to a model, or the active one.

    The backend is inferred from the model type (pyfmi models live in
    ``pyfmi.*`` modules, the fmpy wrapper in ``otfmi.backend.fmpy_backend``)
    or from the ``_otfmi_backend`` attribute that wrappers record at load
    time. This way switching the global backend later does not change how
    an already loaded model is simulated or introspected. pyfmi model
    objects use ``__slots__`` and accept neither attributes nor weak
    references, hence the type-based inference.
    """
    if model is not None:
        module = getattr(type(model), "__module__", "") or ""
        if module.split(".")[0] == "pyfmi":
            return "pyfmi"
        if "fmpy_backend" in module:
            return "fmpy"
        name = getattr(model, "_otfmi_backend", None)
        if name in ("pyfmi", "fmpy"):
            return name
    return backend.BACKEND


def _model_backend(model=None):
    """Get the backend module bound to a model, or the active one."""
    return backend.get_backend(_model_backend_name(model))


def _tag_model(model):
    """Record the active backend on a freshly loaded model, if possible."""
    try:
        model._otfmi_backend = backend.BACKEND
    except (AttributeError, TypeError):
        # pyfmi models use __slots__ and reject new attributes: the backend
        # is then inferred from the model type (see _model_backend_name)
        pass
    return model


def _option_key(model=None):
    """Get the keyword holding the options of the model's backend.

    Each backend exposes its own options dictionary, so that users can pass
    options for several backends at once and let the active one pick its own.
    """
    return f"{_model_backend_name(model)}_options"


def _other_option_key(model=None):
    """Get the options keyword of the backend that is not the model's."""
    return f"{'fmpy' if _model_backend_name(model) == 'pyfmi' else 'pyfmi'}_options"


def _get_causality(model=None):
    """Get causality constants from the model's backend."""
    return _model_backend(model).CAUSALITY


def _get_causality_name(model=None):
    """Get causality names from the model's backend."""
    return _model_backend(model).CAUSALITY_NAME


def _get_types(model=None):
    """Get variable types from the model's backend."""
    return _model_backend(model).TYPES


def get_fmi_version(model):
    """Get the FMI version of an FMU.

    Parameters
    ----------
    model : pyfmi.fmi.FMUModelBase or str
        Pyfmi model object or path to an FMU.

    Returns
    -------
    version : str
        FMI version, one of "1.0", "2.0", "3.0" (depending on the backend).
    """

    if not hasattr(model, "get_version"):
        model = load_fmu(model)

    version = model.get_version()
    causality = _get_causality(model)
    if version not in causality:
        raise ValueError(f"Unsupported FMI version {version} (supported versions:"
                         f" {', '.join(causality)})")
    return version


def get_causality_input(model):
    """Get the causality identifier of input variables.

    Parameters
    ----------
    model : pyfmi.fmi.FMUModelBase
        Pyfmi model object

    Returns
    -------
    causality : int
        FMI1: INPUT(0)
        FMI2: INPUT(2)
        FMI3: INPUT(3)
    """

    return _get_causality(model)[get_fmi_version(model)]["input"]


def get_causality_output(model):
    """Get the causality identifier of output variables.

    Parameters
    ----------
    model : pyfmi.fmi.FMUModelBase
        Pyfmi model object

    Returns
    -------
    causality : int
        FMI1: OUTPUT(1)
        FMI2: OUTPUT(3)
        FMI3: OUTPUT(4)
    """

    return _get_causality(model)[get_fmi_version(model)]["output"]


def get_causality_parameter(model):
    """Get the causality identifier of parameter variables.

    Parameters
    ----------
    model : pyfmi.fmi.FMUModelBase
        Pyfmi model object

    Returns
    -------
    causality : int or None
        FMI1: None, as FMI 1.0 has no such causality
        FMI2: PARAMETER(0)
        FMI3: PARAMETER(1)
    """

    return _get_causality(model)[get_fmi_version(model)]["parameter"]


def get_causality_local(model):
    """Get the causality identifier of local variables.

    Parameters
    ----------
    model : pyfmi.fmi.FMUModelBase
        Pyfmi model object

    Returns
    -------
    causality : int or None
        FMI1: None, as FMI 1.0 has no such causality
        FMI2: LOCAL(4)
        FMI3: LOCAL(5)
    """

    return _get_causality(model)[get_fmi_version(model)]["local"]


def load_fmu(path_fmu, kind=None, **kwargs):
    """Load an FMU.

    Parameters
    ----------
    path_fmu : str or path-like
        Path to the FMU file.

    kind : str, one of "ME" (model exchange) or "CS" (co-simulation)
        select a kind of FMU if both are available.
        Note:
        Contrary to pyfmi, the default here is "CS" (co-simulation). The
        rationale behind this choice is that co-simulation may be used to
        impose a solver not available in pyfmi.

    Additional keyword arguments are passed on to the backend's 'load_fmu'
    function.

    """
    return _tag_model(backend.load_fmu(path_fmu, kind=kind, **kwargs))


def load_unzipped_fmu(path_fmu, kind=None, **kwargs):
    """Load an unzipped FMU.

    The FMI version and the kind of FMU are read from the modelDescription.xml
    file, as pyfmi requires the matching model class to be picked explicitly.

    Parameters
    ----------
    path_fmu : str or path-like
        Path to the directory of an unzipped FMU.

    kind : str, one of "ME" (model exchange) or "CS" (co-simulation)
        select a kind of FMU if both are available.
        Note:
        Contrary to pyfmi, the default here is "CS" (co-simulation). The
        rationale behind this choice is that co-simulation may be used to
        impose a solver not available in pyfmi.

    Additional keyword arguments are passed on to the backend.

    """
    return _tag_model(backend.load_unzipped_fmu(path_fmu, kind=kind, **kwargs))


def read_unzipped_model_description(path_fmu):
    """Read the FMI version and kind of an unzipped FMU.

    Parameters
    ----------
    path_fmu : str or path-like
        Path to the directory of an unzipped FMU.

    Returns
    -------
    version : str
        FMI version, as declared in modelDescription.xml.

    kind : str
        Either "ME" (model exchange) or "CS" (co-simulation). Co-simulation
        takes precedence when the FMU provides both.
    """
    return backend.read_unzipped_model_description(path_fmu)


def simulate(
    model,
    initialization_script=None,
    initialization_parameters=None,
    reset=True,
    **kwargs
):
    """Simulate an FMU.

    Parameters
    ----------
    model : pyfmi.fmi.FMUModelBase or backend model object
        Model object, as returned by :func:`load_fmu`.

    initialization_script : path-like
        Path to the script file.

    initialization_parameters : tuple of str/float pairs
        tuple of keys/values to initialize parameters

    reset : bool
        Toggle resetting the FMU prior to simulation. True by default.

    pyfmi_options, fmpy_options : dict
        Backend-specific simulation options. Only the dictionary matching the
        model's backend is forwarded; the other one is discarded.

    Additional keyword arguments are passed on to the backend's simulate.

    """
    # keep only the options of the model's backend, and rename them to whatever
    # the underlying model expects: pyfmi spells it "options", whereas the fmpy
    # wrapper reads "fmpy_options"
    backend_name = _model_backend_name(model)
    active, inactive = _option_key(model), _other_option_key(model)
    kwargs.pop(inactive, None)
    options = kwargs.pop(active, None)
    if options is not None:
        target = "options" if backend_name == "pyfmi" else "fmpy_options"
        if backend_name == "pyfmi":
            legacy = kwargs.pop("options", None)
            if legacy is not None:
                options = {**legacy, **options}
        kwargs[target] = options

    if reset:
        model.reset()
        # Needed (?!) for restoring default values in some settings (windows
        # co-simulation).
        try:
            model.free_instance()
            model.instantiate()
        except AttributeError:
            pass  # Probably FMI version 1.
    try:
        apply_initialization_script(model, initialization_script)
    except TypeError:
        pass

    if initialization_parameters is not None:
        apply_initialization_parameters(model, initialization_parameters)

    return model.simulate(**kwargs)


def parse_kwargs_simulate(
    value_input=None, name_input=None, name_output=None, model=None, **kwargs
):
    """Parse simulation keyword arguments and feed the
    simulate method of the backend's object.

    Parameters
    ----------
    value_input : Vector or array-like with time steps as rows.

    name_input : Sequence of string
        input names.

    name_output : Sequence of string
        output names

    model : pyfmi.FMUModel*
        fmu model.

    pyfmi_options : dict
        Options forwarded to pyfmi's simulate method. Ignored if the model's
        backend is not pyfmi.

    fmpy_options : dict
        Options forwarded to fmpy's simulate_fmu function. Ignored if the
        model's backend is not fmpy.
    """

    value_input_array = reshape_input(value_input, len(name_input))
    time, kwargs = guess_time(value_input_array, **kwargs)

    version = get_fmi_version(model)

    # Backend-specific simulation options. Users pass pyfmi_options and/or
    # fmpy_options; only the ones matching the model's backend are forwarded.
    backend_name = _model_backend_name(model)
    key = _option_key(model)
    kwargs.pop(_other_option_key(model), None)
    options = dict(kwargs.pop(key, dict()))

    if backend_name == "pyfmi":
        # store only variables of interest
        options.setdefault("filter", name_output)

        if version != "3.0":
            # store results in memory instead of binary file, cleaner and a bit
            # faster (pyfmi cannot store FMI 3.0 results in memory)
            options.setdefault("result_handling", "memory")

        # only available for CS model
        if "FMUModelCS" in model.__class__.__name__:
            options.setdefault("silent_mode", True)
    else:
        # fmpy spells the output filter 'output'
        options.setdefault("output", name_output)

    kwargs[key] = options

    if len(time) > 1:
        kwargs.setdefault("start_time", time[0])
        kwargs.setdefault("final_time", time[-1])

    if value_input is not None:
        fmix_input = get_causality_input(model)
        fmix_parameter = get_causality_parameter(model)

        # remap desired variables to fmi inputs/parameters:
        causality = dict(zip(name_input, get_causality(model, name_input)))
        name_input_fmi = [var for var in name_input if causality[var] == fmix_input]

        # 1. PARAMETER variables must be set using model.set (initialization_parameters)
        if fmix_parameter is not None:
            name_parameter_fmi = [
                var for var in name_input if causality[var] == fmix_parameter
            ]
            indices_parameter_fmi = [
                i
                for i in range(len(name_input))
                if causality[name_input[i]] == fmix_parameter
            ]
            value_parameter_fmi = [value_input[k] for k in indices_parameter_fmi]
            if len(name_parameter_fmi) > 0:
                kwargs["initialization_parameters"] = (
                    name_parameter_fmi,
                    value_parameter_fmi,
                )

        # 2. INPUT variables values are passed with model.simulate (input)
        indices_input_fmi = [
            i for i in range(len(name_input)) if causality[name_input[i]] == fmix_input
        ]
        if value_input_array.ndim == 1:
            value_input_fmi = value_input_array[indices_input_fmi]
        else:  # 2-d array
            value_input_fmi = value_input_array[:, indices_input_fmi]
        if len(name_input_fmi) > 0:
            kwargs["input"] = (name_input_fmi, np.column_stack((time, value_input_fmi)))

    return kwargs


def strip_simulation(simulation, name_output, final=None):
    """Extract some final values or trajectories from a simulation result.

    Parameters
    ----------
    simulation : simulation result object
        Backend-specific simulation result.

    name_output : Sequence of strings, output variables names.

    final : String
        If "final" (default), return only final values instead of whole
        trajectories.
        If "result" return the result object.
        If "trajectory" returns outputs trajectories.

    """

    if final is None:
        final = "final"

    if final == "final":
        return [simulation.final(name) for name in name_output]
    elif final == "result":
        return simulation
    elif final == "trajectory":
        return (
            simulation["time"],
            np.column_stack([simulation[name] for name in name_output]),
        )
    else:
        raise ValueError("Unexpected value for the 'final' parameter: '%s'." % final)


def reshape_input(value_input, input_dimension):
    """Ensure appropriate number of dimensions for input data.
    Note: only the dimension is affected. The exact shape is not checked.

    Parameters
    ----------
    value_input : Sequence or array of data.

    input_dimension : Integer, number of input variables.

    """

    if value_input is None:
        return None

    if input_dimension > 1:
        return np.atleast_2d(value_input)
    else:
        return np.atleast_1d(value_input)


def guess_time(value_input, **kwargs):
    """Guess the time vector from input data.

    Parameters
    ----------
    value_input : Pandas dataframe with a time index or array-like with
    timesteps as rows.

    time : Sequence of floats, time vector (optional).

    timestep : Float, timestep in seconds (optional).

    """

    try:
        time = kwargs.pop("time")
    except KeyError:
        if value_input is None:
            return None, kwargs

        timestep = kwargs.pop("timestep", 1.0)
        try:
            # Is value_input a time-indexed pandas dataframe?
            time_index = list(value_input.values())[0].index
        except AttributeError:
            # value_input is array-like.
            time = np.arange(len(value_input)) * timestep
        else:
            time = (time_index - time_index[0]).total_seconds()
    return time, kwargs


def parse_initialization_line(line):
    """Parse one line of a Dymola initialization script.

    Parameters
    ----------
    line : String, line to parse.

    """

    # TODO: use a custom error for better discrimination in catching.
    name, value = line.split("=")
    name = name.strip()
    value = value.split(";")[0]
    try:
        value = float(value)
    except ValueError:
        try:
            value = {"true": True, "false": False}[value.lower()]
        except KeyError:
            message = "The value '%s' could not be interpreted." % value
            raise ValueError(message)
    return name, value


def parse_initialization_script(path_script):
    """Parse a Dymola initialization script.

    Parameters
    ----------
    path_script : path-like
        Path to the script file.
    """

    list_name = []
    list_value = []
    with open(path_script, "r") as f:
        for line in f:
            if line.strip().startswith("//"):
                continue

            try:
                name, value = parse_initialization_line(line)
            except ValueError:
                warnings.warn(
                    "Following line could not be parsed:\n {}".format(line),
                    SyntaxWarning,
                )
            else:
                list_name.append(name)
                list_value.append(value)
    return list_name, list_value


def apply_initialization_parameters(model, initialization_parameters):
    """Apply a list of initialization parameters to a model.

    Parameters
    ----------
    model : pyfmi.fmi.FMUModelBase
        Pyfmi model object
    initialization_parameters : tuple of keys/values
    """

    list_name, list_value = initialization_parameters
    FMUException = _model_backend(model).FMUException
    try:
        model.set(list_name, list_value)
    except FMUException:
        for name, value in zip(list_name, list_value):
            try:
                model.set(name, value)
            except FMUException:
                pass


def apply_initialization_script(model, path_script):
    """Apply an initialization script to a model.

    Parameters
    ----------
    model : pyfmi.fmi.FMUModelBase
        Pyfmi model object
    path_script : path-like
        Path to the script file.
    """

    list_name, list_value = parse_initialization_script(path_script)
    apply_initialization_parameters(model, (list_name, list_value))


def get_name_variable(model, **kwargs):
    """Get the list of variable names.

    Parameters
    ----------
    model : Pyfmi model object (pyfmi.fmi.FMUModelBase) or path to an FMU.

    Returns
    -------
    var_names : list of str
        Variable names
    """

    if not hasattr(model, "get_model_variables"):
        if not isinstance(model, str):
            raise TypeError("model should be an FMU model or a str")
        path_fmu = model
        model = load_fmu(path_fmu)

    return list(model.get_model_variables(**kwargs).keys())


def get_causality(model, names=None):
    """Get the causality of the variables (input, output, or other).

    If the variable causality is "input" or "parameter", its value can be
    modified using otfmi.fmi.set_dict_value. Setting the value of a variable
    with other causality is not possible (nonphysical).

    Parameters
    ----------
    model : Pyfmi model object (pyfmi.fmi.FMUModelBase) or path to an FMU.

    names : Sequence of string, default=None
        Variable names

    Returns
    -------
    causality : list of int
        FMI1: INPUT(0), OUTPUT(1), INTERNAL(2), NONE(3), UNKNOWN(4)

        FMI2: PARAMETER(0), CALCULATED_PARAMETER(1), INPUT(2), OUTPUT(3), LOCAL(4), INDEPENDENT(5), UNKNOWN(6)

        FMI3: STRUCTURAL_PARAMETER(0), PARAMETER(1), CALCULATED_PARAMETER(2),
              INPUT(3), OUTPUT(4), LOCAL(5), INDEPENDENT(6), UNKNOWN(7)
    """

    try:
        model.get_variable_causality
    except AttributeError:
        model = load_fmu(model)

    if names is None:
        names = get_name_variable(model)

    return [model.get_variable_causality(name) for name in names]


def get_causality_str(model, name):
    """
    Get the causality of a variable (input, output, or other).

    If the variable causality is "input" or "parameter", its value can be
    modified using otfmi.fmi.set_dict_value. Setting the value of a variable
    with other causality is not possible (nonphysical).

    Parameters
    ----------
    model : pyfmi.fmi.FMUModelBase or str
        Pyfmi model object or path to an FMU.

    name : str
        Variable name

    Returns
    -------
    causality : str
        Causality identifier
    """

    causalitystr = _get_causality_name(model)[get_fmi_version(model)]
    return causalitystr.get(get_causality(model, [name])[0], "UNKNOWN")


def get_variability(model):
    """Get the variability of the variables (constant, discrete, continuous,
    or other).

    Parameters
    ----------
    model : Pyfmi model object (pyfmi.fmi.FMUModelBase) or path to an FMU.

    Returns
    -------
    variability : list of int
        FMI1: CONSTANT(0), PARAMETER(1), DISCRETE(2), CONTINUOUS(3), UNKNOWN(4)

        FMI2: CONSTANT(0), FIXED(1), TUNABLE(2), DISCRETE(3), CONTINUOUS(4), UNKNOWN(5)

        FMI3: CONSTANT(0), FIXED(1), TUNABLE(2), DISCRETE(3), CONTINUOUS(4), UNKNOWN(5)
    """

    try:
        model.get_variable_variability
    except AttributeError:
        model = load_fmu(model)

    return [model.get_variable_variability(name) for name in get_name_variable(model)]


def get_fixed_value(model):
    """Get the values of the variables with 'fixed' variability,
    ignoring aliases.

    Parameters
    ----------
    model : Pyfmi model object (pyfmi.fmi.FMUModelBase) or path to an FMU.

    """

    try:
        model.get_model_variables
    except AttributeError:
        model = load_fmu(model)

    list_name_variable = list(
        model.get_model_variables(include_alias=False, variability=1).keys()
    )
    try:
        # not available with FMI 3.0
        model.setup_experiment()
    except AttributeError:
        pass
    try:
        model.initialize()
    except _model_backend(model).FMUException:
        pass
    return {name: model.get(name) for name in list_name_variable}


def get_start_value(model):
    """Get the values of the variables with a start value ignoring aliases.

    Parameters
    ----------
    model : Pyfmi model object (pyfmi.fmi.FMUModelBase) or path to an FMU.

    Returns
    -------
    start_vars : dict of int/float
        Names and values of start variables

    """

    try:
        model.get_model_variables
    except AttributeError:
        model = load_fmu(model)

    list_name_variable = []
    # numeric and boolean types only, string-like types are filtered out
    for typ in _get_types(model)[get_fmi_version(model)]:
        lnvt = list(
            model.get_model_variables(
                type=typ, include_alias=False, only_start=True
            ).keys()
        )
        list_name_variable.extend(lnvt)

    return {name: model.get_variable_start(name) for name in list_name_variable}


def set_dict_value(model, dict_value):
    """Set values from a dictionary with variable names as keys.

    Parameters
    ----------
    model : Pyfmi model object (pyfmi.fmi.FMUModelBase) or path to an FMU.

    dict_value : Dictionary, with variable names as keys.

    """

    try:
        model.set
    except AttributeError:
        model = load_fmu(model)

    model.set(*list(zip(*list(dict_value.items()))))


def format_trajectory(model, time, trajectory, time_interpolate=None):
    """Store trajectories in a dictionary, and possibly reinterpolate them.

    Arguments:
    model -- OpenTURNSFMUFunction, simulated model.

    time -- Sequence of floats, simulation time.

    trajectory -- Array of floats, trajectories.

    time_interpolate -- Sequence of floats, time for interpolation of
    trajectories.

    """

    list_output = model.getFMUOutputDescription()

    if time_interpolate is not None:
        list_trajectory = [np.interp(time_interpolate, time, zz) for zz in trajectory.T]
    else:
        list_trajectory = list(trajectory.T)

    dict_trajectory = {key: value for key, value in zip(list_output, list_trajectory)}
    return dict_trajectory


# TODO: refactor format_sample_trajectory.
def format_sample_trajectory(model, list_output, time_interpolate=None):
    """Store samples of trajectories in a dictionary, and possibly
    reinterpolate them.

    Arguments:
    model -- OpenTURNSFMUFunction, simulated model.

    list_output -- Sequence of pairs of time (vector of floats) and
    trajectories (array of floats).

    time_interpolate -- Sequence of floats, time for interpolation of
    trajectories.

    """

    list_dict_trajectory = []
    for time, trajectory in list_output:
        list_dict_trajectory.append(
            format_trajectory(
                model, time, trajectory, time_interpolate=time_interpolate
            )
        )

    dict_trajectory_sample = dict()
    for name_output in model.getFMUOutputDescription():
        dict_trajectory_sample[name_output] = np.column_stack(
            [dd[name_output] for dd in list_dict_trajectory]
        )

    if time_interpolate is None:
        list_time, _ = zip(*list_output)
    else:
        list_time = [time_interpolate for _ in list_output]

    return list_time, dict_trajectory_sample


def simulate_trajectory(
    path_fmu,
    value_input,
    timestep,
    list_input=None,
    list_output=None,
    final_time=None,
    ncp=None,
):
    """Simulate a sample of trajectories with an FMU.

    Arguments:
    list_input -- Sequence of strings, input names.

    list_output -- Sequence of strings or single string, output names.

    path_fmu -- String, path to FMU.

    value_input -- Sequence of floats, input values.

    timestep -- Float or sequence of floats, time step or sequence of times
    for trajectory interpolation.

    final_time -- Float, simulation final time.

    """

    try:
        list_output.__iter__
    except AttributeError:
        list_output = [list_output]

    model = otfmi.OpenTURNSFMUFunction(
        path_fmu=path_fmu, inputs_fmu=list_input, outputs_fmu=list_output
    )
    model._OpenTURNSFMUFunction__final = "trajectory"

    try:
        timestep.__iter__
    except AttributeError:
        time_interpolate = np.linspace(0, final_time, final_time / float(timestep))
    else:
        time_interpolate = timestep
        final_time = time_interpolate[-1]

    options = dict()
    if ncp is not None:
        options["ncp"] = ncp

    out = model.simulate_sample(
        list_value_input=value_input, final_time=final_time, options=options
    )
    list_time, dict_trajectory = format_sample_trajectory(model, out, time_interpolate)
    time = list_time[0]
    return time, dict_trajectory
