"""Agilent 33220a
=================

.. autoclass:: Agilent33220a
   :members:
   :private-members:


"""

__all__ = ['Agilent33220a']

from fluidlab.instruments.iec60488 import (
    IEC60488, PowerOn, Calibration, Trigger, ObjectIdentification,
    StoredSetting)


from fluidlab.instruments.features import (
    SuperValue, QueryCommand)

import re


class Agilent33220a_Vdc(SuperValue):
    def __init__(self):
        super(Agilent33220a_Vdc, self).__init__(
            'vdc', doc='DC voltage')

    def set(self, value):
        self._interface.write('OUTP:LOAD INF')
        self._interface.write('APPLY:DC DEF, DEF, ' + str(value))
        if value != 0.0:
            self._interface.write('OUTP ON')
        else:
            self._interface.write('OUTP OFF')

    def get(self):
        valeurs = self._driver.get_generator_state()
        return valeurs[3]


class Agilent33220a_Vrms(SuperValue):
    def __init__(self):
        super(Agilent33220a_Vrms, self).__init__(
            'vrms', doc='RMS voltage')

    def set(self, value):
        self._interface.write('OUTP:LOAD INF')
        self._interface.write('VOLT:UNIT VRMS')
        if value != 0.0:
            (iFunc, iFreq, iAmpl, iOffset) = self._driver.get_generator_state()
            self._interface.write('APPLY:SIN ' + str(iFreq) + ', ' +
                                  str(value) + ', ' + str(iOffset))
            self._interface.write('OUTP ON')
        else:
            self._interface.write('OUTP OFF')

    def get(self):
        valeurs = self._driver.get_generator_state()
        return valeurs[2]


class Agilent33220a_Frequency(SuperValue):
    def __init__(self):
        super(Agilent33220a_Frequency, self).__init__(
            'frequency', doc='Wave frequency')

    def set(self, value):
        (iFunc, iFreq, iAmpl, iOffset) = self._driver.get_generator_state()
        self._interface.write('APPLY:SIN ' + str(value) + ', ' +
                              str(iAmpl) + ', ' + str(iOffset))

    def get(self):
        valeurs = self._driver.get_generator_state()
        return valeurs[1]


def parse_agilent33220a_configuration_str(str):
    """Parse the Agilent 33220A configuration string.

    Returns 4 elements: function name, frequency, amplitude, offset """
    valeurs = re.split(',', str)
    function_frequency = valeurs[0]
    amplitude = valeurs[1]
    offset = valeurs[2]
    Nchars = len(offset)
    valeurs = re.split(' ', function_frequency)
    function = valeurs[0]
    frequency = valeurs[1]
    return (function[1::], float(frequency),
            float(amplitude), float(offset[0:(Nchars-2)]))


class Agilent33220a(IEC60488, PowerOn, Calibration,
                    Trigger, ObjectIdentification, StoredSetting):
    """
    A driver for the function generator Agilent 33220A


    """


features = [
    QueryCommand(
        'get_generator_state',
        doc='Get the current configuration of the funcgen',
        command_str='APPLy?',
        parse_result=parse_agilent33220a_configuration_str),
    Agilent33220a_Vdc(),
    Agilent33220a_Vrms(),
    Agilent33220a_Frequency()
]

Agilent33220a._build_class_with_features(features)
