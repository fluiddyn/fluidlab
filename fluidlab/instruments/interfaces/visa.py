"""Interfaces with pyvisa (:mod:`fluidlab.instruments.interfaces.visa`)
=======================================================================

Provides:

.. autoclass:: PyvisaInterface
   :members:
   :private-members:

"""

import pyvisa as visa

from fluidlab.instruments.interfaces import QueryInterface

opened_devices_for_rm = dict() # key: rm, object: device
resource_managers = dict()     # key: backend(str), object: rm 

class PyvisaInterface(QueryInterface):
    def __init__(self, resource_name, backend="@py"):
        super(PyvisaInterface, self).__init__()
        self.resource_name = resource_name
        self.backend = backend
        
    def _open(self):
        if self.backend in resource_managers:
            rm = resource_managers[self.backend]
            opened_devices_for_rm[rm].add(self)
        else:
            rm = visa.ResourceManager(backend)
            resource_managers[self.backend] = rm
            opened_devices_for_rm[rm] = {self}
        self.rm = rm
        instr = rm.get_instrument(self.resource_name)
        self._lowlevel = instr
        self.pyvisa_instr = instr
        self.assert_trigger = instr.assert_trigger
        try:
            self.wait_for_srq = instr.wait_for_srq
        except AttributeError as e:
            # with @py ?
            print(e)
    
    def _close(self):
        self.pyvisa_instr.close()
        opened_devices_for_rm[self.rm].remove(self)
        if len(opened_devices_for_rm[self.rm]) == 0:
            del opened_devices_for_rm[self.rm]
            self.rm.close()
            del resource_managers[self.backend]

    # methods below are rewritten to accept optional arguments
    # for compatibility with linuxgpib interface

    def _write(
        self,
        message,
        termination=None,
        encoding=None,
        verbose=False,
        tracing=False,
    ):
        # input('Sending '+message+'?')
        return self.pyvisa_instr.write(message, termination, encoding)

    def _read(self, termination=None, encoding=None, verbose=False, tracing=False):
        return self.pyvisa_instr.read(termination, encoding)

    def _query(self, message, time_delay=None, verbose=False, tracing=False):
        return self.pyvisa_instr.query(message, time_delay)


if __name__ == "__main__":
    with PyvisaInterface("ASRL2::INSTR", backend="@sim") as interface:
        pass
