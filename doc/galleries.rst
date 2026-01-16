:hide-sidebar-primary: true
:hide-sidebar-secondary: true
:hide-related-pages: true

Example Galleries
=================

.. toctree::
   :hidden:

   examples/doc_FMUPointToFieldFunction_example/GALLERY_HEADER.rst
   examples/doc_FMUPointToFieldFunction_example/subgallery_beam/GALLERY_HEADER.rst
   examples/doc_FMUPointToFieldFunction_example/subgallery_epid/GALLERY_HEADER.rst
   examples/doc_export_example/GALLERY_HEADER.rst
   examples/doc_application/GALLERY_HEADER.rst
   examples/doc_application_persalys/use_persalys
   examples/model_description

.. grid:: 1 1 2 2
    :gutter: 2 3 4 4

    .. grid-item-card::
        :text-align: center

        .. button-ref:: examples/auto_FMUPointToFieldFunction_example/index
            :ref-type: doc
            :expand:
            :color: primary
            :click-parent:

            **Model with scalar inputs**

        How to run simulations with models with time-independent inputs.

    .. grid-item-card::
        :text-align: center

        .. button-ref:: examples/auto_export_example/index
            :ref-type: doc
            :expand:
            :color: primary
            :click-parent:

            **Export models**

        OTFMI can transform your OpenTURNS functions into FMU or Modelica model, ready to be integrated in larger models.

    .. grid-item-card::
        :text-align: center

        .. button-ref:: examples/auto_application/index
            :ref-type: doc
            :expand:
            :color: primary
            :click-parent:

            **Applications**

        Here are some specific analysis you can perform with OpenTURNS and OTFMI.


    .. grid-item-card::
        :text-align: center

        .. button-ref:: examples/doc_application_persalys/use_persalys
            :ref-type: doc
            :expand:
            :color: primary
            :click-parent:

            **Use Persalys**

        You can import fmu files into Persalys, which uses OTFMI, to study the effect of uncertain parameters on the output.

    .. grid-item-card::
        :text-align: center

        .. button-ref:: examples/model_description
            :ref-type: doc
            :expand:
            :color: primary
            :click-parent:

            **Model descriptions**

        See descriptions of the models used in examples.
