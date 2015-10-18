# Author: Nicholas Weir, Nils Guillermin
# Date: 6/5/14
# Purpose: Cutting I-V measurements time from hours to minutes

import sys, time
import serial as _serial
from itertools import chain

if sys.platform == 'nt':
    import msvcrt
elif sys.platform == 'darwin':
    print "You're on OS X! Unfortunately OS X is not supported right now."
else:
    print "Platform not supported."
    sys.exit(0)

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
        self.__bias = None
        self.__sensitivity = None

        portcheck(self.serial)

    def __del__(self):
        self.serial.close()

    def bias_on(self):
        self.serial.write("BSON1\n")
        if self.__bias is None:
            bias = raw_input('>> What is bias set to (milliVolts)?\n')
            # Sanitize input?
            self.__bias = int(bias)

    def bias_off(self):
        self.serial.write("BSON0\n")

    def set_bias_millivolts(self, mv):
        input = "BSLV" + str(mv) + "\r\n"
        self.serial.write(input)
        self.__bias = mv

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
        self.__trace = 0
        self.__measure = None

        portcheck(self.serial)

    def __del__(self):
        self.serial.close()

    def setMeasureType(self,mtype):
        # MEAS?g{,i} where i selects 0:Spectrum; 1:PSD; 2,3 are Time Record
        # and Octave (not used by us)
        self.serial.write("MEAS" + str(self.__trace) + "," + str(mtype))
        self.__measure = mtype

    def getWindow(self):
        # Get the window (starting frequency, center frequency, frequency span)
        # of the Spec.
        # Use SPAN?{i}, STRF?{i}, CTRF?{i} commands
        # Possibly use BVAL? command to just get marker frequency?
        self.freq_span = self.getSpan()
        self.start_freq = 1000*int(self.send('STRF?'))

        if (self.freq_span > 0) or (self.start_freq > 0):
            return 1
        else:
            return 0
            
    def getSpan(self):
        sp = (191,382,763,1500,3100,6100,12200,24400,48750,97500,195000,
              390000,780000,1560000,3125000,6250000,12500000,25000000,
              50000000,100000000)
        
        i = int(self.send('SPAN?'))
        return sp[i]

    def getFFT(self,freq):
        # The following command asks for the value of a frequency. The frequency span
        # of the window is split into 400 bins, 0<i<399
        # The bin whose value is thus captured therefore depends
        # on the window size of the Spec.
        if not self.getWindow():
            return -1
        if freq - self.start_freq < 0 or freq > self.start_freq + self.freq_span:
            print freq, " is outside of spectrum window."
            # TODO: Offer choice to set window correctly?
            return 0
        else:
            i = self.freq_span/400
            difference = (1000*freq) - self.start_freq
            nbin = str(int(difference // i)).zfill(3)

            msg = "SPEC?" + str(self.__trace) + "0," + nbin 

        return self.send(msg)
        
    def getAverage(self,freq,count):
        self.serial.write('AVGO1\r\n')
        self.serial.write('NAVG'+str(count)+'\r\n')
        self.serial.write('STRT\r\n')
        time.sleep(0.025*count)
        return self.getFFT(freq)
        

    def identify(self):
        return self.send('*IDN?')
        
        
    def send(self,msg):
    # From http://stackoverflow.com/questions/676172/full-examples-of-using
    # -pyserial-package
    
    # Shocking realization...if the command has ? in it then it expects an answer
    # Otherwise, it doesn't (so, use serial.write for ? and .send for the rest))
        msg = msg + '\r\n'
        self.serial.write(msg)
        out = ''
        time.sleep(1)
        calibrating = False
        while self.serial.inWaiting() > 0:
            out += self.serial.read(1)
        if out != '' and out is not None:
            return out.rstrip()
        else:
            print 'Calibrating Offset...'
            time.sleep(15)
            self.sreial.flushInput()
            self.serial.flushOutput()
            return self.send(msg)


def portcheck(ser):
    if ser.isOpen():
        ser.flushInput()
        ser.flushOutput()
        ser.close()
    ser.open()


def split_voltages(voltages):
    return reversed([x for x in voltages if x<0]), [x for x in voltages if x>=0] 


def capture(preamp, spec, voltages):
    db = db_connect()
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
                data[V] = (preamp.sensitivity, spec.getFFT(600))
    except KeyboardInterrupt:
            print ">> Capture cancelled."
    return data


####################


def comma_separatify(data_dict):
    out = []
    for k, v in sorted(data_dict.items()):
        print k
        out.append(','.join([str(k), str(v[0]), str(v[1]), str(v[0]*float(v[1])),'']))
    return out

def save(data,filename):
    with open(filename, "w") as f:
        for l in comma_separatify(data):
            f.write(l+'\n')
        print "Write successful."

def save_multiple(datadict_list,filename):
    voltages_set = set(chain(*[ddl.keys() for ddl in datadict_list]))
    # From http://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
    with open(filename, 'a') as f:
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
        print "Write successful."
        
    
# 3.90625
# #### Test######
# testy = {"1.0": "1E-4, 2u", "2.0": "200E-4, 20u", "4.0": "2050E-4, 200u"}

if __name__ == '__main__':
    ports = ['COM4','COM5']
    for i, com in enumerate(ports):
        spec = SpectrumAnalyzer(com)
        if spec.identify()=='Stanford_Research_Systems,SR760,s/n14155,ver138':
            print "SpectrumAnalyzer using " + com
            del ports[i]
            break
        else:
            print "SpectrumAnalyzer failed to identify. Trying next port."
            del spec
    preamp = PreAmplifier(ports[0])
    print "PreAmplifier using " + ports[0]

    del spec
    del preamp
