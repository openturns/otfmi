Common low-level functions
--------------------------

The submodule **otfmi.fmi** gathers a set of useful functions, employed by the (higher-level) classes mentionned above.

.. currentmodule:: otfmi

.. autosummary::
   
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
