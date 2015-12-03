"""
fgen_setup_pulse.py
"""
from FunctionGenerator import FunctionGenerator
import numpy as np
import time
__author__ = "Peter Hollender (pjh7)" 

if __name__=="__main__":
    fgen=FunctionGenerator(1) #Instantiate function generator
    time.sleep(1)
    fgen.clearErrors()
    print fgen.getIdn()
    time.sleep(1)
    fgen.setOutput(1,'OFF')
    fgen.setOutput(2,'OFF')
    fgen.loadSettings('params.txt')
    print fgen.getError() # Gets error off the queue
    


