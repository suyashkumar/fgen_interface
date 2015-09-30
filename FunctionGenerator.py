import usbtmc
class FunctionGenerator:
    """
    This class wraps much of the functionality required to control an Agilent 33522A function generator over USB.
    """
    __author__ = "Suyash Kumar"

    selectorMap={1:"USB0::2391::8967::MY50000586::INSTR"} # Holds USBTMC addresses of fgens in the Nightingale lab 

    def __init__(self, instrumentSelector):
        """
        The constructor for the function generator object needs to know the USBTMC address of the device being used. The address can be directly supplied as a string, or an integer representing the function generator in Dr. Nightingale's lab can be passed. 
        Args:
            instrumentSelector: Either a string representing the USBTMC address of the function generator or a int identifier representing one of the function generators in Kathy Nightingale's lab. 
        """
        # Check if instrumentSelector is a string or an int, assign/lookup address as needed
        if (isinstance(instrumentSelector, int)):
            self.addr=self.selectorMap[instrumentSelector]
            print "int"
        elif(isinstance(instrumentSelector, str)):
            self.addr=instrumentSelector
            print "str"

        self.instr =  usbtmc.Instrument(self.addr) # Instantiate instrument

    def getIdn(self):
        """
        Asks the function generator to identify itself and retuns a unicode string of the response.
        Returns:
            identity:   a unicode string the attached function generator uses to identify itself.
        """
        return self.instr.ask("*IDN?")
    def write(self,command):
        """
        Writes the given custom SCPI command to the instrument over usbtmc
        Args:
            command:    A string representing the SCPI command 
        """
        self.instr.write(command)
    def getStatus():
        """
            Gets function generator's status and what output/settings are currently set to
            Returns:
              status:   string of current status  
        """
        return self.instr.ask("APPLy?")
    def pushSin(self,frequency, amplitude=1, offset=0):
        """
        Pushes sin wave of the given parameters to function generator AND turns on output
        Args:
            frequency:  the frequency in Hz of the sin wave
            amplitude:  (optional, default set to 1V), amplitude of the sin wave in volts
            offset:     (optional, default set to 0V), dc offset of sin wave in volts. 
        """
        self.write("APPL:SIN "+str(frequency)+", "+str(amplitude)+", "+str(offset))
    def setSin(self, frequencey, amplitude=1, offset=0):
        print "Set sin"
    def getError(self):
        """
        Gets the next error off the queue.
        Returns:
            error:  The next error off the queue
        """
        return self.instr.ask("SYSTem:ERRor?")

    def loadFromMemory(self, stateName):
        """
        Loads given function generator state from a .sta file already on the function generator's memory.
        Args:
            stateName:  The string name of the state (without the .sta extension). For example "HIFU_SIM"
        """
        self.instr.write("MMEMory:LOAD:STATe \""+str(stateName)+"\"")
        
        
        
