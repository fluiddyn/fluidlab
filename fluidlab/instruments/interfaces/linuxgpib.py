"""Interfaces with linux-gpib (:mod:`fluidlab.instruments.interfaces.linuxgpib`)
================================================================================

Provides:

.. autoclass:: GPIBInterface
   :members:
   :private-members:

"""

from __future__ import print_function
import gpib
import time, sys
import six

verbose = False

from fluidlab.instruments.interfaces import QueryInterface


class GPIBInterface(QueryInterface):
    def __init__(self, board_adress, instrument_adress):
        self.board_adress = board_adress
        self.instrument_adress = instrument_adress
        self.handle = gpib.dev(board_adress, instrument_adress)

    def read(self, numbytes=None):
        if verbose:
            sys.stdout.write('* <- ' + str(self.instrument_adress) + ' ')
            sys.stdout.flush()
        if numbytes is not None:
            try:
                data = gpib.read(self.handle, numbytes)
            except gpib.GpibError as ge:
                if verbose:
                    sys.stdout.write("FAILED\n")
                raise
        else:
            try:
                done = False
                data = ''
                while not done:
                    chunk_size = 100
                    chunk = gpib.read(self.handle, chunk_size)
                    if len(chunk) < chunk_size:
                        done = True
                    if six.PY3:
                        data = data + chunk.decode('ascii')
                    else:
                        data = data + chunk
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
            print('* ->', self.instrument_adress, command)
        if six.PY3 and isinstance(command, str):
            command = command.encode('ascii')
        gpib.write(self.handle, command)

    def query(self, command, numbytes=None, time_delay=0.1):
        if six.PY3 and isinstance(command, str):
            command = command.encode('ascii')
        self.write(command)
        time.sleep(time_delay)
        return self.read(numbytes)

    def wait_for_srq(self, timeout=gpib.T10s):
        gpib.WaitSRQ(self.board_adress)
