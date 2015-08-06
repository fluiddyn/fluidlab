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

from fluidlab.instruments.features import SuperValue


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

    def set(self, value):
        self._interface.write_int16(self._adress, value)


class Int16StringValue(SuperValue):
    def __init__(self, name, doc='', interger_list=None, string_list=None, adress=0):
        self._adress = adress
        self.interger_list = interger_list
        self.string_list = string_list
        super(Value, self).__init__(name, doc)
    
    def get(self):
        integer = self._interface.read_int16(self._adress)
        for j in range(len(self.interger_list)):
            if self.interger_list[j] == integer:
                string = self.string_list[j]
        return string
    
    def set(self, string):
        for j in range(len(self.string_list)):
            if self.string_list[j] == string:
                integer = self.integer_list[j]
        self._interface.write_int16(self._adress, integer)


class ReadOnlyFloat32Value(Value):
    def get(self):
        return self._interface.read_readonlyfloat32(self._adress)


class Float32Value(Value):
    def get(self):
        return self._interface.read_float32(self._adress)

    def set(self, value):
        self._interface.write_float32(self._adress, value)
