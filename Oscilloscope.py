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
            #print "int"
        elif(isinstance(instrumentSelector, str)):
            self.addr = instrumentSelector
            #print "str"
        
        self.dso = win32com.client.Dispatch("LeCroy.ActiveDSOCtrl.1")
        # Instantiate instrument
        self.connect()
        self.outputBuffer = ''
        self.channels = ['C1','C2']
        self.memories = ['M1','M2','M3','M4']
        self.traces = ['F1','F5','F6','F7','F8']
        self.xtrigs = ['EX','EX10','EX5']
        self.linetrigs = ['LINE']
        self.ndiv = 10
        
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
        
    def write(self, command,echo=False):
        """
        Writes the given custom command to the instrument

        :param command:    A string representing the oscilloscope command
        """
        if (self.addr != ''):
            if echo:
                print command
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
    
    def setupWaveForm(self,n=0,sparsing=1,firstpoint=0,segment=0):
        """
        Specifies the amount of data in a waveform to be transmitted to the controller.
        Sparsing (SP): The sparsing parameter defines the interval between data points. For
        :param n: The number of points parameter indicates how many points should be transmitted. For example:
            NP = 0 sends all data points
            NP = 1 sends 1 data point
            NP = 50 sends a maximum of 50 data points
            NP = 1001 sends a maximum of 1001 data points
        :param sparsing: interval between data points 
            SP = 0 sends all data points
            SP = 1 sends all data points
            SP = 4 sends every 4th data point
        :param firstpoint: The first point parameter specifies the address of the first data point to be sent. For waveforms acquired in sequence mode, this refers to the relative address in the given segment. For example:
            FP = 0 corresponds to the first data point
            FP = 1 corresponds to the second data point
            FP = 5000 corresponds to data point 5001
        :param segment: The segment number parameter indicates which segment should be sent if the waveform was acquired in sequence mode. This parameter is ignored for non-segmented waveforms. For example:
            SN = 0 all segments
            SN = 1 first segment
            SN = 23 segment 23
        """
        cmd = 'WFSU NP,' + str(n) + ',SP,' + str(sparsing) + ',FP,' + str(firstpoint) + ',SN,' + str(segment)
        self.write(cmd)
        
    def dumpWaveform(self,channel='C1'):
        """
        Shows the hexidecimal contents of the specified waveform
        
        :param channel: String specifying which trace to use {'C1'|'C2} or {1|2}. Defaults to C1 if blank.
        """
        channel = self.checkInput(channel,self.channels,'C')
        cmd = channel + ':WAVEFORM?'
        self.write(cmd)
    
    def sequence(self,mode='ON',segments=[],max_size=[]):
        """
        sets up the scope for sequence mode acquisition
        :param mode: 'ON' or 'OFF'
        :param segments: number of segments to record. Limited by the max memory length per channel (see guide)
        """
        mode = self.getOnOff(mode)
        cmd = 'SEQ ' + mode
        if not(segments==[]):
            cmd = cmd + ',' + str(segments)
            if not(max_size==[]):
                cmd = cmd + ',' + str(max_size)
        self.write(cmd)
        
    def arm(self):
        """
        Arms the scope and forces a single acquisition if it is already armed.
        """
        cmd = 'ARM'
        self.write(cmd)
    
    def wait(self,timeout=[]):
        """
        wait for the current acquisition to be completed.
        :param timeout: timeout in seconds. Leave blank for indefinite
        """
        if (timeout == []):
            cmd = 'WAIT'
        else:
            cmd = 'WAIT ' + str(timeout)
        self.write(cmd)
        
    def setTriggerMode(self,mode='NORM'):
        """
        Sets the trigger mode of the oscilloscope
        
        :param mode: string specifying mode {'AUTO'|'NORM'|'SINGLE'|'STOP'}
        """
        mode = self.checkInput(mode,['AUTO','NORM','SINGLE','STOP'],name='trigger mode')
        self.setParam('TRMD',mode)
    
    def setTriggerCoupling(self,source,coupling):
        """
        Sets the coupling mode of the specified trigger source.
        :param source: trigger source {C1, C2, C3, C4, EX, EX10,ETM10}
        :param coupling: {DC} for channel source
                         {DC50, GND, DC1M, AC1M} for external source
        """
        source = self.checkInput(source,self.channels+self.xtrigs,'C')
        if (source[0][0] == 'C'):
            coupling = self.checkInput(coupling,['AC','DC','HF','HFREJ','LFREJ']) 
        else:
            coupling = self.checkInput(coupling,['DC50','GND','DC1M','AC1M'])
        self.setParam(source + ':TRCP',coupling)

    def setTriggerSlope(self,slope):
        """
        Sets the Trigger slope direction
        
        :param slope: POS or NEG
        """
        slope = self.checkInput(slope,['POS','NEG'],name='slope')
        self.setParam('TRSL',slope)
        
    def setTrigger(self,source,type='EDGE',mode='',slope='',delay=[],level=[],coupling=''):
        """
        sets the Trigger source adn type. Can be used to set the mode, slope, delay, level, coupling and hold types
        """
        if not(type == 'EDGE'):
            raise NameError('Non-Edge triggering modes not yet supported with setTrigger()')
        
        source = self.checkInput(source,self.channels+self.xtrigs,'C')
        cmd = 'TRSE '+ type + ',SR,' + source
        self.write(cmd)
        if not(mode==''):
            self.setTriggerMode(mode)
        if not(slope==''):
            self.setTriggerSlope(slope)
        if not(delay==[]):
            self.setParam('TRDL',delay)
        if not(level==[]):
            self.setParam('TRLV',level)
        if not(coupling==''):
            self.setTriggerCoupling(source,coupling)
            
    # Display Control
    
    def clearSweeps(self):
        """
        restarts the cumulative processing functions: summed or continuous average, extrema, FFT power average, histogram, pulse parameter statistics, Pass/Fail counters, and persistence.
        """
        cmd = 'CLSW'
        self.write(cmd)
    
    def loadParams(self, filename):
        """
        Loads a series of settings from a text file.
        Empty lines and lines beginning with # are ignored

        :param str filename: string name of text file to read from
        """

        print("Loading from " + filename + ":")
        f = open(filename, 'r')
        for line in f:
            sline = line.strip()
            print(sline)
            if (len(sline) > 0) and (sline[0][0] != '#'):
                self.write(sline)
                                  
    def setVisibility(self,trace,visibility):
        """
        turn a specific trace on or off
        :param trace: index of channel {1|2} or string 'C1','C2','F1'...'F8'
        :param visibility: {'ON'|'OFF'}
        """
        trace = self.checkInput(trace,self.channels+self.traces,'C')
        visibility = self.getOnOff(visibility)
        self.setParam(trace + ':TRA',visibility)           
            
    # Memory Management
            
    def clearMem(self,bank='M1'):
        """
        Clears the specified memory bank
        
        :param bank: string specifying memory bank {'M1'|'M2'|'M3'|'M4'} or integer {1|2|3|4}
        """
        bank = self.checkInput(bank,self.memories,'M')
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
        header = self.checkInput(header,self.channels+self.memories+self.traces+self.xtrigs+self.linetrigs,'C')
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
        format = self.checkInput(format,['LONG','SHORT','OFF'])
        cmd = 'COMM_HEADER:' + format
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
    
    def formatWaveForm(self,data_type='WORD',encoding='BIN',block_format='DEF9'):
        """
        Selects the format the oscilloscope uses to send waveform data. The available options allow the data type, the encoding mode to be modified from the default settings, and the block format.
        
        :param data_type: = {'BYTE'|'WORD'}
        :param encoding: = {'BIN'} <-- 'HEX' might work, too?
        :param  block_format: = 'DEF9'
        """
        cmd = 'CFMT ' + block_format + ',' + data_type + ',' + encoding
        self.write(cmd)
    
    #Input Parsing
    def checkInput(self,id,idList,intprefix='',caseInsensitive=True,name='input'):
        """
        Compares a string against a list of possibilities, returning a valid string or and error. Ensures valid calls to the oscilloscope.
        
        :param id: the candidate string or integer
        :param idList: List of acceptable string inputs
        :param intprefix: [optional] if given a numeric input, the number will be appended to this character
        """
        if not isinstance(id,str):
            id = intprefix + str(id)
        for i in idList:
            if ((id == i) | (caseInsensitive & (id.lower() == i.lower()))):
                return i
        raise NameError('Invalid ' + name + ' "' + str(id) + '". Acceptable values are ' + str(idList))    
    
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