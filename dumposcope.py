from Oscilloscope import Oscilloscope
import matplotlib.pyplot as plt
import time

def main():
    osc = Oscilloscope(1)
    osc.write('COMM_HEADER OFF')
    osc.queryParam('WFSU')
    print osc.readBuffer(100)
    nPoints = 5000
    osc.setupWaveForm(n=nPoints,sparsing=100,firstpoint=5,segment=0)
    #osc.write('C1:INSPECT? "FIRST_VALID_PNT"')
    #print osc.dso.ReadString(1e6)
    #osc.write('C1:INSPECT? "LAST_VALID_PNT"')
    #print osc.dso.ReadString(1e6)
    osc.write('C1:INSPECT? "SIMPLE", BYTE')
    s = osc.dso.ReadString(1e9)
    l = s.split()
    ml = [i for i in l if is_number(i)]
    y = [float(i) for i in ml]
    x = range(0,len(y))
    plt.plot(x,y,'bo')
    plt.show()

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
if __name__ == "__main__":
    main()