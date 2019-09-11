model deviation
  "Model from here: http://doc.openturns.org/openturns-latest/html/ExamplesGuide/cid1.xhtml#cid1"
  output Real y;
  input Real E (start=3.0e7);
  input Real F (start=3.0e4);
  input Real L (start=250);
  input Real I (start=400);
equation
  y=(F*L*L*L)/(3.0*E*I);
  annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={                                                                      Rectangle(visible=true, origin={0,
              10},                                                                                                                                                                          fillColor={192,192,192},
            fillPattern =                                                                                                    FillPattern.Solid, extent={{-70.0,-10.0},{70.0,10.0}}),Line(visible=true, origin={
              -70,10},                                                                                                                                                                                                     points={{0.0,50.0},{0.0,-50.0}}, thickness=3),Line(visible=true, origin={60,
              40.0634},                                                                                                                                                                                                        points={{0.0,18.937},{0.0,-18.937}}, color={255,0,0}, thickness=1, arrow={Arrow.None,Arrow.Open}, arrowSize=6),Text(visible=true, origin={
              72.1431,54.7413},                                                                                                                                                                                                        fillColor={255,0,0},
            fillPattern =                                                                                                    FillPattern.Solid, extent={{-5.4548,-6.2587},{5.4548,6.2587}}, textString
            =                                                                                                    "F", fontName="Arial"),Line(visible=true, origin={
              -35,30},                                                                                                                                                          points={{15.0,10.0},{-15.0,-10.0}}, arrow={Arrow.None,Arrow.Open}, arrowSize=6),Text(visible=true, origin={
              -10.0781,44.0169},
            fillPattern =                                                                                                    FillPattern.Solid, extent={{-9.9219,-4.0169},{9.9219,4.0169}}, textString
            =                                                                                                    "E", fontName="Arial"),Line(visible=true, origin={
              0.6293,-10},                                                                                                                                                         points={{-67.248,0.0},{67.248,0.0}}, arrow={Arrow.Open,Arrow.Open}, arrowSize=6),Text(visible=true, origin={
              -3.0781,-16.9831},
            fillPattern =                                                                                                    FillPattern.Solid, extent={{-9.9219,-4.0169},{9.9219,4.0169}}, textString
            =                                                                                                    "L", fontName="Arial")}),
      Diagram(coordinateSystem(preserveAspectRatio=false)));
end deviation;
