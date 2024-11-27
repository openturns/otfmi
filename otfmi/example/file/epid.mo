model epid

parameter Real total_pop = 763;
parameter Real infection_rate = 2.0;
parameter Real healing_rate = 0.5;

Real infected;
Real susceptible;
Real removed;

initial equation
infected = 1;
removed = 0;
total_pop = infected + susceptible + removed;

equation
der(susceptible) = - infection_rate * infected * susceptible / total_pop;
der(infected) = infection_rate * infected * susceptible / total_pop -
                healing_rate * infected;
der(removed) = healing_rate * infected;

annotation(
    experiment(StartTime = 0.0, StopTime = 200.0, Tolerance = 1e-6, Interval = 0.1));
end epid;