# Author: Nicholas Weir, Nils Guillermin
# Date: 6/5/14
# Purpose: Cutting I-V measurements time from hours to minutes

import sys, time, msvcrt
import serial as _serial

# Must Change COM ports in program to match the ones used
# in the computer, they change everytime replugged


"""
SR 570 Low-Noise Current Pre-Amplifier
"""


class PreAmplifier:
    sens = (20, 200, 2000, 20000, 200000)

    def __init__(self, port):
        self.serial = _serial.Serial(
            port=port,
            baudrate=9600,
            parity=_serial.PARITY_NONE,
            stopbits=_serial.STOPBITS_TWO,
            bytesize=_serial.EIGHTBITS,
        )
        self.bias = None
        self.sensitivity = None

        portcheck(self.serial)

    def __del__(self):
        self.serial.close()

    def bias_on(self):
        self.serial.write("BSON1\n")
        if self.bias:
            bias = raw_input('>> What is bias set to (milliVolts)?')
            # Sanitize input?
            self.bias = bias

    def set_bias_millivolts(self, mv):
        input = "BSLV" + str(mv) + "\r\n"
        self.serial.write(input)
        self.bias = mv

    def set_sensitivity_nanoamps(self, val):
        # Does no input sanitization at all
        # Only using 2*multiples of 10 from nanoAmps(n) to microAmps(u)
        # All possible values are [1,2,5,...1e9,2e9,5e9] picoAmps
        n = -1
        sens = val
        while val > 1:
            n += 1
            val = val/10

        if n > -1:
            n = str(10+3*n)
            input = "SENS" + n + "\r\n"
            self.serial.write(input)
            self.sensitivity = sens
        return n

    def lower_sensitivity(self):
        if self.sensitivity is None:
            self.sensitivity = int(raw_input('What is present sensitivity (nanoAmps)?'))
        index_curr = self.sens.index(self.sensitivity)
        if index_curr > 3:
            print ">> Can't lower sensitivity. Sensitivity already at max (amperage)"
            return -1
        else:
            self.set_sensitivity_nanoamps(self.sens[index_curr+1])
            print ">> Sensitivity lowered to %s" % self.sens[index_curr+1]
        return 0

    def raise_sensitivity(self):
        if self.sensitivity is None:
            self.sensitivity = int(raw_input('What is current (present) sensitivity (nanoAmps)?'))
        index_curr = self.sens.index(self.sensitivity)
        if index_curr < 1:
            print ">> Can't raise sensitivity. Sensitivity already at min (amperage)"
            return -1
        else:
            self.set_sensitivity_nanoamps(self.sens[index_curr-1])
            print ">> Sensitivity raised to %s" % self.sens[index_curr-1]
        return 0

    # Clears overload, Never used
    # def clear():
    #   mes = "ROLD" + "\n"
    #   curc.write(mes.encode())
    #   return None


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


def split_voltages(voltages):
    return [x for x in voltages if x<0], [x for x in voltages if x>=0] 


def capture(preamp, spec, voltages):
    neg_volts, pos_volts = split_voltages(voltages)

    if preamp.bias is None:
        preamp.bias_on()
    data = {}
    # progress = ('|','/','--','\\')
    print ">> Hit any key if Pre-Amp overloads (Ctrl-C to cancel)"
    try:
        for voltages in (pos_volts, reversed(neg_volts)):
            preamp.set_sensitivity_nanoamps(20)
            for i, V in enumerate(voltages):
                preamp.set_bias_millivolts(V)
                print ">> %s" % V
                start_time = time.time()
                while True:
                    if msvcrt.kbhit():
                        _ = msvcrt.getch()
                        print ">> Adjust sensitivity (+/-) and hit Enter to resume"
                        start_time = time.time()
                        while True:
                            if msvcrt.kbhit():
                                c = msvcrt.getch()
                                if c == '=' or c == '+':
                                    if preamp.raise_sensitivity() < 0:
                                        print "Ignore reading? [Y/n]"
                                    start_time = time.time()
                                elif c == '-' or c == '_':
                                    if preamp.lower_sensitivity() < 0:
                                        print "Ignore reading? [Y/n]"
                                    start_time = time.time()
                                elif c == '\r':
                                    print ">> Restarting, hit any key if Pre-Amp overloads"
                                    break
                            if (time.time() - start_time) > 10:
                                print ">> Restarting on timeout..."
                                break
                    if (time.time() - start_time) > 5:
                        break
                data[V] = (preamp.sensitivity, spec.getfft().strip())
    except KeyboardInterrupt:
            print ">> Capture cancelled."
    return data

####################


def comma_separatify(data):
    out = []
    for k, v in sorted(data.items()):
        out.append(','.join([str(k), str(v[0]), str(v[1]), '\n']))
    return out

def save(data,filename):
    with open(filename, "w") as f:
        for l in comma_separatify(data):
            f.write(l)
        print "Write successful."

    
# 3.90625
# #### Test######
# testy = {"1.0": "1E-4, 2u", "2.0": "200E-4, 20u", "4.0": "2050E-4, 200u"}

if __name__ == '__main__':
    spec = SpectrumAnalyzer('COM4')
    preamp = PreAmplifier('COM5')

    lo = raw_input('Enter minimum voltage:')
    hi = raw_input('Enter maximum voltage:')
    step = raw_input('Enter step value ([1,2,3] has a step value of 1):')
    data = capture(preamp, spec, numpy.arange(lo, hi, step))
    fi = raw_input('Enter filename:')
    with open(fi, "w") as f:
        for l in comma_separatify(data):
            f.write(l)
        print "Write successful."
