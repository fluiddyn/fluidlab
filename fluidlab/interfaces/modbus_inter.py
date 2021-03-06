"""
Modbus interfaces (:mod:`fluidlab.interfaces.modbus_inter`)
===========================================================

Provides:

.. autofunction:: get_modbus_interface

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

import sys
import collections

from fluidlab.interfaces import Interface


class ModbusInterface(Interface):
    def __init__(self, port, method="rtu", slave_address=1, timeout=1, **kwargs):
        self.port = port
        self.method = method
        self.slave_address = slave_address
        self.timeout = timeout
        super().__init__()

    def __str__(self):
        return (
            f"{self.__class__.__name__}({self.port:}, {self.method:}, "
            f"{self.slave_address:}, {self.timeout})"
        )

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

    def __repr__(self):
        return str(self)


class MinimalModbusInterface(ModbusInterface):
    def _open(self):
        import minimalmodbus

        self._modbus = minimalmodbus.Instrument(
            self.port, self.slave_address, self.method
        )

    def read_readonlybool(self, addresses):
        raise NotImplementedError

    def read_bool(self, addresses):
        if isinstance(addresses, collections.Iterable):
            return self._modbus.read_coils(addresses)

        elif isinstance(addresses, int):
            return self._modbus.read_coil(addresses)

    def write_bool(self, addresses, values):
        raise NotImplementedError

    def read_readonlyint16(self, addresses):
        raise NotImplementedError

    def read_int16(self, addresses):
        if isinstance(addresses, collections.Iterable) and len(addresses) == 2:
            return self._modbus.read_registers(addresses[0], addresses[1])

        elif isinstance(addresses, int):
            return self._modbus.read_register(addresses)

        else:
            raise ValueError(
                "`addresses` must be an int or an iterable of length 2"
            )

    def write_int16(self, address, values, signed=False):
        if isinstance(values, collections.Iterable):
            self._modbus.write_registers(address, values, signed=signed)
        elif isinstance(values, int):
            self._modbus.write_register(address, values, signed=signed)
        else:
            raise ValueError("`values` must be an int or an iterable of ints")

    def read_readonlyfloat32(self, addresses):
        raise NotImplementedError

    def read_float32(self, addresses):
        raise NotImplementedError

    def write_float32(self, addresses, values):
        raise NotImplementedError


class PyModbusInterface(ModbusInterface):
    def _open(self):
        try:
            if sys.version_info.major == 2:
                from pymodbus.client.sync import ModbusSerialClient
            else:
                from pymodbus3.client.sync import ModbusSerialClient
        except ImportError:
            if sys.version_info.major == 2:
                package_name = "pymodbus"
            else:
                package_name = "pymodbus3"
            raise ImportError(
                f"Can not import {package_name}. "
                + "Is it installed? If not, try to install it."
            )

        self._modbus = ModbusSerialClient(method=self.method, port=self.port)

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


class FalseModbusInterface(ModbusInterface):
    def _open(self):
        pass

    def read_readonlybool(self, addresses):
        return False

    def read_bool(self, addresses):
        return False

    def write_bool(self, addresses, values):
        pass

    def read_readonlyint16(self, addresses):
        return 0

    def read_int16(self, addresses):
        return 0

    def write_int16(self, address, values, signed=False):
        pass

    def read_readonlyfloat32(self, addresses):
        return 0.0

    def read_float32(self, addresses):
        return 0.0

    def write_float32(self, addresses, values):
        pass


classes = {
    "minimalmodbus": MinimalModbusInterface,
    "pymodbus": PyModbusInterface,
    "false": FalseModbusInterface,
}


def get_modbus_interface(
    port,
    timeout=1,
    module="minimalmodbus",
    signed=False,
    method="rtu",
    slave_address=1,
    **kwargs,
):
    f"""Get a Modbus interface

    module can be in {list(classes.keys())}

    """
    cls = classes[module]
    interface = cls(
        port,
        method=method,
        slave_address=slave_address,
        timeout=timeout,
        **kwargs,
    )
    interface.open()
    return interface
