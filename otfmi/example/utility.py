# Copyright 2016 EDF. This software was developed with the collaboration of
# Phimeca Engineering (Sylvain Girard, girard@phimeca.com).
"""Utility functions for the examples."""

from pathlib import Path
import sysconfig


def get_path_fmu(name):
    """
    Get example file.

    Parameters
    ----------
    name : str
        Example name

    Returns
    -------
    path_fmu : Path
        FMU file path
    """
    path_example = Path(__file__).parent
    platform = sysconfig.get_platform()
    path_fmu = path_example / "file" / "fmu" / platform / f"{name}.fmu"
    if not path_fmu.exists():
        raise RuntimeError(f"Example {name} is not available on your platform ({platform}) {path_fmu}")
    return path_fmu
