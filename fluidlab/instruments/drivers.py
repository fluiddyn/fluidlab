"""Instrument drivers (:mod:`fluidlab.instruments.drivers`)
==========================================================

.. todo:: Verify potential bug due to the fact that values are class
   attributes.

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
import six

from fluidlab.instruments.interfaces import (
    Interface, FalseInterface)

from fluidlab.instruments.features import SuperValue


class Driver(object):
    """Instrument driver (base class).

    Parameters
    ----------

    interface : :class:`fluidlab.instruments.interface.Interface`
      The interface used to communicate with the instrument.

    """
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
            if isinstance(v, SuperValue):
                self.values[name] = v
                v._interface = self._interface
                v._driver = self

    def __setattr__(self, k, v):
        if (not isinstance(v, SuperValue) and
                k in dir(self) and
                isinstance(getattr(self, k), SuperValue)):
            raise ValueError(
                k + ' is associated with a quantity in the instrument. '
                'Do not set this value by assignment. Use a set function.')

        super(Driver, self).__setattr__(k, v)

    def set(self, name, *args, **kargs):
        """Set a value."""
        value = self._get_value_from_name(name)
        value.set(*args, **kargs)

    def get(self, name, *args, **kargs):
        """Get a value."""
        value = self._get_value_from_name(name)
        return value.get(*args, **kargs)

    def _get_value_from_name(self, name):
        try:
            value = getattr(self, name)
            error_class = None
        except AttributeError:
            error_class = AttributeError
        else:
            if not isinstance(value, SuperValue):
                error_class = ValueError

        if error_class:
            raise error_class(name + ' is not a value of this instrument')

        return value


class VISADriver(Driver):
    """A VISA driver.

    Parameters
    ----------

    interface : {str or interface}
      A VISA interface or a string defining a VISA interface.

    backend : str
      Defines the backend used by pyvisa ("@py", "@ni", "@sim"...)

    """
    def __init__(self, interface=None, backend='@py'):

        if isinstance(interface, six.string_types):
            from fluidlab.instruments.interfaces.visa import PyvisaInterface
            interface = PyvisaInterface(interface, backend=backend)

        super(VISADriver, self).__init__(interface)


if __name__ == '__main__':
    driver = Driver('ASRL4::INSTR', backend='@sim')
