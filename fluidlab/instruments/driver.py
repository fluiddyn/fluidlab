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

    @classmethod
    def _complete_cls(cls, workers):
        for worker in workers:
            worker._complete_driver_class(cls)

    def __setattr__(self, k, v):

        if (not isinstance(v, Value) and
                k in self.__class__.__dict__ and
                isinstance(self.__class__.__dict__[k], Value)):
            raise ValueError(
                k + ' is associated with a quantity in the instrument. '
                'Do not set this value by assignment. Use a set function.')

        super(Driver, self).__setattr__(k, v)

    def __init__(self):
        self._interface = self.interface = Interface()

        for v in self.__class__.__dict__.values():
            if isinstance(v, Value):
                v._interface = self._interface

    def set(self, name, *args, **kargs):
        """Set a value"""
        value = self._get_value_from_name(name)
        value.set(*args, **kargs)

    def get(self, name, *args, **kargs):
        """Get a value"""
        value = self._get_value_from_name(name)
        value.get(*args, **kargs)

    def _get_value_from_name(self, name):
        try:
            value = self.__class__.__dict__[name]
        except AttributeError:
            raise AttributeError()
        if not isinstance(value, Value):
            raise ValueError(name + ' is not a value of this instrument')
        return value

if __name__ == '__main__':
    driver = Driver()
