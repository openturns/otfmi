========================
Documentation of the API
========================

This is the user manual for the Python bindings to the :code:`otfmi` library.

.. currentmodule:: otfmi

.. autosummary::
    :toctree: _generated/
    :template: class.rst_t

    FMUFunction
    OpenTURNSFMUFunction

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

