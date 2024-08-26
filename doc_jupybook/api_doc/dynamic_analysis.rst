Dynamic analysis
----------------

The class **FMUPointToFieldFunction** wraps the FMU in an :py:class:`openturns.PointToFieldFunction`.
Its output is a :py:class:`openturns.Field` gathering the outputs as function of time.

.. currentmodule:: otfmi

.. autosummary::

   :template: class.rst_t

   otfmi.FMUPointToFieldFunction

Its lower-level counterpart is **OpenTURNSFMUPointToFieldFunction**, closer to
PyFMI’s methods but not directly usable with OpenTURNS.

.. autosummary::

   :template: class.rst_t

   otfmi.OpenTURNSFMUPointToFieldFunction
