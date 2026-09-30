# Copyright 2016-2025 EDF Phimeca

"""Low level utility functions for common FMU manipulations."""

import io
from pathlib import Path
import re
import pyfmi
import numpy as np
import warnings
import otfmi

try:
    from pyfmi import fmi3 as _fmi3
except ImportError:  # pragma: no cover
    # pyfmi release without FMI 3.0 support
    _fmi3 = None


# Causality identifiers, per FMI version and per role. FMI 1.0 defines neither
# the "parameter" nor the "local" causality.
_CAUSALITY = {
    "1.0": {"input": pyfmi.fmi.FMI_INPUT,
            "output": pyfmi.fmi.FMI_OUTPUT,
            "parameter": None,
            "local": None},
    "2.0": {"input": pyfmi.fmi.FMI2_INPUT,
            "output": pyfmi.fmi.FMI2_OUTPUT,
            "parameter": pyfmi.fmi.FMI2_PARAMETER,
            "local": pyfmi.fmi.FMI2_LOCAL},
}

# Causality names, per FMI version.
_CAUSALITY_NAME = {
    "1.0": {pyfmi.fmi.FMI_INPUT: "INPUT",
            pyfmi.fmi.FMI_OUTPUT: "OUTPUT",
            pyfmi.fmi.FMI_INTERNAL: "INTERNAL",
            pyfmi.fmi.FMI_NONE: "NONE"},
    "2.0": {pyfmi.fmi.FMI2_PARAMETER: "PARAMETER",
            pyfmi.fmi.FMI2_CALCULATED_PARAMETER: "CALCULATED_PARAMETER",
            pyfmi.fmi.FMI2_INPUT: "INPUT",
            pyfmi.fmi.FMI2_OUTPUT: "OUTPUT",
            pyfmi.fmi.FMI2_LOCAL: "LOCAL",
            pyfmi.fmi.FMI2_INDEPENDENT: "INDEPENDENT",
            pyfmi.fmi.FMI2_UNKNOWN: "UNKNOWN"},
}

# Numeric and boolean variable types, per FMI version. String-like types are
# left out as their start values cannot be converted to float.
_TYPES = {
    "1.0": [pyfmi.fmi.FMI_REAL, pyfmi.fmi.FMI_INTEGER, pyfmi.fmi.FMI_BOOLEAN],
    "2.0": [pyfmi.fmi.FMI2_REAL, pyfmi.fmi.FMI2_INTEGER, pyfmi.fmi.FMI2_BOOLEAN],
}

# pyfmi model classes, per FMI version and per kind.
_MODEL_CLASS = {
    ("1.0", "CS"): pyfmi.fmi.FMUModelCS1,
    ("1.0", "ME"): pyfmi.fmi.FMUModelME1,
    ("2.0", "CS"): pyfmi.fmi.FMUModelCS2,
    ("2.0", "ME"): pyfmi.fmi.FMUModelME2,
}

if _fmi3 is not None:
    _CAUSALITY["3.0"] = {"input": _fmi3.FMI3_Causality.INPUT,
                         "output": _fmi3.FMI3_Causality.OUTPUT,
                         "parameter": _fmi3.FMI3_Causality.PARAMETER,
                         "local": _fmi3.FMI3_Causality.LOCAL}
    _CAUSALITY_NAME["3.0"] = {
        _fmi3.FMI3_Causality.STRUCTURAL_PARAMETER: "STRUCTURAL_PARAMETER",
        _fmi3.FMI3_Causality.PARAMETER: "PARAMETER",
        _fmi3.FMI3_Causality.CALCULATED_PARAMETER: "CALCULATED_PARAMETER",
        _fmi3.FMI3_Causality.INPUT: "INPUT",
        _fmi3.FMI3_Causality.OUTPUT: "OUTPUT",
        _fmi3.FMI3_Causality.LOCAL: "LOCAL",
        _fmi3.FMI3_Causality.INDEPENDENT: "INDEPENDENT",
        _fmi3.FMI3_Causality.UNKNOWN: "UNKNOWN"}
    _TYPES["3.0"] = [_fmi3.FMI3_Type.FLOAT64, _fmi3.FMI3_Type.FLOAT32,
                     _fmi3.FMI3_Type.INT64, _fmi3.FMI3_Type.INT32,
                     _fmi3.FMI3_Type.INT16, _fmi3.FMI3_Type.INT8,
                     _fmi3.FMI3_Type.UINT64, _fmi3.FMI3_Type.UINT32,
                     _fmi3.FMI3_Type.UINT16, _fmi3.FMI3_Type.UINT8,
                     _fmi3.FMI3_Type.BOOL]
    _MODEL_CLASS[("3.0", "CS")] = _fmi3.FMUModelCS3
    _MODEL_CLASS[("3.0", "ME")] = _fmi3.FMUModelME3


def get_fmi_version(model):
    """Get the FMI version of an FMU.

    Parameters
    ----------
    model : pyfmi.fmi.FMUModelBase or str
        Pyfmi model object or path to an FMU.

    Returns
    -------
    version : str
        FMI version, one of "1.0", "2.0", "3.0" (depending on pyfmi).
    """

    if not hasattr(model, "get_version"):
        model = load_fmu(model)

    version = model.get_version()
    if version not in _CAUSALITY:
        raise ValueError(f"Unsupported FMI version {version} (supported versions:"
                         f" {', '.join(_CAUSALITY)})")
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

    return _CAUSALITY[get_fmi_version(model)]["input"]


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

    return _CAUSALITY[get_fmi_version(model)]["output"]


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

    return _CAUSALITY[get_fmi_version(model)]["parameter"]


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

    return _CAUSALITY[get_fmi_version(model)]["local"]


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

    Additional keyword arguments are passed on to pyfmi's 'load_fmu' function.

    """

    # pyfmi writes a log file in current folder even with log_level=0
    kwargs.setdefault("log_file_name", io.StringIO())

    p_fmu = str(Path(path_fmu).resolve())
    if kind is None:
        try:
            return pyfmi.load_fmu(p_fmu, kind="CS", **kwargs)
        except pyfmi.fmi.FMUException:
            return pyfmi.load_fmu(p_fmu, kind="auto", **kwargs)
    else:
        return pyfmi.load_fmu(p_fmu, kind=kind, **kwargs)


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

    Additional keyword arguments are passed on to the pyfmi model constructor.

    """

    # pyfmi writes a log file in current folder even with log_level=0
    kwargs.setdefault("log_file_name", io.StringIO())
    kwargs.setdefault("allow_unzipped_fmu", True)

    version, fmu_kind = read_unzipped_model_description(path_fmu)
    if kind is None:
        kind = fmu_kind
    try:
        model_class = _MODEL_CLASS[(version, kind)]
    except KeyError:
        raise ValueError(f"Unsupported FMI version {version} combined with kind"
                         f" {kind}")
    return model_class(fmu=str(path_fmu), **kwargs)


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

    xml_file = Path(path_fmu) / "modelDescription.xml"
    if not xml_file.is_file():
        raise FileNotFoundError(f"{xml_file} not found, it does not look like an"
                                f" unzipped FMU")

    # the file is scanned line by line instead of being parsed as XML: only the
    # fmiVersion attribute and the FMU type elements are looked for
    version, kind = None, None
    with open(xml_file, encoding="utf-8") as xmlf:
        for line in xmlf:
            if version is None:
                match = re.search(r"""fmiVersion\s*=\s*['"]([^'"]*)['"]""", line)
                if match:
                    version = match.group(1)
            if "<CoSimulation" in line:
                kind = "CS"
                break
            if "<ModelExchange" in line:
                # keep scanning: co-simulation takes precedence when the FMU
                # declares both kinds, as the schemas list ModelExchange first
                kind = "ME"
    if kind is None:
        raise ValueError(f"Cannot guess FMU type from {xml_file}")
    return version, kind


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
    model : pyfmi.fmi.FMUModelBase
        Pyfmi model object

    initialization_script : path-like
        Path to the script file.

    initialization_parameters : tuple of str/float pairs
        tuple of keys/values to initialize parameters

    reset : bool
        Toggle resetting the FMU prior to simulation. True by default.

    Additional keyword arguments are passed on to pyfmi.simulate.

    """
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
    simulate method of pyfmi's object.

    Parameters
    ----------
    value_input : Vector or array-like with time steps as rows.

    name_input : Sequence of string
        input names.

    name_output : Sequence of string
        output names

    model : pyfmi.FMUModel*
        fmu model.
    """

    value_input_array = reshape_input(value_input, len(name_input))
    time, kwargs = guess_time(value_input_array, **kwargs)

    version = get_fmi_version(model)

    options = kwargs.pop("dict_option", dict())

    # store only interest variables
    options.setdefault("filter", name_output)

    if version != "3.0":
        # store results in memory instead of binary file, cleaner and a bit
        # faster (pyfmi cannot store FMI 3.0 results in memory)
        options.setdefault("result_handling", "memory")

    # only available for CS model
    if "FMUModelCS" in model.__class__.__name__:
        options.setdefault("silent_mode", True)

    kwargs["options"] = options

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
    """Extract some final values or trajectories from a PyFMI result object.

    Parameters
    ----------
    simulation : PyFMI result object (pyfmi.fmi_algorithm_drivers.FMIResult),
    simulation result.

    name_output : Sequence of strings, output variables names.

    final : String
        If "final" (default), return only final values instead of whole
        trajectories.
        If "result" return the pyfmi "result" object.
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
    try:
        model.set(list_name, list_value)
    except pyfmi.fmi.FMUException:
        for name, value in zip(list_name, list_value):
            try:
                model.set(name, value)
            except pyfmi.fmi.FMUException:
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

    causalitystr = _CAUSALITY_NAME[get_fmi_version(model)]
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
    except pyfmi.fmi.FMUException:
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
    for typ in _TYPES[get_fmi_version(model)]:
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
