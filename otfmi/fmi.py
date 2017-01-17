# -*- coding: utf-8 -*-
# Copyright 2016 EDF. This software was developed with the collaboration of
# Phimeca Engineering (Sylvain Girard, girard@phimeca.com).
"""Utility functions for common FMU manipulations."""
#§
import pyfmi
import numpy as np

#§
def simulate(model, initialization_script=None, reset=True, **kwargs):
    """Simulate an FMU.

    Parameters:
    ----------
    model : Pyfmi model object (pyfmi.fmi.FMUModelXXX).

    initialization_script : String, path to the script file.

    reset : Boolean, toggle reseting the FMU prior to simulation. True by
    default.

    Additional keyword arguments are parsed by parse_kwargs_simulate.

    """
    if reset:
        model.reset()

    try:
        apply_initialization_script(model, initialization_script)
    except TypeError:
        pass

    return model.simulate(**kwargs)

#§
def parse_kwargs_simulate(value_input=None, name_input=None,
                          dimension_input=None, name_output=None,
                          final=True, **kwargs):
    """Parse simulation key-word arguments and arrange for feeding the
    simulate method of pyfmi's model objects.

    Parameters:
    ----------
    value_input : Vector or array-like with time steps as rows.

    name_input : Sequence of string, input names.

    dimension_input : Integer, number of inputs.

    name_output : Sequence of string, output names.

    final : Boolean, if True (default), return only final values instead of
    whole trajectories.


    Additional (optional) keyword arguments:
    ----------------------------------------
    time : Sequence of floats, time vector.

    timestep : Float, timestep in seconds.

    n_timestep : Integer, number of timesteps.

    options : Dictionary, see pyfmi .simulate method.


    """

    value_input = reshape_input(value_input, dimension_input)
    time, kwargs = guess_time(value_input, **kwargs)

    kwargs.setdefault("options", kwargs.pop("dict_option", dict())) # alias.
    kwargs["options"]["filter"] = name_output

    default_n_timestep = (np.alen(time), 1)[final]
    kwargs["options"]["ncp"] = kwargs.pop("n_timestep", default_n_timestep)

    if value_input is not None:
        kwargs["input"] = (name_input, np.column_stack((time, value_input)))

    return kwargs

#§
def strip_simulation(simulation, name_output, final):
    """Extract some final values or trajectories from a PyFMI result object.

    Parameters:
    ----------
    simulation : PyFMI result object (pyfmi.fmi_algorithm_drivers.FMIResult),
    simulation result.

    name_output : Sequence of strings, output variables names.

    final : Boolean, if True (default), return only final values instead of
    whole trajectories.

    """

    if final:
        return [simulation.final(name) for name in name_output]
    else:
        raise NotImplementedError, "Only final==True is supported."
        return (simulation["time"],
                np.column_stack([simulation[name] for name in name_output]))


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

    Additional (optional) keyword arguments:
    ----------------------------------------
    time : Sequence of floats, time vector.

    timestep : Float, timestep in seconds.

    """

    try:
        time = kwargs.pop("time")
    except KeyError:
        if value_input is None:
            return None, kwargs

        timestep = kwargs.pop("timestep", 1.)
        try:
            # Is it a time-indexed pandas dataframe?
            time_index = value_input.values()[0].index
        except AttributeError:
            # It is array-like.
            time = np.arange(np.alen(value_input)) * timestep
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
    name, value = line.split("=")
    name = name.strip()
    value = float(value.split(";")[0])
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


def apply_initialization_script(model, path_script):
    """Apply an initialization script to a model.

    Parameters
    ----------
    model : Pyfmi model object (pyfmi.fmi.FMUModelXXX).

    path_script : String, path to the script file.

    """

    list_name, list_value = parse_initialization_script(path_script)

    try:
        model.set(list_name, list_value)
    except pyfmi.fmi.FMUException:
        try:
            for name, value  in zip(list_name, list_value):
                model.set(name, value)
        except pyfmi.fmi.FMUException:
            pass

#§
def get_name_variable(model, **kwargs):
    """Get the list of variable names.

    Parameters
    ----------
    model : Pyfmi model object (pyfmi.fmi.FMUModelXXX).

    """

    return model.get_model_variables(**kwargs).keys()

def get_causality(model):
    """Get the causality of the variables.

    Parameters
    ----------
    model : Pyfmi model object (pyfmi.fmi.FMUModelXXX).

    PARAMETER(0), CALCULATED_PARAMETER(1), INPUT(2),
    OUTPUT(3), LOCAL(4), INDEPENDENT(5), UNKNOWN(6)

    """

    return [model.get_variable_causality(name) for name in
            get_name_variable(model)]


#§
# Local Variables:
# tmux-temp-file: "/cluster/home/girard/.tmp/tmux_buffer"
# tmux-repl-window: "fmot"
# End:
