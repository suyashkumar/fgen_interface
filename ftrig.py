from FunctionGenerator import FunctionGenerator
fgen = FunctionGenerator(1)  # Instantiate function generator
fgen.instr.write('TRIGGER1:SOURCE BUS') # Make sure that outputs are on
fgen.instr.write('TRIGGER2:SOURCE BUS')
fgen.sendTrigger()