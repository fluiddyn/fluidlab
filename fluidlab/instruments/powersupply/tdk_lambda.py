"""tdk_lambda
=============

.. autoclass:: TdkLambda
   :members:
   :private-members:


"""

__all__ = ['TdkLambda']

from fluidlab.instruments.iec60488 import IEC60488
from fluidlab.instruments.features import FloatValue, BoolValue

class TdkLambda(IEC60488):
    """Driver for the power supply TDK Lambda

    """

features = [
    FloatValue(
        'idc',
        doc='Get actual current/Set current setpoint',
        command_get='MEAS:CURR?',
        command_set=':CURRENT',
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
        command_set='OUTPUT:STATE',
        check_instrument_value=False,
        pause_instrument=0.1)]

TdkLambda._build_class_with_features(features)
    
