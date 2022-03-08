The epidemiological model
=========================

The epidemiological model describes epidemics which propagate through human contact. An isolated population is considered, whose total number is constant. The people are divided in three categories:

* the Susceptibles (who are not sick yet),
* the Infected (who are currently sick),
* the Removed (who are either dead or immune).

The disease can only be propagated from Infected to Susceptibles. This happens at a rate called ``infection rate`` (:math:`\beta`). An Infected becomes Removed after an infection duration (:math:`\gamma`) corresponding to the inverse of the ``healing_rate``.

.. image:: ../_static/epid.png
   :height: 300px
   :width: 450px
   :alt: alternate text
   :align: center

The evolution of the number of Susceptibles, Infected and Removed over
time writes:

.. math::

   \begin{aligned}
   \frac{\partial S}{\partial t}(t) &= - \beta S(t) I(t) \\
   \frac{\partial I}{\partial t}(t) &= \beta S(t) I(t) - \gamma I(t) \\
   \frac{\partial R}{\partial t}(t) &= \gamma I(t)
   \end{aligned}

This model is implemented in Modelica language. The default simulation time is 50 units of time (days for instance).

.. code::

   model epid

   parameter Real total_pop = 700;
   Real infected;
   Real susceptible;
   Real removed;
   parameter Real infection_rate = 0.007;
   parameter Real healing_rate = 0.02;

   initial equation
   infected = 1;
   removed = 0;
   total_pop = infected + susceptible + removed;

   equation
   der(susceptible) = - infection_rate*infected*susceptible;
   der(infected) = infection_rate*infected*susceptible - healing_rate*infected;
   der(removed) = healing_rate*infected;

   annotation(
       experiment(StartTime = 0, StopTime = 50, Tolerance = 1e-6, Interval = 0.1));
   end epid;

We focus on the effect of the ``infection_rate`` and ``healing_rate`` on the evolution of the ``infected`` category. Hence **two input variables** and **one time-dependent output**.
