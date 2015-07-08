"""Driver (:mod:`fluidlab.instruments.driver`)
==============================================

Provides:

.. autoclass:: Driver
   :members:
   :private-members:

"""

from fluidlab.instruments.interfaces import (
    Interface, FalseInterface)

from fluidlab.instruments.features import Value


class Driver(object):
    """Instrument driver (base class)."""
    @classmethod
    def _build_class_with_features(cls, features):
        for feature in features:
            feature._build_driver_class(cls)

    def __init__(self, interface=None, backend='@py'):
        if interface is None:
            interface = FalseInterface()
        elif isinstance(interface, str):
            from fluidlab.instruments.interfaces.with_visa import (
                PyvisaInterface)
            interface = PyvisaInterface(interface, backend=backend)
        elif not isinstance(interface, Interface):
            raise NotImplementedError('interface:', interface)

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

if __name__ == '__main__':
    driver = Driver('ASRL4::INSTR', backend='@sim')
