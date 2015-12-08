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
        
        self.dso = win32com.client.Dispatch("LeCroy.ActiveDSOCtrl.1")
        # Instantiate instrument
        self.connect()
        self.outputBuffer = ''
        
    # Basic Oscilloscope Communication Protocol    
    
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
        self.outputBuffer = self.dso.ReadString(bytes)
        return self.outputBuffer
    
    def readClearError(self):
        """
        reads and clears the contents of the CoMmand error Register which specifies the last syntax error type detected by your oscilloscope.
        """
        cmd = 'CMR?'
        self.write(cmd)
        lastErrorID = int(self.readBuffer(80))
        errorList = {0:"No Error",1:"Unrecognized command/query header",2:"Illegal header path",3:"Illegal number",4:"Illegal number suffix",5:"Unrecognized keyword",6:"String error",7:"GET embedded in another message",10:"Arbitrary data block expected",11:"Non-digit character in byte count field of arbitrary data block",12:"EOI detected during definite length data block transfer",13:"Extra bytes detected during definite length data block transfer"}
        print errorList[lastErrorID]
        
    # Acquisition Control
    
    def getChannelID(self,channel):
        """
        Converts an integer channel to a string channel ID
        
        :param channel: String specifying which trace to use {'C1'|'C2} or {1|2}
        """
        if (len(str(channel)) == 1):
            channel = 'C' + str(channel)
        else:
            if (len(str(channel)) == 2):
                channel = str(channel)
            else:
                raise NameError('Invalid Channel ID ' + str(channel))
            
        if (channel[0][0] == 'C') & ((channel[1][0] == '1') | (channel[1][0] == '2')):
            return channel
        else:
            raise NameError('Invalid Channel ID ' + channel)
            return
            
    def dumpWaveform(self,channel='C1'):
        """
        Shows the hexidecimal contents of the specified waveform
        
        :param channel: String specifying which trace to use {'C1'|'C2} or {1|2}. Defaults to C1 if blank.
        """
        channel = self.getChannelID(channel)
        cmd = channel + ':WAVEFORM?'
        self.write(cmd)
    
    def arm(self):
        """
        Arms the scope and forces a single acquisition if it is already armed.
        """
        cmd = 'ARM'
        self.write(cmd)
    
    # Display Control
    
    def clearSweeps(self):
        """
        restarts the cumulative processing functions: summed or continuous average, extrema, FFT power average, histogram, pulse parameter statistics, Pass/Fail counters, and persistence.
        """
        cmd = 'CLSW'
        self.write(cmd)
    
    def setVisibility(self,trace,visibility):
        """
        turn a specific trace on or off
        :param trace: index of channel {1|2} or string 'C1','C2','F1'...'F8'
        :param visibility: {'ON'|'OFF'}
        """
        trace = self.getTraceID(trace)
        visibility = self.getOnOff(visibility)
        cmd = trace + ':TRA ' + visibility
        self.write(cmd)
    
    def getOnOff(self,bool):
        """
        converts 1 and True to ON and 0 and False to OFF
        """
        if ((str(bool) == 'True') | (str(bool) == '1') | (str(bool) == 'ON')):
            return 'ON'
        elif ((str(bool) == 'False') | (str(bool) == '0') | (str(bool) == 'OFF')):
            return 'OFF'
        else:
            raise NameError('Invalid boolean On/Off')
            
    
    def getTraceID(self,trace):
        """
        get trace ID
        
        :param trace: index of channel {1|2} or string 'C1','C2','F1'...'F8'
        """
        traceList = ['C1','C2','F1','F2','F3','F4','F5','F6','F7','F8']
        if (len(str(trace)) == 1):
            trace = 'C' + str(trace)
        for t in traceList:
            if (trace == t):
                return t
        raise NameError('Invalid trace ID ' + str(trace))    
        
    # Memory Management
    
    def getMemID(self,bank):
        """
        Converts input to string memory bank ID
        
        :param bank: string specifying memory bank {'M1'|'M2'|'M3'|'M4'} or integer {1|2|3|4}
        """
        if (len(str(bank)) == 1):
            bank = 'M' + str(bank)
        else:
            if (len(str(bank)) == 2):
                bank = str(bank)
            else:
                raise NameError('Invalid Memory ID ' + str(bank))
            
        if (bank[0][0] == 'M') & ((bank[1][0] == '1') | (bank[1][0] == '2') | (bank[1][0] == '3') | (bank[1][0] == '4')):
            return bank
        else:
            raise NameError('Invalid Memory ID ' + bank)
            return
            
    def clearMem(self,bank='M1'):
        """
        Clears the specified memory bank
        
        :param bank: string specifying memory bank {'M1'|'M2'|'M3'|'M4'} or integer {1|2|3|4}
        """
        bank = self.getMemID(bank)
        cmd = 'CLM ' + bank
        self.write(cmd)
        
    # Abstract Parameter I/0    
    
    def setParam(self,parameter,value):
        """
        constructs and sends the command to set a particular parameter
        
        :param parameter: A string representing the parameter to be set i.e. 'C1:VDIV' or 'TDIV'
        :param value: A numeric or string value to set
        """
        cmd = parameter + ' ' + str(value)
        self.write(cmd)
        
    def queryParam(self,parameter):
        """
        constructs and sends the command to query a particular parameter. The result is stored in the oscilloscope's output buffer
        
        :param parameter: A string representing the parameter to be queried
        """
        cmd = parameter + '?'
        self.write(cmd)
            
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
        print cmd
        self.write(cmd)
        
    # Formatting/Configuration
    
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
    
    def formatWaveForm(self,data_type='WORD',encoding='BIN',block_format='DEF9'):
        """
        Selects the format the oscilloscope uses to send waveform data. The available options allow the data type, the encoding mode to be modified from the default settings, and the block format.
        
        :param data_type: = {'BYTE'|'WORD'}
        :param encoding: = {'BIN'} <-- 'HEX' might work, too?
        :param  block_format: = 'DEF9'
        """
        cmd = 'CFMT ' + block_format + ',' + data_type + ',' + encoding
        self.write(cmd)
        
    #VBS Protocols
    
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
     
    #Miscellaneous
    def buzz(self):
        """
        Oscilloscope makes a short beep
        """
        cmd = 'BUZZ BEEP'
        self.write(cmd)