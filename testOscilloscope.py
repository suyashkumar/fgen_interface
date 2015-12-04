from Oscilloscope import Oscilloscope
osc = Oscilloscope(1)
osc.write('C1:VDIV .06')
osc.writeVBS('app.Measure.P1.ParamEngine="Mean"')
osc.dumpVBS('app.Measure.P1.Out.Result.Value')
osc.getValue()