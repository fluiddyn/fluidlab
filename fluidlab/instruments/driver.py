"""Driver (:mod:`fluidlab.instruments.driver`)
==============================================

Provides:

.. autoclass:: Driver
   :members:
   :private-members:

"""

from fluidlab.instruments.interface import Interface

from fluidlab.instruments.features import Value


class Driver(object):
    """Instrument driver (base class)."""
    @classmethod
    def _build_class(cls, workers):
        for worker in workers:
            worker._build_driver_class(cls)

    def __init__(self, interface=None):
        if interface is None:
            self._interface = self.interface = Interface()

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
    driver = Driver()
