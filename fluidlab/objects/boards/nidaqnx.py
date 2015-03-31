"""National Instrument board (:mod:`fluidlab.objects.boards.nidaqnx`)
=====================================================================

.. currentmodule:: fluidlab.objects.boards.nidaqnx

Provides:

.. autoclass:: NIDAQBoard
   :members:
   :private-members:

.. autoclass:: AnalogicOutput
   :members:
   :private-members:

.. autoclass:: AnalogicInput
   :members:
   :private-members:


"""
from __future__ import division, print_function

try:
    import PyDAQmx as daq
    works = True
except (IOError, ImportError):
    works = False

import numpy as np


class NIDAQBoard(object):
    """Handle for a National Instrument board (NIDAQNX)."""
    def __init__(self):
        self.out = AnalogicOutput()
        self.works = True


class AnalogicOutput(object):
    """Analogic output."""
    def __init__(self):

        self.tasks = []
        for i in range(2):
            self.tasks.append(daq.Task())

        # self.task = daq.Task()

        for i in range(2):
            self.tasks[i].CreateAOVoltageChan(
                'Dev2/ao{:1d}'.format(i), '', 0, 5.0, daq.DAQmx_Val_Volts, '')
            self.tasks[i].StartTask()

        # data = np.array(0., dtype=np.float64)

        # int32 DAQmxWriteAnalogF64 (
        #     TaskHandle taskHandle, int32 numSampsPerChan, 
        #     bool32 autoStart, float64 timeout, bool32 dataLayout, 
        #     float64 writeArray[], 
        #     int32 *sampsPerChanWritten, bool32 *reserved);

        # self.task.WriteAnalogF64(
        #     1, 1, 0., daq.DAQmx_Val_GroupByChannel, data, None, None)

        self.set_voltage(0, channels=[0, 1])

    def set_voltage(self, val, channels=0):

        if isinstance(channels, (list, tuple, np.ndarray)):
            for channel in channels:
                self.set_voltage(val, channel)
        else:
            data = np.array(val, dtype=np.float64)
            self.tasks[channels].WriteAnalogF64(
                1, 1, 0., daq.DAQmx_Val_GroupByChannel, data, None, None)







class AnalogicInput(object):
    """Analogic input."""
    def __init__(self):
        self.task = daq.Task()

        self.task.CreateAIVoltageChan(
            "Dev2/ai0", "", DAQmx_Val_Cfg_Default, 
            -10.0,10.0,daq.DAQmx_Val_Volts,None)
        self.task.CfgSampClkTiming(
            "", 10000.0, daq.DAQmx_Val_Rising, daq.DAQmx_Val_FiniteSamps, 1000)

        self.task.StartTask()


    def read(self):
        pass

        # self.task.ReadAnalogF64(1000, 10.0, daq.DAQmx_Val_GroupByChannel,
        #                         data, 1000, &read, None)




if __name__ == "__main__":

    from time import sleep

    out = AnalogicOutput()

    out.set_voltage(0.2)

    sleep(20)
    out.set_voltage(0)


    # input = AnalogicInput()


