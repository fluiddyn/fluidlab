"""tti_tsx3510p
=================

.. autoclass:: TtiTsx3510p
   :members:
   :private-members:


"""

__all__ = ['TtiTsx3510p']

from fluidlab.instruments.iec60488 import (
    IEC60488, PowerOn, Calibration, Trigger, ObjectIdentification,
    StoredSetting)

from fluidlab.instruments.features import SuperValue


class TtiTsx3510p(IEC60488, PowerOn, Calibration,
                  Trigger, ObjectIdentification, StoredSetting):
    """
    A driver for the function generator Thurlby Thandar Instruments (TTI) TSX3510P.

    """


class TTIFloatValue(SuperValue):
    def __init__(self, name, doc='', unit_str='',
                 command_set=None, command_get=None):
        super(TTIFloatValue, self).__init__(name, doc=doc)
        self.unit_str = unit_str
        self.command_set = command_set
        self.command_get = command_get

    def set(self, value):
        self._interface.write(self.command_set + ' ' + str(value))

    def get(self):
        data = self._interface.query(self.command_get)
        if data.endswith(self.unit_str):
            N = len(data)-1-len(self.unit_str)
            data = data[0:N]
            return float(data)
        else:
            raise ValueError('Bad return value')


class TTIBoolValue(SuperValue):
    def __init__(self, name, doc='', command_set=None):
        super(TTIBoolValue, self).__init__(name, doc=doc)
        self.command_set = command_set

    def set(self, value):
        if value:
            value = 1
        elif not value:
            value = 0
        self._interface.write(self.command_set + ' ' + str(value))

features = [
    TTIFloatValue(
        'vdc',
        doc='set voltage setup value in Volts, reads the voltage output',
        unit_str='V',
        command_set='V',
        command_get='VO?'),
    TTIFloatValue(
        'idc',
        doc='set current setup value in Amps, reads the current output',
        unit_str='A',
        command_set='I',
        command_get='IO?'),
    TTIFloatValue(
        'vmax',
        doc='set over-voltage value in Volts',
        unit_str='V',
        command_set='OVP'),
    TTIFloatValue(
        'wdc',
        doc='reads the power output',
        unit_str='W',
        command_get='POWER?'),
    TTIBoolValue(
        'onoff',
        doc='set on or off the power supply',
        command_set='OP'),
]

TtiTsx3510p._build_class_with_features(features)
