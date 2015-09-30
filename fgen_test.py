"""
fgen_test.py
"""
from FunctionGenerator import FunctionGenerator
__author__ = "Suyash Kumar (sk317)" 

if __name__=="__main__":
    fgen=FunctionGenerator(1) #Instantiate function generator
    print fgen.getIdn() # Print identity of function generator
    fgen.pushSin(10)
    fgen.loadFromMemory("HIFU_SIM") 
    print fgen.instr.ask("SYSTem:ERRor?")

