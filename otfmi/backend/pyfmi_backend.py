# Copyright 2016-2026 EDF Phimeca

"""pyfmi implementation of the FMI backend interface.

This module provides the pyfmi-based implementation of the FMI backend
interface. It wraps pyfmi's model loading, simulation, and introspection
functions.
"""

import io
from pathlib import Path
import re

import pyfmi

# Backend identifier
BACKEND = "pyfmi"

try:
    from pyfmi import fmi3 as _fmi3
except ImportError:  # pragma: no cover
    # pyfmi release without FMI 3.0 support
    _fmi3 = None


# Exception classes
FMUException = pyfmi.fmi.FMUException
VariableNotFoundError = pyfmi.common.io.VariableNotFoundError


# ============================================================================
# Causality constants
# ============================================================================

# Causality identifiers, per FMI version and per role. FMI 1.0 defines neither
# the "parameter" nor the "local" causality.
CAUSALITY = {
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
CAUSALITY_NAME = {
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
TYPES = {
    "1.0": [pyfmi.fmi.FMI_REAL, pyfmi.fmi.FMI_INTEGER, pyfmi.fmi.FMI_BOOLEAN],
    "2.0": [pyfmi.fmi.FMI2_REAL, pyfmi.fmi.FMI2_INTEGER, pyfmi.fmi.FMI2_BOOLEAN],
}

# pyfmi model classes, per FMI version and per kind.
MODEL_CLASS = {
    ("1.0", "CS"): pyfmi.fmi.FMUModelCS1,
    ("1.0", "ME"): pyfmi.fmi.FMUModelME1,
    ("2.0", "CS"): pyfmi.fmi.FMUModelCS2,
    ("2.0", "ME"): pyfmi.fmi.FMUModelME2,
}

if _fmi3 is not None:
    CAUSALITY["3.0"] = {"input": _fmi3.FMI3_Causality.INPUT,
                        "output": _fmi3.FMI3_Causality.OUTPUT,
                        "parameter": _fmi3.FMI3_Causality.PARAMETER,
                        "local": _fmi3.FMI3_Causality.LOCAL}
    CAUSALITY_NAME["3.0"] = {
        _fmi3.FMI3_Causality.STRUCTURAL_PARAMETER: "STRUCTURAL_PARAMETER",
        _fmi3.FMI3_Causality.PARAMETER: "PARAMETER",
        _fmi3.FMI3_Causality.CALCULATED_PARAMETER: "CALCULATED_PARAMETER",
        _fmi3.FMI3_Causality.INPUT: "INPUT",
        _fmi3.FMI3_Causality.OUTPUT: "OUTPUT",
        _fmi3.FMI3_Causality.LOCAL: "LOCAL",
        _fmi3.FMI3_Causality.INDEPENDENT: "INDEPENDENT",
        _fmi3.FMI3_Causality.UNKNOWN: "UNKNOWN"}
    TYPES["3.0"] = [_fmi3.FMI3_Type.FLOAT64, _fmi3.FMI3_Type.FLOAT32,
                    _fmi3.FMI3_Type.INT64, _fmi3.FMI3_Type.INT32,
                    _fmi3.FMI3_Type.INT16, _fmi3.FMI3_Type.INT8,
                    _fmi3.FMI3_Type.UINT64, _fmi3.FMI3_Type.UINT32,
                    _fmi3.FMI3_Type.UINT16, _fmi3.FMI3_Type.UINT8,
                    _fmi3.FMI3_Type.BOOL]
    MODEL_CLASS[("3.0", "CS")] = _fmi3.FMUModelCS3
    MODEL_CLASS[("3.0", "ME")] = _fmi3.FMUModelME3


# ============================================================================
# Model loading
# ============================================================================

def load_fmu(path_fmu, kind=None, **kwargs):
    """Load an FMU using pyfmi.

    Parameters
    ----------
    path_fmu : str or path-like
        Path to the FMU file.
    kind : str, one of "ME" (model exchange) or "CS" (co-simulation)
        Select a kind of FMU if both are available.
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
    """Load an unzipped FMU using pyfmi.

    The FMI version and the kind of FMU are read from the modelDescription.xml
    file, as pyfmi requires the matching model class to be picked explicitly.

    Parameters
    ----------
    path_fmu : str or path-like
        Path to the directory of an unzipped FMU.

    kind : str, one of "ME" (model exchange) or "CS" (co-simulation)
        Select a kind of FMU if both are available.

    Additional keyword arguments are passed on to the pyfmi model constructor.

    """
    # pyfmi writes a log file in current folder even with log_level=0
    kwargs.setdefault("log_file_name", io.StringIO())
    kwargs.setdefault("allow_unzipped_fmu", True)

    version, fmu_kind = read_unzipped_model_description(path_fmu)
    if kind is None:
        kind = fmu_kind
    try:
        model_class = MODEL_CLASS[(version, kind)]
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
