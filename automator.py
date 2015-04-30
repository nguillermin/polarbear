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
    sens = (2, 20, 200, 2000, 20000, 200000)

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
        if index_curr > len(self.sens)-2:
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
        self.measure = None

        portcheck(self.serial)

    def __del__(self):
        self.serial.close()

    def setMeasureType(self,mtype):
        # MEAS?g{,i} where i selects 0:Spectrum; 1:PSD; 2,3 are Time Record
        # and Octave (not used by us)
        self.serial.write("MEAS" + str(self.trace) + "," + str(mtype))
        self.measure = mtype

    def getWindow(self):
        # Get the window (starting frequency, center frequency, frequency span)
        # of the Spec.
        # Use SPAN?{i}, STRF?{i}, CTRF?{i} commands
        # Possibly use BVAL? command to just get marker frequency?
        self.freq_span = self.serial.send('SPAN?')
        self.start_freq = self.serial.send('STRF?')

        if (self.span > 0) or (self.start_freq) >  0):
            return 1
        else
            return 0

    def getFFT(self,freq):
        # The following command asks for the value of a bin i, 0<i<399
        # In this case the value is 91 (out of 399)
        # The frequency whose value is thus captured therefore depends
        # on the window size of the of the Spec.
        if !self.getWindow():
            return -1 
        if freq - self.start_freq < 0 or freq - self.start_freq > self.freq_span:
            print freq, " is outside of spectrum window."
            # TODO: Offer choice to set window correctly?
            return 0
        else:
            i = self.freq_span/400
            difference = freq - self.start_freq
            nbin = str(int(difference // i)).zfill(3)

            msg = "SPEC?" + str(self.trace) + "0," + nbin 

        # From http://stackoverflow.com/questions/676172/full-examples-of-using
        # -pyserial-package
        return self.send(input)

    def identify(self):
        return self.send('*IDN?')
          
    def send(self,msg):
        msg = msg + '\r\n'
        self.serial.write(msg)
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
    return reversed([x for x in voltages if x<0]), [x for x in voltages if x>=0] 


def capture(preamp, spec, voltages):
    neg_volts, pos_volts = split_voltages(voltages)

    if preamp.bias is None:
        preamp.bias_on()
    data = {}
    # progress = ('|','/','--','\\')
    print ">> Hit any key if Pre-Amp overloads (Ctrl-C to cancel)"
    try:
        for volts in (pos_volts, neg_volts):
            preamp.set_sensitivity_nanoamps(2)
            for i, V in enumerate(volts):
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
                                        print "Max sensitivity, hit Ctrl-C to cancel reading or Enter to continue"
                                    start_time = time.time()
                                elif c == '-' or c == '_':
                                    if preamp.lower_sensitivity() < 0:
                                        print "Min sensitivity, hit Ctrl-C to cancel reading or Enter to continue"
                                    start_time = time.time()
                                elif c == '\r':
                                    print ">> Restarting, hit any key if Pre-Amp overloads"
                                    break
                            if (time.time() - start_time) > 10:
                                print ">> Restarting on timeout..."
                                break
                    if (time.time() - start_time) > 3:
                        break
                data[V] = (preamp.sensitivity, spec.getfft().strip())
    except KeyboardInterrupt:
            print ">> Capture cancelled."
    return data

####################


def comma_separatify(data_dict):
    out = []
    for k, v in sorted(data_dict.items()):
        print k
        out.append(','.join([str(k), str(v[0]), str(v[1]), str(v[0]*float(v[1]))]))
    return out

def save(data,filename):
    with open(filename, "w") as f:
        for l in comma_separatify(data):
            f.write(l+'\n')
        print "Write successful."

def save_multiple(datadict_list,filename):
    all_voltages = []
    for ddl in datadict_list:
        all_voltages.extend(ddl.keys())
    voltages_set = set(all_voltages)
    with open(filename, 'w') as f:
        f.write(",".join(["Bias,Sensitivity,Reading,Value,," for n in datadict_list]) + "\n")
        for v in sorted(voltages_set):
            output = []
            for ddl in datadict_list:
                if v in ddl.keys():
                    line = map(str,[v,ddl[v][0],ddl[v][1],ddl[v][0]*float(ddl[v][1])])
                    output.append(",".join(line))
                else:
                    output.append(',,,')
            f.write(",".join(output) + "\n")
                    
    
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
