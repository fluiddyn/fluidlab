"""PowerDAQ board (:mod:`fluidlab.objects.boards.powerdaq`).


"""

from __future__ import division, print_function

cimport numpy as np
import numpy as np
np.import_array()

import time 

cimport powerdaq as pdaq

cdef extern from "Windows.h":
    ctypedef unsigned short WORD
    ctypedef unsigned long DWORD
    ctypedef DWORD *PDWORD
    ctypedef PVOID HANDLE
    ctypedef PVOID *PHANDLE

    BOOL QueryPerformanceFrequency(np.int64_t *lpFrequency)
    BOOL QueryPerformanceCounter(np.int64_t *lpPerformanceCount)

dt_DWORD_big = np.dtype('>I32') # big-endian 
dt_DWORD_lit = np.dtype('<I32') # little-endian 
dt_DWORD_def = np.dtype('=I32') # hardware-native

# ltest = [1,2]

# test_big = np.array(ltest, dtype=dt_DWORD_big)
# test_lit = np.array(ltest, dtype=dt_DWORD_lit)
# test_def = np.array(ltest, dtype=dt_DWORD_def)

# print('big', bin(test_big[0]),  bin(test_big[1]))
# print('lit', bin(test_lit[0]),  bin(test_lit[1]))
# print('def', bin(test_def[0]),  bin(test_def[1]))









cdef extern from "pdfw_def.h":
    int AIB_INPRANGE
    int AIB_CVSTART0, AIB_CVSTART1, AIB_CLSTART0, AIB_CLSTART1
    int AIB_STARTTRIG0
    int AIB_INTCVSBASE
    int AIN_RANGE_5V, AIN_RANGE_10V
    int AIN_BIPOLAR, AIN_UNIPOLAR, AIN_DIFFERENTIAL, AIN_SINGLE_ENDED
    int AOB_CVSTART0, AOB_CVSTART1, AOB_STARTTRIG0, AOB_REGENERATE
    int BUF_BUFFERWRAPPED, BUF_BUFFERRECYCLED, BUF_DWORDVALUES



cdef extern from "string.h":
    void *memcpy  (void *TO, const void *FROM, size_t SIZE)

from libc.stdlib cimport malloc, free


def _print_if_error(noerror, error_code, name_function):
    if not noerror:
        raise ValueError('Problem in function '+name_function+' , '+
                         'error_code: {0}'.format(error_code))


cdef class SubSystem(object):
    cdef HANDLE hadapter
    cdef DWORD code_subsystem # codes defined in a header

    def __init__(self, PowerDAQBoard board):
        cdef DWORD error_code

        self.hadapter = board.hadapter
        if self.code_subsystem == 0:
            raise ValueError("self.code_subsystem has to be reset.")
        noerror = pdaq.PdAdapterAcquireSubsystem(
            self.hadapter, &error_code, self.code_subsystem, 1)
        _print_if_error(noerror, error_code, 'PdAdapterAcquireSubsystem')


cdef class AnalogicSubSystem(SubSystem):
    # cdef HANDLE hadapter
    cdef np.uint8_t external_trigger, Cv_master, range10V, bipolar, differential
    # cdef DWORD code_subsystem # codes defined in a header
    cdef DWORD code_config
    cdef public np.float64_t freq_max, freq_used
    cdef DWORD clock_conv_Cv_coef, clock_list_Cl_coef
    cdef np.float64_t dt_channel_list

    cdef np.float64_t bit_weight, range_volt, volt_max

    cdef np.ndarray channel_list
    cdef object nb_channels_used

    cdef np.uint8_t converting, ready

    def __init__(self, PowerDAQBoard board):

        self.freq_max = 11.e6 # (Hz)
        super(AnalogicSubSystem, self).__init__(board)



cdef class AnalogInput(AnalogicSubSystem):
    cdef public object channels
    cdef np.ndarray gain_channels
    cdef list gain_coefs
    cdef list slow_bits_for_delay

    def __init__(self, PowerDAQBoard board):
        cdef DWORD error_code

        # always like that for this board
        self.gain_coefs = [1, 2, 5, 10]

        self.code_subsystem = 1 # means analogic input
        super(AnalogInput, self).__init__(board)

        # set parameters to the default values
        self.Cv_master = False
        self.range10V = True
        self.bipolar = True
        self.external_trigger = False
        self.differential = False

        # give these default values to the board
        self._change_set_config()

        # set channel list
        self.nb_channels_used = 1
        self.channels = [0]
        self.channel_list = np.zeros(1, dtype=np.int32)
        self._set_channel_list_in_board()

        # set up clocking; default to 100 Hz
        self._set_clocking(sample_freq=100)

        # enable conversion
        self._change_enable_conversion(enable=True)

        self.converting = False
        self.ready = True




    def _change_set_config(self, 
                           Cv_master=None,
                           range10V=None,
                           bipolar=None,
                           external_trigger=None, 
                           differential=None
                       ):
        """Set the configuration "_PdAInSetCfg(...)"

        We first have to compute a DWORD carrying the parameters
        (self.code_config).

        The parameters for the time clocking deal with two clocks, Cv
        (conversion) and Cl (list). Four bits are used to give the
        parameters for the time clocking (2 for Cv and 2 for Cl) so
        there are 4 constants to help to set self.code_config. For
        each clock, the bits can be set as follow (notation: bit 1
        bit 0):
        00    software source
        01    internal clock
        10    external clock
        11    continuous (fastest as possible)

        """

        cdef DWORD error_code

        # change the booleans of this code
        if Cv_master is not None:
            self.Cv_master = Cv_master
        if range10V is not None:
            self.range10V = range10V
        if bipolar is not None:
            self.bipolar = bipolar
        if external_trigger is not None:
            self.external_trigger = external_trigger
        if differential is not None:
            self.differential = differential

        # set self.code_config
        # time clocking:
        if self.Cv_master:
            # Cv internal clock, Cl continuous
            self.code_config = AIB_CVSTART0 + AIB_CLSTART0 + AIB_CLSTART1
        else:
            # Cl internal clock, Cv continuous
            self.code_config = AIB_CLSTART0 + AIB_CVSTART0 + AIB_CVSTART1


        # to avoid an ununderstandable bug...
        if not self.range10V and not self.bipolar:
            print(
"""When the options "not self.range10V and not self.bipolar" are given
to the board, the results are actually consistent with the options
"self.range10V and not self.bipolar". self.range10V is switched to
True in order to avoid false results due to this strange behaviour."""
            )
            self.range10V = True

        # range:
        if self.range10V:
            self.code_config |= AIN_RANGE_10V 
            self.volt_max = 10.
        else:
            self.code_config |= AIN_RANGE_5V
            self.volt_max = 5.

        # print('AIN_RANGE_10V {0:08b}'.format(AIN_RANGE_10V))
        # print('AIN_RANGE_5V  {0:08b}'.format(AIN_RANGE_5V))

        # unipolar or bipolar:
        if self.bipolar:
            self.code_config |= AIN_BIPOLAR
            self.range_volt = 2*self.volt_max
        else:
            self.code_config |= AIN_UNIPOLAR
            self.range_volt = self.volt_max

        # print('AIN_BIPOLAR   {0:08b}'.format(AIN_BIPOLAR))
        # print('AIN_UNIPOLAR  {0:08b}'.format(AIN_UNIPOLAR))
        # print('code_config   {0:08b}'.format(self.code_config))

        self.bit_weight = self.range_volt/65535

        # differential or Single-ended
        if self.differential:
            self.code_config |= AIN_DIFFERENTIAL
        else:
            self.code_config |= AIN_SINGLE_ENDED

        # external (start) trigger or not
        if self.external_trigger:
            self.code_config = (
                (self.code_config & ~AIB_STARTTRIG0) 
                + AIB_STARTTRIG0 )    
        else: # software trigger only
            self.code_config = (
                (self.code_config & ~AIB_STARTTRIG0)) 

        # set up config in the board
        noerror = pdaq._PdAInSetCfg(self.hadapter, &error_code,
                                    self.code_config, 0, 0)
        _print_if_error(noerror, error_code, 'PdAInSetCfg')








    def __dealloc__(self):
        cdef DWORD error_code
        # print('run __dealloc__() AnalogIn')
        pdaq._PdAInSwStopTrig(self.hadapter, &error_code)



    def _compute_clock_coef(self, sample_freq):
        """Calculate the clock divisor for the specified sample freq."""

        if sample_freq > self.freq_max:
            print('Warning: since sample_freq > self.freq_max !\n'
                  '         sample_freq = self.freq_max')
            sample_freq = self.freq_max

        # # very strange !
        # if ((self.code_config & AIB_INTCVSBASE) == 0):
        #     C_coef = self.freq_max/sample_freq - 1  # 11MHz base (?)
        # else:
        #     C_coef = self.freq_max/sample_freq - 1  # 33Mhz base (?)

        C_coef = self.freq_max/sample_freq - 1
        return int(np.round(C_coef))


    def configure(self, sample_freq=None,
                  # object nb_samples=None,
                  object channels=None,
                  object gain_channels=1,
                  object slow_bits_for_delay=False,
                  Cv_master=None,
                  range10V=None,
                  bipolar=None,
                  external_trigger=None, 
                  differential=None
              ):
        """Configure the input subsystem.

        parameters:
        ...

        Be carreful, a call of configure will change the values of 
        gain_channels and slow_bits_for_delay.

        For all other parameters, if it is not given, no change will
        be performed.

        The board is initialized with 
        sample_freq=100,
        channels=[0],
        gain_channels=1,
        object slow_bits_for_delay=False,
        Cv_master=False,
        range10V=True,
        bipolar=False,
        external_trigger=False, 
        differential=False

        """
        cdef DWORD error_code

        self._change_enable_conversion(enable=False)

        self._change_set_config(Cv_master=Cv_master,
                                range10V=range10V,
                                bipolar=bipolar,
                                external_trigger=external_trigger, 
                                differential=differential
                            )

        # Set channel list
        self._set_channel_list(channels, gain_channels, 
                               slow_bits_for_delay)
        # self._verify_channel_list()

        # Set up clocking
        self._set_clocking(sample_freq)

        if self.external_trigger:
            self._change_enable_conversion(enable=True)





    def _change_enable_conversion(self, enable=True):
        """Enable and disable the conversion between analogic and digital
            signals

            """
        cdef DWORD enable_code, error_code
        if enable:
            enable_code = 1
        else:
            enable_code = 0
        pdaq._PdAInEnableConv(self.hadapter, &error_code, 
                              enable_code)
        return error_code




    def _set_clocking(self, sample_freq=None):
        """
        Set the clocking parameters Cv and Cl

        input: sample_freq   (the frequency in Hz)

        For each clock
        $$   dt_v = dt_{min}  (Cv + 1),  $$
        where $dt_v$ is the period of time between two conversions, ...


        """
        cdef DWORD error_code

        if sample_freq is not None:
            self.freq_used = float(sample_freq)

        C_coef = self._compute_clock_coef(self.freq_used)
        if (self.Cv_master):
            self.clock_conv_Cv_coef = C_coef
            pdaq._PdAInSetCvClk(self.hadapter, &error_code,
                                self.clock_conv_Cv_coef)
            self.freq_used = self.freq_max/(self.clock_conv_Cv_coef + 1)
            self.dt_channel_list = float(self.nb_channels_used)/self.freq_used

        else:
            self.clock_list_Cl_coef = C_coef
            pdaq._PdAInSetClClk(self.hadapter, &error_code,
                                self.clock_list_Cl_coef)
            self.freq_used = self.freq_max/(self.clock_list_Cl_coef + 1)
            self.dt_channel_list = 1./self.freq_used





    def _set_channel_list(self, channels, gain_channels, 
                          slow_bits_for_delay):
        cdef DWORD error_code

        if channels is None:
            pass
        elif isinstance(channels, (list, tuple, np.ndarray)):
            self.nb_channels_used = len(channels)
            if not self.nb_channels_used > 0:
                raise ValueError('channels is empty')
            self.channels = channels
        elif isinstance(channels, (int)):
            self.nb_channels_used = 1
            self.channels = [channels]

        if isinstance(gain_channels, (list, tuple, np.ndarray)):
            self.gain_channels = np.array(gain_channels, dtype=np.uint32)
        elif isinstance(gain_channels, int):
            self.gain_channels = gain_channels*np.ones(
                self.nb_channels_used, dtype=np.uint32)
        else:
            raise ValueError('problem with gain_channels')

        if any(self.gain_channels<1) or any(self.gain_channels>4):
            raise ValueError('gain_channels should be between 1 and 4.')

        if len(self.gain_channels) != self.nb_channels_used:
            raise ValueError(
                'channels and gain_channels should have the same length\n'+
                '(the number of channels).')


        if isinstance(slow_bits_for_delay, bool):
            self.slow_bits_for_delay = [
                slow_bits_for_delay 
                for i in xrange(self.nb_channels_used)]
        elif  isinstance(slow_bits_for_delay, (list, tuple, np.array)):
            if len(slow_bits_for_delay) != self.nb_channels_used:
                raise ValueError(
                    'channels and slow_bits_for_delay '+
                    'should have the same length\n'+
                    '(the number of channels).')
            self.slow_bits_for_delay = list(slow_bits_for_delay)


        self.channel_list = np.zeros(self.nb_channels_used, 
                                     dtype=np.uint32)

        for ic, channel_indice in enumerate(self.channels):
            code_channel = "{0:06b}".format(channel_indice)

            if self.slow_bits_for_delay[ic]:
                code_slow_bit = "1"
            else:
                code_slow_bit = "0"

            if self.gain_channels[ic] == 1:
                code_gain = "00"
            elif self.gain_channels[ic] == 2:
                code_gain = "01"
            elif self.gain_channels[ic] == 3:
                code_gain = "10"
            elif self.gain_channels[ic] == 4:
                code_gain = "11"
            else:
                raise ValueError(
                    'gain_channels should be an int between 1 and 4...')

            self.channel_list[ic] = <DWORD> int(
                code_slow_bit+code_gain+code_channel, 
                base=2)

        self._set_channel_list_in_board()


    def _set_channel_list_in_board(self):
        cdef DWORD error_code

        pdaq._PdAInSetChList(self.hadapter, &error_code,
                             <DWORD> self.nb_channels_used, 
                             <DWORD*> &(self.channel_list.data[0]))


    def _verify_channel_list(self):

        for val in self.channel_list:
            print('channel code: {0:3d}'.format(val), 
                  '{0:09b}'.format(val))






    def _read_with_fifo(self, nb_acq_channel_list):
        cdef DWORD nb_this_sample, error_code
        cdef np.ndarray volts
        cdef np.ndarray[np.uint16_t] raw_values
        cdef int nb_values_got

        cdef np.uint16_t *craw


        if isinstance(nb_acq_channel_list, float):
            nb_acq_channel_list = int(np.round(nb_acq_channel_list))

        nb_values = nb_acq_channel_list*self.nb_channels_used
        t_expect = nb_acq_channel_list*self.dt_channel_list


        # nFIFO = 512
        nFIFO = 400#512 # Number of value in FIFO before transfer only
        # 400 in order to avoid a strange bug (see the remark below on
        # the C array and the numpy array).
        len_raw = nb_values+nFIFO-1
        # raw_values = np.empty(len_raw, dtype=np.uint16, order='C')
        # raw_values = np.ones(len_raw, dtype=np.uint16, order='C')
        # raw_values = np.zeros(len_raw, dtype=np.uint16, order='C')

        craw = <np.uint16_t *> malloc(len_raw* sizeof(np.uint16_t))

        dt = self.dt_channel_list/self.nb_channels_used
        tFIFO = min(nFIFO*dt, 100.)  # Maximum wait interval

        # print('self.dt_channel_list {0:9.6g}'.format(self.dt_channel_list)
        # print('self.nb_channels_used', self.nb_channels_used)
        # print('dt {0:10.6g}'.format(dt))
        # print('tFIFO {0:10.6g}'.format(tFIFO))

        if self.ready:
            self.converting = True
            self.ready = False
        else:
            raise ValueError('not ready...')

        if not self.external_trigger:
            pdaq._PdAInSwClStart(self.hadapter, &error_code)
            noerror = pdaq._PdAInSwStartTrig(self.hadapter, &error_code)
            _print_if_error(noerror, error_code, '_PdAInSwStartTrig')

        # total_time_slept = 0.
        # lnb_this_sample = []

        nb_values_got = 0
        while nb_values_got < nb_values:
            if (nb_values_got < nb_values - nFIFO):
                time_to_sleep = tFIFO
            else:
                # Wait for expected time to acquire remaining samples
                time_to_sleep = max(dt*(nb_values - nb_values_got),0.001)

            time.sleep(time_to_sleep)
            pdaq._PdImmediateUpdate(self.hadapter, &error_code)

            # Retrieve as many values as possible at this point
            # pdaq._PdAInGetSamples(
            #     self.hadapter, &error_code,
            #     <DWORD> len_raw - nb_values_got,
            #     <WORD*> &(raw_values[nb_values_got]),
            #     <DWORD*> &(nb_this_sample))

            # Rmk: it could worth it to use a C array in place of the
            # numpy array raw_values (for speed reasons). Define it;
            # allocate the memory; after the function call, copy the
            # data into the numpy array; free the C array memory...

            pdaq._PdAInGetSamples(
                self.hadapter, &error_code,
                <DWORD> len_raw - nb_values_got,
                <WORD*> &(craw[nb_values_got]),
                <DWORD*> &(nb_this_sample))

            nb_values_got += nb_this_sample
            # lnb_this_sample.append(nb_this_sample)


        # print('nb_this_sample', nb_this_sample)
        # print('total_time_slept', total_time_slept)

        # print('nb_values_got', nb_values_got, 'nb_this_sample', nb_this_sample)

        self.converting = False
        self.ready = True

        raw_values = np.empty(nb_values_got, dtype=np.uint16, order='C')
        for i in xrange(nb_values_got):
            raw_values[i] = craw[i]
        free(craw)

        # print('raw_values', raw_values)

        # Convert raw to volt
        volts = self._convert_raw_to_volt(raw_values, nb_values)

        # if abs(volts[0,0])>1:
        #     print('raw_values', raw_values)

        return volts



    def _convert_raw_to_volt(self, raw, nb_values):
        """be careful gain !!"""

        raw = raw[:nb_values]
        raw = raw.reshape([nb_values/self.nb_channels_used,
                           self.nb_channels_used])
        raw = raw.transpose()

        volts = (raw ^ 0x8000)* self.bit_weight
        if self.bipolar:
            volts -= self.volt_max

        # take into account the gain for each channel
        if np.any(self.gain_channels > 1):
            for ic in xrange(self.nb_channels_used):
                if self.gain_channels[ic] != 1:
                    volts[ic] /= self.gain_coefs[self.gain_channels[ic]-1]

        return volts






    def __call__(self, nb_acq=10, return_times=False):

        cdef DWORD error_code

        if nb_acq < 0:
            print('Warning: nb_acq < 0 is incorrect! nb_acq = abs(nb_acq)')
            nb_acq = abs(nb_acq)

        self._change_enable_conversion(enable=True)

        volts = self._read_with_fifo(nb_acq)

        pdaq._PdAInSwStopTrig(self.hadapter, &error_code)
        pdaq._PdAInClearData(self.hadapter, &error_code)

        # These lines usually avoid a ununderstandable bug dealing
        # with the first values measured...
        self._change_enable_conversion(enable=False)
        self._change_set_config()
        self._set_channel_list_in_board()
        self._set_clocking()

        if not return_times:
            return volts
        else:
            ts = 1./self.freq_used*(np.arange(nb_acq)+1)
            return ts, volts















cdef class AnalogOutput(AnalogicSubSystem):

    cdef DWORD nb_max_out_volts
    cdef np.ndarray raw_values
    cdef DWORD nb_values
    cdef DWORD raw_0V

    cdef DWORD* pbuffer
    cdef object buffer_acquired

    cdef object method, loop
    cdef object start

    def __init__(self, PowerDAQBoard board):
        cdef DWORD error_code

        self.code_subsystem = 2 # means "analogic output"
        super(AnalogOutput, self).__init__(board)

        # Reset
        noerror = pdaq._PdAOutReset(self.hadapter, &error_code)
        _print_if_error(noerror, error_code, '_PdAOutReset in __init__')

        self.nb_max_out_volts = 2*1024*1024

        # always the case for the analogic output
        self.bit_weight = 20./0xFFF
        self.raw_0V = int(np.round(0xFFF/2))
        self.range_volt = 20.
        self.volt_max = 10.
        self.channel_list = np.array([0, 1])
        self.nb_channels_used = 2

        # these parameters can be modified
        self.freq_used = 1.
        self.loop = False
        self.external_trigger = False
        self.converting = False
        self.ready = False
        self.method = 'NONE'

        self.buffer_acquired = False


    def __dealloc__(self):
        cdef DWORD error_code
        # print('run __dealloc__() AnalogOutput')
        self.stop()


    def stop(self):
        cdef DWORD error_code
        # print('run stop()        AnalogOutput')
        # Disable conversion
        if self.method in ['FIFO', 'direct']:
            pdaq._PdAOutSwStopTrig(self.hadapter, &error_code)
            pdaq._PdAOutEnableConv(self.hadapter, &error_code, 0)
        elif self.method == 'buffer':
            pdaq._PdAOutAsyncStop(self.hadapter, &error_code)
            pdaq._PdAOutAsyncTerm(self.hadapter, &error_code)
            self._release_buffer()

        pdaq._PdAOutEnableConv(self.hadapter, &error_code, 0)

        noerror = pdaq._PdAOutReset(self.hadapter, &error_code)
        # _print_if_error(noerror, error_code, '_PdAOutReset (in stop())')

        self.method = 'None'


    def __call__(self, 
                 out0=None,
                 out1=None,
                 frequency=None,
                 loop=False,
                 start=True,
                 external_trigger=False,
                 return_times=False
    ):
        cdef DWORD error_code

        # Stop what is currently happening
        self.stop()

        self.loop = loop
        self.external_trigger = external_trigger

        # Basic configuration
        if frequency is not None: # Internal conversion clock
            self.code_config = AOB_CVSTART0 
        else: # External conversion clock
            self.code_config = AOB_CVSTART1 
            frequency = 100.

        self.clock_conv_Cv_coef = np.round(self.freq_max/frequency) - 1
        self.freq_used = self.freq_max/(self.clock_conv_Cv_coef+1)

        if external_trigger:
            self.start = False
            self.code_config = self.config_code + AOB_STARTTRIG0
        else:
            self.start = start
            self.code_config = self.code_config & ~AOB_STARTTRIG0


        # Create output values
        if out0 is not None:
            if isinstance(out0, (list, tuple, np.ndarray)):
                nb_values_channel0 = len(out0)
            elif isinstance(out0, (float, int)):
                nb_values_channel0 = 1
            else:
                raise ValueError('prob with out0')

        if out1 is not None:
            if isinstance(out1, (list, tuple, np.ndarray)):
                nb_values_channel1 = len(out1)
            elif isinstance(out0, (float, int)):
                nb_values_channel1 = 1
            else:
                raise ValueError('prob with out1')

        if out0 is not None and out1 is not None:
            # use both channels
            self.nb_values = nb_values_channel0
            if  nb_values_channel0 !=  nb_values_channel1:
                raise ValueError(
                    'out0 and out1 do not contain the same number of values.')
            self._volt_to_raw(volts0=out0, volts1=out1)

        elif out0 is not None and out1 is None:
            # use only one channel
            self.nb_values = nb_values_channel0
            self._volt_to_raw(volts0=out0)

        elif out0 is None and out1 is not None:
            # use only one channel
            self.nb_values = nb_values_channel1
            self._volt_to_raw(volts1=out1)

        if self.nb_values == 1:
            # print('output with method "direct"')
            self._out_constant()
        else:
            if self.nb_values <= 2048:
                # Only a relatively small amount of data
                # print('output with method "FIFO"',
                      # '{}'.format(self.nb_values))
                self._out_with_fifo()
            else:
                # print('output with method "buffer"',
                      # '{}'.format(self.nb_values))
                self._out_with_buffer()

            # Enable conversion
            if self.start:
                pdaq._PdAOutAsyncStart(self.hadapter, &error_code)
                self.converting = True
                self.ready = False
            elif self.external_trigger:
                self.converting = True
                self.ready = False
            else:
                self.converting = False
                self.ready = True

            if return_times:
                return 1./self.freq_used*(np.arange(self.nb_values)+1)




    def _release_buffer(self):
        cdef DWORD error_code
        if self.buffer_acquired:
            noerror = pdaq._PdReleaseBuffer(
                self.hadapter, &error_code,
                self.code_subsystem, self.pbuffer)
            if noerror:
                self.buffer_acquired = False



    def _out_constant(self):
        """out constant value ..."""
        cdef DWORD raw_value, error_code

        raw_value = self.raw_values[0]

        if (self.method != 'direct'):
            self.method = 'direct'
            # Basic configuration
            self.code_config = 0
            pdaq._PdAOutSetCfg(self.hadapter, &error_code,
                               self.code_config, 0)

        if not self.external_trigger:
            # Start analog input and output using software
            pdaq._PdAOutSwStartTrig(self.hadapter, &error_code)

        # Output
        pdaq._PdAOutPutValue(self.hadapter, &error_code,
                             raw_value)
        self.converting = False
        self.ready = False




    def _out_with_fifo(self):
        """ Method used when there is only a relatively small
        amount of data"""
        cdef DWORD nb_written, error_code

        self.method = 'FIFO'

        if self.loop:
            self.code_config += AOB_REGENERATE

        pdaq._PdAOutSetCfg(self.hadapter, &error_code,
                           self.code_config, 0)
        pdaq._PdAOutSetCvClk(self.hadapter, &error_code,
                             self.clock_conv_Cv_coef)
        # Buffer output - limited to 2048 samples in FIFO
        pdaq._PdAOutClearData(self.hadapter, &error_code)

        pdaq._PdAOutPutBlock(self.hadapter, &error_code,
                             self.nb_values,
                             <DWORD*> &(self.raw_values.data[0]),
                             &nb_written)

        # Enable conversion
        pdaq._PdAOutEnableConv(self.hadapter, &error_code, 1)
        if not self.external_trigger:
            # Start analog input and output using software
            pdaq._PdAOutSwStartTrig(self.hadapter, &error_code)



    def _out_with_buffer(self):
        """ Method used when too much data
        
        Asyncronous oscillation using circular buffer
        """
        cdef DWORD error_code

        pdaq._PdAOutSetCfg(self.hadapter, &error_code,
                           self.code_config, 0)
        self.method = 'buffer'
        if self.loop:
            mode = BUF_BUFFERWRAPPED|BUF_BUFFERRECYCLED
        else:
            mode = 0

        self._release_buffer()

        noerror = pdaq._PdAcquireBuffer(
            self.hadapter, &error_code,
            <void **> &(self.pbuffer), 1,
            <DWORD> int(self.nb_values/2), <DWORD> 2,
            self.code_subsystem, BUF_DWORDVALUES|mode
        )
        if noerror:
            self.buffer_acquired = True

        memcpy(self.pbuffer, 
               <DWORD*> &(self.raw_values.data[0]), 
               sizeof(DWORD)*self.nb_values
           )

        pdaq._PdAOutAsyncInit(self.hadapter, &error_code,
                              self.code_config, 
                              self.clock_conv_Cv_coef, 0)





    def _volt_to_raw(self, volts0=None, volts1=None):
        """Convert_volt_to_raw. 

        The volt values are coded in the raw array on 12 bits.  Each
        time represent 2 channels is coded on one uint32 (12x2 bits +
        8 unsued bits).

        """
        dtype_raw = dt_DWORD_def

        if self.nb_values > self.nb_max_out_volts:
            print('too much data in out0 or/and out1.')
            self.nb_values = self.nb_max_out_volts
            volts0 = volts0[:self.nb_values]
            volts1 = volts1[:self.nb_values]

        if volts0 is None:
            raw0 = self.raw_0V*np.ones(self.nb_values, dtype=dtype_raw)
        else:
            raw0 = np.array(
                np.round((volts0+10)/self.bit_weight), 
                dtype=dtype_raw)
            if self.nb_values > 1:
                raw0[raw0<0] = 0
                raw0[raw0>0xFFF] = 0xFFF
            elif raw0 < 0: raw0 = 0
            elif raw0 > 0xFFF: raw0 = 0xFFF

        if volts1 is None:
            raw1 = self.raw_0V*np.ones(self.nb_values, dtype=dtype_raw)
        else:
            raw1 = np.array(
                np.round((volts1+10)/self.bit_weight), 
                dtype=dtype_raw)

            if self.nb_values > 1:
                raw1[raw1<0] = 0
                raw1[raw1>0xFFF] = 0xFFF
            elif raw1 < 0: raw1 = 0
            elif raw1 > 0xFFF: raw1 = 0xFFF

        raw = (raw1<<12)|raw0
        self.raw_values = raw.flatten()
        # self.raw_values = np.array(raw, dtype=dtype_raw, order='C')



    def _raw_to_volt(self):

        raw = np.array(self.raw_values, dtype=np.uint32)
        raw0 = raw & 0xFFF
        raw1 = (raw >> 12) & 0xFFF 

        print('raw0', raw0)
        print('raw1', raw1)

        volts0 = raw0*self.bit_weight - 10
        volts1 = raw1*self.bit_weight - 10

        print('volts0 ', volts0)
        print('volts1', volts1)







cdef class DigitalInput(SubSystem):

    def __init__(self, PowerDAQBoard board):
        cdef DWORD error_code


        self.code_subsystem = 3 # means digital input
        SubSystem.__init__(self, board)

        noerror = pdaq._PdDInReset(self.hadapter, &error_code)

        # noerror = pdaq._PdDInSetPrivateEvent(self.hadapter,
        #                                      loc(UEI%DIn%hEvent))

        # integer (4), parameter :: eDInEvent = ishft(1,0) ! Digital
        # Input event 

        # noerror = pdaq._PdSetUserEvents(self.hadapter,
        # &error_code, self.code_subsystem, eDInEvent)



cdef class DigitalOutput(SubSystem):

    def __init__(self, PowerDAQBoard board):
        cdef DWORD error_code

        self.code_subsystem = 4 # means digital input
        SubSystem.__init__(self, board)

        noerror = pdaq._PdDOutReset(self.hadapter, &error_code)


    def write(self, DWORD value):

        cdef DWORD error_code

        _PdDOutWrite(self.hadapter, &error_code, value)








cdef class AccurateTimmer(object):
    cdef np.int64_t frequency, count1, count2

    def __init__(self):
        error_code = QueryPerformanceFrequency(&(self.frequency))

    def start(self):
        QueryPerformanceFrequency(&(self.frequency))
        QueryPerformanceCounter(&self.count1)

    def end(self):
        QueryPerformanceCounter(&self.count2)
        return <np.float64_t>(self.count2-self.count1)/self.frequency

    def test(self):
        """time.sleep 0.5 and count (the 2 methods should be based on the same 
        principle)"""
        t1 = time.clock()
        self.start()
        time.sleep(0.5)
        t2 = time.clock()
        result = self.end()
        print('t2-t1 =',t2-t1, ' ;(count2-count1)/freq =', result)




cdef class PowerDAQBoard(object):
    """."""
    # number of nodes in the first and second dimensions
    cdef HANDLE hdriver 
    cdef HANDLE hadapter
    cdef DWORD num_adapters

    cdef public object ain, aout, timer, din, dout, works

    def __init__(self, init_analog_in=True, init_analog_out=True, 
                 init_digital_in=True, init_digital_out=True):
        cdef DWORD error_code

        print('Initialization of the board')
        self.works = True
        self.timer = AccurateTimmer()

        self.num_adapters = 1
        noerror = pdaq.PdDriverOpen(&(self.hdriver), &error_code, 
                                    &(self.num_adapters))
        _print_if_error(noerror, error_code, 'PdDriverOpen')

        noerror = pdaq._PdAdapterOpen(0, &error_code, &(self.hadapter))
        _print_if_error(noerror, error_code, '_PdAdapterOpen')

        noerror = pdaq._PdAdapterEnableInterrupt(self.hadapter, 
                                                 &error_code, 1)
        _print_if_error(noerror, error_code, '_PdAdapterEnableInterrupt')

        if init_analog_in:
            self.ain = AnalogInput(self)

        if init_analog_out:
            self.aout = AnalogOutput(self)

        if init_analog_in:
            self.din = DigitalInput(self)

        if init_analog_out:
            self.dout = DigitalOutput(self)





    def print_info(self):
        print('no infos to give...')




    def __dealloc__(self):
        cdef DWORD error_code
        # print('dealloc board')

        self.aout.stop()

        noerror = pdaq._PdAdapterClose(self.hadapter, &error_code)
        _print_if_error(noerror, error_code, '_PdAdapterClose')

        noerror = pdaq.PdDriverClose(self.hdriver, &error_code)
        _print_if_error(noerror, error_code, 'PdDriverClose')





