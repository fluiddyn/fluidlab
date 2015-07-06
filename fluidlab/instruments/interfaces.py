"""Interfaces with the instruments (:mod:`fluidlab.instruments.interfaces`)
===========================================================================

Provides:

.. autoclass:: Interface
   :members:
   :private-members:

.. autoclass:: FalseInterface
   :members:
   :private-members:

.. autoclass:: PyvisaInterface
   :members:
   :private-members:

"""

import visa


class Interface(object):
    pass


class FalseInterface(Interface):
    def write(self, s):
        print(s)

    def read(self):
        print('read 0 since it is a false Interface class.')
        return 0

    def query(self, s):
        self.write(s)
        return self.read()


class PyvisaInterface(Interface):
    def __init__(self, resource_name, backend='@py'):
        rm = visa.ResourceManager(backend)
        instr = rm.get_instrument(resource_name)
        self.pyvisa_instr = instr
        self.write = instr.write
        self.read = instr.read
        self.query = instr.query
