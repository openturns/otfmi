API documentation
=================

otfmi facilitates the analysis of FMUs over time.

Main API
--------

The class **FMUPointToFieldFunction** wraps the FMU in an :py:class:`openturns.PointToFieldFunction`.
Its output is a :py:class:`openturns.Field` gathering the outputs as function of time.

.. currentmodule:: otfmi

.. autosummary::
   :toctree: _generated/
   :template: class.rst_t

   FMUPointToFieldFunction

Its lower-level counterpart is **OpenTURNSFMUPointToFieldFunction**, closer to
PyFMI’s methods but not directly usable with OpenTURNS.

.. autosummary::
   :toctree: _generated/
   :template: class.rst_t

   OpenTURNSFMUPointToFieldFunction

For convenience the **FMUFunction** is provided for cases in which we absolutely need
a :py:class:`openturns.Function` instead of a :py:class:`openturns.PointToFieldFunction`.

.. autosummary::
   :toctree: _generated/
   :template: class.rst_t

   FMUFunction

Common low-level functions
--------------------------

The submodule **otfmi.fmi** gathers a set of useful functions, employed by the (higher-level) classes mentionned above.

.. autosummary::
   :toctree: _generated/fmi/

   fmi.load_fmu
   fmi.simulate
   fmi.parse_kwargs_simulate
   fmi.apply_initialization_script
   fmi.get_name_variable
   fmi.get_causality_str
   fmi.get_variability
   fmi.get_fixed_value
   fmi.get_start_value
   fmi.set_dict_value

From OpenTURNS to FMI
---------------------

OTFMI can also export an OpenTURNS function in a Modelica source model (.mo) or Functional Mock-up Unit (.fmu).

.. autosummary::
   :toctree: _generated/
   :template: class.rst_t

   FunctionExporter
