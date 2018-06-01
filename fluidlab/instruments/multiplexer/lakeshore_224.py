"""lakeshore_224
================

.. autoclass:: Lakeshore224
   :members:
   :private-members:

"""

__all__ = ['Lakeshore224']

from fluidlab.instruments.iec60488 import IEC60488
from fluidlab.instruments.features import FloatValue, BoolValue,\
                                          IntValue

class Lakeshore224(IEC60488):
    """ Driver for the Lakeshore Model 224 Temperature Monitor
    """


    
    
features = [
    FloatValue(
        'temperature',
        doc='Reads temperature (in Kelvins)',
        command_get="KRDG? {channel:}",
        channel_argument=True),
    FloatValue(
        'sensor_value',
        doc='Reads sensor signal in sensor units',
        command_get="SRDG? {channel:}",
        channel_argument=True)
]

Lakeshore224._build_class_with_features(features)

if __name__ == '__main__':
    with Lakeshore224('GPIB0::12::INSTR') as ls:
        T_Pt, T_Diode = ls.temperature.get(['A', 'B'])
        print('T_Pt =', T_Pt, 'K')
        print('T_Diode =', T_Diode, 'K')
        R_Pt, V_Diode = ls.sensor_value.get(['A', 'B'])
        print('R_Pt =', R_Pt, 'Ohm')
        print('V_Diode =', V_Diode, 'V')