model Solar
  parameter Modelica.SIunits.Distance L = 450;
  parameter Integer NSection = 1;
  output Real heatFlow = NSection * heatSource.C[1].W;
  ThermoSysPro.Solar.Collectors.SolarCollector solarCollector(AlphaGlass = 0.0302, AlphaN = 0.96, DGlass = 0.115, DTube = 0.07, EpsTube = 0.14,L = L, Lambda = 2.89e-2, Ns = NSection, R = 0.93, RimAngle = 70, Tatm(displayUnit = "K"), TauN = 0.95, Tsky(displayUnit = "K"), e = 1e-3, f = 1.79) annotation (
    Placement(visible = true, transformation(origin = {68.7538, -4.75683}, extent = {{-73.4098, -24.1883}, {38.1731, 72.565}}, rotation = 0)));
  ThermoSysPro.Thermal.HeatTransfer.HeatExchangerWall Paroi3(D = 0.06, L = L, Ns = NSection, e = 0.006, lambda = 26) annotation (
    Placement(visible = true, transformation(extent={{11, -64},{71, -16}},    rotation = 0)));
  ThermoSysPro.InstrumentationAndControl.Blocks.Sources.Constante T_atm(k = 300) annotation (
    Placement(visible = true, transformation(origin = {-80, 80}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  ThermoSysPro.InstrumentationAndControl.Blocks.Sources.Constante radiation(k = 70) annotation (
    Placement(visible = true, transformation(origin = {-80, 54}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  ThermoSysPro.InstrumentationAndControl.Blocks.Sources.Constante angle_incidence(k = 30) annotation (
    Placement(visible = true, transformation(origin = {-80, 28}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  ThermoSysPro.Thermal.BoundaryConditions.HeatSource heatSource(T0(each
        displayUnit="K") = {300})                                                                             annotation (
    Placement(visible = true, transformation(origin={40,-62},    extent = {{-10, -10}, {10, 10}}, rotation = 180)));
equation
connect(T_atm.y, solarCollector.AtmTemp) annotation(
    Line(points = {{-69, 80}, {-34, 80}, {-34, 77.7454}, {-11.7897, 77.7454}, {-11.7897, 78}, {-13, 78}}, color = {0, 0, 255}));
connect(radiation.y, solarCollector.ISun) annotation(
    Line(points = {{-69, 54}, {-13, 54}, {-13, 58}}, color = {0, 0, 255}));
connect(angle_incidence.y, solarCollector.IncidenceAngle) annotation(
    Line(points = {{-69, 28}, {-28, 28}, {-28, 37.4315}, {-15.8598, 37.4315}, {-15.8598, 38}, {-13, 38}}, color = {0, 0, 255}));
connect(Paroi3.WT1, heatSource.C) annotation(
    Line(points = {{41, -45}, {40, -45}, {40, -52}}, thickness = 0.5));
connect(solarCollector.ITemperature, Paroi3.WT2) annotation(
    Line(points = {{42, -8}, {42, -36}}, thickness = 0.5));
  annotation (
    Diagram,
    experiment(StartTime = 0, StopTime = 1, Tolerance = 1e-06, Interval = 0.5));
end Solar;