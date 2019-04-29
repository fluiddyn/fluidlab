"""Interfaces with the instruments (:mod:`fluidlab.instruments.interfaces`)
===========================================================================

Provides some classes:

.. autoclass:: Interface
   :members:
   :private-members:

.. autoclass:: QueryInterface
   :members:
   :private-members:

.. autoclass:: FalseInterface
   :members:
   :private-members:


Provides some modules:

.. autosummary::
   :toctree:

   visa
   linuxgpib
   serial_inter
   linuxusbtmc

"""

from time import sleep
import warnings
from enum import IntEnum
import sys
import ipaddress


class PhysicalInterfaceType(IntEnum):
    GPIB = 0
    Ethernet = 1
    Serial = 2
    Modbus = 3


DefaultInterface = {
    PhysicalInterfaceType.GPIB: "VISAInterface",
    PhysicalInterfaceType.Ethernet: "SocketInterface",
    PhysicalInterfaceType.Serial: "SerialInterface",
    PhysicalInterfaceType.Modbus: "MinimalModbusInterface",
}

if sys.platform.startswith("linux"):
    DefaultInterface[PhysicalInterfaceType.GPIB] = "GPIBInterface"


def set_default_interface(interface_type, interface_classname):
    DefaultInterface[interface_type] = interface_classname


def interface_from_string(name, defaultPhysicalInterface=None, **kwargs):
    """
    Infer physicalInterface from name if possible, or use the default provided
    physicalInterface otherwise.
    i.e. if the names contains the physical interface explicitely, then we use it,
    eg.
    GPIB0::1::INSTR is GPIB physical interface
    ASRL0::INSTR is a VISA Serial address
    192.168.0.1 is a IP address, so Ethernet interface
    """
    classname = None
    physicalInterface = None
    if "GPIB" in name:
        physicalInterface = PhysicalInterfaceType.GPIB
    elif "ASRL" in name:
        physicalInterface = PhysicalInterfaceType.Serial
        classname = "VISAInterface"
    elif isinstance(name, ipaddress.IPv4Address) or isinstance(
        name, ipaddress.IPv6Address
    ):
        name = str(name)
        physicalInterface = PhysicalInterfaceType.Ethernet
    else:
        try:
            ip = ipaddress.ip_address(name)
            physicalInterface = (
                PhysicalInterfaceType.Ethernet
                if defaultPhysicalInterface is not PhysicalInterfaceType.Modbus
                else PhysicalInterfaceType.Modbus
            )
        except ValueError:
            pass
    if physicalInterface is None:
        physicalInterface = defaultPhysicalInterface
    if classname is None:
        classname = DefaultInterface[physicalInterface]
    if classname == "VISAInterface":
        from fluidlab.interfaces.visa_inter import VISAInterface

        return VISAInterface(name)
    if classname == "GPIBInterface":
        from fluidlab.interfaces.gpib_inter import GPIBInterface

        if name.endswith("::INSTR"):
            name = name[:-7]
        boardname, devnum = name.split("::")
        if boardname.startswith("GPIB"):
            boardname = boardname[4:]
        board = int(boardname)
        dev = int(devnum)
        return GPIBInterface(board, dev)
    if classname == "SocketInterface":
        from fluidlab.interfaces.socket_inter import SocketInterface

        return SocketInterface(name, **kwargs)
    if classname == "SerialInterface":
        from fluidlab.interfaces.serial_inter import SerialInterface

        return SerialInterface(name, **kwargs)
    if classname == "MinimalModbusInterface":
        from fluidlab.interfaces.modbus_inter import MinimalModbusInterface

        return MinimalModbusInterface(name, **kwargs)
    if classname == "PyModbusInterface":
        from fluidlab.interfaces.modbus_inter import PyModbusInterface

        return PyModbusInterface(name, **kwargs)
    raise ValueError("Unknown interface type")


class InterfaceWarning(Warning):
    pass


class Interface:
    def _open(self):
        # do the actual open (without testing self.opened)
        raise NotImplementedError

    def _close(self):
        # do the actual close (without testing self.opened)
        raise NotImplementedError

    def __init__(self):
        self.opened = False

    def open(self):
        if not self.opened:
            self._open()
            self.opened = True
        else:
            warnings.warn(
                "open() called on already opened interface.", InterfaceWarning
            )

    def close(self):
        if self.opened:
            self._close()
            self.opened = False
        else:
            warnings.warn(
                "close() called on already closed interface.", InterfaceWarning
            )

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type_, value, cb):
        self.close()


class QueryInterface(Interface):
    def _write(self, *args, **kwargs):
        # do the actual write
        raise NotImplementedError

    def _read(self, *args, **kwargs):
        # do the actual read
        raise NotImplementedError

    def write(self, *args, **kwargs):
        if not self.opened:
            warnings.warn(
                "write() called on non-opened interface.", InterfaceWarning
            )
            self.open()
        self._write(*args, **kwargs)

    def read(self, *args, **kwargs):
        if not self.opened:
            warnings.warn(
                "read() called on non-opened interface.", InterfaceWarning
            )
            self.open()
        return self._read(*args, **kwargs)

    def query(self, command, time_delay=0.1, **kwargs):
        if hasattr(self, "_query"):
            if not self.opened:
                warnings.warn(
                    "query() called on non-opened interface.", InterfaceWarning
                )
                self.open()
            return self._query(command, **kwargs)
        else:
            self.write(command)
            sleep(time_delay)
            return self.read(**kwargs)


class FalseInterface(QueryInterface):
    """
    Dummy interface
    """

    def _open(self):
        pass

    def _close(self):
        pass

    def _write(self, s):
        print(s)

    def _read(self):
        print("just return 0 since it is a false Interface class.")
        return 0
