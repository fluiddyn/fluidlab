"""lauda
========

.. autoclass:: Lauda
   :members:
   :private-members:


"""

from __future__ import print_function

__all__ = ["Lauda"]

from fluidlab.instruments.drivers import Driver
from fluidlab.instruments.interfaces.serial_inter import SerialInterface
from fluidlab.instruments.features import Value
from time import sleep

class LaudaException(Exception):
    pass

class LaudaValue(Value):
    def __init__(self, name, doc='', command_set=None, command_get=None, check_instrument_value=False, pause_instrument=0.5, channel_argument=False):
        super(LaudaValue, self).__init__(name, doc, command_set, command_get, check_instrument_value, pause_instrument, channel_argument)

    def get(self):
        result = super(LaudaValue, self).get()
        if len(result) < 3:
            print(result)
            raise LaudaException("Erreur de communication")
        elif result.startswith('ERR'):
            raise LaudaException("Erreur Lauda: " + result)
        else:
            return float(result)

    def set(self, value):
        command = self.command_set.format(value)
        self._interface.write(command)
        sleep(self.pause_instrument)
        confirmation = self._interface.read()
        if confirmation != 'OK':
            print(confirmation)
            raise LaudaException("Erreur de communication")

class LaudaOnOffValue(LaudaValue):
    Supported_ROM = [1200]
    
    def __init__(self):
        super(LaudaOnOffValue, self).__init__(name='onoff', command_get='IN_MODE_02\r')

    def get(self):
        if self._driver.rom in LaudaOnOffValue.Supported_ROM:
            resultat = super(LaudaOnOffValue, self).get()
            return True if (resultat=='1') else False
        else:
            return True

    def set(self, value):
        if value:
            self._interface.write('START\r')
            sleep(self.pause_instrument)

class LaudaStatValue(Value):
    def __init__(self, name, doc='', command_set=None, command_get=None, check_instrument_value=False, pause_instrument=0.5, channel_argument=False):
        super(LaudaStatValue, self).__init__(name, doc, command_set, command_get, check_instrument_value, pause_instrument, channel_argument)

    def get(self):
        result = super(LaudaStatValue, self).get()
        if len(result) < 3:
            raise LaudaException("Erreur de communication")
        elif result.startswith("ERR"):
            raise LaudaException("Erreur Lauda: " + result)
        else:
            print(result)
            return {'overheat': True if (result[0] == '1') else False,
                    'lowlevel': True if (result[1] == '1') else False,
                    'pumperr': True if (result[2] == '1') else False,
                    'controllererror1': True if (result[3] == '1') else False,
                    'controllererror2': True if (result[4] == '1') else False}

class Lauda(Driver):
    # Below is the list of models which has been tested
    # Your model has to be in the list, otherwise a NotImplemented
    # will be raised. This is to avoid to inadvertantly use
    # untested model without knowning.
    Models = {'RP  845': 845,
              'RP  855': 855,
              'E200': 200,
              'VC': 1200}

    def __init__(self, serialPort):
        interface = SerialInterface(serialPort, baudrate=9600, bytesize=8,
                                    parity='N', stopbits=1, timeout=1, xonxoff=False,
                                    rtscts=False, dsrdtr=False)
        super(Lauda, self).__init__(interface)

        identification = self.interface.query('TYPE\r')
        if identification not in Lauda.Models:
            if isinstance(identification, str) and len(identification) > 0:
                raise LaudaException("Unsupported model: " + identification) 
            else:
                raise LaudaException("Cannot communicate with Lauda on " + str(serialPort))
        else:
            self.rom = Lauda.Models[identification]
            print('Identification: ' + identification)

features = [
    LaudaValue(
        'setpoint',
        command_get='IN_SP_00\r',
        command_set='OUT_SP_00 {:.2f}\r'),
    LaudaStatValue(
        'stat',
        command_get='STAT\r'),
    LaudaValue(
        'temperature',
        command_get='IN_PV_00\r'),
    LaudaValue(
        'waterlevel',
        command_get='IN_PV_05\r'),
    LaudaOnOffValue()]

Lauda._build_class_with_features(features)
    
if __name__ == '__main__':
    lauda = Lauda('/dev/ttyS0')
    lauda.setpoint.set(15.0)
    try:
        while True:
            print(lauda.temperature.get())
            sleep(1.0)
    except KeyboardInterrupt:
        pass
