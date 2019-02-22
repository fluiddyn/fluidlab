"""Interfaces with pyvisa (:mod:`fluidlab.instruments.interfaces.visa`)
=======================================================================

Provides:

.. autoclass:: PyvisaInterface
   :members:
   :private-members:

"""

import pyvisa as visa

from fluidlab.instruments.interfaces import QueryInterface


class PyvisaInterface(QueryInterface):
    def __init__(self, resource_name, backend="@py"):
        self.rm = visa.ResourceManager(backend)
        instr = self.rm.get_instrument(resource_name)
        self._lowlevel = instr
        self.pyvisa_instr = instr
        # self.write = instr.write
        # self.read = instr.read
        self.read_raw = instr.read_raw
        # self.query = instr.query
        self.close = instr.close
        self.assert_trigger = instr.assert_trigger
        try:
            self.wait_for_srq = instr.wait_for_srq
        except AttributeError as e:
            # with @py ?
            print(e)

    # methods below are rewritten to accept optional arguments
    # for compatibility with linuxgpib interface

    def write(
        self,
        message,
        termination=None,
        encoding=None,
        verbose=False,
        tracing=False,
    ):
        # input('Sending '+message+'?')
        return self.pyvisa_instr.write(message, termination, encoding)

    def read(self, termination=None, encoding=None, verbose=False, tracing=False):
        return self.pyvisa_instr.read(termination, encoding)

    def query(self, message, time_delay=None, verbose=False, tracing=False):
        return self.pyvisa_instr.query(message, time_delay)


if __name__ == "__main__":
    interface = PyvisaInterface("ASRL2::INSTR", backend="@sim")
