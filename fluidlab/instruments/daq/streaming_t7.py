"""Streaming with a T7 board (LabJack)
======================================

"""

import time

import numpy as np

from labjack import ljm

from fluiddyn.util.query import query_yes_no


def is_power2(num):
    'states if a number is a power of two'
    return ((num & (num - 1)) == 0) and num != 0


class T7(object):
    """Streaming with a T7 board (LabJack)

    """
    def __init__(self, identifier='ANY'):
        # Open a T7 board
        self.handle = ljm.openS('ANY', 'ANY', identifier)
        # handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")

        self.get_info()
        self._closed = False

    def __del__(self):
        self.close()

    def close(self):
        if not self._closed:
            ljm.close(self.handle)
            self._closed = True

    def stop_stream(self):
        handle = self.handle
        ljm.eWriteName(handle, 'DAC0', 0)
        ljm.eWriteName(handle, 'DAC1', 0)
        ljm.eStreamStop(handle)

    def get_info(self):
        info = ljm.getHandleInfo(self.handle)
        print(
            ("Opened a LabJack with Device type: %i, Connection type: %i,\n"
             "Serial number: %i, IP address: %s, "
             "Port: %i,\nMax bytes per MB: %i") %
            (info[0], info[1], info[2], ljm.numberToIP(info[3]),
             info[4], info[5]))

    def write_out_buffer(self, streamout, volt):
        """ to replace
            for l in volt:
                ljm.eWriteName(handle, "STREAM_OUT0_BUFFER_F32", l)
        """

        handle = self.handle
        maxpoints = 8  # 8 = max number points able to write
        N = volt.size
        nloop = N//maxpoints

        if nloop == 0:
            ljm.eWriteNameArray(handle, streamout, volt.size,
                                np.ndarray.tolist(volt))
        else:
            for i in range(nloop):
                ljm.eWriteNameArray(handle, streamout, maxpoints,
                                    np.ndarray.tolist(
                                        volt[i*maxpoints:
                                             i*maxpoints + maxpoints]))
            if N % maxpoints != 0:
                i += 1
                ljm.eWriteNameArray(handle, streamout, volt[i*maxpoints:].size,
                                    np.ndarray.tolist(volt[i*maxpoints:]))

    def prepare_stream_loop(self, IN_NAMES=None, OUT_NAMES=[], volt=[]):
        handle = self.handle

        if IN_NAMES is None:
            IN_NAMES = []

        NUM_IN_CHANNELS = len(IN_NAMES)

        NUM_OUT_CHANNELS = len(OUT_NAMES)

        for indout, out in enumerate(OUT_NAMES):
            outAddress = ljm.nameToAddress(OUT_NAMES[indout])[0]
            ljm.eWriteName(handle, "STREAM_OUT{}_ENABLE".format(indout), 0)
            ljm.eWriteName(handle, "STREAM_OUT{}_TARGET".format(indout),
                           outAddress)

            buffer_size = volt[indout].size*2

            if is_power2(buffer_size):
                ljm.eWriteName(
                    handle, "STREAM_OUT{}_BUFFER_SIZE".format(indout),
                    buffer_size)
            else:
                buffer_size = int(2**(int(np.log(buffer_size)/np.log(2))+1))
                ljm.eWriteName(
                    handle, "STREAM_OUT{}_BUFFER_SIZE".format(indout),
                    buffer_size)

            ljm.eWriteName(handle, "STREAM_OUT{}_ENABLE".format(indout), 1)

        for indout, out in enumerate(OUT_NAMES):
            self.write_out_buffer(
                "STREAM_OUT{}_BUFFER_F32".format(indout), volt[indout])
            ljm.eWriteName(
                handle, "STREAM_OUT{}_LOOP_SIZE".format(indout),
                volt[indout].size)
            ljm.eWriteName(handle, "STREAM_OUT{}_SET_LOOP".format(indout), 1)

        # Scanlist
        aScanList = []

        if IN_NAMES:
            aScanList = ljm.namesToAddresses(NUM_IN_CHANNELS, IN_NAMES)[0]
            aNames = ["AIN_ALL_NEGATIVE_CH", "AIN_ALL_RANGE"]
            aValues = [ljm.constants.GND, 10.0]
            # single-ended, +/-10V, 0 (default),
            # 0 (default)
            ljm.eWriteNames(handle, len(aNames), aNames, aValues)

        if OUT_NAMES:
            aScanList.extend(range(4800, 4800+NUM_OUT_CHANNELS))  # STREAM_OUT0
            aNames = ["STREAM_SETTLING_US", "STREAM_RESOLUTION_INDEX"]
            aValues = [0, 0]
            ljm.eWriteNames(handle, len(aNames), aNames, aValues)

        return aScanList

    def prepare_stream(self, IN_NAMES=[], OUT_NAMES=[], volt=[]):
        handle = self.handle
        NUM_IN_CHANNELS = len(IN_NAMES)
        NUM_OUT_CHANNELS = len(OUT_NAMES)

        for indout, out in enumerate(OUT_NAMES):
            outAddress = ljm.nameToAddress(OUT_NAMES[indout])[0]
            ljm.eWriteName(handle, "STREAM_OUT{}_ENABLE".format(indout), 0)
            ljm.eWriteName(handle, "STREAM_OUT{}_TARGET".format(indout),
                           outAddress)

            buffer_size = volt[indout].size*2
            if is_power2(buffer_size):
                ljm.eWriteName(
                    handle, "STREAM_OUT{}_BUFFER_SIZE".format(indout),
                    buffer_size)
            else:
                buffer_size = int(2**(int(np.log(buffer_size)/np.log(2))+1))
                ljm.eWriteName(
                    handle, "STREAM_OUT{}_BUFFER_SIZE".format(indout),
                    buffer_size)

            ljm.eWriteName(handle, "STREAM_OUT{}_ENABLE".format(indout), 1)

        for indout, out in enumerate(OUT_NAMES):
            ljm.eWriteName(handle, "STREAM_OUT{}_LOOP_SIZE".format(indout),
                           volt[indout].size)
            self.write_out_buffer("STREAM_OUT{}_BUFFER_F32".format(indout),
                                  volt[indout])
            ljm.eWriteName(handle, "STREAM_OUT{}_SET_LOOP".format(indout), 0)

        # Scanlist
        aScanList = []

        if IN_NAMES:
            aScanList = ljm.namesToAddresses(NUM_IN_CHANNELS, IN_NAMES)[0]
            aNames = ["AIN_ALL_NEGATIVE_CH", "AIN_ALL_RANGE"]
            aValues = [ljm.constants.GND, 10.0]
            # single-ended, +/-10V, 0 (default),
            # 0 (default)
            ljm.eWriteNames(handle, len(aNames), aNames, aValues)

        if OUT_NAMES:
            aScanList.extend(range(4800, 4800+NUM_OUT_CHANNELS))  # STREAM_OUT0
            aNames = ["STREAM_SETTLING_US", "STREAM_RESOLUTION_INDEX"]
            aValues = [0, 0]
            ljm.eWriteNames(handle, len(aNames), aNames, aValues)

        return aScanList

    def wait_before_stop(self, total_time, dt=0.2):
        try:
            if total_time is not None:
                t0 = time.time()
                while time.time()-t0 <= total_time:
                    time.sleep(dt)
                self.stop_stream()
            else:
                while True:
                    if query_yes_no('Do you want to stop streaming?',
                                    default='no'):
                        self.stop_stream()
                        break
        except KeyboardInterrupt:
            self.stop_stream()
