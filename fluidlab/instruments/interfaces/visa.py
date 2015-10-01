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
    def __init__(self, resource_name, backend='@py'):
        rm = visa.ResourceManager(backend)
        instr = rm.get_instrument(resource_name)
        self._lowlevel = instr
        self.pyvisa_instr = instr
        self.write = instr.write
        self.read = instr.read
        self.read_raw = instr.read_raw
        self.query = instr.query
        self.close = instr.close
        self.assert_trigger = instr.assert_trigger
        try:
            self.wait_for_srq = instr.wait_for_srq
        except AttributeError as e:
            # with @py ?
            print(e)

if __name__ == '__main__':
    interface = PyvisaInterface('ASRL2::INSTR', backend='@sim')
