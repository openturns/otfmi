# Examples

The mathematical methods applying to static or dynamic FMUs are pretty different. Hence [Otfmi](../index) provides different wrappers for these two kinds of physical models.

```{note} A *static* FMU yields one or several time-invariant output(s).  
A *dynamic* FMU yields one or several output(s) that evolve over time; the FMU simulation time is important to set.
```

## Explore static FMUs

All static examples rely on *deviation.fmu*. This mechanical model represents the deviation of a cantilever beam submitted to a load at its end.

---
See the cantilever beam model [here](../fmus/deviation)

---

```{eval-rst}
.. image:: ../_static/beam.png
 :width: 132px
 :height: 126px
 :scale: 100 %
 :alt: alternate text
 :align: center
```

```{toctree}
:maxdepth: 1

../auto_example/static/plot_basics
../auto_example/static/plot_init
../auto_example/static/plot_set
```

## Explore dynamic FMUs

All dynamic examples rely on *epid.fmu*. This epidemiologic model represents the spreading of an epidemic through a population.

---
See the epidemiological model [here](../fmus/epid).

---

```{eval-rst}
.. image:: ../_static/epid.png
 :height: 150px
 :width: 300px
 :alt: alternate text
 :align: center
```

```{toctree}
:maxdepth: 1

../auto_example/dynamic/plot_dyn_basics
../auto_example/dynamic/plot_dyn_init
../auto_example/dynamic/plot_dyn_set
```

## Common low-level functions

The 4 classes mentionned here upper are based on low-level functions from the submodule `otfmi.fmi`.  
These functions can be used to load, initialize or simulate the FMU with more control. The tutorials are based on the static *deviation.fmu* example.

```{toctree}
:maxdepth: 1

../auto_example/low_level/plot_load_fmu
../auto_example/low_level/plot_explore
../auto_example/low_level/plot_simulate
../auto_example/low_level/plot_initialize
```

## From OpenTURNS to FMU


```{eval-rst}
.. warning::
   **This feature is experimental.**
```

The focus of OTFMI module is to enable FMUs analysis using OpenTURNS. Once a computationnally heavy FMU is metamodeled, the modeler may want to employ the metamodel *instead of the FMU* in the simulation tool.

```{toctree}
:maxdepth: 1

../auto_example/ot_to_fmu/plot_fmu_exporter
../auto_example/ot_to_fmu/plot_model_exporter
```