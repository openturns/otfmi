# -*- coding: utf-8 -*-
# Copyright 2016 EDF. This software was developed with the collaboration of
# Phimeca Engineering (Sylvain Girard, girard@phimeca.com).
"""Utility functions for the examples."""

#§
import platform
dict_platform = {("Linux", "64bit"):"linux64",
                 ("Windows", "32bit"):"win32"}

def get_directory_platform():
    """Get the directory name corresponding to current platform.
    It can be for instance a component of a path to example data files.
    """
    key_platform = (platform.system(), platform.architecture()[0])
    return dict_platform[key_platform]

#§
