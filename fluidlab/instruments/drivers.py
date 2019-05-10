"""Instrument drivers (:mod:`fluidlab.instruments.drivers`)
==========================================================

Abstract base class for instrument drivers.
Concrete classes must define features, and overload default_physical_interface,
and default_inter_params attributes.

Provides:

.. autoclass:: Driver
   :members:
   :private-members:

"""

from fluidlab.interfaces import interface_from_string, FalseInterface, Interface
from fluidlab.instruments.features import SuperValue


class Driver:
    """Instrument driver (base class).

    Parameters
    ----------

    interface : :class:`fluidlab.interfaces.Interface`
      The interface used to communicate with the instrument.

    """

    default_physical_interface = None
    default_inter_params = {}

    @classmethod
    def _build_class_with_features(cls, features):
        for feature in features:
            feature._build_driver_class(cls)

    def __init__(self, interface=None):
        if isinstance(interface, str):
            interface = interface_from_string(
                interface,
                self.default_physical_interface,
                **self.default_inter_params
            )
        elif not interface:
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


if __name__ == "__main__":
    driver = Driver("ASRL4::INSTR", backend="@sim")
