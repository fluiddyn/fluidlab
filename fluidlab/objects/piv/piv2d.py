"""PIV 2d
=========

"""
from __future__ import print_function, division

import os
import time
import sys
from glob import glob
from math import ceil

import numpy as np

from labjack import ljm

from fluiddyn.util.query import query_yes_no
from fluidlab.instruments.daq.streaming_t7 import T7

from fluidlab.exp import Timer
from .signal_double_frame import make_signal_double_frame
from .util import wait_for_file, save_exp, serial_numbers


path_save = os.path.join(os.path.expanduser("~"), '.fluidcoriolis')


def is_new_file(str_name):
    str_name = os.path.expanduser(str_name)
    files_start = glob(str_name)
    while True:
        files = glob(str_name)
        if len(files) > len(files_start):
            return max(files, key=os.path.getctime)
        time.sleep(0.1)


class PIV2D(object):
    """Trigger cameras for PIV 2D (single and double frame)

    Use a T7 board (Labjack).

    """
    def __init__(self):
        self.t7 = T7(identifier=serial_numbers['vert'])

    def single_frame_2d(self, dt, volt=5., total_time=None,
                        wait_file=False, nb_period_to_wait=1.):
        ''' Single frame 2D PIV.

        Send a square signal to trig cameras (DAC0)

        Parameters
        ----------

        dt:
          time between 2 images (in s)

        volt:
          voltage (in V)

        total_time=None:
          total time of acquisition (in s)

        '''
        volt = np.asarray([[0, 5]*6])
        t = np.arange(12) * dt / 2.0
        dt = t[2]
        IN_NAMES = []
        OUT_NAMES = ['DAC0']

        t7 = self.t7
        handle = t7.handle
        aScanList = t7.prepare_stream_loop(
            IN_NAMES=IN_NAMES, OUT_NAMES=OUT_NAMES, volt=volt)

        scanRate = len(OUT_NAMES) / dt
        scansPerRead = scanRate  # It should be an integer
        TOTAL_NUM_CHANNELS = len(IN_NAMES) + len(OUT_NAMES)

        print(
            '\n' + '-' * 79 + '\n' +
            'Connect DAC0 to connector 1 of PCO Edge camera'
            '\n' + '-' * 79 + '\n\n' +
            'Settings in Camware software\n\n'
            '- trigger Mode to "Ext Exp Start"\n'
            '- frame rate >= {} Hz\n'.format(1.0/dt) +
            '- exposure <= {} s \n'.format(dt) +
            '- acquire Mode to "Auto"\n'
            '- I/O Signal: tick only "Exposure Trigger"\n')

        if not query_yes_no('Are you ready to start acquisition?'):
            return

        if wait_file:
            wait_for_file('oscillate_*', nb_period_to_wait)

        save_exp(t, volt, dt=dt, rootname='piv2d_single_frame')

        scanRate = ljm.eStreamStart(
            handle, int(scansPerRead), TOTAL_NUM_CHANNELS, aScanList, scanRate)
        print('Stream started')

        t7.wait_before_stop(total_time, dt)

    def double_frame_2d(self, time_between_pairs, time_expo, delta_t,
                        nb_couples, nb_nodes=256,
                        wait_file=False, nb_period_to_wait=1.):
        """
        Double frame 2D PIV.

        # TODO: Understand volts.

        Parameters
        ----------

        Returns
        -------
        """

        times_signal, volts_signal, time_expo, delta_t, time_between_nodes = \
            make_signal_double_frame(
                time_between_pairs, time_expo, delta_t, nb_nodes)
        # print(volts_signal)

        print(
            'New values for the variables:\n' +
            ('time_between_pairs = {} s\n'
             'time_expo = {} s\n'
             'delta_t = {}').format(time_between_pairs, time_expo, delta_t))

        t7 = self.t7
        handle = t7.handle

        IN_NAMES = []
        OUT_NAMES = ['DAC0']

        a = [v for v in volts_signal]
        # To do: which integer. 12 solves problems with the buffer
        # size encoding??
        volts = np.array([np.array(a)])
        # print(volts)
        aScanList = t7.prepare_stream(
            IN_NAMES=IN_NAMES, OUT_NAMES=OUT_NAMES, volt=volts)

        scanRate = len(OUT_NAMES)/time_between_nodes  # scans/s
        # scans for each call of the function eStreamRead. It should
        # be an integer
        scansPerRead = scanRate

        print('scanRate = {}'.format(scanRate))
        print('ScansPerRead = {}'.format(scansPerRead))

        TOTAL_NUM_CHANNELS = len(IN_NAMES) + len(OUT_NAMES)

        print(
            '\n' + '-' * 79 + '\n' +
            'Connect DAC0 to connector 1 of PCO Edge camera'
            '\n' + '-' * 79 + '\n\n' +
            'Settings in Camware software\n\n'
            '- trigger Mode to "Ext Exp Start"\n'
            '- frame rate >= {} Hz\n'.format(1./delta_t) +
            '- exposure <= {} s \n'.format(time_expo) +
            '- acquire Mode to "Auto"\n'
            '- I/O Signal: tick only "Exposure Trigger"\n')

        if not query_yes_no('Are you ready to start acquisition?'):
            return

        if wait_file:
            wait_for_file('oscillate_*', nb_period_to_wait)

        save_exp(times_signal, volts_signal, dt=delta_t, time_expo=time_expo,
                 time_between_pairs=time_between_pairs,
                 rootname='piv2d_double_frame')

        timer = Timer(time_between_pairs)
        try:
            for i in range(nb_couples):
                scanRate = ljm.eStreamStart(
                    handle, int(scansPerRead), TOTAL_NUM_CHANNELS,
                    aScanList, scanRate)
                print('\r{}/{}'.format(i+1, nb_couples), end='')
                sys.stdout.flush()
                time.sleep(2 * delta_t)
                t7.write_out_buffer('STREAM_OUT0_BUFFER_F32', volts[0])
                timer.wait_tick()
        except KeyboardInterrupt:
            pass
        finally:
            t7.stop_stream()


    def set_voltage(self, volt):
        ljm.eWriteName(self.t7.handle, 'DAC0', volt)

    def stop_stream(self):
        return self.t7.stop_stream()

    def close(self):
        return self.t7.close()


if __name__ == '__main__':

    time_between_pairs = 1.
    time_expo = 0.1
    delta_t = 0.3
    n = 256

    total_time = 30

    piv = PIV2D()

    piv.double_frame_2d(time_between_pairs, time_expo, delta_t, total_time, n)
