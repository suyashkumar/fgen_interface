"""
fgen_test.py
"""
from FunctionGenerator import FunctionGenerator
import numpy as np
__author__ = "Suyash Kumar (sk317)" 

if __name__=="__main__":
    fgen=FunctionGenerator(1) #Instantiate function generator
    print fgen.getIdn() # Print identity of function generator
    #fgen.pushSin(20)
    #fgen.loadFromMemory("HIFU_SIM") # Loads the stored config "HIFU_SIM"
    fgen.pushArbitraryWaveform(list(np.linspace(-2000,2000,200,dtype=np.int))
)
    print fgen.getError() # Gets error off the queue
    print list(np.linspace(-2000,2000,100,dtype=np.int16))


