"""
Use FMU deviation to check if initialization is taken into account.
"""

import unittest
import otfmi
import otfmi.example.utility
import numpy as np
import os


class TestModel(unittest.TestCase):
    def setUp(self):
        """Load FMU"""

        path_fmu = otfmi.example.utility.get_path_fmu("deviation")
        self.model = otfmi.fmi.load_fmu(path_fmu)
        self.var_name = "L"
        self.var_val = float(300)

    def test_no_default(self):
        default_init_var = self.model.get_variable_start(self.var_name)
        assert self.var_val != default_init_var

    def test_inline_initialization(self):
        """Test initialization inline"""
        result = otfmi.fmi.simulate(
            self.model, input=(self.var_name, np.atleast_2d([0, self.var_val]))
        )
        obtained = result.final(self.var_name)
        assert self.var_val == obtained

    def test_initialization_script(self):
        """Test initialization scripts"""

        temporary_file = "initialization.mos"
        with open(temporary_file, "w") as f:
            f.write("{} = {};".format(self.var_name, self.var_val))

        # Simulate with this script
        result = otfmi.fmi.simulate(
            self.model, initialization_script=os.path.abspath(temporary_file)
        )
        obtained = result.final(self.var_name)
        assert self.var_val == obtained


if __name__ == "__main__":
    unittest.main()
