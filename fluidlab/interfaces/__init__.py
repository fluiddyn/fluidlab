"""Interfaces with the instruments (:mod:`fluidlab.instruments.interfaces`)
===========================================================================

Provides some classes:

.. autoclass:: Interface
   :members:
   :private-members:

.. autoclass:: QueryInterface
   :members:
   :private-members:

.. autoclass:: FalseInterface
   :members:
   :private-members:


Provides some modules:

.. autosummary::
   :toctree:

   visa
   linuxgpib
   serial_inter
   linuxusbtmc

"""

from time import sleep
import warnings

class InterfaceWarning(Warning):
    pass

class Interface:
    def _open(self):
        # do the actual open (without testing self.opened)
        raise NotImplementedError
    
    def _close(self):
        # do the actual close (without testing self.opened)
        raise NotImplementedError
    
    def __init__(self):
        self.opened = False
        
    def open(self):
        if not self.opened:
            self._open()
            self.opened = True
        else:
            warnings.warn('open() called on already opened interface.', InterfaceWarning)
            
    def close(self):
        if self.opened:
            self._close()
            self.opened = False
        else:
            warnings.warn('close() called on already closed interface.', InterfaceWarning)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type_, value, cb):
        self.close()
        
class QueryInterface(Interface):

    def _write(self, *args, **kwargs):
        # do the actual write
        raise NotImplementedError

    def _read(self, *args, **kwargs):
        # do the actual read
        raise NotImplementedError
        
    def write(self, *args, **kwargs):
        if not self.opened:
            warnings.warn('write() called on non-opened interface.', InterfaceWarning)
            self.open()
        self._write(*args, **kwargs)

    def read(self, *args, **kwargs):
        if not self.opened:
            warnings.warn('read() called on non-opened interface.', InterfaceWarning)
            self.open()
        return self._read(*args, **kwargs)

    def query(self, command, time_delay=0.1, **kwargs):
        if hasattr(self, '_query'):
            if not self.opened:
                warnings.warn('query() called on non-opened interface.', InterfaceWarning)
                self.open()
            return self._query(command, **kwargs)
        else:
            self.write(command)
            sleep(time_delay)
            return self.read(**kwargs)

class FalseInterface(QueryInterface):
    """
    Dummy interface
    """
    
    def _open(self):
        pass
        
    def _close(self):
        pass
        
    def _write(self, s):
        print(s)

    def _read(self):
        print("just return 0 since it is a false Interface class.")
        return 0