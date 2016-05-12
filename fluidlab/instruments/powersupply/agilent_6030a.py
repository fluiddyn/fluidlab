"""agilent_6030a
=============

.. autoclass:: Agilent6030a
   :members:
   :private-members:


"""

__all__ = ['Agilent6030a']

from fluidlab.instruments.iec60488 import IEC60488
from fluidlab.instruments.features import FloatValue, BoolValue

class Agilent6030a(IEC60488):
    """Driver for the power supply Agilent 6030a

    """

features = [
    FloatValue(
        'idc',
        doc='Get actual current/Set current setpoint',
        command_get='MEAS:CURR?',
        command_set='SOUR:CURR',
        check_instrument_value=False,
        pause_instrument=0.1),
    FloatValue(
        'vdc',
        doc='Get actual voltage/Set voltage setpoint',
        command_get='MEAS:VOLT?',
        command_set='SOUR:VOLT',
        check_instrument_value=False,
        pause_instrument=0.1),
    BoolValue(
        'onoff',
        doc='Toggle output ON/OFF',
        command_set='OUTP:STAT',
        check_instrument_value=False,
        pause_instrument=0.1)]

Agilent6030a._build_class_with_features(features)
    
