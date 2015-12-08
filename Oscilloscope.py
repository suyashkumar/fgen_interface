class Oscilloscope:
    """
    This class wraps much of the functionality required to control a LeCroy WaveSurfer 42Mxs-B over ethernet
    """
    __author__ = "Peter Hollender"
    # Based on Suyash Kumar's FunctionGenerator code
    
    # Holds USBTMC addresses of fgens in the Nightingale lab
    selectorMap = {1: "IP:192.168.3.220"}

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
        import win32com.client

        # Check if instrumentSelector is a string or an int, assign/lookup
        # address as needed
        if (isinstance(instrumentSelector, int)):
            self.addr = self.selectorMap[instrumentSelector]
            print "int"
        elif(isinstance(instrumentSelector, str)):
            self.addr = instrumentSelector
            print "str"
        
        self.dso = 'win32com.client.Dispatch("LeCroy.ActiveDSOCtrl.1")'  # Instantiate instrument
        self.connect()
        #
    def connect(self):
        """
        Connects the scope to the object
        """
        if (self.addr != ''):
            self.dso.MakeConnection(self.addr)
            
    def disconnect(self):
        """
        Disconnects the scope from the object
        """
        self.dso.Disconnect()
        
    def write(self, command):
        """
        Writes the given custom command to the instrument

        :param command:    A string representing the oscilloscope command
        """
        if (self.addr != ''):
            self.dso.WriteString(command,1)
        else:
            print command
        
    def readBuffer(self,bytes=80):
        """
        returns the string in the oscilloscope's output buffer
        
        :param bytes: optional specifier for the number of bytes to read. default is 80.
        """
        
        return self.dso.ReadString(bytes)
        
    def setParam(self,header,parameter,value):
        """
        constructs and sends the command to set a particular parameter
        
        :param header: A string representing a resource
            C1|C2 - Channels
            M1|M2|M3|M4 - Memories
            F1|F2|F3|F4|F5|F6|F7|F8 - Traces
            EX|EX10|EX5 - External Triggers
            LINE - LINE source for trigger
        :param parameter: A string representing the parameter to be set
        :param value: A numeric or string value to set
        """
        cmd = ''+ header + ':' + parameter + ' ' + str(value)
        self.write(cmd)
        
    def queryParam(self,header,parameter):
        """
        constructs and sends the command to query a particular parameter. The result is stored in the oscilloscope's output buffer
        
        :param header: A string representing a resource
            C1|C2 - Channels
            M1|M2|M3|M4 - Memories
            F1|F2|F3|F4|F5|F6|F7|F8 - Traces
            EX|EX10|EX5 - External Triggers
            LINE - LINE source for trigger
        :param parameter: A string representing the parameter to be queried
        """
        cmd = ''+ header + ':' + parameter + '?'
        self.write(cmd)
    
    def formatByteOrder(self,order=1):
        """
        Sets the order of bytes for waveform dumping
        :param order: 0 = high byte first, 1 = low byte first, Default is 1
        """
        if (order == 1) | (order == 0):
            cmd = 'COMM_ORDER ' + str(order)
            self.write(cmd)
        else:
            print('COMM_ORDER must be 0 or 1')
            
    def inspectParam(self,header,parameter,format='default'):    
        """
        constructs and sends the command to inspect a particular parameter. The result is printed to the standard output. WARNING - if the data block contains thousands of items the output will be VERY LONG.
        
        :param header: A string representing a resource
            C1|C2 - Channels
            M1|M2|M3|M4 - Memories
            F1|F2|F3|F4|F5|F6|F7|F8 - Traces
            EX|EX10|EX5 - External Triggers
            LINE - LINE source for trigger
        :param parameter: A string representing the parameter to be inspected
        :param format: [optional] string to format output as 'byte'|'word'
        """
        cmd = ''+ header + ':INSPECT? "' + parameter + '"'
        if(format != 'default'):
            cmd = cmd + ', ' + format
        self.write(cmd)
        
    def dumpWaveform(self,header='C1'):
        """
        Shows the hexidecimal contents of the specified waveform
        
        :param header: String specifying which trace to use {'C1'|'C2}. Defaults to C1 if blank.
        """
        cmd = header + ':WAVEFORM?'
        self.write(cmd)
        
    def formatHeader(self,format):
        """
        sets the oscilloscope query response format
        
        :param format: String representing the format {'long','short','off'}
            example:
            long:   C1:TRIG_SLOPE NEG 
            short:  C1:TRSL NEG
            off:    NEG
        """
        format = format.upper()
        if (format == 'LONG') | (format == 'SHORT') | (format == 'OFF'):
            cmd = 'COMM_HEADER:' + format
            self.write(cmd)
        else:
            print 'invalid Header format ' + format

    def VBScommand(self,command):
        """
        formats and writes the VBS command
        
        :param command:    A string representing the VBS command
        """
        cmd = 'VBS  \''+command+' \' '
        self.write(cmd)
        
    def VBSquery(self,command):
        """
        dumps the requested value to the oscilloscope's memory
        
        :param command: string to the requested parameter
        """
        
        cmd = 'VBS?  \'return='+command+' \' '
        self.write(cmd)
    
    def VBSreturn(self,command):
        """
        dumps the requested value to the oscilloscope's memory, and then returns the value
        
        :param command: string to the requested parameter
        """
        self.VBSquery(command)
        return self.readBuffer()
     
        