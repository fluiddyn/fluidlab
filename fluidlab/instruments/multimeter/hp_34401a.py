"""hp_34401a
============

.. autoclass:: HP34401a
   :members:
   :private-members:


"""

from fluidlab.instruments.iec60488 import (
    IEC60488)

from fluidlab.instruments.features import (
    FloatValue)

class HP34401a(IEC60488):
    """Driver for the multimeter HP 34401a.

    """

features = [
    FloatValue(
        'ohm',
        doc="""2-wire Ohm measurement""",
        command_get=':MEAS:RES?'),
    FloatValue(
        'ohm_4w',
        doc="""4-wire Ohm measurement""",
        command_get=':MEAS:FRES?'),
    FloatValue(
        'vdc',
        doc="""Voltage measurement""",
        command_get=':MEAS:VOLT:DC?')]

HP34401a._build_class_with_features(features)
