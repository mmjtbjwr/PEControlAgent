within ;
model modified_boost_converter
  Modelica.Electrical.Analog.Sources.ConstantVoltage constantVoltage(V=80)
    annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=-90,
        origin={-180,16}))); Modelica.Electrical.PowerConverters.DCDC.ChopperStepUp boost annotation (
      Placement(visible = true, transformation(origin={-86,12}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Electrical.Analog.Basic.Inductor inductor(L=0.001) annotation (
      Placement(visible = true, transformation(origin={-158,50}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Electrical.Analog.Basic.Capacitor capacitor(v(start=170), C=0.001)  annotation (
      Placement(visible = true, transformation(origin={-36,8}, extent = {{-10, -10}, {10, 10}}, rotation = -90)));
  Modelica.Electrical.Analog.Basic.Resistor resistor(R=20) annotation (
      Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=-90,
        origin={78,38})))
; 
end modified_boost_converter;