# API documentation

Otfmi facilitates the analysis of FMUs **at a given time step and/or over time** (*static* versus *dynamic* analyses).

## Static analysis

The class **FMUFunction** wraps the FMU in an OpenTURNS [Function](http://shorturl.at/cAGH1).
Its output corresponds to the FMU's output at its last simulation time.
When the FMU is static (i.e. its output is time-independent), the value of the last simulation time is indifferent.

```{eval-rst}
.. currentmodule:: otfmi

.. autosummary::
    :toctree: _generated/
    :template: class.rst_t

    FMUFunction
```

Its lower-level counterpart is **OpenTURNSFMUFunction**, closer to PyFMI's methods but not directly usable with OpenTURNS.

```{eval-rst}
.. autosummary::
    :toctree: _generated/
    :template: class.rst_t

    OpenTURNSFMUFunction
```


## Dynamic analysis

The class **FMUPointToFieldFunction** wraps the FMU in an OpenTURNS [PointToFieldFunction](http://shorturl.at/aduBM).
Its output is a [Field](http://shorturl.at/ptDKW) gathering the outputs as function of time.

```{eval-rst}
.. autosummary::
    :toctree: _generated/
    :template: class.rst_t

    FMUPointToFieldFunction
```

Its lower-level counterpart is **OpenTURNSFMUPointToFieldFunction**, closer to PyFMI's methods but not directly usable with OpenTURNS.

```{eval-rst}
.. autosummary::
    :toctree: _generated/
    :template: class.rst_t

    OpenTURNSFMUPointToFieldFunction
```

## Common low-level functions

The submodule **otfmi.fmi** gathers a set of useful functions, employed by the (higher-level) classes mentionned above.

```{eval-rst}
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
```

## From OpenTURNS to FMU

Otfmi can also embed an OpenTURNS function in a Modelica model and/or FMU.

```{eval-rst}
.. autosummary::
    :toctree: _generated/
    :template: class.rst_t

    FunctionExporter
```