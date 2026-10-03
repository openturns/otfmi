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

The class **FMUFieldFunction** wraps the FMU evaluation in an :py:class:`openturns.FieldFunction`.
Its input is a :py:class:`openturns.Field` and its output is a
:py:class:`openturns.Field` gathering the outputs as function of time.

.. autosummary::
   :toctree: _generated/
   :template: class.rst_t

   FMUFieldFunction

The class **FMUFieldToPointFunction** wraps the FMU evaluation in an :py:class:`openturns.FieldToPointFunction`.
Its input is a :py:class:`openturns.Field` and its output is a vector
(:py:class:`openturns.Point`) consisting of the values at the final simulation time.

.. autosummary::
   :toctree: _generated/
   :template: class.rst_t

   FMUFieldToPointFunction


Here is a summary of the different variants:

+-------------------------------------------+---------+----------+
| Class                                     | Input   | Output   |
+===========================================+=========+==========+
| :class:`~otfmi.FMUPointToFieldFunction`   | Point   | Field    |
+-------------------------------------------+---------+----------+
| :class:`~otfmi.FMUFunction`               | Point   | Point    |
+-------------------------------------------+---------+----------+
| :class:`~otfmi.FMUFieldFunction`          | Field   | Field    |
+-------------------------------------------+---------+----------+
| :class:`~otfmi.FMUFieldToPointFunction`   | Field   | Point    |
+-------------------------------------------+---------+----------+


FMI backend
-----------

Driving a FMU requires an FMI backend, that is an implementation of the FMI
standard. Two are supported, behind a common interface:
`PyFMI <https://pypi.org/project/PyFMI/>`__ and
`FMPy <https://pypi.org/project/fmpy/>`__ (see :doc:`terminology`).

PyFMI is used by default whenever it is installed, otherwise otfmi falls back
to FMPy. The active backend is reported by ``otfmi.backend.BACKEND`` and can be
selected at runtime with **use_backend**, in the spirit of the matplotlib
backends:

.. code-block:: python

    import otfmi

    otfmi.backend.BACKEND  # 'pyfmi' or 'fmpy'
    otfmi.use_backend("fmpy")

Backend-specific simulation options are passed with the ``pyfmi_options`` and
``fmpy_options`` keyword arguments. Only the options matching the active
backend are taken into account, so the same call can carry options for both:

.. code-block:: python

    model(x, pyfmi_options={"silent_mode": True}, fmpy_options={"solver": "Euler"})

.. autosummary::
   :toctree: _generated/

   use_backend

Common low-level functions
--------------------------

The submodule **otfmi.fmi** gathers a set of useful functions, employed by the (higher-level) classes mentioned above.

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
