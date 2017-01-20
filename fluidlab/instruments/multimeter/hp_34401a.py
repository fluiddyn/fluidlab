"""hp_34401a
============

.. autoclass:: HP34401a
   :members:
   :private-members:


"""

from __future__ import print_function

__all__ = ["HP34401a"]

from fluidlab.instruments.iec60488 import IEC60488
from fluidlab.instruments.features import FloatValue, QueryCommand

class HP34401aValue(FloatValue):
    """
    Value class for HP34401a.
    Each "get" commands take optional range and resolution
    parameters.

    Range can be:
     - "DEF" for autorange, or alternatively autorange=True
     - "MIN" for the lowest range
     - "MAX" for the highest range 
     - or one acceptable value for the specified measurement

    Possible RES and FRES range values:
     - 100 Ohm (1 mA)
     - 1 kOhm (1 mA)
     - 10 kOhm (100 microA)
     - 100 kOhm (10 microA)
     - 1 MOhm (5 microA)
     - 10 MOhm (500 nA)
     - 100 MOhm (500 nA // 10 MOhm)

    Resolution can be:
     - "DEF" for default value (10 PLC), i.e. 5 1/2 digits
     - "MIN" for the smallest value (max resolution) or "BEST"
     - "MAX" for the largest value (min resolution)
     - or a value in PLC
    """

    def get(self, _range=None, resolution=None, autorange=False):
        """
        If no _range and no resolution is specified, call get command
        directely. This should not change current settings.
        """
        if resolution == "BEST":
            resolution = "MIN"
        if _range or resolution:
            if not _range:
                _range = "DEF"
            if not resolution:
                resolution = "DEF"
            command = self.command_get + " " + str(_range) + "," + str(resolution)
        else:
            command = self.command_get
        result = self._convert_from_str(
            self._interface.query(command))
        self._check_value(result)
        return result

class HP34401a(IEC60488):
    """Driver for the multimeter HP 34401a.

    """
    
    def print_configuration(self):
        s = self.query_configuration().strip()
        N=len(s)
        s=s[1:(N-1)].split(' ')
        t=s[1].split(",")
        print('function=' + s[0] + ', range=' + t[0] + ', resolution=' + t[1])

features = [
    HP34401aValue(
        'ohm',
        doc="""2-wire Ohm measurement""",
        command_get=':MEAS:RES?'),
    HP34401aValue(
        'ohm_4w',
        doc="""4-wire Ohm measurement""",
        command_get=':MEAS:FRES?'),
    HP34401aValue(
        'vdc',
        doc="""Voltage measurement""",
        command_get=':MEAS:VOLT:DC?'),
    QueryCommand(
        'query_configuration',
        'Query the multimeter present configuration and return a quoted string.',
        'CONF?')]

HP34401a._build_class_with_features(features)
