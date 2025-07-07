model boost_converter
  Modelica.Electrical.Analog.Sources.ConstantVoltage constantVoltage(V=80)
    annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=-90,
        origin={-70,20})));
  Modelica.Electrical.PowerConverters.DCDC.ChopperStepUp boost annotation (
    Placement(visible = true, transformation(origin={24,16},     extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Electrical.Analog.Basic.Inductor inductor(L=0.001)   annotation (
    Placement(visible = true, transformation(origin={-48,54},     extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Electrical.Analog.Basic.Ground ground annotation (
    Placement(visible = true, transformation(origin={-70,-36},     extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Electrical.PowerConverters.DCDC.Control.SignalPWM pwm(
    constantDutyCycle=0.2,
    f=20000,
    startTime=0,
    useConstantDutyCycle=false)                                                                                                                   annotation (
    Placement(visible = true, transformation(origin={24,-62},     extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Electrical.Analog.Sensors.CurrentSensor currentSensor annotation (
    Placement(visible = true, transformation(origin={-12,54},     extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Electrical.Analog.Basic.Capacitor capacitor(          v(start=170), C=
        0.0006)                                                                    annotation (
    Placement(visible = true, transformation(origin={74,12},     extent = {{-10, -10}, {10, 10}}, rotation = -90)));
  Modelica.Electrical.Analog.Sensors.VoltageSensor voltageSensor annotation (
    Placement(visible = true, transformation(origin={106,12},   extent = {{-10, 10}, {10, -10}}, rotation = -90)));
  Modelica.Electrical.Analog.Sensors.CurrentSensor currentSensor1 annotation (
    Placement(visible = true, transformation(origin={104,72},  extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Electrical.Analog.Basic.VariableResistor resistor1 annotation (
      Placement(transformation(
        extent={{-9,-9},{9,9}},
        rotation=-90,
        origin={159,47})));
  Modelica.Blocks.Sources.Constant const3(k=0.5)
    annotation (Placement(transformation(extent={{-44,-72},{-24,-52}})));
  Modelica.Blocks.Sources.Step step1(
    height=5,
    offset=20,
    startTime=0.5)
    annotation (Placement(transformation(extent={{210,36},{190,56}})));
equation
  connect(constantVoltage.p,inductor. p) annotation (
    Line(points={{-70,30},{-70,54},{-58,54}},           color = {0, 0, 255}));
  connect(constantVoltage.n,ground. p) annotation (
    Line(points={{-70,10},{-70,-26}},                                 color = {0, 0, 255}));
  connect(constantVoltage.n,boost. dc_n1) annotation (
    Line(points={{-70,10},{14,10}},        color = {0, 0, 255}));
  connect(pwm.fire,boost. fire_p) annotation (
    Line(points={{18,-51},{18,4}},         color = {255, 0, 255}));
  connect(boost.dc_p2,capacitor. p) annotation (
    Line(points={{34,22},{74,22}},                              color = {0, 0, 255}));
  connect(boost.dc_n2,capacitor. n) annotation (
    Line(points={{34,10},{50,10},{50,2},{74,2}},                        color = {0, 0, 255}));
  connect(capacitor.p,voltageSensor. p) annotation (
    Line(points={{74,22},{106,22}},                          color = {0, 0, 255}));
  connect(capacitor.n,voltageSensor. n) annotation (
    Line(points={{74,2},{106,2}},      color = {0, 0, 255}));
  connect(capacitor.p,currentSensor1. p) annotation (
    Line(points={{74,22},{74,72},{94,72}},          color = {0, 0, 255}));
  connect(inductor.n,currentSensor. p)
    annotation (Line(points={{-38,54},{-22,54}},   color={0,0,255}));
  connect(currentSensor.n,boost. dc_p1) annotation (Line(points={{-2,54},{6,54},
          {6,22},{14,22}},        color={0,0,255}));
  connect(currentSensor1.n, resistor1.p) annotation (Line(points={{114,72},{158,
          72},{158,56},{159,56}}, color={0,0,255}));
  connect(resistor1.n, voltageSensor.n) annotation (Line(points={{159,38},{160,
          38},{160,2},{106,2}}, color={0,0,255}));
  connect(step1.y, resistor1.R) annotation (Line(points={{189,46},{189,47},{
          169.8,47}},      color={0,0,127}));
  connect(const3.y, pwm.dutyCycle)
    annotation (Line(points={{-23,-62},{12,-62}}, color={0,0,127}));
  annotation (
    Icon(coordinateSystem(preserveAspectRatio=false, extent={{-100,-100},{240,
            100}})),
    Diagram(coordinateSystem(preserveAspectRatio=false, extent={{-100,-100},{
            240,100}})),
    uses(Modelica(version="4.0.0")),
    version="1",
    conversion(noneFromVersion=""));
end boost_converter;
