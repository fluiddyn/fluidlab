"""Interfaces with linux-gpib (:mod:`fluidlab.instruments.interfaces.linuxgpib`)
================================================================================

Provides:

.. autoclass:: GPIBInterface
   :members:
   :private-members:

"""

import gpib
import time

from fluidlab.instruments.interfaces import Interface


class GPIBInterface(Interface):
    def __init__(self, board_adress, instrument_adress):
        self.handle = gpib.dev(board_adress, instrument_adress)

    def read(self, numbytes=100):
        return gpib.read(self.handle, numbytes)

    def write(self, command):
        gpib.write(self.handle, command)

    def query(self, command, numbytes=100, time_delay=0.1):
        self.write(command)
        time.sleep(time_delay)
        return self.read(numbytes)
