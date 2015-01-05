# Author: Nicholas Weir
# Date: 6/5/14
# Purpose: Cutting I-V measurements time from hours to minutes

import time
import serial as _serial

# Must Change COM ports in program to match the ones used
# in the computer, they change everytime replugged

"""
SR 570 Low-Noise Current Pre-Amplifier
"""


class PreAmplifier:
    def __init__(self, port):
        self.serial = _serial.Serial(
            port=port,
            baudrate=9600,
            parity=_serial.PARITY_NONE,
            stopbits=_serial.STOPBITS_TWO,
            bytesize=_serial.EIGHTBITS,
        )
        self.bias = None
        self.sensitivity = -1

        portcheck(self.serial)

    def __del__(self):
        self.serial.close()
        
    def set_sensitivity(self, val):
        # Changes Sensitivity, notation n,u is used
        sens_code = {'2n': 10, '20n': 13, '200n': 16, '2u': 19, '20u': 22,
                     '200u': 25}
        v = str(val)
        input = "SENS" + sens_code[v] + "\n"
        self.serial.write(input)
        self.sensitivity = v

        #sens_real = {'2n': 2e-9, '20n': 2e-8, '200n': 2e-7, '2u': 2e-6, 
        #             '20u': 2e-5, '200u': 2e-4}
        
                
    # Turn Bias On/Off (1/0)
    #def biason(val):
    #    mes = "BSON" + str(int(val)) + "\n"
    #    curc.write(mes.encode())
    #    return val


    # Changes Bias -5 to 5
    def set_bias_millivolt(self, val):
        input = "BSLV" + str(val) + "\n"
        self.serial.write(input)

    # Clears overload, Never used
    #def clear():
    #    mes = "ROLD" + "\n"
    #    curc.write(mes.encode())
    #    return None

    # Manual Sensivity checker, Could be improved greatly
    def sencheck():
        mes1 = int(raw_input("Adjust sensitivity (1/0)?: "))
        while mes1:
            mes = raw_input("Adjust Sensitivity (200u,20u.. etc): ")
            sensch(str(mes))
            try:
                mes1 = int(raw_input("Again (1/0)? (Remember to wait!!): "))
            except:
                print("Invalid Input")
                mes1 = int(raw_input("Again (1/0)? (Remember to wait!!): "))
        return None


    # Auto Sensitivity checker
    def sencheck2():
        n = 1
        while n:
            mes = raw_input("Adjust Sensitivity: ")
            if mes == '':
                pass
                n = 0
            else:
                sensch(str(mes))
        return None


"""
SR 760 FFT Spectrum Analyzer
"""


class SpectrumAnalyzer:
    def __init__(self, port):
        self.serial = _serial.Serial(
            port=port,
            baudrate=19200,
            parity=_serial.PARITY_NONE,
            stopbits=_serial.STOPBITS_ONE,
            rtscts=0,
            dsrdtr=0,
            bytesize=_serial.EIGHTBITS,
        )
        
        self.trace = 0

        portcheck(self.serial)

    def __del__(self):
        self.serial.close()

    def getfft(self):
        input = "SPEC?" + str(self.trace) + "0,154"
        # From http://stackoverflow.com/questions/676172/full-examples-of-using-pyserial-package
        # send the character to the device
        # (note that I append a \r\n carriage return and line feed to the characters - this is requested by my device)
        self.serial.write(input + '\r\n')
        out = ''
        # let's wait one second before reading output (let's give device time to answer)
        time.sleep(1)
        while self.serial.inWaiting() > 0:
            out += self.serial.read(1)

        if out != '':
            return out
        
    def donothing():
        print "I'm here!"
        
    def identify(self):
        self.serial.write("*IDN?\r\n")

            
def portcheck(ser):
    if ser.isOpen():
        ser.flushInput()
        ser.flushOutput()
        ser.close()
    ser.open()

# Get Sensitivity times fft value
def value(sen=None, fft=None):
    if sen is None:
        value = float(getfft()) * senreal[sensitivity]
    else:
        value = None
    return value


# Float based range creator
def frange(x, y, jump):
    if jump > 0:
        while x < y:
            yield x
            x += jump
    if jump < 0:
        while x > y:
            yield x
            x += jump


# Takes a dict and swaps out the values
def retake(adict):
    Biases = []
    senss = []
    n = 1
    while n == 1:
        Biases.append(raw_input("Bias you would like to retake?: "))
        senss.append(raw_input("Enter coresponding sensitivity: "))
        n = raw_input("Continue? (1/0): ")
    for i in range(len(Biases)):
        biasch(Biases(i))
        sensch(senss(i))
        adict[str(biases[i])] = str(sensitivity) + ", " + str(fftd)
    return adict


def dicprint2(adict, mode='n', filename=None):
    dat = str("Bias(V), Value(A)" + "\n")
    for key, value in adict.items():
        dat += str(key) + ", " + str(value) + "\n"
    if mode == 'n':
        print(dat)
    if mode == 'f':
        pass
    return None


# File creator and Handler
def filehandle(adict, name):
    return None


# ### TO DO #####
# do some error handling so loss of data doesnt happen
# create file writer

def automode(preamp, spec, rmin, rmax, interval):
        data = dict()
        vals = []
        n = 0
        # set bias
        bias = preamp.biasch("{0:.2f}".format(rmin))
        # Turn sensitivity to the highest
        preamp.sensch("200u")
        for i in frange(rmin, rmax, interval):

            # Manual Starting Sensitivity
            if n == 0:
                sencheck2()
            bias = biasch("{0:.2f}".format(i))
            time.sleep(4)

            # Take value
            val = value()
            vals.append(val)

            # Check Overload
            if n % 3 == 0 and n != 0:
                sencheck2()

            print(str(bias) + "   " + str(val))
            data[str(bias)] = val

            n += 1

        dicprint2(data, "n", None)
        return None

####################


# Manual so ranges can be figured out
# I hope you enjoy the "if" statements
def manual():
    print(" Enter Commands here, type exit to escape")
    print(" Enter bias (1), sen (2), or fft (3)")
    while 1:
        # get keyboard raw_input
        val = str(raw_input(">> "))
        if (val == 'back') or (val == 1):
            curc.close()
            fft.close
        if val == 'bias':
            print("Input desired bias voltage.")
            val = raw_input("  >> ")
            biasch(val)
        if val == 'fft':
            print(getfft())
        if val == 'sen':
            print("Input desired sensitivity.")
            temp = raw_input("  >>")
            sensch(temp)
        if val == 'biason':
            biason(1)
        if val == 'biasoff':
            biason(0)
        if val == 'exit':
            break


# 3.90625
# #### Test######
#testy = {"1.0": "1E-4, 2u", "2.0": "200E-4, 20u", "4.0": "2050E-4, 200u"}

# http://eli.thegreenplace.net/2009/07/31/listing-all-serial-ports-on-windows-with-python/
from serial.tools import list_ports
import _winreg as winreg
import itertools

def enumerate_serial_ports():
    """ Uses the Win32 registry to return an
        iterator of serial (COM) ports
        existing on this computer.
    """
    path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
    except WindowsError:
        raise IterationError

    for i in itertools.count():
        try:
            val = winreg.EnumValue(key, i)
            yield str(val[1])
        except EnvironmentError:
            break

if __name__ == '__main__':
    spec = SpectrumAnalyzer('COM4')
    preamp = PreAmplifier('COM5')
