===
API
===

This is the user manual for the :code:`otfmi` library.

.. currentmodule:: otfmi

Top-level classes:

.. autosummary::
    :toctree: _generated/
    :template: class.rst_t

    FMUFunction
    FunctionExporter
    FMUPointToFieldFunction

Lower-level utility functions:

.. autosummary::
    :toctree: _generated/

    fmi.load_fmu
    fmi.simulate
    fmi.parse_kwargs_simulate

    fmi.apply_initialization_script

    fmi.get_name_variable
    fmi.get_causality
    fmi.get_variability
    fmi.get_fixed_value
    fmi.get_start_value
    fmi.set_dict_value

    mo2fmu.mo2fmu
