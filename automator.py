# Author: Nicholas Weir, Nils Guillermin
# Date: 6/5/14
# Purpose: Cutting I-V measurements time from hours to minutes

import time, thread
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

    def bias_on(self):
        self.serial.write("BSON1\n")
        bias = raw_input('>> What is bias set to (milliVolts)?')
        # Sanitize input?
        self.bias = bias

    def set_bias_millivolt(self, val):
        input = "BSLV" + str(val) + "\r\n"
        self.serial.write(input)

    def set_sensitivity(self, val):
        # Changes Sensitivity, notation n,u is used
        sens_code = {'2n': 10, '20n': 13, '200n': 16, '2u': 19, '20u': 22,
                     '200u': 25}
        # Only using 2*multiples of 10 from nanoAmps(n) to microAmps(u)
        v = str(val)
        input = "SENS" + sens_code[v] + "\r\n"
        self.serial.write(input)
        self.sensitivity = v

        # sens_real = {'2n': 2e-9, '20n': 2e-8, '200n': 2e-7, '2u': 2e-6,
        #             '20u': 2e-5, '200u': 2e-4}

    def set_sensitivity_nanoamps(self, val):
        # Only using 2*multiples of 10 from nanoAmps(n) to microAmps(u)
        # All possible values are [1,2,5,...1e9,2e9,5e9] picoAmps
        n = -1
        while val > 0:
            n += 1
            val = val/10

        if n > -1:
            n = str(10+3*n)
            input = "SENS" + n + "\r\n"
            self.serial.write(input)
            self.sensitivity = val
        return n

    # Clears overload, Never used
    # def clear():
    #   mes = "ROLD" + "\n"
    #   curc.write(mes.encode())
    #   return None

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

        # From http://stackoverflow.com/questions/676172/full-examples-of-using
        # -pyserial-package
        # send the character to the device
        # (note that I append a \r\n carriage return and line feed to the
        # characters - this is requested by my device)
        self.serial.write(input + '\r\n')
        out = ''
        # let's wait one second before reading output (let's give device time
        # to answer)
        time.sleep(1)
        while self.serial.inWaiting() > 0:
            out += self.serial.read(1)

        if out != '':
            return out

    def identify(self):
        self.serial.write("*IDN?\r\n")
        out = ''
        time.sleep(1)
        while self.serial.inWaiting() > 0:
            out += self.serial.read(1)
        if out != '':
            return out


def portcheck(ser):
    if ser.isOpen():
        ser.flushInput()
        ser.flushOutput()
        ser.close()
    ser.open()


# Get Sensitivity times fft value
def value(spec, sen=None, fft=None):
    if sen is None:
        value = float(spec.getfft()) * senreal[sensitivity]
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

def input_thread(L):
    raw_input()
    L.append(None)


def automode(preamp, spec, voltages):
    if preamp.bias is None:
        preamp.bias_on()
    # Turn sensitivity to the highest
    preamp.set_sensitivity_nanoamps(20)

    voltages = sorted(voltages)
    index_zero = voltages.index(0)
    positive_voltages = voltages[index_zero:]
    negative_voltages = reversed(voltages[:index_zero+1])

    data = []
    print "Capturing ascending positive voltages..."
    data.append(capture(preamp, spec, positive_voltages))
    print "...Capturing descending negative voltages"
    data.append(reversed(capture(preamp, spec, negative_voltages)))

    return data


def capture(preamp, spec, voltages):
    data = []
    # progress = ('|','/','--','\\')
    print ">> Hit any key if sensitivity overload"
    for i, V in enumerate(voltages):
        L = []
        thread.start_new_thread(input_thread, (L,))
        preamp.set_bias_millivolts(V*1000)
        time.sleep(3.0)
        if L:
            print ">> Set sensitivity and hit any key to resume measure"
            raw_input()
            print ">> Resuming..."
            time.sleep(1.0)
        data.append(spec.getfft())

    return data

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
# testy = {"1.0": "1E-4, 2u", "2.0": "200E-4, 20u", "4.0": "2050E-4, 200u"}

if __name__ == '__main__':
    spec = SpectrumAnalyzer('COM4')
    preamp = PreAmplifier('COM5')
