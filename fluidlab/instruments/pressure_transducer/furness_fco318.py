"""furness_fco318
=================

.. autoclass:: FurnessFCO318
   :members:
   :private-members:


"""

__all__ = ["FurnessFCO318"]

from fluidlab.instruments.drivers import Driver
from fluidlab.instruments.interfaces.serial_inter import SerialInterface
from fluidlab.instruments.features import Value
from time import sleep
import numpy as np

class FurnessException(Exception):
    pass

class FurnessValue(Value):
    def __init__(self, name, doc='', command_character='L'):
        super(FurnessValue, self).__init__(name, doc, command_set=None, 
                                           command_get='!' + command_character + '\r',
                                           check_instrument_value=False,
                                           pause_instrument=0.5,
                                           channel_argument=False)
  
    def get(self):
        result = super(FurnessValue, self).get()
        if result[:2] != self.command_get[:2]:
            raise FurnessException('Echo missing (got "' + result[:2] + '"')
        value = result[3:]
        print('value: "' + value + '"')
        if value in ['-.---', '--.---']: # below minimum
            value = 0.0
        elif value in ['+.+++', '++.+++']: # above maximum
            value = np.nan
        elif ',' in value:
            values = value.split(',')
            print(values)
            value = {'T_BITS': int(values[0]),
                     'RAW_ADC': int(values[1]),
                     'COMP_ADC': int(values[2]),
                     'LIN_ADC': int(values[3]),
                     'OP_VAL': int(values[4])}
        elif value.endswith('MM'):
            values = value.split(' ')
            value = float(values[0])
        else:
            value = float(value)

        return value

    def set(self):
        pass

class FurnessFCO318(Driver):
    def __init__(self, serialPort):
        interface = SerialInterface(serialPort, baudrate=2400, bytesize=8,
                                    parity='N', stopbits=1, timeout=1, xonxoff=False,
                                    rtscts=False, dsrdtr=False)
        super(FurnessFCO318, self).__init__(interface)

features = [
        FurnessValue('pressure',
            doc='Returns the displayed data',
            command_character='L'),
        FurnessValue('firmware',
            doc='Returns the current firmware version',
            command_character='I'),
        FurnessValue('internal',
            doc='Returns internal readings for advanced use',
            command_character='M')]

FurnessFCO318._build_class_with_features(features)

if __name__ == '__main__':
    fco = Furness_FCO318('/dev/ttyS0')
    firmware = fco.firmware.get()
    print('Firmware: ' + firmware)
    pressure = fco.pressure.get()
    print('Displayed pressure: ' + str(pressure))
    internal = fco.internal.get()
    print('Internal values: ' + str(internal))
    
