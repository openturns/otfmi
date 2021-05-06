# -*- coding: utf-8 -*-
# Copyright 2016 EDF. This software was developed with the collaboration of
# Phimeca Engineering (Sylvain Girard, girard@phimeca.com).
"""Utility functions for common FMU manipulations."""
#§
import pyfmi
import numpy as np
from distutils.version import LooseVersion
import os
import tempfile

#§
def load_fmu(path_fmu, kind=None, **kwargs):
    """Load and FMU.

    Parameters
    ----------
    path_fmu : String, path to the FMU file.

    kind : String, one of "ME" (model exchange) or "CS" (co-simulation)
        select a kind of FMU if both are available.
        Note:
        Contrary to pyfmi, the default here is "CS" (co-simulation). The
        rationale behind this choice is is that co-simulation may be used to
        impose a solver not available in pyfmi.

    Additional keyword arguments are passed on to pyfmi's 'load_fmu' function.

    """

    # pyfmi writes a log in current folder even with log_level=0
    log_file_name = "" if os.access('.', os.W_OK) else os.path.join(tempfile.gettempdir(), os.path.basename(path_fmu) + '_log.txt')

    if kind is None:
        try:
            return pyfmi.load_fmu(path_fmu, kind="CS", log_file_name=log_file_name)
        except pyfmi.fmi.FMUException:
            return pyfmi.load_fmu(path_fmu, kind="auto", log_file_name=log_file_name)
    else:
        return pyfmi.load_fmu(path_fmu, kind=kind, log_file_name=log_file_name)


#§
def simulate(model, initialization_script=None, initialization_parameters=None, reset=True, **kwargs):
    """Simulate an FMU.

    Parameters
    ----------
    model : Pyfmi model object (pyfmi.fmi.FMUModelXXX).

    initialization_script : String, path to the script file.

    initialization_parameters : tuple of keys/values to initialize parameters

    reset : Boolean
        Toggle resetting the FMU prior to simulation. True by default.

    Additional keyword arguments are passed on to pyfmi.simulate.

    """
    if reset:
        model.reset()
        # Needed (?!) for restoring default values in some settings (windows
        # co-simulation).
        try:
            model.instantiate()
        except AttributeError:
            pass # Probably FMI version 1.
    try:
        apply_initialization_script(model, initialization_script)
    except TypeError:
        pass

    if initialization_parameters is not None:
        apply_initialization_parameters(model, initialization_parameters)

    return model.simulate(**kwargs)

#§
def parse_kwargs_simulate(value_input=None, name_input=None,
                          name_output=None,
                          model=None, **kwargs):
    """Parse simulation key-word arguments and arrange for feeding the
    simulate method of pyfmi's model objects.

    Parameters
    ----------
    value_input : Vector or array-like with time steps as rows.

    name_input : Sequence of string, input names.

    name_output : Sequence of string, output names.

    model : fmu model.
    """

    value_input_array = reshape_input(value_input, len(name_input))
    time, kwargs = guess_time(value_input_array, **kwargs)

    kwargs.setdefault("options", kwargs.pop("dict_option", dict())) # alias.
    kwargs["options"]["filter"] = name_output

    # https://github.com/modelon-community/PyFMI/commit/df8228d4d97cfde3cd3fc321a4f3da31b417d4be
    # only available for CS model
    if (LooseVersion(pyfmi.__version__)  >= '2.6') and ('FMUModelCS' in model.__class__.__name__):
        kwargs["options"]["silent_mode"] = True

    try:
        kwargs.setdefault("start_time", time[0])
        kwargs.setdefault("final_time", time[-1])
    except TypeError:
        pass

    if value_input is not None:
        fmix_input = pyfmi.fmi.FMI2_INPUT if model.get_version() == '2.0' else pyfmi.fmi.FMI_INPUT

        # remap desired variables to fmi inputs/parameters:
        causality = dict(zip(name_input, get_causality(model, name_input)))
        name_input_fmi = [var for var in name_input if causality[var] == fmix_input]

        # 1. PARAMETER variables must be set using model.set (initialization_parameters)
        if model.get_version() == '2.0':
            name_parameter_fmi = [var for var in name_input if causality[var] == pyfmi.fmi.FMI2_PARAMETER]
            indices_parameter_fmi = [i for i in range(len(name_input)) if causality[name_input[i]] == pyfmi.fmi.FMI2_PARAMETER]
            value_parameter_fmi = [value_input[k] for k in indices_parameter_fmi]
            if len(name_parameter_fmi) > 0:
                kwargs["initialization_parameters"] = (name_parameter_fmi, value_parameter_fmi)

        # 2. INPUT variables values are passed with model.simulate (input)
        indices_input_fmi = [i for i in range(len(name_input)) if causality[name_input[i]] == fmix_input]
        value_input_fmi = [value_input[k] for k in indices_input_fmi]
        value_input_fmi = reshape_input(value_input_fmi, len(name_input_fmi))
        if len(name_input_fmi) > 0:
            kwargs["input"] = (name_input_fmi, np.column_stack((time, value_input_fmi)))

    # pyfmi writes a result file in current folder
    if not os.access('.', os.W_OK):
        kwargs['options']['result_file_name'] = os.path.join(tempfile.gettempdir(), model.get_identifier() + '_result.mat')

    return kwargs

#§
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
        return (simulation["time"],
                np.column_stack([simulation[name] for name in name_output]))
    else:
        raise ValueError("Unexpected value for the 'final' parameter: '%s'." %
                         final)

#§
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

        timestep = kwargs.pop("timestep", 1.)
        try:
            # Is value_input a time-indexed pandas dataframe?
            time_index = list(value_input.values())[0].index
        except AttributeError:
            # value_input is array-like.
            time = np.arange(len(value_input)) * timestep
        else:
            time = (time_index - time_index[0]).total_seconds()
    return time, kwargs


#§
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
            value = {"true":True, "false":False}[value.lower()]
        except KeyError:
            message = "The value '%s' could not be interpreted." % value
            raise ValueError(message)
    return name, value

def parse_initialization_script(path_script):
    """Parse a Dymola initialization script.

    Parameters
    ----------
    path_script : String, path to the script file.

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
                pass
            else:
                list_name.append(name)
                list_value.append(value)
    return list_name, list_value


def apply_initialization_parameters(model, initialization_parameters):
    """Apply a list of initialization parameters to a model.

    Parameters
    ----------
    model : Pyfmi model object (pyfmi.fmi.FMUModelXXX).

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
    model : Pyfmi model object (pyfmi.fmi.FMUModelXXX).

    path_script : String, path to the script file.

    """

    list_name, list_value = parse_initialization_script(path_script)
    apply_initialization_parameters((list_name, list_value))

#§
def get_name_variable(model, **kwargs):
    """Get the list of variable names.

    Parameters
    ----------
    model : Pyfmi model object (pyfmi.fmi.FMUModelXXX) or path to an FMU.

    Returns
    -------
    var_names : list of str
        Variable names
    """

    try:
        model.get_model_variables
    except AttributeError:
        model = load_fmu(model)

    return list(model.get_model_variables(**kwargs).keys())

def get_causality(model, names=None):
    """Get the causality of the variables.

    Parameters
    ----------
    model : Pyfmi model object (pyfmi.fmi.FMUModelXXX) or path to an FMU.

    names : Sequence of string, default=None
        Variable names

    Returns
    -------
    causality : list of int
        FMI1: INPUT(0), OUTPUT(1), INTERNAL(2), NONE(3), UNKNOWN(4)

        FMI2: PARAMETER(0), CALCULATED_PARAMETER(1), INPUT(2), OUTPUT(3), LOCAL(4), INDEPENDENT(5), UNKNOWN(6)
    """

    try:
        model.get_variable_causality
    except AttributeError:
        model = load_fmu(model)

    if names is None:
        names = get_name_variable(model)

    return [model.get_variable_causality(name) for name in names]


def get_variability(model):
    """Get the variability of the variables.

    Parameters
    ----------
    model : Pyfmi model object (pyfmi.fmi.FMUModelXXX) or path to an FMU.

    Returns
    -------
    variability : list of int
        FMI1: CONSTANT(0), PARAMETER(1), DISCRETE(2), CONTINUOUS(3), UNKNOWN(4)

        FMI2: CONSTANT(0), FIXED(1), TUNABLE(2), DISCRETE(3), CONTINUOUS(4), UNKNOWN(5)
    """

    try:
        model.get_variable_variability
    except AttributeError:
        model = load_fmu(model)

    return [model.get_variable_variability(name) for name in
            get_name_variable(model)]


#§
def get_fixed_value(model):
    """Get the values of the variables with 'fixed' variability,
    ignoring aliases.

    Parameters
    ----------
    model : Pyfmi model object (pyfmi.fmi.FMUModelXXX) or path to an FMU.

    """

    try:
        model.get_model_variables
    except AttributeError:
        model = load_fmu(model)

    list_name_variable = list(model.get_model_variables(include_alias=False,
                                                   variability=1).keys())
    try:
        model.setup_experiment()
        model.initialize()
    except pyfmi.fmi.FMUException:
        pass
    return {name:model.get(name) for name in list_name_variable}



def get_start_value(model):
    """Get the values of the variables with a start value ignoring aliases.

    Parameters
    ----------
    model : Pyfmi model object (pyfmi.fmi.FMUModelXXX) or path to an FMU.

    Returns
    -------
    start_vars : dict of float
        Values of start variables

    """

    try:
        model.get_model_variables
    except AttributeError:
        model = load_fmu(model)

    list_name_variable = list(model.get_model_variables(include_alias=False,
                                                   only_start=True).keys())
    return {name:model.get_variable_start(name) for name in list_name_variable}


#§
def set_dict_value(model, dict_value):
    """Set values from a dictionary with variable names as keys.

    Parameters
    ----------
    model : Pyfmi model object (pyfmi.fmi.FMUModelXXX) or path to an FMU.

    dict_value : Dictionary, with variable names as keys.

    """

    try:
        model.set
    except AttributeError:
        model = load_fmu(model)

    model.set(*list(zip(*list(dict_value.items()))))

#§
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
        list_trajectory = [np.interp(time_interpolate, time, zz) for zz in
                           trajectory.T]
    else:
        list_trajectory = list(trajectory.T)

    dict_trajectory = {key:value for key, value in
                       zip(list_output, list_trajectory)}
    return dict_trajectory

#§
#TODO: refactor format_sample_trajectory.
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
        list_dict_trajectory.append(format_trajectory(
            model, time, trajectory, time_interpolate=time_interpolate))

    dict_trajectory_sample = dict()
    for name_output in model.getFMUOutputDescription():
        dict_trajectory_sample[name_output] = np.column_stack(
            [dd[name_output] for dd in list_dict_trajectory])

    if time_interpolate is None:
        list_time, _ = zip(*list_output)
    else:
        list_time = [time_interpolate for _ in list_output]

    return list_time, dict_trajectory_sample


#§
def simulate_trajectory(path_fmu, value_input, timestep,
                        list_input=None, list_output=None,
                        final_time=None, ncp=None):
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

    model = otfmi.OpenTURNSFMUFunction(path_fmu=path_fmu,
                                       inputs_fmu=list_input,
                                       outputs_fmu=list_output)
    model._OpenTURNSFMUFunction__final = "trajectory"
    model._OpenTURNSFMUFunction__expect_trajectory = False # False is the default

    try:
        timestep.__iter__
    except AttributeError:
        time_interpolate = np.linspace(0, final_time,
                                       final_time / float(timestep))
    else:
        time_interpolate = timestep
        final_time = time_interpolate[-1]


    options = dict()
    if ncp is not None:
        options["ncp"] = ncp

    out = model.simulate_sample(list_value_input=value_input,
                                final_time=final_time,
                                options=options)
    list_time, dict_trajectory = format_sample_trajectory(
        model, out, time_interpolate)
    time = list_time[0]
    return time, dict_trajectory



#§
