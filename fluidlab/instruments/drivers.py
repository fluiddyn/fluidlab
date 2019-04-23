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

from fluidlab.interfaces import Interface, FalseInterface

from fluidlab.instruments.features import SuperValue


class Driver:
    """Instrument driver (base class).

    Parameters
    ----------

    interface : :class:`fluidlab.interfaces.Interface`
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
            raise ValueError("interface should be an Interface.")

        self._interface = self.interface = interface

        self.values = {}
        for name in dir(self):
            v = getattr(self, name)
            if isinstance(v, SuperValue):
                self.values[name] = v
                v._interface = self._interface
                v._driver = self

    def __setattr__(self, k, v):
        if (
            not isinstance(v, SuperValue)
            and k in dir(self)
            and isinstance(getattr(self, k), SuperValue)
        ):
            raise ValueError(
                k + " is associated with a quantity in the instrument. "
                "Do not set this value by assignment. Use a set function."
            )

        super().__setattr__(k, v)

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
            raise error_class(name + " is not a value of this instrument")

        return value

    def __enter__(self):
        self.interface.__enter__()
        return self

    def __exit__(self, type_, value, cb):
        self.interface.__exit__(type_, value, cb)


class VISADriver(Driver):
    """A VISA driver.

    Parameters
    ----------

    interface : {str or interface}
      A VISA interface or a string defining a VISA interface.

    backend : str
      Defines the backend used by pyvisa ("@py", "@ni", "@sim"...)

      
    Note: this class is actually more general than just VISA, because
    IEC60488 inherits from it, and there are SCPI conforming devices which
    uses serial or socket communications, and can be used with other interfaces.
    
    """

    def __init__(self, interface=None, backend="@ni"):

        if isinstance(interface, str):
            if hasattr(self, 'default_port'):
                from fluidlab.interfaces.socket_inter import SocketInterface
                interface = SocketInterface(interface, self.default_port)
            else:
                from fluidlab.interfaces.visa_inter import PyvisaInterface
                interface = PyvisaInterface(interface, backend=backend)

        super().__init__(interface)

class ModbusDriver(Driver):
    """Driver for instruments communicating with Modbus."""

    def __init__(self, port, method="rtu", timeout=1, module="minimalmodbus"):

        if module == "minimalmodbus":
            from fluidlab.interfaces.modbus_inter import (
                MinimalModbusInterface as Interface,
            )

        elif module == "pymodbus":
            from fluidlab.interfaces.modbus_inter import (
                PyModbusInterface as Interface,
            )

        else:
            raise ValueError

        interface = Interface(port, method, timeout)

        super().__init__(interface)

if __name__ == "__main__":
    driver = Driver("ASRL4::INSTR", backend="@sim")
