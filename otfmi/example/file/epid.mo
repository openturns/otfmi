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