"""
Modbus features (:mod:`fluidlab.instruments.modbus.features`)
=============================================================

Provides:

.. autoclass:: Value
   :members:
   :private-members:

.. autoclass:: ReadOnlyBoolValue
   :members:
   :private-members:

.. autoclass:: BoolValue
   :members:
   :private-members:

.. autoclass:: ReadOnlyInt16Value
   :members:
   :private-members:

.. autoclass:: Int16Value
   :members:
   :private-members:

.. autoclass:: ReadOnlyFloat32Value
   :members:
   :private-members:

.. autoclass:: Float32Value
   :members:
   :private-members:


"""

import warnings

from fluidlab.instruments.features import SuperValue


def _custom_formatwarning(message, category, filename, lineno, line=None):
    return '{}:{}: {}: {}\n'.format(
        filename, lineno, category.__name__, message)

warnings.formatwarning = _custom_formatwarning
warnings.simplefilter('always', UserWarning)


class Value(SuperValue):
    def __init__(self, name, doc='', adress=0):
        self._adress = adress
        super(Value, self).__init__(name, doc)


class ReadOnlyBoolValue(Value):
    def get(self):
        return self._interface.read_readonlybool(self._adress)


class BoolValue(Value):
    def get(self):
        return self._interface.read_bool(self._adress)

    def set(self, value):
        self._interface.write_bool(self._adress, value)


class ReadOnlyInt16Value(Value):
    def get(self):
        return self._interface.read_readonlyint16(self._adress)


class Int16Value(Value):
    def get(self):
        return self._interface.read_int16(self._adress)

    def set(self, value, signed=False):
        self._interface.write_int16(self._adress, value, signed)


class DecimalInt16Value(Int16Value):
    def __init__(self, name, doc='', address=0, number_of_decimals=0):
        self._number_of_decimals = number_of_decimals
        super(DecimalInt16Value, self).__init__(name, doc, address)

    def get(self):
        raw_value = super(DecimalInt16Value, self).get()

        if self._number_of_decimals == 0:
            return raw_value
        else:
            return float(raw_value) / 10 ** self._number_of_decimals

    def set(self, value, check=True, signed=False):
        """Set the Value to value.

        If check, checks that the value was properly set.
        """
        if self._number_of_decimals == 0:
            raw_int = int(value)
        else:
            raw_int = int(value * 10 ** self._number_of_decimals)

        super(DecimalInt16Value, self).set(raw_int, signed)

        if check:
            self._check_value(value)

    def _check_value(self, value):
        """After a value is set, checks the instrument value and
        sends a warning if it doesn't match."""
        instr_value = self.get()
        if instr_value != value:
            msg = ('Value {} could not be set to {} and was set '
                   'to {} instead').format(self._name, value, instr_value)
            warnings.warn(msg, UserWarning)


class Int16StringValue(SuperValue):
    def __init__(self, name, doc='', int_dict=None, adress=0):
        self._adress = adress
        self._int_dict = int_dict
        string_dict = {}
        for k in int_dict:
            string_dict[int_dict[k]]=k
        self._string_dict = string_dict
        super(Int16StringValue, self).__init__(name, doc)

    def get(self):
        return self._int_dict[self._interface.read_int16(self._adress)]

    def set(self, string):
        self._interface.write_int16(self._adress, self._string_dict[string])


class ReadOnlyFloat32Value(Value):
    def get(self):
        return self._interface.read_readonlyfloat32(self._adress)


class Float32Value(Value):
    def get(self):
        return self._interface.read_float32(self._adress)

    def set(self, value):
        self._interface.write_float32(self._adress, value)
