"""
fgen_setup_pulse.py
"""
from FunctionGenerator import FunctionGenerator
# import numpy as np
# import time

__author__ = "Peter Hollender (pjh7)"


def main():
    fgen = FunctionGenerator(1)  # Instantiate function generator
    fgen.reset()
    print(fgen.getIdn())
    fgen.setOutput(1, 'OFF')
    fgen.setOutput(2, 'OFF')
    fgen.loadSettings('params.txt')
    print(fgen.getError())  # Gets error off the queue

if __name__ == "__main__":
    main()
