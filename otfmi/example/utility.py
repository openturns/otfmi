# -*- coding: utf-8 -*-
# Copyright 2016 EDF. This software was developed with the collaboration of
# Phimeca Engineering (Sylvain Girard, girard@phimeca.com).
"""Utility functions for the examples."""

#§
import platform
import os

dict_platform = {("Linux", "64bit"):"linux64",
                 ("Windows", "64bit"):"win64"}

def get_directory_platform():
    """Get the directory name corresponding to current platform.
    It can be for instance a component of a path to example data files.
    """
    key_platform = (platform.system(), platform.architecture()[0])
    return dict_platform[key_platform]

def get_path_fmu(name):
    """Get the path to an example FMU.

    Parameters
    ----------
    name : String, one of "deviation", "bil100" and
    "bil100_initialization_script

    """

    path_here = os.path.dirname(os.path.abspath(__file__))
    import pyfmi
    try:
        directory_platform = get_directory_platform()
        return os.path.join(path_here, "file", "fmu", directory_platform,
                            "%s.fmu" % name)
    except KeyError:
        raise RuntimeError("Examples are not available on your platform"
                           " (%s)." % "-".join(key_platform))
        sys.exit()
    except FMUException:
        raise FMUException("The example FMU '%s' is not"
                           " available on your platform (%s)." %
                           (name, "-".join(key_platform)))
        sys.exit()

#§
