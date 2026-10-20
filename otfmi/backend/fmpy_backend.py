# Copyright 2016-2026 EDF Phimeca

"""fmpy implementation of the FMI backend interface.

This module provides the fmpy-based implementation of the FMI backend
interface. It wraps fmpy's model description and simulation functions
to provide an interface compatible with the pyfmi backend.
"""

from pathlib import Path
import numpy as np
from packaging.version import Version

import fmpy


# Backend identifier
BACKEND = "fmpy"


# fmpy < 0.3.23 cannot handle an input table with a single sample: the
# interpolation returns the two-dimensional table, which is then assigned
# element-wise to the FMI buffer and raises
# "only 0-dimensional arrays can be converted to Python scalars".
# Since 0.3.23 the interpolated values are flattened before the assignment.
_FMPY_INPUT_FIXED = Version(fmpy.__version__) >= Version("0.3.23")


# Fallbacks for the default experiment, matching the ones pyfmi applies when
# the FMU does not define them.
_DEFAULT_START_TIME = 0.0
_DEFAULT_STOP_TIME = 1.0
_DEFAULT_STEP = 0.01


# Exception classes
class FMUException(Exception):
    """Exception raised for FMU-related errors."""
    pass


class VariableNotFoundError(Exception):
    """Exception raised when a variable is not found in the FMU."""
    pass


# ============================================================================
# Causality constants
# ============================================================================

# Causality identifiers, per FMI version and per role. These are mapped to
# the same integer values as pyfmi for compatibility.
CAUSALITY = {
    "1.0": {"input": 0, "output": 1, "parameter": None, "local": None},
    "2.0": {"input": 2, "output": 3, "parameter": 0, "local": 4},
    "3.0": {"input": 3, "output": 4, "parameter": 1, "local": 5},
}

# Causality names, per FMI version.
CAUSALITY_NAME = {
    "1.0": {0: "INPUT", 1: "OUTPUT", 2: "INTERNAL", 3: "NONE"},
    "2.0": {0: "PARAMETER", 1: "CALCULATED_PARAMETER", 2: "INPUT",
            3: "OUTPUT", 4: "LOCAL", 5: "INDEPENDENT", 6: "UNKNOWN"},
    "3.0": {0: "STRUCTURAL_PARAMETER", 1: "PARAMETER",
            2: "CALCULATED_PARAMETER", 3: "INPUT", 4: "OUTPUT",
            5: "LOCAL", 6: "INDEPENDENT", 7: "UNKNOWN"},
}

# Numeric and boolean variable types, per FMI version. String-like types are
# left out as their start values cannot be converted to float.
TYPES = {
    "1.0": ["Real", "Integer", "Boolean"],
    "2.0": ["Real", "Integer", "Boolean"],
    "3.0": ["Float64", "Float32", "Int64", "Int32", "Int16", "Int8",
            "UInt64", "UInt32", "UInt16", "UInt8", "Bool"],
}

# fmpy model classes (not used, but kept for API compatibility)
MODEL_CLASS = {}


# fmpy string-to-integer mappings
_FMPY_CAUSALITY_TO_INT = {
    "1.0": {"input": 0, "output": 1, "internal": 2, "none": 3, "unknown": 4},
    "2.0": {"parameter": 0, "calculatedParameter": 1, "input": 2,
            "output": 3, "local": 4, "independent": 5, "unknown": 6},
    "3.0": {"structuralParameter": 0, "parameter": 1, "calculatedParameter": 2,
            "input": 3, "output": 4, "local": 5, "independent": 6, "unknown": 7},
}

_FMPY_VARIABILITY_TO_INT = {
    "constant": 0, "fixed": 1, "tunable": 2,
    "discrete": 3, "continuous": 4, "unknown": 5,
}


# ============================================================================
# fmpy model wrapper
# ============================================================================

class _FMPYModel:
    """Wrapper around fmpy model description to provide a pyfmi-like interface.

    This class wraps fmpy's ModelDescription and simulate_fmu to provide
    an interface compatible with pyfmi model objects.
    """

    def __init__(self, path_fmu, kind=None, model_description=None):
        self._path_fmu = str(Path(path_fmu).resolve())
        self._kind = kind
        self._otfmi_backend = BACKEND
        self._model_description = model_description or fmpy.read_model_description(
            self._path_fmu
        )
        self._variables = {v.name: v for v in self._model_description.modelVariables}
        self._values = {}

    def get_version(self):
        """Get the FMI version."""
        return self._model_description.fmiVersion

    def get_model_variables(self, include_alias=True, variability=None,
                            type=None, only_start=False):
        """Get model variables as a dict.

        Parameters
        ----------
        include_alias : bool
            Include alias variables.
        variability : int or None
            Filter by variability (integer constant).
        type : str or None
            Filter by type (string name).
        only_start : bool
            Only include variables with a start value.
        """
        result = {}
        for name, var in self._variables.items():
            if not include_alias and getattr(var, "alias", None) is not None:
                continue
            if variability is not None:
                var_variability = _FMPY_VARIABILITY_TO_INT.get(var.variability, -1)
                if var_variability != variability:
                    continue
            if type is not None and var.type != type:
                continue
            if only_start and var.start is None:
                continue
            result[name] = var
        return result

    def get_variable_causality(self, name):
        """Get the causality of a variable as an integer."""
        var = self._variables[name]
        version = self.get_version()
        causality_map = _FMPY_CAUSALITY_TO_INT.get(version, {})
        return causality_map.get(var.causality, -1)

    def get_variable_variability(self, name):
        """Get the variability of a variable as an integer."""
        var = self._variables[name]
        return _FMPY_VARIABILITY_TO_INT.get(var.variability, -1)

    @staticmethod
    def _convert_start(var):
        """Convert a raw fmpy start value according to its type."""
        start = var.start
        if start is None:
            return None
        if isinstance(start, bool):
            return start
        if isinstance(start, str):
            lowered = start.strip().lower()
            if lowered in ("true", "false"):
                return lowered == "true"
        return float(start)

    def get_variable_start(self, name):
        """Get the start value of a variable."""
        return self._convert_start(self._variables[name])

    def set(self, name, value):
        """Set variable value(s), stored for the next simulation.

        Mirrors pyfmi's signature: both ``set(name, value)`` and
        ``set(names, values)`` are accepted.
        """
        if isinstance(value, (list, tuple, np.ndarray)):
            # set(names, values)
            self._values.update(zip(name, value))
        else:
            # set(name, value)
            self._values[name] = value

    def get(self, name):
        """Get a variable value (returns start value from model description)."""
        return self._convert_start(self._variables[name])

    def setup_experiment(self):
        """No-op for fmpy (handled by simulate_fmu)."""
        pass

    def initialize(self):
        """No-op for fmpy (handled by simulate_fmu)."""
        pass

    def simulate(self, **kwargs):
        """Simulate the FMU using fmpy.

        Parameters
        ----------
        **kwargs
            Keyword arguments including:
            - start_time, final_time: simulation time range
            - input: (names, values) tuple for input variables
            - initialization_parameters: (names, values) tuple for parameters
            - fmpy_options: dict of fmpy-specific options

        Returns
        -------
        _FMPYResult
            Simulation result wrapper.
        """
        fmpy_kwargs = {}

        if "start_time" in kwargs:
            fmpy_kwargs["start_time"] = kwargs["start_time"]
        if "final_time" in kwargs:
            fmpy_kwargs["stop_time"] = kwargs["final_time"]

        # Handle input
        start_values = {}
        if "initialization_parameters" in kwargs:
            names, values = kwargs["initialization_parameters"]
            start_values.update(dict(zip(names, values)))

        # Handle stored values (from set calls)
        start_values.update(self._values)

        if "input" in kwargs:
            names, values = kwargs["input"]
            time = values[:, 0]
            data = values[:, 1:]
            if len(time) == 1 and not _FMPY_INPUT_FIXED:
                # a single sample means the inputs are constant over time: pass
                # them as start values, which every fmpy version handles.
                # fmpy < 0.3.23 cannot interpolate a one-sample input table,
                # see https://github.com/CATIA-Systems/FMPy/issues
                start_values.update(
                    {name: float(value) for name, value in zip(names, data[0])}
                )
            else:
                dtype = [("time", "<f8")] + [(name, "<f8") for name in names]
                input_array = np.zeros(len(time), dtype=dtype)
                input_array["time"] = time
                for i, name in enumerate(names):
                    input_array[name] = data[:, i]
                fmpy_kwargs["input"] = input_array

        # Handle fmpy-specific options
        fmpy_options = dict(kwargs.get("fmpy_options") or {})
        # pyfmi records every variable when no output filter is given, whereas
        # fmpy only records the outputs: ask for all variables explicitly
        fmpy_options.setdefault("output", list(self._variables))
        fmpy_kwargs.update(fmpy_options)

        if start_values:
            fmpy_kwargs.setdefault("start_values", {}).update(start_values)

        if self._kind is not None:
            fmpy_kwargs.setdefault(
                "fmi_type",
                {"ME": "ModelExchange", "CS": "CoSimulation"}.get(
                    self._kind, self._kind
                ),
            )

        result = fmpy.simulate_fmu(self._path_fmu, **fmpy_kwargs)
        return _FMPYResult(result)

    def reset(self):
        """Reset the model (clear stored values)."""
        self._values = {}

    def get_default_experiment_start_time(self):
        """Get the default experiment start time."""
        return self._default_experiment_value("startTime", _DEFAULT_START_TIME)

    def get_default_experiment_stop_time(self):
        """Get the default experiment stop time."""
        return self._default_experiment_value("stopTime", _DEFAULT_STOP_TIME)

    def get_default_experiment_step(self):
        """Get the default experiment step size."""
        return self._default_experiment_value("stepSize", _DEFAULT_STEP)

    def _default_experiment_value(self, name, default):
        """Read a default experiment attribute, or pyfmi's fallback.

        fmpy leaves an attribute unset when the FMU does not provide it, while
        pyfmi substitutes a default. Fall back to the same values so that both
        backends agree on the simulation time interval and mesh.
        """
        experiment = self._model_description.defaultExperiment
        value = getattr(experiment, name, None) if experiment else None
        return default if value is None else value

    def get_log(self):
        """Get log messages (empty for fmpy)."""
        return ""

    def free_instance(self):
        """No-op for fmpy."""
        pass

    def instantiate(self):
        """No-op for fmpy."""
        pass


class _FMPYResult:
    """Wrapper around fmpy simulation result to provide a pyfmi-like interface."""

    def __init__(self, result):
        self._result = result

    def final(self, name):
        """Get the final value of a variable."""
        return self._result[-1][name]

    def __getitem__(self, name):
        """Get a variable trajectory."""
        return self._result[name]

    def keys(self):
        """Get the names of all variables in the result."""
        return self._result.dtype.names


# ============================================================================
# Model loading
# ============================================================================

def load_fmu(path_fmu, kind=None, **kwargs):
    """Load an FMU using fmpy.

    Parameters
    ----------
    path_fmu : str or path-like
        Path to the FMU file.
    kind : str, one of "ME" (model exchange) or "CS" (co-simulation)
        Select a kind of FMU if both are available.

    Additional keyword arguments are accepted for API compatibility.

    Returns
    -------
    _FMPYModel
        FMU model wrapper object.
    """
    return _FMPYModel(path_fmu, kind=kind)


def load_unzipped_fmu(path_fmu, kind=None, **kwargs):
    """Load an unzipped FMU using fmpy.

    Parameters
    ----------
    path_fmu : str or path-like
        Path to the directory of an unzipped FMU.
    kind : str, one of "ME" (model exchange) or "CS" (co-simulation)
        Select a kind of FMU if both are available.

    Returns
    -------
    _FMPYModel
        FMU model wrapper object.
    """
    # check the directory looks like an unzipped FMU
    xml_file = Path(path_fmu) / "modelDescription.xml"
    if not xml_file.is_file():
        raise FileNotFoundError(f"{xml_file} not found, it does not look like an"
                                f" unzipped FMU")
    return _FMPYModel(path_fmu, kind=kind)
