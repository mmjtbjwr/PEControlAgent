model boost_converter
  Modelica.Electrical.Analog.Sources.ConstantVoltage constantVoltage(V=80)
    annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=-90,
        origin={-180,16})));
  Modelica.Electrical.PowerConverters.DCDC.ChopperStepUp boost annotation (
    Placement(visible = true, transformation(origin={-86,12},    extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Electrical.Analog.Basic.Inductor inductor(L=0.001)   annotation (
    Placement(visible = true, transformation(origin={-158,50},    extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Electrical.Analog.Basic.Ground ground annotation (
    Placement(visible = true, transformation(origin={-180,-40},    extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Electrical.PowerConverters.DCDC.Control.SignalPWM pwm(
    constantDutyCycle=0.2,
    f=10000,
    startTime=0,
    useConstantDutyCycle=false)                                                                                                                   annotation (
    Placement(visible = true, transformation(origin={-86,-58},    extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Electrical.Analog.Sensors.CurrentSensor currentSensor annotation (
    Placement(visible = true, transformation(origin={-122,50},    extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Electrical.Analog.Basic.Capacitor capacitor(          v(start=170), C=
        0.001)                                                                     annotation (
    Placement(visible = true, transformation(origin={-36,8},     extent = {{-10, -10}, {10, 10}}, rotation = -90)));
  Modelica.Electrical.Analog.Sensors.VoltageSensor voltageSensor annotation (
    Placement(visible = true, transformation(origin={-4,8},     extent = {{-10, 10}, {10, -10}}, rotation = -90)));
  Modelica.Electrical.Analog.Sensors.CurrentSensor currentSensor1 annotation (
    Placement(visible = true, transformation(origin={-6,68},   extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Electrical.Analog.Sources.SignalCurrent signalCurrent annotation (
      Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=-90,
        origin={112,42})));
  Modelica.Blocks.Sources.Step step(
    height=-100,
    offset=0,
    startTime=0.1)
    annotation (Placement(transformation(extent={{-8,-48},{12,-28}})));
  Modelica.Blocks.Math.Division division
    annotation (Placement(transformation(extent={{80,-54},{100,-34}})));
  Modelica.Electrical.Analog.Basic.Resistor resistor(R=20) annotation (
      Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=-90,
        origin={78,38})));
  Modelica.Blocks.Interfaces.RealOutput i_l annotation (
    Placement(visible = true, transformation(origin={-122,18},   extent = {{-10, -10}, {10, 10}}, rotation=-90), iconTransformation(origin={-102,38},   extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Interfaces.RealOutput v_o annotation (
    Placement(visible = true, transformation(origin={30,8},     extent = {{-10, -10}, {10, 10}}, rotation = 0), iconTransformation(origin={40,12},    extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Interfaces.RealOutput i_o annotation (
    Placement(visible = true, transformation(origin={18,50},    extent = {{-10, -10}, {10, 10}}, rotation = 0), iconTransformation(origin={28,54},    extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Sources.Constant const(k=500)
    annotation (Placement(transformation(extent={{-44,-116},{-24,-96}})));
  Modelica.Blocks.Sources.Step step1(
    height=200,
    offset=0,
    startTime=0.2)
    annotation (Placement(transformation(extent={{-8,-80},{12,-60}})));
  Modelica.Blocks.Interfaces.RealOutput sum annotation (Placement(
      visible=true,
      transformation(
        origin={92,-18},
        extent={{-10,-10},{10,10}},
        rotation=0),
      iconTransformation(
        origin={28,54},
        extent={{-10,-10},{10,10}},
        rotation=0)));
  Modelica.Blocks.Math.Add3 add3_1
    annotation (Placement(transformation(extent={{46,-48},{66,-28}})));
  Modelica.Blocks.Sources.Constant const1(k=0.5)
    annotation (Placement(transformation(extent={{-138,-68},{-118,-48}})));
equation
  connect(constantVoltage.p,inductor. p) annotation (
    Line(points={{-180,26},{-180,50},{-168,50}},        color = {0, 0, 255}));
  connect(constantVoltage.n,ground. p) annotation (
    Line(points={{-180,6},{-180,-30}},                                color = {0, 0, 255}));
  connect(constantVoltage.n,boost. dc_n1) annotation (
    Line(points={{-180,6},{-96,6}},        color = {0, 0, 255}));
  connect(pwm.fire,boost. fire_p) annotation (
    Line(points={{-92,-47},{-92,0}},       color = {255, 0, 255}));
  connect(boost.dc_p2,capacitor. p) annotation (
    Line(points={{-76,18},{-36,18}},                            color = {0, 0, 255}));
  connect(boost.dc_n2,capacitor. n) annotation (
    Line(points={{-76,6},{-60,6},{-60,-2},{-36,-2}},                    color = {0, 0, 255}));
  connect(capacitor.p,voltageSensor. p) annotation (
    Line(points={{-36,18},{-4,18}},                          color = {0, 0, 255}));
  connect(capacitor.n,voltageSensor. n) annotation (
    Line(points={{-36,-2},{-4,-2}},    color = {0, 0, 255}));
  connect(voltageSensor.v,v_o)  annotation (
    Line(points={{7,8},{30,8}},                             color = {0, 0, 127}));
  connect(capacitor.p,currentSensor1. p) annotation (
    Line(points={{-36,18},{-36,68},{-16,68}},       color = {0, 0, 255}));
  connect(currentSensor1.i,i_o)  annotation (
    Line(points={{-6,57},{-6,50},{18,50}},                         color = {0, 0, 127}));
  connect(inductor.n,currentSensor. p)
    annotation (Line(points={{-148,50},{-132,50}}, color={0,0,255}));
  connect(currentSensor.n,boost. dc_p1) annotation (Line(points={{-112,50},{
          -104,50},{-104,18},{-96,18}},
                                  color={0,0,255}));
  connect(i_l,i_l)
    annotation (Line(points={{-122,18},{-122,18}}, color={0,0,127}));
  connect(currentSensor.i,i_l)
    annotation (Line(points={{-122,39},{-122,18}}, color={0,0,127}));
  connect(voltageSensor.v,division. u2) annotation (Line(points={{7,8},{28,8},{
          28,-50},{78,-50}},       color={0,0,127}));
  connect(division.y,signalCurrent. i)
    annotation (Line(points={{101,-44},{124,-44},{124,42}},
                                                          color={0,0,127}));
  connect(currentSensor1.n,signalCurrent. p)
    annotation (Line(points={{4,68},{112,68},{112,52}},  color={0,0,255}));
  connect(voltageSensor.n,signalCurrent. n)
    annotation (Line(points={{-4,-2},{112,-2},{112,32}},    color={0,0,255}));
  connect(resistor.p,signalCurrent. p) annotation (Line(points={{78,48},{78,68},
          {112,68},{112,52}}, color={0,0,255}));
  connect(resistor.n,signalCurrent. n) annotation (Line(points={{78,28},{78,-2},
          {112,-2},{112,32}},  color={0,0,255}));
  connect(division.u1, sum) annotation (Line(points={{78,-38},{72,-38},{72,-18},
          {92,-18}}, color={0,0,127}));
  connect(step.y, add3_1.u1) annotation (Line(points={{13,-38},{38,-38},{38,-30},
          {44,-30}}, color={0,0,127}));
  connect(step1.y, add3_1.u2) annotation (Line(points={{13,-70},{38,-70},{38,
          -38},{44,-38}}, color={0,0,127}));
  connect(const.y, add3_1.u3) annotation (Line(points={{-23,-106},{36,-106},{36,
          -46},{44,-46}}, color={0,0,127}));
  connect(add3_1.y, division.u1) annotation (Line(points={{67,-38},{72,-38},{72,
          -38},{78,-38}}, color={0,0,127}));
  connect(const1.y, pwm.dutyCycle)
    annotation (Line(points={{-117,-58},{-98,-58}}, color={0,0,127}));
  annotation (
    Icon(coordinateSystem(preserveAspectRatio=false)),
    Diagram(coordinateSystem(preserveAspectRatio=false)),
    uses(Modelica(version="4.0.0")),
    version="1",
    conversion(noneFromVersion=""));
end boost_converter;