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
        
        self.scope = win32com.client.Dispatch("LeCroy.ActiveDSOCtrl.1")  # Instantiate instrument
        self.scope.MakeConnection(self.addr)
        print 'OK'
        
    def disconnect(self):
        """
        Disconnects the scope from the object
        """
        self.scope.Disconnect()
        
    def write(self, command):
        """
        Writes the given custom command to the instrument

        :param command:    A string representing the oscilloscope command
        """
        self.scope.WriteString(command,1)
        
    def writeVBS(self,command):
        """
        formats and writes the VBS command

        :param command:    A string representing the VBS command
        """
        cmd = 'VBS  \''+command+' \' '
        self.scope.WriteString(cmd,1)
        
    def dumpVBS(self,command):
        """
        dumps the requested value to the oscilloscope's memory
        
        :param command: string to the requested parameter
        """
        
        cmd = 'VBS?  \'return='+command+' \' '
        self.scope.WriteString(cmd,1)
        
    def getValue(self):
        """
        returns the value (up to 80 bytes) of the last-dumped measurement
        """
        
        return self.scope.ReadString(80)
    
    def getVBS(self,command):
        """
        dumps the requested value to the oscilloscope's memory, and then returns the value
        
        :param command: string to the requested parameter
        """
        self.dumpVBS(command)
        return self.getValue()
     
        