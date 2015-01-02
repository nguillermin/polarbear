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

        portcheck(port)

    def set_sensitivity(self, val):
        # Changes Sensitivity, notation n,u is used
        sens_code = {'2n': 10, '20n': 13, '200n': 16, '2u': 19, '20u': 22,
                     '200u': 25}
        v = str(val)
        mes = "SENS" + sens_code[v] + "\n"
        self.serial.write(mes.encode())
        self.sensitivity = v

        #sens_real = {'2n': 2e-9, '20n': 2e-8, '200n': 2e-7, '2u': 2e-6, 
        #             '20u': 2e-5, '200u': 2e-4}


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

        portcheck(port)

    def getfft(self,trace=0):
        mestot = "\r" + "SPEC?" + str(trace) + "0,154" + "\n"
        self.serial.write(mestot.encode())
        # Wait a bit for response
        time.sleep(1)
        out = str(fft.readline().decode())
        print out
        if out is not None and out is not '':
            return(str(out))
        else:
            time.sleep(7)
            out = str(fft.readline().decode())
            return str(out)

def portcheck(port):
    if port.isOpen:
        port.flushInput()
        port.flushOutput()
        port.close()


# Gets fft of trace
# 0 for spectrum, 1 for PSD


# Get Sensitivity times fft value
def value(sen=None, fft=None):
    if sen is None:
        value = float(getfft()) * senreal[sensitivity]
    else:
        value = None
    return value


# Turn Bias On/Off (1/0)
def biason(val):
    es = "BSON" + str(int(val)) + "\n"
    curc.write(mes.encode())
    return val


# Changes Bias -5 to 5
def biasch(val):
    mes = "BSLV" + str(int(float(val)*1000)) + "\n"
    curc.write(mes.encode())
    return val




# Clears overload, Never used
def clear():
    mes = "ROLD" + "\n"
    curc.write(mes.encode())
    return None


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

def automode(rmin, rmax, interval):
        data = dict()
        vals = []
        n = 0
        # Turn bias on
        biason(1)
        # set bias
        bias = biasch("{0:.2f}".format(rmin))
        # Turn sensitivity to the highest
        sensch("200u")
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

if __name__ == '__main__':
    spec = SpectrumAnalyzer('COM4')
    preamp = PreAmplifier('COM5')
