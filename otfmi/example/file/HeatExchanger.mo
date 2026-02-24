
model HeatExchanger

// Heat exchanger
  parameter Real HeatTransfer_coeff(unit = "kW/K") = 192 "Heat transfer coefficient of the exchange surface" annotation(
    Dialog(group = "Heat Exchanger"));

  Real Qc_ratio "Ratio of thermal flow rates";
  Real NTU "Number of Transfer Unit relative";
  Real efficiency_countercurrent "efficiency for a perfect counter current HX";
  Modelica.Units.SI.HeatFlowRate Power_exchanged "Heat Power exchanged by the HX";

// air
  parameter Modelica.Units.NonSI.Temperature_degC Temp_air_inlet = 25.0 "Inlet air temperature" annotation(
    Dialog(group = "Air"));
  parameter Real density_air = 1.0 annotation(
    Dialog(group = "Air"));
  parameter Modelica.Units.SI.SpecificHeatCapacity cp_air = 1006 annotation(
    Dialog(group = "Air"));
  parameter Modelica.Units.SI.VolumeFlowRate total_air_flow = 200 "air Volume flow" annotation(
    Dialog(group = "Air"));
  final parameter Modelica.Units.SI.ThermalConductance Qc_air(min=0) = total_air_flow*cp_air*density_air "Thermal flow rate unit of air";

  Modelica.Units.NonSI.Temperature_degC Temp_air_outlet(min = 0.0);
  
//coolant
  parameter Modelica.Units.NonSI.Temperature_degC Temp_coolant_inlet = 50.0  "Inlet coolant temperature" annotation(
    Dialog(group = "Coolant"));
  parameter Real density_cool = 1.1 annotation(
    Dialog(group = "Coolant"));
  parameter Modelica.Units.SI.SpecificHeatCapacity cp_cool = 3600 annotation(
    Dialog(group = "Coolant"));
  parameter Modelica.Units.NonSI.Temperature_degC Temp_coolant_outlet_start = 50 "start value for the coolant outlet temp"  annotation(
    Dialog(group = "Coolant"));
  parameter Modelica.Units.SI.VolumeFlowRate VolFlow_coolant = 160 "volume flow rate for coolant in kg/m³" annotation(
    Dialog(group = "Coolant"));
  final parameter Modelica.Units.SI.ThermalConductance Qc_coolant(min=0) = VolFlow_coolant*cp_cool*density_cool "Thermal flow rate unit of coolant";
  
  Modelica.Units.NonSI.Temperature_degC Temp_coolant_outlet(start = Temp_coolant_outlet_start, min = 0.0, max = 100.0) "Coolant outlet temperature [°C]";

equation

  // thermal power exchanged from NTU approach
  NTU = HeatTransfer_coeff * 1000 / max( min(Qc_coolant, Qc_air), 1e3*Modelica.Constants.small ) ;
  Qc_ratio = min(Qc_coolant, Qc_air) / max( max(Qc_coolant, Qc_air), 1e3*Modelica.Constants.small) ;
  efficiency_countercurrent = Modelica.Fluid.Utilities.regStep(
      x = 0.98 - Qc_ratio, 
      x_small = 1.0e-2,
      y1 = (1.0 - exp(-NTU * (1.0 - Qc_ratio))) / (1.0 - Qc_ratio * exp(-NTU * (1.0 - Qc_ratio))),
      y2 = NTU / (NTU + 1.0));

  Power_exchanged = efficiency_countercurrent * min(Qc_coolant, Qc_air) * (Temp_coolant_inlet - Temp_air_inlet) ;
  
  // determine the coolant outlet temperature
  Power_exchanged + Qc_coolant * (Temp_coolant_outlet - Temp_coolant_inlet) = 0 ;
  
  // equilibrium to get the air outlet temperature
  Qc_coolant * (Temp_coolant_outlet - Temp_coolant_inlet) + Qc_air * (Temp_air_outlet - Temp_air_inlet) = 0 ;

  annotation(
    Documentation(info = "<html>
    <head></head>
    <body><p>The Heat eXchanger (HX) is in charge of heat dissipation from the coolant fluid to the air.</p></body>
    </html>"));

end HeatExchanger;


