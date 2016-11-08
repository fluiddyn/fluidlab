"""agilent_34970a
=================

.. autoclass:: Agilent34970a
   :members:
   :private-members:

"""

__all__ = ["Agilent34970a"]

import numpy as np

from fluidlab.instruments.iec60488 import (
    IEC60488)

from fluidlab.instruments.features import SuperValue


class Agilent34970aValue(SuperValue):
    def __init__(self, name, doc='', function_name=None):
        super(Agilent34970aValue, self).__init__(name, doc)
        self.function_name = function_name

    def _build_driver_class(self, Driver):
        name = self._name
        function_name = self.function_name

        setattr(Driver, name, self)

        def get(self, chanList, samplesPerChan=1, sampleRate=None):
            """Get """ + name
            result = self._driver.scan(
                chanList, function_name, samplesPerChan, sampleRate)
            if len(result) == 1:
                result = result[0]
            return result

        self.get = get.__get__(self, self.__class__)

        def set(self, channel, value, warn=True):
            """Set """ + name
            # Makes sense for voltage on AO channels only
            if name == 'vdc':
                self._driver.write_vdc(channel, value)
            else:
                raise ValueError('Specified value cannot be written')

        self.set = set.__get__(self, self.__class__)


class Agilent34970a(IEC60488):
    """Driver for the multiplexer Agilent 34970A.

    """

    def __init__(self, interface=None, backend=''):
        super(Agilent34970a, self).__init__(interface, backend)
        # Define instance variables for optional NPLC and Range settings
        # to be used when scanning
        #
        # If no key is defined, NPLC and Range settings are not
        # changed if self.NPLC["101"] exists, then NPLC will be set
        # when scanning channel 101 if self.Range["203"] exists, then
        # Manual range will be set when scanning channel 203 Auto
        # Range will be set to ON otherwise
        self.NPLC = dict()
        self.Range = dict()
        self.TkType = dict()

    def set_range(self, channelNumber, manualRange=False, rangeValue=None):
        if not manualRange and str(channelNumber) in self.Range:
            del self.Range[str(channelNumber)]
        elif manualRange:
            self.Range[str(channelNumber)] = rangeValue

    def set_nplc(self, channelNumber, nplcValue):
        self.NPLC[str(channelNumber)] = nplcValue

    def set_tk_type(self, channelNumber, tkType):
        if tkType in ('B', 'E', 'J', 'K', 'N', 'R', 'S'):
            self.TkType[str(channelNumber)] = tkType
        else:
            raise ValueError("Unknown TK type")

    def scan(self, channelList, functionName, samplesPerChan, sampleRate):
        """ Initiates a scan """

        try:
            # Checks if channelList is iterable
            numChans = len([x for x in channelList])
        except:
            # If not, convert to 1-tuple
            channelList = (channelList, )
            numChans = 1
            pass

        # Max number of points: 50000
        if samplesPerChan*numChans > 50000:
            raise ValueError(
                'Maximum number of samples is 50000 on Agilent 34970A')
        if samplesPerChan > 1:
            timeInterval = 1./sampleRate
            if timeInterval < 1e-3:
                raise ValueError(
                    'The timer resolution of the Agilent 34970A is 1 ms')

        # Check that channel numbers are right
        badChans = [x for x in channelList if ((x < 100) and (x >= 400))]
        if len(badChans) > 0:
            raise ValueError(
                'Channels must be specified in the form scc, where s is '
                'the slot number (100, 200, 300), and cc is the channel '
                'number. For example, channel 10 on the slot 300 is referred '
                'to as 310.')

        # Set measurement type to desired function on specified channels
        msg = 'SENS:FUNC "' + functionName +'",(@'
        for i in range(numChans):
            msg = msg + str(channelList[i])
            if i < (numChans-1):
                msg = msg + ','
            else:
                msg = msg + ')'
        self.interface.write(msg)

        # Set range on specified channels
        for chan in channelList:
            if str(chan) in self.Range:
                # set channel to manual range
                self.interface.write(
                    'SENS:' + functionName + ':RANG ' +
                    str(self.Range[str(chan)]) +',(@' + str(chan) + ')')
            elif functionName != 'TEMP':
                # set channel to Auto Range
                self.interface.write('SENS:' + functionName +
                                     ':RANG:AUTO ON,(@' + str(chan) + ')')

        # Set NPLC for specified channels
        for chan in channelList:
            if str(chan) in self.NPLC:
                # set NPLC to specified value
                self.interface.write(
                    'SENS:' + functionName + ':NPLC ' +
                    str(self.NPLC[str(chan)]) + ',(@' + str(chan) + ')')

        # Set TK Type for specified channels (if TK channel and TkType defined)
        if functionName == 'TEMP':
            for chan in channelList:
                if str(chan) in self.TkType:
                    # set Tk type to specified value
                    self.interface.write(
                        'SENS:TEMP:TRAN:TC:TYPE ' + str(self.TkType[str(chan)]) +',(@' + str(chan) + ')')

        # Setup scan list
        msg = 'ROUT:SCAN (@'
        for i in range(numChans):
            msg = msg + str(channelList[i])
            if i < (numChans-1):
                msg = msg + ','
            else:
                msg = msg + ')'
        self.interface.write(msg)

        # Setup trigger and timer & Format
        if samplesPerChan > 1:
            self.interface.write('TRIG:SOUR TIM')
            self.interface.write('TRIG:TIM ' + str(timeInterval))
            self.interface.write('TRIG:COUN ' + str(samplesPerChan))
            self.interface.write('FORM:READ:TIME ON')
        else:
            self.interface.write('TRIG:SOUR IMM')
            self.interface.write('TRIG:COUN 1')
            self.interface.write('FORM:READ:TIME OFF')
        self.interface.write('FORM:READ:ALAR OFF')
        self.interface.write('FORM:READ:CHAN OFF')
        self.interface.write('FORM:READ:UNIT OFF')

        # Prepare status and event register
        self.clear_status()
        self.event_status_enable_register.set(1)
        self.status_enable_register.set(32)

        # Initiate scan and trigger Operation Complete event after completion
        self.interface.write('INIT')

        # Wait for Service Request (triggered by *OPC after the scan
        # is complete)
        self.wait_till_completion_of_operations()
        # self.interface.assert_trigger()
        self.interface.wait_for_srq()

        # Unassert SRQ
        self.clear_status()

        # Fetch data
        data = self.interface.query('FETCH?')

        # Parse data
        if samplesPerChan > 1:
            # timeStamp + value for each channel
            expectedEntriesPerLine = 2*numChans
            retval = np.zeros((samplesPerChan, expectedEntriesPerLine))
            i=0
            for line in data.splitlines():
                retval[i, :] = [float(x) for x in line.split(',')]
                i=i+1
        else:
            expectedEntriesPerLine = numChans
            # only value for each channel
            retval = np.array([float(x) for x in data.split(',')])

        return retval

    def write_vdc(self, channel, value):
        """Write DC-Voltage on specified AO channel.

        .. todo::

           Solve an evident bug in this function (should be easy).

        """

        print('Warning there is clearly a bug here: channelList !')

        # Check that channel numbers are right
        badChans = [x for x in channelList if ((x < 100) and (x >= 400))]
        if badChans > 0:
            raise ValueError(
                'Channels must be specified in the form scc, where s is the '
                'slot number (100, 200, 300), and cc is the channel number. '
                'For example, channel 10 on the slot 300 is referred to '
                'as 310.')

        # Write DC Voltage
        self.interface.write(
            'SOUR:VOLT ' + str(value) + ',(@' + str(channel) + ')')

features = [
    Agilent34970aValue('vdc',
                       doc='DC Voltage',
                       function_name='VOLT:DC'),
    Agilent34970aValue('vrms',
                       doc='RMS Voltage',
                       function_name='VOLT:AC'),
    Agilent34970aValue('temperature',
                       doc='Temperature',
                       function_name='TEMP'),
    Agilent34970aValue('ohm',
                       doc='2-wire resistance',
                       function_name='RES'),
    Agilent34970aValue('ohm_4w',
                       doc='4-wire resistance',
                       function_name='FRES'),
    Agilent34970aValue('idc',
                       doc='DC Current',
                       function_name='CURR:DC')]


Agilent34970a._build_class_with_features(features)
