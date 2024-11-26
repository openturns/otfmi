The cantilever beam model
=========================

The cantilever beam model describes the vertical deviation of a diving
board created by a child diver. It is a widely-use `OpenTURNS use
case <http://openturns.github.io/openturns/master/usecases/use_case_cantilever_beam.html>`__.

.. image:: ../_static/beam.png
   :scale: 25 %
   :alt: alternate text
   :align: center

We consider a cantilever beam defined by its Young’s modulus ``E``, its length ``L`` and its section modulus ``I``.
One end of the cantilever beam is built in a wall and we apply a concentrated
bending load ``F`` at the other end of the beam, resulting in a deviation ``Y``.

The mechanical equation ruling the deviation writes:

.. math::

   Y = \frac{FL^3}{3EI}

This model is implemented in Modelica language:

.. code::

   model deviation
     output Real y;
     input Real E (start=3.0e7);
     input Real F (start=3.0e4);
     input Real L (start=250);
     input Real I (start=400);
   equation
     y=(F*L^3)/(3.0*E*I);
   end deviation;

.. note::
   This model is time-independent: the simulation start and final times do not matter.

We focus on the effect of the ``E``, ``F``, ``L`` and ``I`` on the
deviation ``Y``. Hence **four input variables** and **one
time-independent output**.
