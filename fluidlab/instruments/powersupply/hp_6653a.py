"""HP_6653A
=================

.. autoclass:: HP_6653A
   :members:
   :private-members:


"""

__all__ = ['HP_6653A']

from fluidlab.instruments.iec60488 import (
    IEC60488, PowerOn, Calibration, Trigger, ObjectIdentification,
    StoredSetting)

from fluidlab.instruments.features import SuperValue


class HP_6653A(IEC60488, PowerOn, Calibration,
                  Trigger, ObjectIdentification, StoredSetting):
    """
    A driver for the power supply HP_6653A

    """


class HPFloatValue(SuperValue):
    def __init__(self, name, doc='', unit_str='',
                 command_set=None, command_get=None):
        super(HPFloatValue, self).__init__(name, doc=doc)
        self.unit_str = unit_str
        self.command_set = command_set
        self.command_get = command_get

    def set(self, value):
        self._interface.write(self.command_set + ' ' + str(value))

    def get(self):
        data = self._interface.query(self.command_get)
        return float(data)


class HPBoolValue(SuperValue):
    def __init__(self, name, doc='', command_set=None):
        super(HPBoolValue, self).__init__(name, doc=doc)
        self.command_set = command_set

    def set(self, value):
        if value:
            value = 1
        elif not value:
            value = 0
        self._interface.write(self.command_set + ' ' + str(value))

features = [
    HPFloatValue(
        'vdc',
        doc='set voltage setup value in Volts, reads the programmed voltage command, reads the value from sense terminals',
        unit_str='V',
        command_set='VOLT',
        #command_get='VOLT?'),
		command_get='MEAS:VOLT?'),
    HPFloatValue(
        'idc',
        doc='set current setup value in Amps, reads the programmed current command, reads the value from sense terminals',
        unit_str='A',
        command_set='CURR',
        #command_get='CURR?',
		command_get='MEAS:CURR?'),
		
	HPFloatValue(
        'vmax',
        doc='set over-voltage value in Volts',
        unit_str='V',
        command_set='VOLT:PROT',
		command_get='VOLT:PROT?'),
		
	HPFloatValue(
        'imax',
        doc='set over-current value in Amps',
        unit_str='A',
        command_set='CURR:PROT',
		command_get='CURR:PROT?'),

    HPBoolValue(
        'onoff',
        doc='set on or off the power supply',
        command_set='OUTP'),
]

HP_6653A._build_class_with_features(features)
