"""
DAQmx (National Instruments, :mod:`fluidlab.instruments.daq.daqmx`)
===================================================================

.. todo:: DAQmx interface and drivers (using Comedi API?)...

Provides:

.. autofunction:: read_analog

"""

from collections import Iterable
from numbers import Number

import numpy as np

from PyDAQmx import Task, byref, float64, int32

from PyDAQmx import (
    DAQmx_Val_Cfg_Default, DAQmx_Val_RSE, DAQmx_Val_NRSE, DAQmx_Val_Diff,
    DAQmx_Val_PseudoDiff, DAQmx_Val_Volts, DAQmx_AI_Coupling,
    DAQmx_Val_DC, DAQmx_Val_AC, DAQmx_Val_GND,
    DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, DAQmx_Val_GroupByChannel)


_coupling_values = {
    'DC': DAQmx_Val_DC, 'AC': DAQmx_Val_AC, 'GND': DAQmx_Val_GND}


def read_analog(resource_names, terminal_config, volt_min, volt_max,
                samples_per_chan=1, sample_rate=1, coupling_types='DC',
                output_filename=None):
    """Read from the analog input subdevice.

    Parameters
    ----------

    resource_names: {str or iterable of str}

      Analogic input identifier(s), eg. 'Dev1/ai0'

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

    """

    if output_filename is not None:
        raise NotImplementedError()

    # prepare resource_names
    if isinstance(resource_names, str):
        resource_names = [resource_names]
    elif not isinstance(resource_names, Iterable):
        raise ValueError('resource_names has to be a string or an iterable.')

    nb_resources = len(resource_names)

    # prepare terminal_config
    if terminal_config is None:
        print('DAQmx: Default terminal configuration will be used.')
        terminal_config = DAQmx_Val_Cfg_Default
    elif terminal_config == 'RSE':
        print('DAQmx: Referenced single-ended mode')
        terminal_config = DAQmx_Val_RSE
    elif terminal_config == 'NRSE':
        print('DAQmx: Non-referenced single-ended mode')
        terminal_config = DAQmx_Val_NRSE
    elif terminal_config == 'Diff':
        print('DAQmx: Differential mode')
        terminal_config = DAQmx_Val_Diff
    elif terminal_config == 'PseudoDiff':
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
    if not isinstance(samples_per_chan, int) or samples_per_chan <= 0:
        raise ValueError('samples_per_chan has to be a positive integer.')

    # prepare coupling_types
    if (not isinstance(coupling_types, str) and
            len(coupling_types) != nb_resources):
        raise ValueError(
            'coupling_types has to be a number or an iterable '
            'of the same length as resource_names')
    if isinstance(coupling_types, str):
        coupling_types = [coupling_types] * nb_resources

    possible_keys_coupling = _coupling_values.keys()
    for coupling in coupling_types:
        if coupling not in possible_keys_coupling:
            raise ValueError(
                'Bad value in coupling_types, got: {}'.format(coupling))

    task = Task()

    actual_volt_min = float64()
    actual_volt_max = float64()

    for ir, resource in enumerate(resource_names):
        task.CreateAIVoltageChan(
            resource, '', terminal_config, volt_min[ir], volt_max[ir],
            DAQmx_Val_Volts, None)

        # check volt range
        task.GetAIRngHigh(resource, byref(actual_volt_max))
        task.GetAIRngLow(resource, byref(actual_volt_min))
        if actual_volt_min != volt_min or actual_volt_max != volt_max:
            print('DAQmx: Actual range for ' + resource +
                  ' is actually [{:6.2f} V, {:6.2f} V].'.format(
                      actual_volt_min, actual_volt_max))

        # set coupling
        coupling_value = _coupling_values[coupling_types[ir]]
        task.SetChanAttribute(resource, DAQmx_AI_Coupling, coupling_value)

    # configure clock and DMA input buffer
    if samples_per_chan > 1:
        task.CfgSampClkTiming(
            'OnboardClock', sample_rate, DAQmx_Val_Rising,
            DAQmx_Val_FiniteSamps, samples_per_chan)

        task.CfgInputBuffer(samples_per_chan)

    # start task
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

    return data.reshape([nb_resources, samples_per_chan])
