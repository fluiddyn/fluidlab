"""
Modbus interfaces (:mod:`fluidlab.instruments.modbus.interfaces`)
=================================================================

Provides:

.. autoclass:: ModbusInterface
   :members:
   :private-members:

.. autoclass:: MinimalModbusInterface
   :members:
   :private-members:

.. autoclass:: PyModbusInterface
   :members:
   :private-members:

"""

from fluidlab.instruments.interfaces import Interface


class ModbusInterface(Interface):

    def read_readonlybool(self, addresses):
        raise NotImplementedError

    def read_bool(self, addresses):
        raise NotImplementedError

    def write_bool(self, addresses, values):
        raise NotImplementedError

    def read_readonlyint16(self, addresses):
        raise NotImplementedError

    def read_int16(self, addresses):
        raise NotImplementedError

    def write_int16(self, addresses, values):
        raise NotImplementedError

    def read_readonlyfloat32(self, addresses):
        raise NotImplementedError

    def read_float32(self, addresses):
        raise NotImplementedError

    def write_float32(self, addresses, values):
        raise NotImplementedError


class MinimalModbusInterface(ModbusInterface):

    def __init__(self, port, method='rtu', timeout=1):
        import minimalmodbus
        self._modbus = minimalmodbus.Instrument(port)

    def read_readonlybool(self, addresses):
        raise NotImplementedError

    def read_bool(self, addresses):
        if isinstance(addresses, (list, tuple)):
            return self._modbus.read_coils(addresses)
        elif isinstance(addresses, int):
            return self._modbus.read_coil(addresses)

    def write_bool(self, addresses, values):
        raise NotImplementedError

    def read_readonlyint16(self, addresses):
        raise NotImplementedError

    def read_int16(self, addresses):
        raise NotImplementedError

    def write_int16(self, addresses, values):
        raise NotImplementedError

    def read_readonlyfloat32(self, addresses):
        raise NotImplementedError

    def read_float32(self, addresses):
        raise NotImplementedError

    def write_float32(self, addresses, values):
        raise NotImplementedError


class PyModbusInterface(ModbusInterface):

    def __init__(self, port, method='rtu', timeout=1):
        try:
            from pymodbus.client.sync import ModbusSerialClient
        except ImportError:
            raise ImportError(
                'Can not import pymodbus. '
                'Is it installed? If not, try to install it.')

        self._modbus = ModbusSerialClient(method=method, port=port)

    def read_readonlybool(self, addresses):
        raise NotImplementedError

    def read_bool(self, addresses):
        raise NotImplementedError

    def write_bool(self, addresses, values):
        raise NotImplementedError

    def read_readonlyint16(self, addresses):
        raise NotImplementedError

    def read_int16(self, addresses):
        raise NotImplementedError

    def write_int16(self, addresses, values):
        raise NotImplementedError

    def read_readonlyfloat32(self, addresses):
        raise NotImplementedError

    def read_float32(self, addresses):
        raise NotImplementedError

    def write_float32(self, addresses, values):
        raise NotImplementedError
