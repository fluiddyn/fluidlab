"""Interfaces with linux-gpib (:mod:`fluidlab.instruments.interfaces.linuxgpib`)
================================================================================

Provides:

.. autoclass:: GPIBInterface
   :members:
   :private-members:

"""

import gpib
import time

verbose = False

from fluidlab.instruments.interfaces import QueryInterface


class GPIBInterface(QueryInterface):
    def __init__(self, board_adress, instrument_adress):
        self.board_adress = board_adress
        self.handle = gpib.dev(board_adress, instrument_adress)

    def read(self, numbytes=100):
        data = gpib.read(self.handle, numbytes)
        if verbose:
            print '<-', data
        return data

    def write(self, command):
        if verbose:
            print '->', command
        gpib.write(self.handle, command)

    def query(self, command, numbytes=100, time_delay=0.1):
        self.write(command)
        time.sleep(time_delay)
        return self.read(numbytes)

    def wait_for_srq(self, timeout=gpib.T10s):
        gpib.WaitSRQ(self.board_adress)
