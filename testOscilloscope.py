from Oscilloscope import Oscilloscope
osc = Oscilloscope('')
osc.setParam('C1','VDIV',.06)
osc.VBScommand('app.Measure.P1.ParamEngine="Mean"')
osc.VBSquery('app.Measure.P1.Out.Result.Value')
