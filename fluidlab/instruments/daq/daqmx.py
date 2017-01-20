"""
DAQmx (National Instruments, :mod:`fluidlab.instruments.daq.daqmx`)
===================================================================

.. todo:: DAQmx interface and drivers (using Comedi API?)...

Provides:

.. autofunction:: read_analog

.. autofunction:: write_analog

.. autofunction:: measure_freq


"""

from __future__ import print_function

from collections import Iterable
from numbers import Number
from platform import platform
import time

import numpy as np

import ctypes
import six

from PyDAQmx import Task, byref, float64, int32, uInt32

from PyDAQmx import (
    DAQmx_Val_Cfg_Default, DAQmx_Val_RSE, DAQmx_Val_NRSE, DAQmx_Val_Diff,
    DAQmx_Val_Volts, DAQmx_AI_Coupling,
    DAQmx_Val_DC, DAQmx_Val_AC, DAQmx_Val_GND,
    DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, DAQmx_Val_GroupByChannel,
    DAQmx_Val_Hz, DAQmx_Val_LowFreq1Ctr)

try:
    from PyDAQmx import DAQmx_Val_PseudoDiff
except ImportError:
    DAQmx_Val_PseudoDiff = None
    pass

_coupling_values = {
    'DC': DAQmx_Val_DC, 'AC': DAQmx_Val_AC, 'GND': DAQmx_Val_GND}


def _parse_resource_names(resource_names):

    if isinstance(resource_names, six.string_types):
        if six.PY3 and isinstance(resource_names, str):
            resource_names = resource_names.encode('ascii')
        resource_names = [resource_names]
    elif isinstance(resource_names, Iterable):
        if six.PY3 and isinstance(resource_names[0], str):
            resource_names = [r.encode('ascii') for r in resource_names]
    else:
        raise ValueError('resource_names has to be a string or an iterable.')

    nb_resources = len(resource_names)

    return resource_names, nb_resources


def read_analog(resource_names, terminal_config, volt_min, volt_max,
                samples_per_chan=1, sample_rate=1, coupling_types='DC',
                output_filename=None, verbose=False):
    """Read from the analog input subdevice.

    Parameters
    ----------

    resource_names: {str or iterable of str}

      Analogic input identifier(s), e.g. 'Dev1/ai0'.

    terminal_config: {'Diff', 'PseudoDiff', 'RSE', 'NRSE'}

      A type of configuration (apply to all terminals).

    volt_min : {number or iterable of numbers}

      Minima for the channels.

    volt_max : {number or iterable of numbers}

      Maxima for the channels.

    samples_per_chan: number

      Number of samples per channel to read.

    sample_rate: number

      Sample rate for all channels (Hz).

    coupling_types : {'DC', 'AC', 'GND', list of str}

      Type of coupling for each resource.

    output_filename: {None, str}

      If specified data is output into this file instead of output
      arrays.

    verbose: {False, boolean}

      If True, print more verbose message

    """
    if output_filename is not None:
        raise NotImplementedError()

    # prepare resource_names
    resource_names, nb_resources = _parse_resource_names(resource_names)

    # prepare terminal_config
    if terminal_config is None:
        if verbose:
            print('DAQmx: Default terminal configuration will be used.')
        terminal_config = DAQmx_Val_Cfg_Default
    elif terminal_config == 'RSE':
        if verbose:
            print('DAQmx: Referenced single-ended mode')
        terminal_config = DAQmx_Val_RSE
    elif terminal_config == 'NRSE':
        if verbose:
            print('DAQmx: Non-referenced single-ended mode')
        terminal_config = DAQmx_Val_NRSE
    elif terminal_config == 'Diff':
        if verbose:
            print('DAQmx: Differential mode')
        terminal_config = DAQmx_Val_Diff
    elif terminal_config == 'PseudoDiff':
        if verbose:
            print('DAQmx: Pseudodifferential mode')
        terminal_config = DAQmx_Val_PseudoDiff
    else:
        raise ValueError('DAQmx: Unrecognized terminal mode')

    # prepare volt_min, volt_max
    if not isinstance(volt_min, Number) and len(volt_min) != nb_resources:
        raise ValueError(
            'volt_min has to be a number or an iterable of the same length '
            'as resource_names')
    if not isinstance(volt_max, Number) and len(volt_max) != nb_resources:
        raise ValueError(
            'volt_max has to be a number or an iterable of the same length '
            'as resource_names')
    if isinstance(volt_min, Number):
        volt_min = [volt_min] * nb_resources
    if isinstance(volt_max, Number):
        volt_max = [volt_max] * nb_resources

    # check samples_per_chan
    if not isinstance(samples_per_chan, six.integer_types) or samples_per_chan <= 0:
        raise ValueError('samples_per_chan has to be a positive integer.')

    # prepare coupling_types
    if (not isinstance(coupling_types, six.string_types) and
            len(coupling_types) != nb_resources):
        raise ValueError(
            'coupling_types has to be a number or an iterable '
            'of the same length as resource_names')
    if isinstance(coupling_types, six.string_types):
        coupling_types = [coupling_types] * nb_resources

    possible_keys_coupling = _coupling_values.keys()
    for coupling in coupling_types:
        if coupling not in possible_keys_coupling:
            raise ValueError(
                'Bad value in coupling_types, got: {}'.format(coupling))

    if verbose:
        print('DAQmx: Create Task')
    task = Task()

    actual_volt_min = float64()
    actual_volt_max = float64()

    for ir, resource in enumerate(resource_names):
        if verbose:
            print('DAQmx: Create AI Voltage Chan (' + str(resource) + ' [' + str(volt_min[ir]) + 'V;' + str(volt_max[ir]) + 'V])')
        task.CreateAIVoltageChan(
            resource, '', terminal_config, volt_min[ir], volt_max[ir],
            DAQmx_Val_Volts, None)

    # Attention SetChanAttribute doit être dans une deuxième boucle car dans le cas d'une acquisition
    # multi-cartes, DAQmx impose que toutes les voies soient ajouté à la task avant
    # de changer quelque paramètre
    for ir, resource in enumerate(resource_names):
        # check volt range
        task.GetAIRngHigh(resource, byref(actual_volt_max))
        task.GetAIRngLow(resource, byref(actual_volt_min))
        actual_vmin = actual_volt_min.value
        actual_vmax = actual_volt_max.value
        if actual_vmin != volt_min[ir] or actual_vmax != volt_max[ir]:
            print('DAQmx: Actual range for ' + str(resource) +
                  ' is actually [{:6.2f} V, {:6.2f} V].'.format(
                      actual_vmin, actual_vmax))

        # set coupling
        coupling_value = _coupling_values[coupling_types[ir]]
        if verbose:
            for name, value in _coupling_values.items():
                if value == coupling_value:
                    print('DAQmx: Setting AI channel coupling (' + str(resource) + '): ' + name)
        task.SetChanAttribute(resource, DAQmx_AI_Coupling, coupling_value)

    # configure clock and DMA input buffer
    if samples_per_chan > 1:
        verbose_text = 'DAQmx: Configure clock timing ('
        if verbose:
            if samples_per_chan < 1000:
                verbose_text = verbose_text + str(samples_per_chan) + " samp/chan @ "
            elif samples_per_chan < 1000000:
                verbose_text = verbose_text + str(samples_per_chan/1000) + " kSamp/chan @ "
            else:
                verbose_text = verbose_text + str(samples_per_chan/1000000) + " MSamp/chan @ "
            if sample_rate < 1000:
                verbose_text = verbose_text + ("%.2f Hz using OnboardClock)" % sample_rate)
            elif sample_rate < 1000000:
                verbose_text = verbose_text + ("%.2f kHz using OnboardClock)" % (sample_rate/1000.0))
            else:
                verbose_text = verbose_text + ("%.2f MHz using OnboardClock)" % (sample_rate/1e6))
            print(verbose_text)
        task.CfgSampClkTiming(
            'OnboardClock', sample_rate, DAQmx_Val_Rising,
            DAQmx_Val_FiniteSamps, samples_per_chan)
        if verbose:
            print("DAQmx: Configure DMA input buffer")
        task.CfgInputBuffer(samples_per_chan)

    # start task
    if verbose:
        if platform().startswith('Windows'):
            dateformat = '%A %d %B %Y - %X (%z)'
        else:
            dateformat = '%A %e %B %Y - %H:%M:%S (UTC%z)'
        starttime = time.time()
        starttime_str = time.strftime(dateformat, time.localtime(starttime))
        endtime = starttime+samples_per_chan/sample_rate
        endtime_str = time.strftime(dateformat, time.localtime(endtime))
        print("DAQmx: Starting acquisition: " + starttime_str)
        print("       Expected duration: %.2f min" % (samples_per_chan/(60.0*sample_rate)))
        print("       Expected end time: " + endtime_str)

    task.StartTask()

    # read data
    # why 10?
    timeout = float(10*samples_per_chan / sample_rate)
    buffer_size_in_samps = int(samples_per_chan * nb_resources)
    data = np.zeros((buffer_size_in_samps,), dtype=np.float64)
    samples_per_chan_read = int32()
    task.ReadAnalogF64(
        samples_per_chan, timeout, DAQmx_Val_GroupByChannel, data,
        buffer_size_in_samps, byref(samples_per_chan_read), None)

    if verbose:
        print("DAQmx: %d samples read." % samples_per_chan_read.value)

    return data.reshape([nb_resources, samples_per_chan])


def write_analog(resource_names, sample_rate, signals, blocking=True):
    """Write analogic output

    Parameters
    ----------

    resource_name:

      Analogic input identifier(s), e.g. 'Dev1/ao0'.

    sample_rate: number

      Frequency rate for all channels (Hz).

    signals: numpy.ndarray

      The signals to be output.

    blocking: bool

      Specifies whether to wait until the task is done before
      returning. If blocking=false, then a task object is
      returned. To stop the task, ???.

    """
    # prepare resource_names
    resource_names, nb_resources = _parse_resource_names(resource_names)

    if signals.ndim == 1:
        nb_samps_per_chan = len(signals)
    elif signals.ndim == 2:
        nb_samps_per_chan = signals.shape[1]
    else:
        raise ValueError('signals has to be an array of dimension 1 or 2.')

    # create task
    task = Task()

    # create AO channels
    for ir, resource in enumerate(resource_names):
        task.CreateAOVoltageChan(
            resource, '', -10., 10., DAQmx_Val_Volts, None)

    # configure clock
    task.CfgSampClkTiming(
        '', sample_rate, DAQmx_Val_Rising,
        DAQmx_Val_FiniteSamps, nb_samps_per_chan)

    # write data
    written = int32()
    task.WriteAnalogF64(
        nb_samps_per_chan, 0, 10.0, DAQmx_Val_GroupByChannel,
        signals.ravel(), byref(written), None)

    task.StartTask()

    if blocking:
        task.WaitUntilTaskDone(1.1*nb_samps_per_chan/sample_rate)
        task.StopTask()
    else:
        return task


def write_analog_end_task(task, timeout=0.):
    """End task.

    Parameters
    ----------

    task : PyDAQmx.Task

      The task to end.

    timeout : number

      Time (in s) to wait before stopping the task if it is not done.

    """

    task.WaitUntilTaskDone(timeout)
    task.StopTask()
    task.ClearTask()


def measure_freq(resource_name, freq_min=1, freq_max=1000):
    """Write analogic output

    Parameters
    ----------

    resource_name: str

      Analogic input identifier, e.g. 'Dev1/ctr0'.

    freq_min : number

      The minimum frequency (Hz) that you expect to measure.

    freq_max : number

      The maximum frequency (Hz) that you expect to measure.

    """
    # create task
    task = Task()

    # it seems that this argument is actually not used with the method
    # DAQmx_Val_LowFreq1Ctr.
    measure_time = 0.5
    task.CreateCIFreqChan(
        resource_name, "", freq_min, freq_max, DAQmx_Val_Hz,
        DAQmx_Val_Rising, DAQmx_Val_LowFreq1Ctr, measure_time, 1, "")

    task.StartTask()

    timeout = 10
    result = float64()
    null = ctypes.POINTER(ctypes.c_uint)()
    task.ReadCounterScalarF64(timeout, byref(result), None)

    return result.value


if __name__ == '__main__':

    # data = read_analog(
    #     resource_names='dev1/ai0',
    #     terminal_config='Diff',
    #     volt_min=-10,
    #     volt_max=10,
    #     samples_per_chan=10,
    #     sample_rate=10,
    #     coupling_types='DC')

    # data = read_analog(
    #     resource_names=['dev1/ai{}'.format(ic) for ic in range(4)],
    #     terminal_config='Diff',
    #     volt_min=-10,
    #     volt_max=10,
    #     samples_per_chan=10,
    #     sample_rate=10,
    #     coupling_types='DC')

    # signals = np.cos(np.linspace(0, 2*np.pi, 100))
    # write_analog('dev1/ao0', 10, signals, blocking=True)

    signals = np.cos(np.linspace(0, 2*np.pi, 100))
    signals = np.vstack((signals, signals + 2))
    write_analog(['dev1/ao{}'.format(i) for i in (0, 2)], 10, signals,
                 blocking=True)
    
