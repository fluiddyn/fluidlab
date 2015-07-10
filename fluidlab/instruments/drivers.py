"""Instrument drivers (:mod:`fluidlab.instruments.drivers`)
==========================================================

Provides:

.. autoclass:: Driver
   :members:
   :private-members:

.. autoclass:: VISADriver
   :members:
   :private-members:

"""

import re
import platform

from fluidlab.instruments.interfaces import (
    Interface, FalseInterface)

from fluidlab.instruments.features import Value


class Driver(object):
    """Instrument driver (base class)."""
    @classmethod
    def _build_class_with_features(cls, features):
        for feature in features:
            feature._build_driver_class(cls)

    def __init__(self, interface=None):
        if not interface:
            interface = FalseInterface()
        elif not isinstance(interface, Interface):
            raise ValueError('interface should be an Interface.')

        self._interface = self.interface = interface

        self.values = {}
        for name in dir(self):
            v = getattr(self, name)
            if isinstance(v, Value):
                self.values[name] = v
                v._interface = self._interface

    def __setattr__(self, k, v):
        if (not isinstance(v, Value) and
                k in dir(self) and
                isinstance(getattr(self, k), Value)):
            raise ValueError(
                k + ' is associated with a quantity in the instrument. '
                'Do not set this value by assignment. Use a set function.')

        super(Driver, self).__setattr__(k, v)

    def set(self, name, *args, **kargs):
        """Set a value"""
        value = self._get_value_from_name(name)
        value.set(*args, **kargs)

    def get(self, name, *args, **kargs):
        """Get a value"""
        value = self._get_value_from_name(name)
        return value.get(*args, **kargs)

    def _get_value_from_name(self, name):
        try:
            value = getattr(self, name)
            Error = None
        except AttributeError:
            Error = AttributeError
        else:
            if not isinstance(value, Value):
                Error = ValueError

        if Error:
            raise Error(name + ' is not a value of this instrument')

        return value


class VISADriver(Driver):
    def __init__(self, interface=None, backend='@py'):

        if isinstance(interface, str):
            if interface.startswith('GPIB') and backend == '@py':
                # pyvisa-py does not yet support GPIB so we use
                # ni-visa under Windows and linuxgpib otherwise,

                if platform.system() == 'Windows':
                    backend = '@ni'
                else:
                    from fluidlab.instruments.interfaces.linuxgpib import (
                        GPIBInterface)

                    # we have to parse the resource string (I don't
                    # know how to do that cleanly)
                    resource_bits = re.split(r'(\d+)', interface)
                    tmp = []
                    for resource_bit in resource_bits:
                        try:
                            i = int(resource_bit)
                        except ValueError:
                            pass
                        else:
                            tmp.append(i)

                    if len(tmp) == 0:
                        raise ValueError('Incorrect GPIB resource string.')
                    elif len(tmp) == 1:
                        board_adress = 0
                        instrument_adress = tmp[1]
                    elif len(tmp) == 2:
                        board_adress = tmp[0]
                        instrument_adress = tmp[0]
                    else:
                        raise ValueError(
                            'GPIB resource string not understood.')

                    interface = GPIBInterface(board_adress, instrument_adress)

        if isinstance(interface, str):
            from fluidlab.instruments.interfaces.visa import (
                PyvisaInterface)
            interface = PyvisaInterface(interface, backend=backend)

        super(VISADriver, self).__init__(interface)


if __name__ == '__main__':
    driver = Driver('ASRL4::INSTR', backend='@sim')
