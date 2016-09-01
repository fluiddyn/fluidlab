#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""stanford_sr830
===============

.. autoclass:: StanfordSR830
   :members:
   :private-members:


"""

__all__ = ['StanfordSR830']

from fluidlab.instruments.iec60488 import IEC60488
from fluidlab.instruments.features import FloatValue

class StanfordSR830SenseValue(FloatValue):
    sense_values = [2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9, 500e-9, 1e-6,
                    2e-6, 5e-6, 10e-6, 20e-6, 50e-6, 100e-6, 200e-6, 500e-6, 1e-3,
                    2e-3, 5e-3, 10e-3, 20e-3, 50e-3, 100e-3, 200e-3, 500e-3, 1]

    def __init__(self):
        super(StanfordSR830SenseValue, self).__init__('sen',
                                                 doc="""Input sense""",
                                                 command_get="SENS ?",
                                                 command_set="SENS")
    
    def get(self):
        value = super(StanfordSR830SenseValue, self).get()
        return self.sense_values[int(value)]

    def set(self, value):
        super(StanfordSR830SenseValue, self).set(sense_values.index(value))
  
class StanfordSR830TCValue(FloatValue):
    tc_values = [10e-6,  30e-6, 100e-6, 300e-6, 1e-3, 3e-3, 10e-3, 30e-3,
                 100e-3, 300e-3, 1, 3, 10, 30, 100, 300, 1e3, 3e3, 10e3, 30e3]

    def __init__(self):
        super(StanfordSR830TCValue, self).__init__('tc',
                                                   doc="""Time constant""",
                                                   command_get="OFLT ?",
                                                   command_set="OFLT",
                                                   check_instrument_value=False)

    def get(self):
        value = super(StanfordSR830TCValue, self).get()
        return self.tc_values[int(value)]

    def set(self, value):
        super(StanfordSR830TCValue, self).set(self.tc_values.index(value))

class StanfordSR830OffsetValue(FloatValue):
    def _convert_from_str(self,value):
        values = value.split(',')
        return float(values[0])

class StanfordSR830ExpandValue(FloatValue):
    def _convert_from_str(self,value):
        values = value.split(',')
        return float(values[1])

class StanfordSR830(IEC60488):
    """Driver for Lock-in Amplifier Stanford 830.

    """

features = [
    FloatValue(
        'angle',
        doc="""Angle of the demodulated signal""",
        command_get="OUTP ? 4"),
    FloatValue(
        'freq',
        doc="""Frequency of the excitation""",
        command_get="FREQ ?",
        command_set="FREQ"),
    FloatValue(
        'mag',
        doc="""Magnitude of the demodulated signal""",
        command_get="OUTP ? 3"),
    StanfordSR830OffsetValue(
        'offset',
        doc="""Channel offset in % of Sen (channel value is 1 or 2)""",
        command_get="OEXP ? {channel}",
        command_set="OEXP {channel},{value},0",
        channel_argument=True),
    StanfordSR830ExpandValue(
        'expand',
        doc="""Channel expand coefficient (channel value is 1 or 2)""",
        command_get="OEXP ? {channel}",
        command_set="OEXP {channel},{value},0",
        channel_argument=True),
    FloatValue(
        'reference_phase',
        doc="""Phase shift in degrees""",
        command_get="PHAS ?",
        command_set="PHAS"),
    FloatValue(
        'vrms',
        doc="""RMS Voltage of the excitation""",
        command_get="SLVL ?",
        command_set="SLVL"),
    FloatValue(
        'x',
        doc="""Demodulated value at theta=0""",
        command_get="OUTP ? 1"),
    FloatValue(
        'y',
        doc="""Demodulated value at theta=90°""",
        command_get="OUTP ? 2"),
    StanfordSR830SenseValue(),
    StanfordSR830TCValue()]

StanfordSR830._build_class_with_features(features)
    
        
