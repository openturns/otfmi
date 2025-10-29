API documentation
=================

otfmi facilitates the analysis of FMUs over time.

Main API
--------

The class **FMUPointToFieldFunction** wraps the FMU evaluation in an :py:class:`openturns.PointToFieldFunction`.
Its input is a vector (:py:class:`openturns.Point`) and its output is a
:py:class:`openturns.Field` gathering the outputs as function of time.

.. currentmodule:: otfmi

.. autosummary::
   :toctree: _generated/
   :template: class.rst_t

   FMUPointToFieldFunction

The **FMUFunction** allows to perform the FMU evaluation as a :py:class:`openturns.Function`.
Both its input and output vector are a vector (:py:class:`openturns.Point`),
the output consisting of the values at the final simulation time.

.. autosummary::
   :toctree: _generated/
   :template: class.rst_t

   FMUFunction

The class **FMUFieldToPointFunction** wraps the FMU evaluation in an :py:class:`openturns.FieldToPointFunction`.
Its input is a :py:class:`openturns.Field` and its output is a vector
(:py:class:`openturns.Point`) consisting of the values at the final simulation time.

.. autosummary::
   :toctree: _generated/
   :template: class.rst_t

   FMUFieldToPointFunction

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
