# Copyright 2016 EDF. This software was developed with the collaboration of
# Phimeca Engineering (Sylvain Girard, girard@phimeca.com).
"""Utility functions for the examples."""

import os
import sysconfig


def get_path_fmu(name):
    path_example = os.path.dirname(os.path.abspath(__file__))
    platform = sysconfig.get_platform()
    path_fmu = os.path.join(path_example, "file", "fmu", platform, f"{name}.fmu")
    if not os.path.exists(path_fmu):
        raise RuntimeError(f"Example {name} is not available on your platform ({platform})")
    return path_fmu
