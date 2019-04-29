"""Interfaces with GPIB (:mod:`fluidlab.interfaces.gpib_inter`)
===============================================================

Provides:

.. autoclass:: GPIBInterface
   :members:
   :private-members:

"""

import gpib
import time, sys

from fluidlab.interfaces import QueryInterface

timeout_values = {
    gpib.T1000s: 1000.0,
    gpib.T100ms: 100e-3,
    gpib.T100s: 100.0,
    gpib.T100us: 100e-6,
    gpib.T10ms: 10e-3,
    gpib.T10s: 10.0,
    gpib.T10us: 10e-6,
    gpib.T1ms: 1e-3,
    gpib.T1s: 1.0,
    gpib.T300ms: 300e-3,
    gpib.T300s: 300.0,
    gpib.T300us: 300e-6,
    gpib.T30ms: 30e-3,
    gpib.T30s: 30.0,
    gpib.T30us: 30e-6,
    gpib.T3ms: 3e-3,
    gpib.T3s: 3.0,
}


def closest_timeout(t):
    out = gpib.T1000s
    for k, v in timeout_values.items():
        if v >= t and v <= timeout_values[out]:
            out = k
    return out


class GPIBInterface(QueryInterface):
    def __init__(self, board_adress, instrument_adress, timeout=1.0):
        super().__init__()
        self.board_adress = board_adress
        self.instrument_adress = instrument_adress
        self.default_tmo = closest_timeout(timeout)

    def __str__(self):
        return f"GPIBInterface({self.board_adress:d}, {self.instrument_adress:d})"

    def __repr__(self):
        return str(self)

    def _open(self):
        self.handle = gpib.dev(self.board_adress, self.instrument_adress)
        gpib.timeout(self.handle, self.default_tmo)

    def _close(self):
        gpib.close(self.handle)

    def _read(self, numbytes=None, verbose=False, tracing=False):
        if tracing:
            sys.stdout.write("* <- " + str(self.instrument_adress) + " ")
            sys.stdout.flush()
        if numbytes is not None:
            try:
                data = gpib.read(self.handle, numbytes)
            except gpib.GpibError as ge:
                raise

        else:
            try:
                data = ""
                while True:
                    chunk_size = 150
                    chunk = gpib.read(self.handle, chunk_size)
                    data = data + chunk.decode("ascii")

                    if verbose:
                        sys.stdout.write(
                            "{:d} bytes read       \r".format(len(data))
                        )
                    if len(chunk) < chunk_size:
                        break

            except gpib.GpibError as ge:
                pass
        if verbose:
            sys.stdout.write("\n")
        if tracing:
            sys.stdout.write(data.strip())
            sys.stdout.write("\n")

        return data

    def _write(self, command, tracing=False):
        if tracing:
            print("* ->", self.instrument_adress, command)
        if isinstance(command, str):
            command = command.encode("ascii")
        gpib.write(self.handle, command)

    def wait_for_srq(self, timeout=None):
        """
        timeout is expressed in milliseconds for compatibility
        with pyvisa
        """
        timeout = float(timeout * 1e-3)
        # now timeout is in seconds
        try:
            if timeout is not None:
                tmo = closest_timeout(timeout)
                # print('setting timeout to', timeout_values[tmo])
                gpib.timeout(self.handle, tmo)
            tstart = time.monotonic()
            while True:
                sta = gpib.wait(self.board_adress, gpib.TIMO | gpib.SRQI)
                if (sta & gpib.TIMO) != 0:
                    # Timed out
                    if time.monotonic() - start > timeout:
                        print("Timeout occured")
                        break
                else:
                    # SRQ asserted
                    print("SRQ was asserted")
                    break
        finally:
            gpib.timeout(self.handle, self.default_tmo)
