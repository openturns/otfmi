Static analysis
---------------

The class **FMUFunction** wraps the FMU in an :py:class:`openturns.Function`.
Its output corresponds to the FMU’s output at its last simulation time.
When the FMU is static (i.e. its output is time-independent),
the value of the last simulation time is indifferent.

.. currentmodule:: otfmi

.. autosummary::

   :template: class.rst_t

   otfmi.FMUFunction

Its lower-level counterpart is **OpenTURNSFMUFunction**, closer to PyFMI’s methods but not directly usable with OpenTURNS.

.. autosummary::

   :template: class.rst_t

   otfmi.OpenTURNSFMUFunction
