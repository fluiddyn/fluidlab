"""Streaming with a T7 board (LabJack)
======================================

"""
from __future__ import print_function

import time

import numpy as np

import sys

from labjack import ljm

from fluiddyn.io.query import query_yes_no


def is_power2(num):
    "states if a number is a power of two"
    return ((num & (num - 1)) == 0) and num != 0


class T7:
    """Streaming with a T7 board (LabJack)

    """

    def __init__(self, identifier="ANY"):
        # Open a T7 board
        self.handle = ljm.openS("ANY", "ANY", identifier)
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
        print("stop_stream")
        handle = self.handle
        ljm.eWriteName(handle, "DAC0", 0)
        ljm.eWriteName(handle, "DAC1", 0)
        ljm.eStreamStop(handle)

    def get_info(self):
        info = ljm.getHandleInfo(self.handle)
        print(
            (
                "Opened a LabJack with Device type: %i, Connection type: %i,\n"
                "Serial number: %i, IP address: %s, "
                "Port: %i,\nMax bytes per MB: %i"
            )
            % (
                info[0],
                info[1],
                info[2],
                ljm.numberToIP(info[3]),
                info[4],
                info[5],
            )
        )

    def split_data_in_buffer(self, data):
        MAX_BUFFER_SIZE = 512
        BYTES_PER_VALUE = 2
        buffer_size = []
        data_splited = []
        for d in data:
            loop_size = d.size
            data_byte_size = loop_size * BYTES_PER_VALUE
            if is_power2(data_byte_size):
                buff_size = data_byte_size
            else:
                buff_size = int(
                    2 ** (int(np.log(data_byte_size) / np.log(2)) + 1)
                )
            if buff_size <= MAX_BUFFER_SIZE:
                buffer_size.append(buff_size)
                data_splited.append([d])
            else:
                NUMBER_SAMPLE = 2 * (data_byte_size // MAX_BUFFER_SIZE + 1)
                data_splited.append(np.split(d, NUMBER_SAMPLE))
                buffer_size.append(MAX_BUFFER_SIZE)
        return buffer_size, data_splited

    def write_out_buffer(self, streamout, volt):
        """ to replace
            for l in volt:
                ljm.eWriteName(handle, "STREAM_OUT0_BUFFER_F32", l)
        """

        handle = self.handle
        maxpoints = 8  # 8 = max number points able to write
        N = volt.size
        nloop = N // maxpoints

        if nloop == 0:
            ljm.eWriteNameArray(
                handle, streamout, volt.size, np.ndarray.tolist(volt)
            )
        else:
            for i in range(nloop):
                ljm.eWriteNameArray(
                    handle,
                    streamout,
                    maxpoints,
                    np.ndarray.tolist(
                        volt[i * maxpoints : i * maxpoints + maxpoints]
                    ),
                )
            if N % maxpoints != 0:
                i += 1
                ljm.eWriteNameArray(
                    handle,
                    streamout,
                    volt[i * maxpoints :].size,
                    np.ndarray.tolist(volt[i * maxpoints :]),
                )

    def prepare_stream_loop(self, IN_NAMES=None, OUT_NAMES=[], volt=[]):
        handle = self.handle

        if IN_NAMES is None:
            IN_NAMES = []

        NUM_IN_CHANNELS = len(IN_NAMES)

        NUM_OUT_CHANNELS = len(OUT_NAMES)
        buffer_size, volt_splitted = self.split_data_in_buffer(volt)
        for indout, out in enumerate(OUT_NAMES):
            outAddress = ljm.nameToAddress(OUT_NAMES[indout])[0]
            ljm.eWriteName(handle, f"STREAM_OUT{indout}_ENABLE", 0)
            ljm.eWriteName(handle, f"STREAM_OUT{indout}_TARGET", outAddress)

            ljm.eWriteName(
                handle, f"STREAM_OUT{indout}_BUFFER_SIZE", buffer_size[indout]
            )

            ljm.eWriteName(handle, f"STREAM_OUT{indout}_ENABLE", 1)

            self.write_out_buffer(
                f"STREAM_OUT{indout}_BUFFER_F32", volt_splitted[indout][0]
            )
            ljm.eWriteName(
                handle,
                f"STREAM_OUT{indout}_LOOP_SIZE",
                volt_splitted[indout][0].size,
            )
            ljm.eWriteName(handle, f"STREAM_OUT{indout}_SET_LOOP", 1)

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
            aScanList.extend(range(4800, 4800 + NUM_OUT_CHANNELS))  # STREAM_OUT0
            aNames = ["STREAM_SETTLING_US", "STREAM_RESOLUTION_INDEX"]
            aValues = [0, 0]
            ljm.eWriteNames(handle, len(aNames), aNames, aValues)

        return aScanList, volt_splitted

    def prepare_stream(self, IN_NAMES=[], OUT_NAMES=[], volt=[]):
        handle = self.handle
        NUM_IN_CHANNELS = len(IN_NAMES)
        NUM_OUT_CHANNELS = len(OUT_NAMES)

        for indout, out in enumerate(OUT_NAMES):
            outAddress = ljm.nameToAddress(OUT_NAMES[indout])[0]
            ljm.eWriteName(handle, f"STREAM_OUT{indout}_ENABLE", 0)
            ljm.eWriteName(handle, f"STREAM_OUT{indout}_TARGET", outAddress)

            buffer_size = volt[indout].size * 2
            if is_power2(buffer_size):
                ljm.eWriteName(
                    handle, f"STREAM_OUT{indout}_BUFFER_SIZE", buffer_size
                )
            else:
                buffer_size = int(2 ** (int(np.log(buffer_size) / np.log(2)) + 1))
                ljm.eWriteName(
                    handle, f"STREAM_OUT{indout}_BUFFER_SIZE", buffer_size
                )

            ljm.eWriteName(handle, f"STREAM_OUT{indout}_ENABLE", 1)

        for indout, out in enumerate(OUT_NAMES):
            ljm.eWriteName(
                handle, f"STREAM_OUT{indout}_LOOP_SIZE", volt[indout].size
            )
            self.write_out_buffer(f"STREAM_OUT{indout}_BUFFER_F32", volt[indout])
            ljm.eWriteName(handle, f"STREAM_OUT{indout}_SET_LOOP", 0)

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
            aScanList.extend(range(4800, 4800 + NUM_OUT_CHANNELS))  # STREAM_OUT0
            aNames = ["STREAM_SETTLING_US", "STREAM_RESOLUTION_INDEX"]
            aValues = [0, 0]
            ljm.eWriteNames(handle, len(aNames), aNames, aValues)

        return aScanList

    def wait_before_stop(self, total_time=None, dt=None):
        try:
            if total_time is not None:
                if dt is not None:
                    nb_ticks = int(round(total_time / dt))
                    i = 1
                sys.stdout.flush()
                t0 = time.time()
                t = 0.0
                while t <= total_time:
                    if dt is not None:
                        print(f"\r{i}/{nb_ticks}; time ~= {t:.3f} s", end="")
                        sys.stdout.flush()
                        i += 1
                    time.sleep(dt)
                    t = time.time() - t0
                self.stop_stream()
            else:
                while True:
                    if query_yes_no(
                        "Do you want to stop streaming?", default="no"
                    ):
                        self.stop_stream()
                        break

        except KeyboardInterrupt:
            self.stop_stream()
