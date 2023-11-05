"""Testing basic features with PyFMI only."""

import unittest
import otfmi.example.utility
import pyfmi


class TestPyfmi(unittest.TestCase):
    def setUp(self):
        """Load example FMU."""
        self.path_fmu = otfmi.example.utility.get_path_fmu("deviation")

    def test_empty(self):
        """Check module import and setup."""
        pass

    def test_load_fmu(self):
        """Load an fmu."""
        pyfmi.load_fmu(self.path_fmu)

    def test_simulate(self):
        """Simulate an fmu."""
        model = pyfmi.load_fmu(self.path_fmu)
        model.simulate(options={"silent_mode": True})

    def test_reset(self):
        """Reset an fmu."""
        model = pyfmi.load_fmu(self.path_fmu)
        model.simulate(options={"silent_mode": True})
        model.reset()
        model.simulate(options={"silent_mode": True})


if __name__ == "__main__":
    unittest.main()
