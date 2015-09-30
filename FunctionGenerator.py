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

        
