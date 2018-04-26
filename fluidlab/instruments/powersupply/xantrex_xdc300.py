"""xantrex_xdc300
=================

.. autoclass:: XantrexXDC300
   :members:
   :private-members:

"""

__all__ = ['XantrexXDC300']

from fluidlab.instruments.iec60488 import IEC60488
from fluidlab.instruments.features import FloatValue, BoolValue

class XantrexXDC300(IEC60488):
    """ Driver for the power supply Xantrex XDC300
    """
    
features = [
    FloatValue(
        'idc',
        doc='Get actual current/Set current setpoint',
        command_get="MEAS:CURR?",
        command_set=("SYST:REM:SOUR GPIB\n"
                     "SYST:REM:STAT REM\n"
                     "SOUR:CURR "),
        check_instrument_value=False,
        ),
    FloatValue(
        'vdc',
        doc='Get actual voltage/Set voltage setpoint',
        command_get="MEAS:VOLT?",
        command_set=("SYST:REM:SOUR GPIB\n"
                     "SYST:REM:STAT REM\n"
                     "SOUR:VOLT "),
        check_instrument_value=False,
        ),
    FloatValue(
        'wdc',
        doc='Get actual power/Set power setpoint',
        command_get="MEAS:POW?",
        command_set=("SYST:REM:SOUR GPIB\n"
                     "SYST:REM:STAT REM\n"
                     "SOUR:POW "),
        check_instrument_value=False,
        ),
    BoolValue(
        'onoff',
        doc='Toggle output ON/OFF',
        command_set="OUTP ",
        true_string='ON', 
        false_string='OFF',
        check_instrument_value=False,
        ),
    ]
    
XantrexXDC300._build_class_with_features(features)