# -*- coding: utf-8 -*-
"""Testing basic features with PyFMI only."""
#§ Identifying the platform
import platform
key_platform = (platform.system(), platform.architecture()[0])
# Call to either 'platform.system' or 'platform.architecture' *after*
# importing pyfmi causes a segfault.
dict_platform = {("Linux", "64bit"):"linux64",
                 ("Windows", "32bit"):"win32",
                 ("Windows", "64bit"):"win64"}

import numpy as np
import unittest

import otfmi.example
import pyfmi

import os

#§
class TestPyfmi(unittest.TestCase):
    def setUp(self):
        """Load example FMU."""
        path_example = os.path.dirname(os.path.abspath(
            otfmi.example.__file__))
        try:
            directory_platform = dict_platform[key_platform]
            self.path_fmu = os.path.join(path_example, "file", "fmu",
                                    directory_platform, "deviation.fmu")
        except KeyError:
            raise RuntimeError ("Tests are not available on your platform"
                                " (%s)." % key_platform)

    def test_empty(self):
        """Check module import and setup."""
        pass

    def test_load_fmu(self):
        """Load an fmu."""
        model = pyfmi.load_fmu(self.path_fmu)

    def test_simulate(self):
        """Simulate an fmu."""
        model = pyfmi.load_fmu(self.path_fmu)
        model.simulate(options={'silent_mode': True})

    def test_reset(self):
        """Reset an fmu."""
        model = pyfmi.load_fmu(self.path_fmu)
        model.simulate(options={'silent_mode': True})
        model.reset()
        model.simulate(options={'silent_mode': True})


#§
if __name__ == '__main__':
    unittest.main()

#§
