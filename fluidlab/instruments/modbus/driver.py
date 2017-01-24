"""
Modbus driver (:mod:`fluidlab.instruments.modbus.driver`)
=========================================================

Provides:

.. autoclass:: ModbusDriver
   :members:
   :private-members:

"""

from fluidlab.instruments.drivers import Driver


class ModbusDriver(Driver):
    """Driver for instruments communicating with Modbus."""

    def __init__(self, port, method='rtu', timeout=1,
                 module='minimalmodbus'):

        if module == 'minimalmodbus':
            from fluidlab.instruments.modbus.interfaces import \
                MinimalModbusInterface as Interface

        elif module == 'pymodbus':
            from fluidlab.instruments.modbus.interfaces import \
                PyModbusInterface as Interface

        else:
            raise ValueError
            
        interface = Interface(port, method, timeout)

        super(ModbusDriver, self).__init__(interface)
