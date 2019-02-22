"""keithley_2400
================

.. autoclass:: Keithley2400
   :members:
   :private-members:


"""

__all__ = ["Keithley2400"]

from fluidlab.instruments.iec60488 import IEC60488
from fluidlab.instruments.features import (
    FloatValue,
    BoolValue,
    FloatScientificValue,
)


class Keithley2400(IEC60488):
    """Driver for the sourcemeter Keithley 2400.

    """


features = [
    BoolValue(
        "front",
        doc="True if route is using Front. False if Rear.",
        true_string="FRONT",
        false_string="REAR",
        command_get=":ROUT:TERM?",
        command_set=":ROUT:TERM",
    ),
    FloatScientificValue(
        "idc",
        doc="""Get output current/Set current setpoint""",
        command_get=':FUNC:CONC 0\n:FUNC "CURR"\n:FORM:ELEM CURR\n:READ?',
        command_set=":SOUR:FUNC CURR\n:SOUR:CURR:MODE FIX\n:SOUR:CURR:RANG:AUTO ON\n :SOUR:CURR:LEVEL",
        check_instrument_value=False,
    ),
    BoolValue(
        "onoff",
        doc="Toggle output ON/OFF",
        command_set=":OUTP",
        check_instrument_value=False,
        true_string="ON",
        false_string="OFF",
    ),
    FloatValue(
        "ohm_4w",
        doc="""Read impedance in 4-wire mode""",
        command_get=':SYST:RSEN ON\n:FUNC:CONC 0\n:RES:MODE MAN\n:FUNC "RES"\n:FORM:ELEM RES\n:READ?',
    ),
    FloatValue(
        "ohm",
        doc="""Read impedance in 2-wire mode""",
        command_get=':SYST:RSEN OFF\n:FUNC:CONC 0\n:RES:MODE MAN\n:FUNC "RES"\n:FORM:ELEM RES\n:READ?',
    ),
    FloatScientificValue(
        "vdc",
        doc="""Read output voltage/set voltage setpoint""",
        command_get=':FUNC:CONC 0\n:FUNC "VOLT"\n:FORM:ELEM VOLT\n:READ?',
        command_set=":SOUR:FUNC VOLT\n:SOUR:VOLT:MODE FIX\n:SOUR:VOLT:LEVEL",
        check_instrument_value=False,
    ),
    FloatScientificValue(
        "compliance_idc",
        doc="""Set compliance current level""",
        command_set=":SENS:CURR:DC:PROT:LEV",
        command_get=":SENS:CURR:DC:PROT:LEV?",
        check_instrument_value=False,
    ),
    FloatScientificValue(
        "compliance_vdc",
        doc="""Set compliance voltage level""",
        command_set=":SENS:VOLT:DC:PROT:LEV",
        command_get=":SENS:VOLT:DC:PROT:LEV?",
        check_instrument_value=False,
    ),
    FloatScientificValue(
        "range_vdc",
        doc="""Set adequate range voltage for the given expected voltage""",
        command_set=":SOUR:VOLT:RANG",
        command_get=":SOUR:VOLT:RANG?",
        check_instrument_value=False,
    ),
    FloatScientificValue(
        "range_idc",
        doc="""Set adequate current voltage for the given expected current""",
        command_set=":SOUR:CURR:RANG",
        command_get=":SOUR:CURR:RANG?",
        check_instrument_value=False,
    ),
]

Keithley2400._build_class_with_features(features)
