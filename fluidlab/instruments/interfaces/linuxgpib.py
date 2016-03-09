"""Interfaces with linux-gpib (:mod:`fluidlab.instruments.interfaces.linuxgpib`)
================================================================================

Provides:

.. autoclass:: GPIBInterface
   :members:
   :private-members:

"""

import gpib
import time, sys

verbose = False

from fluidlab.instruments.interfaces import QueryInterface


class GPIBInterface(QueryInterface):
    def __init__(self, board_adress, instrument_adress):
        self.board_adress = board_adress
        self.instrument_adress = instrument_adress
        self.handle = gpib.dev(board_adress, instrument_adress)

    def read(self, numbytes=100):
        if verbose:
            sys.stdout.write('* <- ' + str(self.instrument_adress) + ' ')
            sys.stdout.flush()
        try:
            data = gpib.read(self.handle, numbytes)
        except gpib.GpibError as ge:
            if verbose:
                sys.stdout.write("FAILED\n")
            raise
        if verbose:
            sys.stdout.write(data.strip())
            sys.stdout.write("\n")
            
        return data

    def write(self, command):
        if verbose:
            print '* ->', self.instrument_adress, command
        gpib.write(self.handle, command)

    def query(self, command, numbytes=100, time_delay=0.1):
        self.write(command)
        time.sleep(time_delay)
        return self.read(numbytes)

    def wait_for_srq(self, timeout=gpib.T10s):
        gpib.WaitSRQ(self.board_adress)
