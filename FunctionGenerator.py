class FunctionGenerator:
    """
    This class wraps much of the functionality required to control an Agilent
    33522A function generator over USB.
    """
    __author__ = "Suyash Kumar"

    # Holds USBTMC addresses of fgens in the Nightingale lab
    selectorMap = {1: "USB0::2391::8967::INSTR"}

    def __init__(self, instrumentSelector):
        """
        The constructor for the function generator object needs to know the
        USBTMC address of the device being used. The address can be directly
        supplied as a string, or an integer representing the function generator
        in Dr. Nightingale's lab can be passed.

        :param instrumentSelector: Either a string representing the USBTMC
        address of the function generator or a int identifier representing one
        of the function generators in Kathy Nightingale's lab.
        """
        import usbtmc

        # Check if instrumentSelector is a string or an int, assign/lookup
        # address as needed
        if (isinstance(instrumentSelector, int)):
            self.addr = self.selectorMap[instrumentSelector]
            print "int"
        elif(isinstance(instrumentSelector, str)):
            self.addr = instrumentSelector
            print "str"

        self.instr = usbtmc.Instrument(self.addr)  # Instantiate instrument

    def getIdn(self):
        """
        Asks the function generator to identify itself and retuns a unicode
        string of the response.

        :returns: identity -- a unicode string the attached function generator
        uses to identify itself.
        """
        return self.instr.ask("*IDN?")

    def write(self, command):
        """
        Writes the given custom SCPI command to the instrument over usbtmc

        :param command:    A string representing the SCPI command
        """
        self.instr.write(command)

    def getStatus(self):
        """
        Gets function generator's status and what output/settings are currently
        set to

        :returns: status -- string of current status
        """
        return self.instr.ask("APPLy?")

    def pushSin(self, frequency, amplitude=1, offset=0):
        """
        Pushes sin wave of the given parameters to function generator AND turns
        on output

        :param frequency:  the frequency in Hz of the sin wave
        :param amplitude:  (optional, default set to 1V), amplitude of the sin
        wave in volts
        :param offset:     (optional, default set to 0V), dc offset of sin wave
        in volts.
        """
        self.write("APPL:SIN "+str(frequency)+", \
                   "+str(amplitude)+", "+str(offset))

    def setSin(self, frequencey, amplitude=1, offset=0):
        print "Set sin"

    def getError(self):
        """
        Gets the next error off the queue.
       
        :returns: error -- The next error off the queue
        """
        return self.instr.ask("SYSTem:ERRor?")

    def loadFromMemory(self, stateName):
        """
        Loads given function generator state from a .sta file already on the
        function generator's memory.

        :param stateName: The string name of the state (without the .sta
        extension). For example "HIFU_SIM"
        """
        self.instr.write("MMEMory:LOAD:STATe \""+str(stateName)+"\"")

    def loadArbitraryWaveform(self, intWaveform):
        """
        Loads arbitrary waveform into function generator's VOLATILE memory
        (supports between 8 and 16,000 points). MUST be integers between -2047
        and +2047

        :param intWaveform:    A list of integers between -2047 and +2047 with
        length between 8 and 16,000 inclusive.
        """
        import sys

        if (not all((isinstance(n, int) and n >= -2047 and n <= 2047)
                    for n in intWaveform)):
            print("Oops, you input integer wavefrom is not well formed. The "
                  "problem is one of the following:")
            # Raise custom Exception here
            # TODO: FINISH
            sys.exit(1)
        # self.instr.write("DATA:DEL VOLATILE")
        sendString = "DATA:DAC VOLATILE, " + \
            str(intWaveform)[1:len(str(intWaveform))-1]
        print sendString
        self.instr.write(sendString)
    def loadSettings(self, filename):
        """
        Loads a series of settings from a text file.
        Empty lines and lines beginning with # are ignored
        TODO: Query error stack after each line, to make sure we abort in case of error. Should probably turn all outputs OFF in such a case, too.
        """
        import time
        print "Loading from " + filename + ":"
        f = open(filename,'r')
        for line in f:
            sline = line.strip()
            print sline
            if (len(sline)>0) and (sline[0][0] != '#'):
                self.instr.write(sline)
            time.sleep(0.1)
    def clearErrors(self):
        """
        Clears our any Error statuses from the function generator, eliminating the need to power cycle.
        """
        self.instr.write("*CLS")
    def setOutput(self,channel,state):
        """
        sets the specified channel to the ON or OFF state
        """
        if (channel == 1) or (channel == 2):
            if (state == 'ON') or (state == 1):
                cmdstate = 'ON'
            else: 
                if (state == 'OFF') or (state == 0):
                    cmdstate = 'OFF'
                else:
                    print('ERROR:Invalid State')
                    return
        else:
            print('ERROR:Invalid Channel')
            return
        syscmd = 'OUTPUT'+str(channel)+" "+cmdstate
        print syscmd
        self.instr.write(syscmd)
    def pushArbitraryWaveform(self, intWaveform):
        """
        Loads arbitrary waveform into memory according to
        loadArbitraryWaveform() and then selects and outputs the waveform.

        :param intWaveform:    A list of integers between -2047 and +2047 with
        length between 8 and 16,000 inclusive.
        """

        self.loadArbitraryWaveform(intWaveform)  # Loads arb waveform into
                                                 # volatile memory
        self.instr.write("FUNC:ARB VOLATILE")  # Selects volatile for the arb
                                               # shape
        self.instr.write("FUNC:SHAP ARB")  # Selects the arb function
