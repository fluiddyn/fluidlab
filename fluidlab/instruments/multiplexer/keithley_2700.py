"""keithley_2700
================

.. autoclass:: Keithley2700
   :members:
   :private-members:

"""

__all__ = ['Keithley2700']

import numpy as np
from datetime import datetime
import time

from clint.textui import colored
from fluidlab.instruments.iec60488 import IEC60488
from fluidlab.instruments.features import SuperValue, BoolValue

class Keithley2700(IEC60488):
    """Driver for the multiplexer Keithley 2700 Series
    
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Range = dict()
        self.NPLC = dict()
    
    def set_range(self, channelNumber, manualRange=False, rangeValue=None):
        if not manualRange and channelNumber in self.Range:
            del self.Range[channelNumber]
        elif manualRange:
            self.Range[channelNumber] = rangeValue
            
    def set_nplc(self, channelNumber, nplcValue):
        """
        This function sets the integration time of the ADC.
        This time is expressed in terms of line frequency (PLC). It spans
        from 0.01 to 10.
        The default PLC is 1.
        
        >Fast: NPLC=0.01 3 1/2 digits
        Fast:  NPLC=0.1 5 1/2 digits
        Med:   NPLC=1.0 6 1/2 digits
        Slow:  NPLC=5.0
        
        """
        nplcValue = float(nplcValue)
        self.NPLC[channelNumber] = nplcValue
        
    def scan(self, channelList, functionName, samplesPerChan,
             sampleRate, verbose):
        """ Initiates a scan"""
        
        # Make sure channelList is iterable
        try:
            channelList[0]
        except TypeError:
            channelList = [channelList]
            
        # Check Front/Rear switch
        if len(channelList) > 1 and self.front.get() == True:
            raise ValueError('Cannot get several channels while Front/Read switch is Front')
            
        # Check number of points (max memory 450000 data points)
        if samplesPerChan*len(channelList) > 450000:
            raise ValueError('Cannot request more than 450000 on Keithley 2700')
        
        # Check sampleRate
        if sampleRate:
            timeInterval = 1/sampleRate
            if timeInterval < 1e-3:
                raise ValueError('The timer resolution is 1 ms')
        else:
            timeInterval = 1e-3
            
        if channelList == [1]:
            # Lecture en face avant
            data = self.interface.query("MEAS:{:}?".format(functionName))
            parsed = data.split(",")
            values = parsed[0]
        else:
            ListeChan = "(@" +\
                        ",".join([str(c) for c in channelList]) +\
                        ")"
            self.clear_status()
            self.interface.write("TRAC:CLE") # clear buffer
            self.interface.write("INIT:CONT OFF") # disable continuous initialisation
            
            # Set up the trigger subsystem
            if samplesPerChan > 1:
                self.interface.write("TRIG:SOUR TIM")
                self.interface.write("TRIG:TIM {:}".format(timeInterval))
            self.interface.write("TRIG:COUN {:}".format(samplesPerChan))
            self.interface.write("SAMP:COUN {:}".format(len(channelList)))
                
            # Measurement subsystem
            self.interface.write('SENS:FUNC "{:}", {:}'.format(functionName, ListeChan))
            
            # Set range on specified channels
            for chan in channelList:
                if chan in self.Range:
                    self.interface.write(\
                        "SENS:{func:}:RANG {rang:},(@{chan:})".format(func=functionName,
                                                                      rang=self.Range[chan],
                                                                      chan=chan))
                else:
                    self.interface.write(\
                        "SENS:{func:}:RANG:AUTO ON,(@{chan:})".format(func=functionName,
                                                                      chan=chan))
            
            # Set NPLC
            max_nplc = None
            for chan in channelList:
                if chan in self.NPLC:
                    nplc = self.NPLC[chan]
                else:
                    nplc = 1.0 # med (default value)
                if max_nplc is None or nplc > max_nplc:
                    max_nplc = nplc
                self.interface.write("SENS:{func:}:NPLC {nplc:},(@{chan:})".format(func=functionName,
                                                                                   nplc=nplc,
                                                                                   chan=chan))
            
            # Starts scan
            self.interface.write("ROUT:SCAN {:}".format(ListeChan))
            self.interface.write("ROUT:SCAN:TSO IMM")
            self.interface.write("ROUT:SCAN:LSEL INT")
            
            if samplesPerChan*len(channelList) > 1:
                self.interface.write("TRAC:CLE") # clear buffer
                self.interface.write("TRAC:POIN {:}".format(samplesPerChan*len(channelList)))
                self.interface.write("TRAC:NOT {:}".format(samplesPerChan*len(channelList)-1)) # notify on nth reading
                self.interface.write("TRAC:FEED SENS; FEED:CONT NEXT")
                #self.interface.write("TRIG:COUN 1")
                #self.interface.write("SAMP:COUN {:}".format(len(channelList)))
                
                self.interface.write("STAT:PRES") # Reset measure enable bits
                self.clear_status()  # *CLS
                self.interface.write("STAT:MEAS:ENAB 64") # Enable buffer bits B6 (buffer notify) (, 8, 9, 12, 13)
                self.event_status_enable_register.set(0)  # *ESE 0
                self.status_enable_register.set(1)  # *SRE 1
        
                self.interface.write("INIT:IMM")
                start_meas = time.monotonic()
                #self.wait_till_completion_of_operations()  # *OPC
                if samplesPerChan > 1:
                    tmo = 1000*(samplesPerChan/sampleRate)*1.5
                else:
                    tmo = 1000*len(channelList)*max_nplc*(1/50)*1.5
                tmo*=10
                if tmo < 10e3:
                    tmo = 10e3
                #print("tmo =", tmo, "ms")
                try:
                    self.interface.wait_for_srq(timeout=tmo)
                except:
                    print(colored.red('Error while waiting SRQ'))
                else:
                    print(colored.green('SRQ received after {:.1f} seconds'.format(time.monotonic()-start_meas)))
                
                # Unassert SRQ
                self.clear_status()
                
                # Query number of points in buffer
                npoints = int(self.interface.query('TRAC:POIN?'))
                print('npoints =', npoints)
                
                # Fetch data
                self.interface.write("FORM:ELEM READ,TST,CHAN")
                self.interface.write("TRAC:DATA?")
                data = ""
                start_fetch = time.monotonic()
                while True:
                    try:
                        data += self.interface.read()
                        start_fetch = time.monotonic() # reset if something was returned
                    except:
                        print('Timeout reading on interface')
                    nread = len(data.split(','))//3
                    if nread == npoints:
                        print(colored.green('All datapoints read'))
                        break
                    time.sleep(0.5)
                    self.interface.write("TRAC:DATA?")
                    if time.monotonic() - start_fetch > 15:
                        print(colored.red('Timeout fetching data'))
                        break
            else:
                #self.interface.write("TRIG:COUN {:}".format(samplesPerChan))
                #self.interface.write("SAMP:COUN {:}".format(len(channelList)))
                self.interface.write("FORM:ELEM READ,TST,CHAN")
                data = self.interface.query("READ?")
                npoints = 1
            
            self.interface.write(":ROUT:SCAN:LSEL NONE")
            
            # Parsing data
            #print(data.strip())
            data = np.array([float(x) for x in data.split(",")])
            #print(data.size//3, "values returned")
            if data.size//3 != npoints:
                raise ValueError('Not all points were fetched')
            values = data[::3]
            timestamps = data[1::3]
            channels = data[2::3]
            if values.size != timestamps.size:
                raise ValueError('Error while parsing')
            if channels.size != timestamps.size:
                raise ValueError('Error while parsing')
            if samplesPerChan > 1:
                # returns timeStamp, value for each channelList
                retval = list()
                for channum, chan in enumerate(channelList):
                    this_values = values[channum::len(channelList)]
                    this_timestamps = timestamps[channum::len(channelList)]
                    this_chans = channels[channum::len(channelList)]
                    if not (this_chans == chan).all():
                        raise ValueError('Error while parsing')
                    retval.append(this_timestamps)
                    retval.append(this_values)
            else:
                # returns values only
                retval = values
            
            return retval
                    
                
class Keithley2700Value(SuperValue):
    
    def __init__(self, name, doc="", function_name=None):
        super().__init__(name, doc)
        self.function_name = function_name
        
    def _build_driver_class(self, Driver):
        name = self._name
        function_name = self.function_name

        setattr(Driver, name, self)

        def get(self, chanList, samplesPerChan=1, sampleRate=None, verbose=None):
            """Get """ + name
            if verbose is None:
                # default is verbose for acquisitions
                verbose = (samplesPerChan > 1)
            result = self._driver.scan(
                chanList, function_name, samplesPerChan, sampleRate, verbose
            )
            if len(result) == 1:
                result = result[0]
            return result

        self.get = get.__get__(self, self.__class__)

        def set(self, channel, value, warn=True):
            """Set """ + name
            # Makes sense for voltage on AO channels only
            if name == "vdc":
                self._driver.write_vdc(channel, value)
            else:
                raise ValueError("Specified value cannot be written")

        self.set = set.__get__(self, self.__class__)
                
            
features = [
    BoolValue("front",
              doc="True if switch Front/Rear is on Front",
              command_get=":SYST:FRSW?"),
    Keithley2700Value("vdc",
                      doc="DC voltage",
                      function_name="VOLT:DC"),
    Keithley2700Value("vrms",
                      doc="RMS voltage",
                      function_name="VOLT:AC"),
    Keithley2700Value("ohm_4w",
                      doc="4-wire resistance",
                      function_name="FRES"),
    Keithley2700Value("ohm",
                      doc="2-wire resistance",
                      function_name="RES"),
    Keithley2700Value("idc",
                      doc="DC current",
                      function_name="CURR:DC"),
    Keithley2700Value("irms",
                      doc="RMS current",
                      function_name="CURR:AC"),
]

Keithley2700._build_class_with_features(features)

if __name__ == '__main__':
    with Keithley2700('GPIB0::16::INSTR') as km:
        print('Front/Read switch:', km.front.get())
        print('Single channel one-shot measurement')
        print(km.vdc.get(101))
        print('Multiple channel one-shot measurement')
        R1, R2 = km.ohm.get([101,102])
        print(R1,R2)
        print('Single channel timeseries')
        ts, R = km.ohm.get(101, samplesPerChan=100, sampleRate=10.0)
        print('actual frame rate:', 1/np.mean(ts[1:]-ts[:-1]), 'Hz')
        import matplotlib.pyplot as plt
        plt.plot(ts, R, 'o')
        plt.show()