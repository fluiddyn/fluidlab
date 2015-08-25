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

    def __init__(self, port, method='rtu', slave_adress=1, timeout=1):
        import minimalmodbus
        self._modbus = minimalmodbus.Instrument(port, slave_adress, method)

    def read_readonlybool(self, adresses):
        raise NotImplementedError

    def read_bool(self, adresses):
        if isinstance(adresses, (list, tuple)):
            return self._modbus.read_coils(adresses)
        elif isinstance(adresses, int):
            return self._modbus.read_coil(adresses)

    def write_bool(self, adresses, values):
        raise NotImplementedError

    def read_readonlyint16(self, adresses):
        raise NotImplementedError

    def read_int16(self, adresses):
        if isinstance(adresses, (list, tuple)) and len(adresses) == 2:
            return self._modbus.read_registers(adresses[0], adresses[1])
        elif isinstance(adresses, int):
            return self._modbus.read_register(adresses)
        else:
            raise ValueError('Argument must be int or int list of length 2')

    def write_int16(self, adress, values):
        if isinstance(values, list):
            self._modbus.write_registers(adress, values)
        elif isinstance(values, int):
            self._modbus.write_register(adress, values)
        else:
            raise ValueError('Argument must be int or list of ints')

    def read_readonlyfloat32(self, adresses):
        raise NotImplementedError

    def read_float32(self, adresses):
        raise NotImplementedError

    def write_float32(self, adresses, values):
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
