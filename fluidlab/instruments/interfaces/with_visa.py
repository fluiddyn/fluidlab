"""Interfaces with pyvisa (:mod:`fluidlab.instruments.interfaces.with_visa`)
============================================================================

Provides:

.. autoclass:: PyvisaInterface
   :members:
   :private-members:

"""

import visa

from fluidlab.instruments.interfaces import Interface


class PyvisaInterface(Interface):
    def __init__(self, resource_name, backend='@py'):
        rm = visa.ResourceManager(backend)
        instr = rm.get_instrument(resource_name)
        self.pyvisa_instr = instr
        self.write = instr.write
        self.read = instr.read
        self.query = instr.query
